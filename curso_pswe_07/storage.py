import json
import os
from pathlib import Path
import tempfile

from .models import Task, TaskSnapshot
from .service import StorageError


def unique_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"Duplicate field: {key}")
        result[key] = value
    return result


class JsonTaskStore:
    def __init__(self, path: Path) -> None:
        self.path = path

    def load(self) -> TaskSnapshot:
        try:
            text = self.path.read_text(encoding="utf-8")
        except FileNotFoundError:
            return TaskSnapshot()
        except (OSError, UnicodeError) as error:
            raise StorageError(f"Cannot load tasks: {error}") from error
        try:
            document = json.loads(text, object_pairs_hook=unique_object)
            if not isinstance(document, dict) or set(document) != {"version", "next_id", "tasks"}:
                raise ValueError("Expected version, next_id, and tasks fields")
            if type(document["version"]) is not int or document["version"] != 1:
                raise ValueError("Unsupported data version")
            if not isinstance(document["tasks"], list):
                raise ValueError("Tasks must be a list")
            tasks = []
            for record in document["tasks"]:
                if not isinstance(record, dict) or set(record) != {"id", "title", "description", "done"}:
                    raise ValueError("Invalid task fields")
                tasks.append(Task(**record))
            return TaskSnapshot(tuple(tasks), document["next_id"])
        except (ValueError, TypeError, RecursionError) as error:
            raise StorageError(f"Cannot load tasks: {error}") from error

    def save(self, snapshot: TaskSnapshot) -> None:
        temporary: Path | None = None
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            with tempfile.NamedTemporaryFile(
                mode="w", encoding="utf-8", dir=self.path.parent,
                prefix=".tasks-", suffix=".tmp", delete=False,
            ) as handle:
                temporary = Path(handle.name)
                json.dump({
                    "version": 1, "next_id": snapshot.next_id,
                    "tasks": [
                        {"id": task.id, "title": task.title,
                         "description": task.description, "done": task.done}
                        for task in snapshot.tasks
                    ],
                }, handle, ensure_ascii=False)
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temporary, self.path)
        except (OSError, ValueError, TypeError) as error:
            cleanup_error = ""
            if temporary is not None:
                try:
                    temporary.unlink(missing_ok=True)
                except OSError as cleanup:
                    cleanup_error = f"; temporary-file cleanup failed: {cleanup}"
            raise StorageError(f"Cannot save tasks: {error}{cleanup_error}") from error
