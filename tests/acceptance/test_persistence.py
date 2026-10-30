from pathlib import Path
from tempfile import TemporaryDirectory
import asyncio
import platform
import time
import unittest

from textual.widgets import Button, Input, Static

from curso_pswe_07.models import TaskSnapshot
from curso_pswe_07.service import TaskService
from curso_pswe_07.storage import JsonTaskStore
from curso_pswe_07.tui import TaskApp
from tests.unit.test_service import FakeStore


class PersistenceTests(unittest.IsolatedAsyncioTestCase):
    async def test_sc005_save_and_filter_actions_under_one_second(self):
        with TemporaryDirectory() as directory:
            store = JsonTaskStore(Path(directory) / "tasks.json")
            from curso_pswe_07.models import Task
            from textual.widgets import TextArea

            store.save(TaskSnapshot(tuple(
                Task(index, f"Task {index}", done=index % 2 == 0)
                for index in range(1, 101)
            ), 101))
            app = TaskApp(TaskService(store))
            measurements = []
            async with app.run_test(size=(80, 24)) as pilot:
                async def activate(button):
                    button.focus()
                    start = time.monotonic()
                    rendered = asyncio.Event()
                    button.press()
                    await pilot.pause()
                    app.call_after_refresh(rendered.set)
                    await asyncio.wait_for(rendered.wait(), timeout=1)
                    elapsed = time.monotonic() - start
                    measurements.append((button.id, round(elapsed, 4)))
                    self.assertLess(elapsed, 1.0, measurements)

                for filter_id in ("pending", "done", "all"):
                    await activate(app.screen.query_one(f"#{filter_id}", Button))
                    self.assertEqual(app.active_filter.value.lower(), filter_id)
                await pilot.press("enter")
                edited_id = app.screen.task_id
                await activate(app.screen.query_one("#toggle", Button))
                app.screen.query_one("#edit", Button).focus()
                await pilot.press("enter")
                app.screen.query_one(Input).value = "Changed"
                app.screen.query_one(TextArea).load_text("description")
                await activate(app.screen.query_one("#save", Button))
                self.assertEqual(next(task.title for task in store.load().tasks if task.id == edited_id), "Changed")
                await pilot.press("escape")
                app.screen.query_one("#add", Button).focus()
                await pilot.press("enter")
                app.screen.query_one(Input).value = "New"
                await activate(app.screen.query_one("#save", Button))
                self.assertEqual(len(store.load().tasks), 101)
                app.screen.query_one("#open", Button).focus()
                await pilot.press("enter")
                app.screen.query_one("#delete", Button).focus()
                await pilot.press("enter")
                await activate(app.screen.query_one("#confirm", Button))
                self.assertEqual(len(store.load().tasks), 100)
            print(f"SC-005: {platform.system()} Python {platform.python_version()}, "
                  f"80x24, 100 tasks, actions through rendered result: {measurements}")

    async def test_edit_delete_reopen_in_persistent_and_temporary_modes(self):
        with TemporaryDirectory() as directory:
            path = Path(directory) / "tasks.json"
            store = JsonTaskStore(path)
            seed = TaskService(store)
            seed.create("Original", "text")
            seed.create("Delete me")
            for temporary in (False, True):
                if temporary:
                    path.write_text("corrupt original")
                service = TaskService(store)
                if temporary:
                    service.create("Original", "text")
                    service.create("Delete me")
                app = TaskApp(service)
                async with app.run_test() as pilot:
                    await pilot.press("enter")
                    app.screen.query_one("#edit", Button).focus()
                    await pilot.press("enter", *"Changed", "tab", "tab", "enter")
                    await pilot.press("escape", "down", "enter")
                    app.screen.query_one("#delete", Button).focus()
                    await pilot.press("enter")
                    app.screen.query_one("#confirm", Button).focus()
                    await pilot.press("enter")
                    self.assertEqual([task.title for task in service.list_tasks()], ["Changed"])
                    self.assertEqual(
                        str(app.screen.query_one("#message", Static).content),
                        service.mutation_message,
                    )
                reopened = TaskService(store)
                if temporary:
                    self.assertEqual(path.read_text(), "corrupt original")
                    self.assertEqual(reopened.list_tasks(), ())
                else:
                    self.assertEqual([task.title for task in reopened.list_tasks()], ["Changed"])

    async def test_create_and_status_survive_new_app(self):
        with TemporaryDirectory() as directory:
            store = JsonTaskStore(Path(directory) / "tasks.json")
            service = TaskService(store)
            app = TaskApp(service)
            async with app.run_test() as pilot:
                app.screen.query_one("#add", Button).focus()
                await pilot.press("enter", *"Saved", "tab", "tab", "enter")
                self.assertEqual(service.get(1).title, "Saved")
                app.screen.query_one("#open", Button).focus()
                await pilot.press("enter")
                app.screen.query_one("#toggle", Button).focus()
                await pilot.press("enter")
            restored = TaskApp(TaskService(store))
            async with restored.run_test():
                self.assertTrue(restored.service.get(1).done)

    async def test_load_failure_temporary_banner_and_no_writes(self):
        store = FakeStore()
        store.fail_load = True
        service = TaskService(store)
        app = TaskApp(service)
        async with app.run_test() as pilot:
            self.assertTrue(service.temporary)
            self.assertIn("Cannot load", str(app.screen.query_one("#message", Static).content))
            self.assertIn("TEMPORARY", str(app.screen.query_one("#notice", Static).content))
            app.screen.query_one("#add", Button).focus()
            await pilot.press("enter")
            self.assertIn("lost on close", str(app.screen.query_one("#notice", Static).content))
            await pilot.press(*"Temporary", "tab", "tab", "enter")
            self.assertEqual(service.get(1).title, "Temporary")
            app.screen.query_one("#open", Button).focus()
            await pilot.press("enter")
            self.assertIn("TEMPORARY", str(app.screen.query_one("#notice", Static).content))
            app.screen.query_one("#toggle", Button).focus()
            await pilot.press("enter")
            self.assertIn("not saved", str(app.screen.query_one("#message", Static).content))
            await pilot.press("escape")
            app.screen.query_one("#done", Button).focus()
            await pilot.press("enter")
            self.assertEqual(app.screen.visible_ids, [1])
            self.assertEqual(store.saves, 0)
        store.fail_load = False
        self.assertEqual(TaskService(store).snapshot, TaskSnapshot())

    async def test_save_failure_retains_draft_and_snapshot(self):
        store = FakeStore()
        app = TaskApp(TaskService(store))
        async with app.run_test() as pilot:
            app.screen.query_one("#add", Button).focus()
            await pilot.press("enter", *"Unsaved")
            store.fail_save = True
            await pilot.press("tab", "tab", "enter")
            self.assertEqual(app.screen.query_one(Input).value, "Unsaved")
            self.assertIn("Cannot save", str(app.screen.query_one("#error", Static).content))
            self.assertEqual(app.service.snapshot, TaskSnapshot())
