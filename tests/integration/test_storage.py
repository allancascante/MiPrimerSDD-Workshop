from dataclasses import asdict
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from curso_pswe_07.models import Task, TaskSnapshot
from curso_pswe_07.service import StorageError
from curso_pswe_07.storage import JsonTaskStore


class StorageTests(unittest.TestCase):
    def setUp(self):
        self.directory = TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.path = Path(self.directory.name) / "data" / "tasks.json"
        self.store = JsonTaskStore(self.path)

    def test_missing_and_roundtrip(self):
        self.assertEqual(self.store.load(), TaskSnapshot())
        for snapshot in (
            TaskSnapshot((Task(1, "Café"), Task(2, "Café", "updated", True)), 3),
            TaskSnapshot((Task(2, "edited"),), 3),
            TaskSnapshot((), 3),
        ):
            self.store.save(snapshot)
            self.assertEqual(self.store.load(), snapshot)
        self.assertEqual(set(json.loads(self.path.read_text())), {"version", "next_id", "tasks"})

    def test_reject_invalid_documents_without_writing(self):
        task = asdict(Task(1, "task"))
        valid = {"version": 1, "next_id": 2, "tasks": [task]}
        invalid = [
            "{", '{"version":1,"version":1,"next_id":1,"tasks":[]}',
            "[" * 2000 + "]" * 2000,
            json.dumps({**valid, "version": True}),
            json.dumps({**valid, "version": 2}),
            json.dumps({**valid, "next_id": 1}),
            json.dumps({**valid, "next_id": True}),
            json.dumps({**valid, "next_id": None}),
            json.dumps({"version": 1, "tasks": []}),
            json.dumps({**valid, "extra": 1}),
            json.dumps({**valid, "tasks": {}}),
            json.dumps({**valid, "tasks": [task, task]}),
            json.dumps({**valid, "tasks": [{key: value for key, value in task.items() if key != "title"}]}),
            json.dumps({**valid, "tasks": [{**task, "done": 1}]}),
            json.dumps({**valid, "tasks": [{**task, "id": True}]}),
            json.dumps({**valid, "tasks": [{**task, "title": " "}]}),
            json.dumps({**valid, "tasks": [{**task, "extra": 1}]}),
            json.dumps({**valid, "tasks": [{**task, "description": None}]}),
        ]
        self.path.parent.mkdir()
        for index, document in enumerate(invalid):
            with self.subTest(case=index):
                self.path.write_text(document)
                with self.assertRaises(StorageError):
                    self.store.load()
                self.assertEqual(self.path.read_text(), document)
        self.path.write_bytes(b"\xff")
        with self.assertRaises(StorageError):
            self.store.load()

    def test_io_errors_and_precommit_failures(self):
        self.store.save(TaskSnapshot((Task(1, "old"),), 2))
        original = self.path.read_bytes()
        for target in ("json.dump", "os.fsync", "os.replace"):
            with self.subTest(target=target):
                with patch(f"curso_pswe_07.storage.{target}", side_effect=OSError("disk failure")):
                    with self.assertRaisesRegex(StorageError, "disk failure"):
                        self.store.save(TaskSnapshot((Task(1, "new"),), 2))
                self.assertEqual(self.path.read_bytes(), original)
                self.assertEqual(list(self.path.parent.iterdir()), [self.path])
        with patch.object(Path, "read_text", side_effect=PermissionError("permission")):
            with self.assertRaisesRegex(StorageError, "permission"):
                self.store.load()

    def test_cleanup_failure_is_reported(self):
        self.path.parent.mkdir()
        with patch("curso_pswe_07.storage.os.replace", side_effect=OSError("replace failed")), \
             patch.object(Path, "unlink", side_effect=OSError("cleanup failed")):
            with self.assertRaisesRegex(StorageError, "replace failed.*cleanup failed"):
                self.store.save(TaskSnapshot())

    def test_write_flush_close_failures_leave_original_unchanged(self):
        import tempfile

        self.store.save(TaskSnapshot((Task(1, "original"),), 2))
        original = self.path.read_bytes()
        create_file = tempfile.NamedTemporaryFile
        for stage in ("write", "flush", "close"):
            with self.subTest(stage=stage):
                class FaultyFile:
                    def __init__(self, **kwargs):
                        self.handle = create_file(**kwargs)
                        self.name = self.handle.name

                    def __enter__(self):
                        return self

                    def write(self, text):
                        if stage == "write":
                            raise OSError("write failure")
                        return self.handle.write(text)

                    def flush(self):
                        if stage == "flush":
                            raise OSError("flush failure")
                        return self.handle.flush()

                    def fileno(self):
                        return self.handle.fileno()

                    def __exit__(self, *_args):
                        self.handle.close()
                        if stage == "close":
                            raise OSError("close failure")

                with patch("curso_pswe_07.storage.tempfile.NamedTemporaryFile", FaultyFile):
                    with self.assertRaisesRegex(StorageError, f"{stage} failure"):
                        self.store.save(TaskSnapshot())
                self.assertEqual(self.path.read_bytes(), original)
                self.assertEqual(list(self.path.parent.iterdir()), [self.path])
