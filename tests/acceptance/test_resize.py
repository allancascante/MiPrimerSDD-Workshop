import unittest

from textual.widgets import Button, Input, ListView, Static, TextArea

from curso_pswe_07.dialogs import TaskDialog
from curso_pswe_07.models import Task, TaskSnapshot
from curso_pswe_07.service import TaskService
from curso_pswe_07.tui import TaskApp
from tests.unit.test_service import FakeStore


class ResizeTests(unittest.IsolatedAsyncioTestCase):
    async def test_small_startup_and_list_state_recovery(self):
        service = TaskService(FakeStore(TaskSnapshot(tuple(
            Task(index, f"Task {index}") for index in range(1, 101)
        ), 101)))
        app = TaskApp(service)
        async with app.run_test(size=(79, 23)) as pilot:
            self.assertEqual(type(app.screen).__name__, "ResizeGuard")
            await pilot.resize_terminal(80, 24)
            self.assertEqual(type(app.screen).__name__, "TaskView")
            app.screen.query_one("#pending", Button).focus()
            await pilot.press("enter", "end")
            view = app.screen
            listing = view.query_one(ListView)
            old_scroll = listing.scroll_y
            old_index = listing.index
            await pilot.resize_terminal(79, 24)
            await view.on_button_pressed(Button.Pressed(view.query_one("#add", Button)))
            await pilot.resize_terminal(100, 30)
            self.assertIs(app.screen, view)
            self.assertEqual(app.active_filter.value, "Pending")
            self.assertEqual(listing.index, old_index)
            self.assertIs(app.focused, listing)
            self.assertGreater(old_scroll, 0)
            self.assertGreater(listing.scroll_y, 0)

    async def test_temporary_notices_do_not_overlap_dialog_fields(self):
        for size in ((80, 24), (100, 30)):
            store = FakeStore()
            store.fail_load = True
            service = TaskService(store)
            service.create("Title")
            app = TaskApp(service)
            async with app.run_test(size=size) as pilot:
                await pilot.press("enter")
                for action, field in (("edit", "#title"), ("delete", "#delete-dialog")):
                    app.screen.query_one(f"#{action}", Button).focus()
                    await pilot.press("enter")
                    notice = app.screen.query_one("#notice", Static)
                    self.assertEqual(notice.region.height, 1)
                    self.assertGreaterEqual(notice.region.y, 3)
                    self.assertLessEqual(notice.region.bottom, app.screen.query_one(field).region.y)
                    self.assertLessEqual(app.screen.query_one("#cancel").region.bottom, size[1] - 1)
                    await pilot.press("escape")

    async def test_editor_survives_guard_and_stale_mutation_events(self):
        store = FakeStore()
        store.fail_load = True
        app = TaskApp(TaskService(store))
        async with app.run_test() as pilot:
            app.screen.query_one("#add", Button).focus()
            await pilot.press("enter", *"Draft")
            editor = app.screen
            self.assertIsInstance(editor, TaskDialog)
            await pilot.press("tab", *"description")
            previous_focus = app.focused
            for size in ((79, 24), (80, 23), (50, 12)):
                await pilot.resize_terminal(*size)
                self.assertEqual(type(app.screen).__name__, "ResizeGuard")
                self.assertIn("80", str(app.screen.query_one("#resize", Static).content))
                self.assertIn("TEMPORARY", str(app.screen.query_one("#resize", Static).content))
                editor.on_button_pressed(Button.Pressed(editor.query_one("#save", Button)))
                await pilot.press("enter", "space", "escape")
                self.assertEqual(app.service.list_tasks(), ())
                self.assertEqual(sum(type(screen).__name__ == "ResizeGuard" for screen in app.screen_stack), 1)
            await pilot.resize_terminal(100, 30)
            self.assertIs(app.screen, editor)
            self.assertIs(app.focused, previous_focus)
            self.assertEqual(editor.query_one(Input).value, "Draft")
            self.assertEqual(editor.query_one(TextArea).text, "description")
            await pilot.press("tab", "enter")
            self.assertEqual(app.service.get(1).description, "description")
            self.assertEqual(store.saves, 0)

    async def test_delete_guard_blocks_confirmation_and_preserves_focus(self):
        app = TaskApp(TaskService(FakeStore(TaskSnapshot((Task(1, "Keep"),), 2))))
        async with app.run_test() as pilot:
            await pilot.press("enter")
            app.screen.query_one("#delete", Button).focus()
            await pilot.press("enter")
            dialog = app.screen
            dialog.query_one("#confirm", Button).focus()
            await pilot.resize_terminal(79, 24)
            dialog.on_button_pressed(Button.Pressed(dialog.query_one("#confirm", Button)))
            self.assertEqual(len(app.service.list_tasks()), 1)
            await pilot.resize_terminal(80, 24)
            self.assertIs(app.screen, dialog)
            self.assertEqual(app.focused.id, "confirm")
            await pilot.press("escape")
            self.assertEqual(app.focused.id, "delete")

    async def test_long_content_literal_render_and_layout_at_supported_sizes(self):
        title = "[red]" + "T" * 200 + "\x1b[31m"
        description = "\n".join(f"line {index}: " + "D" * 40 for index in range(50))
        snapshot = TaskSnapshot(tuple(
            Task(index, title if index == 100 else f"Task {index}", description)
            for index in range(1, 101)
        ), 101)
        for size in ((80, 24), (100, 30)):
            app = TaskApp(TaskService(FakeStore(snapshot)))
            async with app.run_test(size=size) as pilot:
                await pilot.press("end")
                self.assertEqual(app.screen.query_one(ListView).index, 99)
                await pilot.press("enter")
                details = app.screen.query_one("#details", Static)
                self.assertIn("[red]", str(details.content))
                self.assertIn("\\x1b", str(details.content))
                self.assertNotIn("\x1b", str(details.content))
                await pilot.press("pagedown")
                self.assertGreater(app.screen.query_one("#body").scroll_y, 0)
                for widget in app.screen.query(Button):
                    self.assertGreater(widget.region.width, 0)
                    self.assertLessEqual(widget.region.right, size[0])
                    self.assertLessEqual(widget.region.bottom, size[1])
                app.screen.query_one("#edit", Button).focus()
                await pilot.press("enter")
                self.assertEqual(app.screen.query_one(Input).value, title)
                self.assertEqual(app.screen.query_one(TextArea).text, description)
                for selector in ("#title", "#description", "#save", "#cancel", "#error"):
                    region = app.screen.query_one(selector).region
                    self.assertGreater(region.height, 0)
                    self.assertLessEqual(region.bottom, size[1])
                await pilot.press("escape")
                app.screen.query_one("#delete", Button).focus()
                await pilot.press("enter")
                for selector in ("#confirm", "#cancel", "#error"):
                    region = app.screen.query_one(selector).region
                    self.assertGreater(region.height, 0)
                    self.assertLessEqual(region.bottom, size[1] - 1)
