import unittest

from textual.widgets import Button, Input, ListView, Static

from curso_pswe_07.service import TaskService
from curso_pswe_07.models import Task, TaskSnapshot
from curso_pswe_07.tui import TaskApp
from tests.unit.test_service import FakeStore


class AddViewTests(unittest.IsolatedAsyncioTestCase):
    async def test_ascii_frames_fixed_actions_and_keyboard_focus_at_supported_sizes(self):
        for size in ((80, 24), (100, 30)):
            app = TaskApp(TaskService(FakeStore(TaskSnapshot((Task(1, "Completed", done=True),), 2))))
            async with app.run_test(size=size) as pilot:
                heading = app.screen.query_one("#heading", Static)
                body = app.screen.query_one("#body")
                actions = app.screen.query_one(".actions")
                hints = app.screen.query_one("#hints", Static)
                self.assertEqual(heading.styles.border_top[0], "ascii")
                self.assertEqual(body.styles.border_top[0], "ascii")
                self.assertEqual(heading.region.width, size[0])
                self.assertLessEqual(body.region.bottom, actions.region.y)
                self.assertEqual(hints.region.bottom, size[1])
                self.assertTrue(app.screen.query_one(ListView).children[0].has_class("completed"))
                self.assertIn("All", str(app.screen.query_one("#filter", Static).content))
                app.screen.query_one("#add", Button).focus()
                await pilot.pause()
                self.assertTrue(str(app.focused.label).startswith("> "))
                await pilot.press("enter")
                dialog = app.screen.query_one("#dialog")
                self.assertEqual(dialog.styles.border_top[0], "ascii")
                self.assertLessEqual(dialog.region.bottom, size[1] - 1)
                await pilot.press("escape")

    async def test_interrupt_discards_editor_and_exits_with_130(self):
        app = TaskApp(TaskService(FakeStore()))
        async with app.run_test() as pilot:
            app.screen.query_one("#add", Button).focus()
            await pilot.press("enter", *"Draft", "tab", *"text", "ctrl+c")
        self.assertEqual(app.return_code, 130)
        self.assertEqual(app.service.list_tasks(), ())

    async def test_add_open_back(self):
        service = TaskService(FakeStore())
        app = TaskApp(service)
        async with app.run_test() as pilot:
            self.assertIn("Curso-PSWE-07", str(app.screen.query_one("#heading", Static).content))
            self.assertIn("No tasks", str(app.screen.query_one("#empty", Static).content))
            app.screen.query_one("#add", Button).focus()
            await pilot.press("enter")
            await pilot.press(*"Prepare")
            await pilot.press("tab", "tab", "enter")
            self.assertEqual(service.get(1).title, "Prepare")
            app.screen.query_one(ListView).focus()
            await pilot.press("enter")
            self.assertIn("No description", str(app.screen.query_one("#details", Static).content))
            await pilot.press("escape")
            self.assertIsNotNone(app.screen.query_one("#add", Button))

    async def test_cancel_add_keeps_store_empty(self):
        service = TaskService(FakeStore())
        app = TaskApp(service)
        async with app.run_test() as pilot:
            app.screen.query_one("#add", Button).focus()
            await pilot.press("enter")
            await pilot.press(*"draft", "escape")
            self.assertEqual(service.list_tasks(), ())


class CompletionViewTests(unittest.IsolatedAsyncioTestCase):
    async def test_selected_row_marker_and_status_changes_under_prior_filter(self):
        service = TaskService(FakeStore(TaskSnapshot((Task(1, "one"), Task(2, "two")), 3)))
        app = TaskApp(service)
        async with app.run_test() as pilot:
            def markers():
                return [str(item.query_one(Static).content).startswith("> ")
                        for item in app.screen.query_one(ListView).children]
            self.assertEqual(markers(), [True, False])
            await pilot.press("down")
            self.assertEqual(markers(), [False, True])
            app.screen.query_one("#pending", Button).focus()
            await pilot.press("enter", "enter")
            self.assertEqual(app.screen.task_id, 2)
            app.screen.query_one("#toggle", Button).focus()
            await pilot.press("enter")
            self.assertTrue(str(app.screen.query_one("#toggle", Button).label).startswith("> "))
            await pilot.press("escape")
            self.assertEqual(app.screen.visible_ids, [1])
            app.screen.query_one("#done", Button).focus()
            await pilot.press("enter", "enter")
            app.screen.query_one("#toggle", Button).focus()
            await pilot.press("enter", "escape")
            self.assertEqual(app.screen.visible_ids, [])

    async def test_keyboard_groups_selection_and_disabled_commands(self):
        app = TaskApp(TaskService(FakeStore(TaskSnapshot(
            tuple(Task(index, f"Task {index}") for index in range(1, 101)), 101
        ))))
        async with app.run_test() as pilot:
            await pilot.press("pagedown")
            self.assertGreater(app.screen.query_one(ListView).index, 0)
            await pilot.press("end")
            self.assertEqual(app.screen.query_one(ListView).index, 99)
            await pilot.press("home")
            self.assertEqual(app.screen.query_one(ListView).index, 0)
            app.screen.query_one("#all", Button).focus()
            await pilot.press("right")
            self.assertEqual(app.focused.id, "pending")
            await pilot.press("space")
            self.assertEqual(app.active_filter.value, "Pending")
            app.screen.query_one("#add", Button).focus()
            await pilot.press("right")
            self.assertEqual(app.focused.id, "open")
            await pilot.press("ctrl+p", "f2", "x")
            self.assertEqual(type(app.screen).__name__, "TaskView")
            self.assertEqual(len(app.service.list_tasks()), 100)

    async def test_filters_status_and_add_under_done(self):
        service = TaskService(FakeStore(TaskSnapshot((Task(1, "First"),), 2)))
        app = TaskApp(service)
        async with app.run_test() as pilot:
            await pilot.press("enter")
            app.screen.query_one("#toggle", Button).focus()
            await pilot.press("enter")
            self.assertTrue(service.get(1).done)
            self.assertIn("Mark as not done", str(app.screen.query_one("#toggle", Button).label))
            await pilot.press("escape")
            app.screen.query_one("#pending", Button).focus()
            await pilot.press("enter")
            self.assertIn("No tasks match", str(app.screen.query_one("#empty", Static).content))
            app.screen.query_one("#done", Button).focus()
            await pilot.press("enter")
            app.screen.query_one("#add", Button).focus()
            await pilot.press("enter", *"Another", "tab", "tab", "enter")
            self.assertEqual(app.screen.visible_ids, [1])
            self.assertEqual(app.active_filter.value, "Done")
