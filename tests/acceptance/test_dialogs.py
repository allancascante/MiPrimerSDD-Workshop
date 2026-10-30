import unittest

from textual.widgets import Button, Input, TextArea, Static

from curso_pswe_07.service import TaskService
from curso_pswe_07.models import Task, TaskSnapshot
from curso_pswe_07.tui import TaskApp
from tests.unit.test_service import FakeStore


class AddDialogTests(unittest.IsolatedAsyncioTestCase):
    async def test_field_isolation_focus_cycle_and_retry(self):
        store = FakeStore()
        app = TaskApp(TaskService(store))
        async with app.run_test() as pilot:
            app.screen.query_one("#add", Button).focus()
            await pilot.press("enter", *"Add Delete Done", "enter")
            self.assertEqual(app.service.list_tasks(), ())
            await pilot.press("tab", *"description", "enter", *"second line", "tab")
            self.assertEqual(app.focused.id, "save")
            await pilot.press("tab", "tab")
            self.assertEqual(app.focused.id, "title")
            await pilot.press("tab")
            self.assertIn("newline", str(app.screen.query_one("#hints", Static).content))
            await pilot.press("shift+tab")
            await pilot.press("shift+tab")
            self.assertEqual(app.focused.id, "cancel")
            await pilot.press("shift+tab")
            store.fail_save = True
            await pilot.press("enter")
            self.assertIn("Cannot save", str(app.screen.query_one("#error", Static).content))
            self.assertEqual(app.screen.query_one(TextArea).text, "description\nsecond line")
            store.fail_save = False
            await pilot.press("tab", "tab", "enter")
            self.assertEqual(len(app.service.list_tasks()), 1)
            self.assertEqual(app.focused.id, "add")

    async def test_validation_focus_draft_and_keyboard_cancel(self):
        service = TaskService(FakeStore())
        app = TaskApp(service)
        async with app.run_test() as pilot:
            app.screen.query_one("#add", Button).focus()
            await pilot.press("enter")
            self.assertIsInstance(app.focused, Input)
            await pilot.press("space", "tab")
            await pilot.press(*"description", "tab", "enter")
            self.assertIn("Title is required", str(app.screen.query_one("#error", Static).content))
            self.assertIsInstance(app.focused, Input)
            self.assertEqual(app.screen.query_one(TextArea).text, "description")
            await pilot.press("shift+tab")
            self.assertEqual(app.focused.id, "cancel")
            await pilot.press("enter")
            self.assertEqual(service.list_tasks(), ())


class EditDeleteDialogTests(unittest.IsolatedAsyncioTestCase):
    async def test_invalid_and_failed_edit_keep_values_and_cancel_is_safe(self):
        store = FakeStore(TaskSnapshot((Task(1, "Original", "description"),), 2))
        app = TaskApp(TaskService(store))
        async with app.run_test() as pilot:
            await pilot.press("enter")
            app.screen.query_one("#edit", Button).focus()
            await pilot.press("enter", "space", "tab", "tab", "enter")
            self.assertIn("Title is required", str(app.screen.query_one("#error", Static).content))
            self.assertEqual(app.screen.query_one(TextArea).text, "description")
            await pilot.press(*"Changed", "tab", "tab")
            store.fail_save = True
            await pilot.press("enter")
            self.assertEqual(app.screen.query_one(Input).value, "Changed")
            self.assertEqual(app.service.get(1).title, "Original")
            await pilot.press("escape")
            self.assertEqual(app.focused.id, "edit")
            app.screen.query_one("#delete", Button).focus()
            await pilot.press("enter", "escape")
            self.assertEqual(app.focused.id, "delete")
            self.assertEqual(len(app.service.list_tasks()), 1)

    async def test_edit_prefill_cancel_save_and_safe_delete(self):
        service = TaskService(FakeStore(TaskSnapshot((Task(1, "Before", "description", True),), 2)))
        app = TaskApp(service)
        async with app.run_test() as pilot:
            await pilot.press("enter")
            app.screen.query_one("#edit", Button).focus()
            await pilot.press("enter")
            self.assertEqual(app.screen.query_one(Input).value, "Before")
            self.assertEqual(app.screen.query_one(TextArea).text, "description")
            await pilot.press(*"Discarded", "escape")
            self.assertEqual(service.get(1).title, "Before")
            app.screen.query_one("#edit", Button).focus()
            await pilot.press("enter", *"After", "tab", "f7", "backspace", "tab", "enter")
            self.assertEqual(service.get(1), Task(1, "After", "", True))
            app.screen.query_one("#delete", Button).focus()
            await pilot.press("enter")
            self.assertEqual(app.focused.id, "cancel")
            await pilot.press("enter")
            self.assertEqual(len(service.list_tasks()), 1)
            app.screen.query_one("#delete", Button).focus()
            await pilot.press("enter")
            app.screen.query_one("#confirm", Button).focus()
            await pilot.press("enter")
            self.assertEqual(service.list_tasks(), ())
            self.assertIn("No tasks yet", str(app.screen.query_one("#empty", Static).content))

    async def test_failed_delete_stays_in_dialog(self):
        store = FakeStore(TaskSnapshot((Task(1, "Keep"),), 2))
        app = TaskApp(TaskService(store))
        async with app.run_test() as pilot:
            await pilot.press("enter")
            app.screen.query_one("#delete", Button).focus()
            await pilot.press("enter")
            store.fail_save = True
            app.screen.query_one("#confirm", Button).focus()
            await pilot.press("enter")
            self.assertIn("Cannot save", str(app.screen.query_one("#error", Static).content))
            self.assertEqual(app.service.get(1).title, "Keep")
