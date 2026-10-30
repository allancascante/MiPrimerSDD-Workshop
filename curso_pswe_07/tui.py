"""Full-screen task views. Storage is accessible only through the service."""

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual import events
from textual.containers import Horizontal, VerticalScroll
from textual.screen import ModalScreen, Screen
from textual.widgets import Button, ListItem, ListView, Static
from typing import cast

from .dialogs import DeleteDialog, MenuButton, TaskDialog, display_text
from .models import CompletionFilter, Task, TaskSnapshot
from .service import StorageError, TaskService


class TaskRow(ListItem):
    def __init__(self, task_id: int, content: str, done: bool) -> None:
        self.content = content
        super().__init__(Static("  " + content, markup=False), id=f"task-{task_id}",
                         classes="completed" if done else "")

    def watch_highlighted(self, value: bool) -> None:
        super().watch_highlighted(value)
        self.query_one(Static).update(("> " if value else "  ") + self.content)

    def update_task(self, task: Task) -> None:
        content = display_text(f"{'Done' if task.done else 'Pending'} | {task.title}")
        if self.content != content:
            self.content = content
            self.query_one(Static).update(("> " if self.highlighted else "  ") + content)
        self.set_class(task.done, "completed")


class TaskList(ListView):
    BINDINGS = [
        ("home", "move_to('first')", "First"),
        ("end", "move_to('last')", "Last"),
        ("pageup", "move_to('up')", "Page up"),
        ("pagedown", "move_to('down')", "Page down"),
    ]

    def action_move_to(self, destination: str) -> None:
        if not self.children:
            return
        last = len(self.children) - 1
        page = max(1, self.size.height - 1)
        self.index = (
            0 if destination == "first" else last if destination == "last"
            else max(0, min(last, (self.index or 0) + (page if destination == "down" else -page)))
        )


class DetailBody(VerticalScroll):
    can_focus = True


class ResizeGuard(ModalScreen[None]):
    def compose(self) -> ComposeResult:
        service = cast("TaskApp", self.app).service
        yield Static(
            "Curso-PSWE-07\nResize terminal to at least 80 columns x 24 rows."
            + ("\nTEMPORARY LIST: not saved; lost on close." if service.temporary else ""),
            id="resize", markup=False,
        )


class TaskView(Screen[None]):
    BINDINGS = [("escape", "back", "Back")]

    def __init__(self, service: TaskService, task_id: int | None = None) -> None:
        super().__init__()
        self.service = service
        self.task_id = task_id
        self.visible_ids: list[int] = []
        self.rendered_snapshot: TaskSnapshot | None = None
        self.rendered_filter: CompletionFilter | None = None

    def compose(self) -> ComposeResult:
        yield Static("Curso-PSWE-07 | " + ("List" if self.task_id is None else "Detail"),
                     id="heading")
        yield Static(self.service.notice, id="notice", markup=False)
        with DetailBody(id="body", disabled=False):
            if self.task_id is None:
                with Horizontal(id="filters"):
                    for filter_by in CompletionFilter:
                        yield MenuButton(filter_by.value, id=filter_by.value.lower())
                yield Static("", id="filter")
                yield Static("", id="empty")
                yield TaskList(id="tasks")
            else:
                task = self.service.get(self.task_id)
                yield Static(
                    display_text(f"{task.title}\n\n{task.description or 'No description'}"
                                 f"\n\nStatus: {'Done' if task.done else 'Pending'}"),
                    id="details", markup=False,
                )
        with Horizontal(classes="actions"):
            if self.task_id is None:
                yield MenuButton("Add task", id="add")
                yield MenuButton("Open", id="open")
            else:
                yield MenuButton("Back", id="back")
                task = self.service.get(self.task_id)
                yield MenuButton("Mark as not done" if task.done else "Mark as done", id="toggle")
                yield MenuButton("Edit", id="edit")
                yield MenuButton("Delete", id="delete", variant="error")
            yield MenuButton("Exit", id="exit")
        yield Static(self.service.load_error, id="message", markup=False)
        yield Static("Tab: focus | Arrows: select | Enter: action | Esc: Back", id="hints")

    async def on_mount(self) -> None:
        if self.task_id is None:
            self.query_one("#body").can_focus = False
            await self.refresh_tasks()
        else:
            self.query_one("#body").focus()

    def on_descendant_focus(self, event: events.DescendantFocus) -> None:
        hints = (
            "Arrows/Home/End/PageUp/PageDown: select | Enter: Open | Tab: menu"
            if isinstance(event.widget, ListView)
            else "Arrows/PageUp/PageDown: scroll | Tab: menu | Esc: Back"
            if event.widget.id == "body"
            else "Tab/Arrows: focus | Enter/Space: action | Esc: Back | Ctrl+Q: Exit"
        )
        self.query_one("#hints", Static).update(hints)

    async def refresh_tasks(self) -> None:
        app = cast("TaskApp", self.app)
        tasks = self.service.list_tasks(app.active_filter)
        listing = self.query_one(ListView)
        old_index = listing.index or 0
        selected_id = self.visible_ids[old_index] if self.visible_ids and old_index < len(self.visible_ids) else None
        self.visible_ids = [task.id for task in tasks]
        self.rendered_snapshot = self.service.snapshot
        self.rendered_filter = app.active_filter
        wanted = {f"task-{task.id}": index for index, task in enumerate(tasks)}
        existing = {row.id: row for row in listing.children}
        await listing.remove_children([row for row in listing.children if row.id not in wanted])
        await listing.extend(
            TaskRow(task.id, display_text(
                f"{'Done' if task.done else 'Pending'} | {task.title}"
            ), task.done)
            for task in tasks if f"task-{task.id}" not in existing
        )
        listing.sort_children(key=lambda row: wanted[row.id or ""])
        for task in tasks:
            row = existing.get(f"task-{task.id}")
            if isinstance(row, TaskRow):
                row.update_task(task)
        self.query_one("#empty", Static).update(
            "" if tasks else "No tasks yet. Add a task!" if not self.service.snapshot.tasks
            else "No tasks match this filter."
        )
        self.query_one("#filter", Static).update(f"> Filter: {app.active_filter.value}")
        self.query_one("#open", Button).disabled = not tasks
        if tasks:
            listing.index = (
                self.visible_ids.index(selected_id) if selected_id in self.visible_ids
                else min(old_index, len(tasks) - 1)
            )
            listing.focus()
        else:
            self.query_one("#add", Button).focus()

    def open_task(self) -> None:
        if not cast("TaskApp", self.app).can_interact(self):
            return
        index = self.query_one(ListView).index
        if index is not None and index < len(self.visible_ids):
            self.app.push_screen(TaskView(self.service, self.visible_ids[index]))

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        self.open_task()

    async def added(self, saved: bool | None) -> None:
        if saved:
            if self.rendered_snapshot != self.service.snapshot:
                await self.refresh_tasks()
            self.query_one("#message", Static).update(self.service.mutation_message)
        self.query_one("#add", Button).focus()

    def edited(self, saved: bool | None) -> None:
        if saved:
            self.refresh_detail()
            self.query_one("#message", Static).update(self.service.mutation_message)
        self.query_one("#edit", Button).focus()

    def deleted(self, saved: bool | None) -> None:
        if saved:
            self.app.pop_screen()
            self.app.screen.query_one("#message", Static).update(self.service.mutation_message)
        else:
            self.query_one("#delete", Button).focus()

    def refresh_detail(self) -> None:
        assert self.task_id is not None
        task = self.service.get(self.task_id)
        toggle = self.query_one("#toggle", Button)
        toggle.label = (
            ("> " if toggle.has_focus else "")
            + ("Mark as not done" if task.done else "Mark as done")
        )
        self.query_one("#details", Static).update(display_text(
            f"{task.title}\n\n{task.description or 'No description'}"
            f"\n\nStatus: {'Done' if task.done else 'Pending'}"
        ))

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        event.stop()
        app = cast("TaskApp", self.app)
        if not app.can_interact(self):
            return
        if event.button.id in ("all", "pending", "done"):
            app.active_filter = CompletionFilter(event.button.id.capitalize())
            await self.refresh_tasks()
            return
        match event.button.id:
            case "add":
                self.app.push_screen(TaskDialog(), self.added)
            case "open":
                self.open_task()
            case "back":
                self.action_back()
            case "exit":
                self.app.exit()
            case "edit":
                self.app.push_screen(TaskDialog(self.task_id), self.edited)
            case "delete":
                assert self.task_id is not None
                self.app.push_screen(DeleteDialog(self.task_id), self.deleted)
            case "toggle":
                assert self.task_id is not None
                try:
                    self.service.set_done(self.task_id, not self.service.get(self.task_id).done)
                except StorageError as error:
                    self.query_one("#message", Static).update(str(error))
                else:
                    self.query_one("#message", Static).update(self.service.mutation_message)
                    self.refresh_detail()

    async def on_screen_resume(self) -> None:
        app = cast("TaskApp", self.app)
        if (self.task_id is None and self.is_mounted
                and (self.rendered_snapshot != self.service.snapshot
                     or self.rendered_filter != app.active_filter)):
            await self.refresh_tasks()

    def action_back(self) -> None:
        if self.task_id is not None and cast("TaskApp", self.app).can_interact(self):
            self.app.pop_screen()


class TaskApp(App[int]):
    CSS_PATH = "styles.tcss"
    ENABLE_COMMAND_PALETTE = False
    BINDINGS = [
        Binding("ctrl+q", "quit", "Exit", priority=True),
        Binding("ctrl+c", "interrupt", "Interrupt", priority=True),
    ]
    TITLE = "Curso-PSWE-07"

    def __init__(self, service: TaskService) -> None:
        super().__init__()
        self.service = service
        self.active_filter = CompletionFilter.ALL
        self.resize_guard: ResizeGuard | None = None
        self._view_ready = False

    async def on_mount(self) -> None:
        await self.push_screen(TaskView(self.service))
        self._view_ready = True
        self.check_size()

    def can_interact(self, screen: Screen) -> bool:
        return self.size.width >= 80 and self.size.height >= 24 and self.screen is screen

    def on_resize(self, event: events.Resize) -> None:
        if self._view_ready:
            self.check_size(event.size.width, event.size.height)

    def check_size(self, width: int | None = None, height: int | None = None) -> None:
        small = (self.size.width if width is None else width) < 80 or (
            self.size.height if height is None else height
        ) < 24
        if small and self.resize_guard is None:
            self.resize_guard = ResizeGuard()
            self.push_screen(self.resize_guard)
        elif not small and self.resize_guard is not None:
            self.resize_guard.dismiss()
            self.resize_guard = None

    def action_quit(self) -> None:
        self.exit(return_code=0)

    def action_interrupt(self) -> None:
        self.exit(return_code=130)
