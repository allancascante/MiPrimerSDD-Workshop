"""Framework-independent task data."""

from dataclasses import dataclass
from enum import Enum


class CompletionFilter(Enum):
    ALL = "All"
    PENDING = "Pending"
    DONE = "Done"


@dataclass(frozen=True)
class Task:
    id: int
    title: str
    description: str = ""
    done: bool = False

    def __post_init__(self) -> None:
        if type(self.id) is not int or self.id < 1:
            raise ValueError("Task ID must be a positive integer")
        if not isinstance(self.title, str) or not self.title.strip():
            raise ValueError("Title is required")
        if not isinstance(self.description, str) or type(self.done) is not bool:
            raise ValueError("Invalid task description or completion status")
        if not self.description.strip():
            object.__setattr__(self, "description", "")


@dataclass(frozen=True)
class TaskSnapshot:
    tasks: tuple[Task, ...] = ()
    next_id: int = 1

    def __post_init__(self) -> None:
        if not isinstance(self.tasks, tuple) or not all(
            isinstance(task, Task) for task in self.tasks
        ):
            raise ValueError("Snapshot tasks must be a tuple of Task values")
        ids = [task.id for task in self.tasks]
        if len(ids) != len(set(ids)):
            raise ValueError("Duplicate task IDs")
        if type(self.next_id) is not int or self.next_id <= max(ids, default=0):
            raise ValueError("next_id must be a positive integer greater than all IDs")
