from dataclasses import FrozenInstanceError
import unittest

from curso_pswe_07.models import CompletionFilter, Task, TaskSnapshot
from curso_pswe_07.service import TaskService, StorageError


class FakeStore:
    def __init__(self, snapshot=TaskSnapshot()):
        self.snapshot = snapshot
        self.fail_save = False
        self.fail_load = False
        self.saves = 0

    def load(self):
        if self.fail_load:
            raise StorageError("Cannot load test store")
        return self.snapshot

    def save(self, snapshot):
        self.saves += 1
        if self.fail_save:
            raise StorageError("Cannot save test store")
        self.snapshot = snapshot


class ModelTests(unittest.TestCase):
    def test_valid_text_is_preserved_and_description_normalized(self):
        task = Task(1, "  Café " + "x" * 200, " \n ")
        self.assertEqual(task.title, "  Café " + "x" * 200)
        self.assertEqual(task.description, "")
        self.assertFalse(task.done)
        with self.assertRaises(FrozenInstanceError):
            task.title = "changed"

    def test_invalid_fields(self):
        for args in [(True, "title"), (0, "title"), (1, ""), (1, " \n"),
                     (1, 3), (1, "title", None), (1, "title", "", 1)]:
            with self.subTest(args=args), self.assertRaises(ValueError):
                Task(*args)

    def test_snapshot_identity_and_next_id(self):
        tasks = (Task(1, "same"), Task(2, "same"))
        self.assertEqual(TaskSnapshot(tasks, 3).next_id, 3)
        for snapshot_args in [(tasks, 2), ((tasks[0], tasks[0]), 3), ((), True)]:
            with self.assertRaises(ValueError):
                TaskSnapshot(*snapshot_args)

    def test_filter_values(self):
        self.assertEqual([item.value for item in CompletionFilter],
                         ["All", "Pending", "Done"])


class FoundationTests(unittest.TestCase):
    def test_initial_load_lookup_and_unknown_id(self):
        service = TaskService(FakeStore(TaskSnapshot((Task(1, "task"),), 2)))
        self.assertEqual(service.get(1).title, "task")
        self.assertEqual(service.list_tasks(), (Task(1, "task"),))
        with self.assertRaises(ValueError):
            service.get(9)

    def test_publish_only_after_save(self):
        store = FakeStore()
        service = TaskService(store)
        store.fail_save = True
        with self.assertRaises(StorageError):
            service._commit(TaskSnapshot((Task(1, "new"),), 2))
        self.assertEqual(service.snapshot, TaskSnapshot())


class CreateTests(unittest.TestCase):
    def test_duplicate_titles_and_commit(self):
        store = FakeStore()
        service = TaskService(store)
        first = service.create("same", " ")
        second = service.create("same", "details")
        self.assertEqual((first.id, second.id), (1, 2))
        self.assertFalse(first.done)
        self.assertEqual(first.description, "")
        self.assertEqual(store.snapshot, service.snapshot)

    def test_validation_and_save_failure_do_not_allocate_id(self):
        store = FakeStore()
        service = TaskService(store)
        with self.assertRaises(ValueError):
            service.create(" ")
        self.assertEqual(store.saves, 0)
        store.fail_save = True
        with self.assertRaises(StorageError):
            service.create("task")
        self.assertEqual(service.snapshot.next_id, 1)


class CompletionTests(unittest.TestCase):
    def test_toggle_filters_and_identity(self):
        service = TaskService(FakeStore(TaskSnapshot(
            (Task(1, "same"), Task(2, "same", "details", True)), 3
        )))
        self.assertEqual([task.id for task in service.list_tasks(CompletionFilter.PENDING)], [1])
        service.set_done(1, True)
        self.assertEqual(service.list_tasks(CompletionFilter.PENDING), ())
        service.set_done(2, False)
        self.assertEqual(service.get(2), Task(2, "same", "details", False))
        self.assertEqual([task.id for task in service.list_tasks(CompletionFilter.DONE)], [1])

    def test_status_failure_retains_snapshot(self):
        store = FakeStore(TaskSnapshot((Task(1, "task"),), 2))
        service = TaskService(store)
        store.fail_save = True
        with self.assertRaises(StorageError):
            service.set_done(1, True)
        self.assertFalse(service.get(1).done)


class EditDeleteTests(unittest.TestCase):
    def test_edit_clear_preserve_identity_and_delete(self):
        service = TaskService(FakeStore(TaskSnapshot(
            (Task(1, "same", "description", True), Task(2, "same")), 3
        )))
        service.edit(1, "renamed", "")
        self.assertEqual(service.get(1), Task(1, "renamed", "", True))
        service.delete(1)
        self.assertEqual(service.snapshot, TaskSnapshot((Task(2, "same"),), 3))
        with self.assertRaises(ValueError):
            service.delete(1)
        with self.assertRaises(ValueError):
            service.edit(2, " ", "invalid")
        self.assertEqual(service.get(2).title, "same")

    def test_failed_edit_delete_do_not_publish(self):
        store = FakeStore(TaskSnapshot((Task(1, "before"),), 2))
        service = TaskService(store)
        store.fail_save = True
        for mutation in (lambda: service.edit(1, "after", ""), lambda: service.delete(1)):
            with self.assertRaises(StorageError):
                mutation()
            self.assertEqual(service.snapshot, store.snapshot)
