"""Application operations; independent of the terminal and file formats."""

from dataclasses import replace
from typing import Protocol

from .models import CompletionFilter, Task, TaskSnapshot


class StorageError(Exception):
    """An expected storage operation failed."""


class TaskStore(Protocol):
    def load(self) -> TaskSnapshot: ...

    def save(self, snapshot: TaskSnapshot) -> None: ...


class TaskService:
    def __init__(self, store: TaskStore) -> None:
        self._store = store
        self.temporary = False
        self.load_error = ""
        try:
            self.snapshot = store.load()
        except StorageError as error:
            self.snapshot = TaskSnapshot()
            self.temporary = True
            self.load_error = str(error)

    @property
    def notice(self) -> str:
        return (
            "TEMPORARY LIST: Changes are not saved and will be lost on close."
            if self.temporary else ""
        )

    @property
    def mutation_message(self) -> str:
        return "Updated temporary list; not saved." if self.temporary else "Saved."

    def get(self, task_id: int) -> Task:
        for task in self.snapshot.tasks:
            if task.id == task_id:
                return task
        raise ValueError(f"Task {task_id} does not exist")

    def list_tasks(self, filter_by: CompletionFilter = CompletionFilter.ALL) -> tuple[Task, ...]:
        return tuple(
            task for task in self.snapshot.tasks
            if filter_by is CompletionFilter.ALL
            or task.done == (filter_by is CompletionFilter.DONE)
        )

    def create(self, title: str, description: str = "") -> Task:
        task = Task(self.snapshot.next_id, title, description)
        self._commit(TaskSnapshot((*self.snapshot.tasks, task), task.id + 1))
        return task

    def set_done(self, task_id: int, done: bool) -> None:
        updated = replace(self.get(task_id), done=done)
        self._commit(TaskSnapshot(
            tuple(updated if task.id == task_id else task for task in self.snapshot.tasks),
            self.snapshot.next_id,
        ))

    def _commit(self, candidate: TaskSnapshot) -> None:
        if not self.temporary:
            self._store.save(candidate)
        self.snapshot = candidate

    def edit(self, task_id: int, title: str, description: str) -> None:
        updated = replace(self.get(task_id), title=title, description=description)
        self._commit(TaskSnapshot(
            tuple(updated if task.id == task_id else task for task in self.snapshot.tasks),
            self.snapshot.next_id,
        ))

    def delete(self, task_id: int) -> None:
        self.get(task_id)
        self._commit(TaskSnapshot(
            tuple(task for task in self.snapshot.tasks if task.id != task_id),
            self.snapshot.next_id,
        ))
