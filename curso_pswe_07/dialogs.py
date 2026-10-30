"""Modal task editor."""

from typing import TYPE_CHECKING, cast

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual import events
from textual.screen import ModalScreen
from textual.widgets import Button, Input, Static, TextArea

from .service import StorageError

if TYPE_CHECKING:
    from .tui import TaskApp


def display_text(value: str) -> str:
    return "".join(
        char if char in "\n\t" or char.isprintable() else repr(char)[1:-1]
        for char in value
    )


class MenuButton(Button):
    BINDINGS = [("space", "press", "Activate")]
    def on_focus(self) -> None:
        if not str(self.label).startswith("> "):
            self.label = f"> {self.label}"

    def on_blur(self) -> None:
        self.label = str(self.label).removeprefix("> ")

    def on_key(self, event: events.Key) -> None:
        if event.key in ("left", "up", "right", "down"):
            buttons = [button for button in self.parent.query(Button) if not button.disabled]
            offset = -1 if event.key in ("left", "up") else 1
            buttons[(buttons.index(self) + offset) % len(buttons)].focus()
            event.stop()
            event.prevent_default()


class TaskDialog(ModalScreen[bool]):
    BINDINGS = [("escape", "cancel", "Cancel")]

    def __init__(self, task_id: int | None = None) -> None:
        super().__init__()
        self.task_id = task_id

    def compose(self) -> ComposeResult:
        service = cast("TaskApp", self.app).service
        task = service.get(self.task_id) if self.task_id is not None else None
        yield Static("Curso-PSWE-07 | " + ("Edit task" if task else "Add task"), id="heading")
        yield Static(cast("TaskApp", self.app).service.notice, id="notice", markup=False)
        with Vertical(id="dialog"):
            yield Static("Title")
            yield Input(task.title if task else "", id="title")
            yield Static("Description")
            yield TextArea(task.description if task else "", id="description", tab_behavior="focus")
            yield Static("", id="error", markup=False)
            with Horizontal(classes="actions"):
                yield MenuButton("Save", id="save")
                yield MenuButton("Cancel", id="cancel")
        yield Static("Tab: focus | Enter: action | Esc: Cancel", id="hints")

    def on_mount(self) -> None:
        self.query_one("#title", Input).focus()

    def on_descendant_focus(self, event: events.DescendantFocus) -> None:
        hints = (
            "Enter: newline | F7: select all | Tab: next | Esc: Cancel"
            if isinstance(event.widget, TextArea)
            else "Type title | Tab: description | Esc: Cancel"
            if isinstance(event.widget, Input)
            else "Tab/Arrows: focus | Enter/Space: action | Esc: Cancel"
        )
        self.query_one("#hints", Static).update(hints)

    def action_cancel(self) -> None:
        if cast("TaskApp", self.app).can_interact(self):
            self.dismiss(False)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        event.stop()
        if not cast("TaskApp", self.app).can_interact(self):
            return
        if event.button.id == "cancel":
            self.action_cancel()
        elif event.button.id == "save":
            app = cast("TaskApp", self.app)
            try:
                title = self.query_one("#title", Input).value
                description = self.query_one("#description", TextArea).text
                if self.task_id is None:
                    app.service.create(title, description)
                else:
                    app.service.edit(self.task_id, title, description)
            except (ValueError, StorageError) as error:
                self.query_one("#error", Static).update(str(error))
                self.query_one("#title", Input).focus()
            else:
                self.dismiss(True)


class DeleteDialog(ModalScreen[bool]):
    BINDINGS = [("escape", "cancel", "Cancel")]

    def __init__(self, task_id: int) -> None:
        super().__init__()
        self.task_id = task_id

    def compose(self) -> ComposeResult:
        yield Static("Curso-PSWE-07 | Delete task", id="heading")
        yield Static(cast("TaskApp", self.app).service.notice, id="notice", markup=False)
        with Vertical(id="delete-dialog"):
            yield Static("Delete this task? This cannot be undone.", markup=False)
            yield Static(display_text(cast("TaskApp", self.app).service.get(self.task_id).title),
                         markup=False, id="delete-title")
            yield Static("", id="error", markup=False)
            with Horizontal(classes="actions"):
                yield MenuButton("Confirm", id="confirm", variant="error")
                yield MenuButton("Cancel", id="cancel")
        yield Static("Tab: focus | Enter: action | Esc: Cancel", id="hints")

    def on_mount(self) -> None:
        self.query_one("#cancel", Button).focus()

    def action_cancel(self) -> None:
        if cast("TaskApp", self.app).can_interact(self):
            self.dismiss(False)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        event.stop()
        if not cast("TaskApp", self.app).can_interact(self):
            return
        if event.button.id == "cancel":
            self.action_cancel()
        elif event.button.id == "confirm":
            try:
                cast("TaskApp", self.app).service.delete(self.task_id)
            except StorageError as error:
                self.query_one("#error", Static).update(str(error))
            else:
                self.dismiss(True)
