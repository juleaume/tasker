import json
import os
from json import JSONDecodeError
from typing import Generator, Tuple, List, Dict, Optional

from .task import Task


SAVE_PATH = os.path.join(os.path.expanduser("~"), ".tasker")
FILE_NAME = os.path.join(SAVE_PATH, "tasks.json")

Serialized = Dict[str, Dict[str, str | int]]


class Tasker:
    def __init__(self) -> None:
        self._tasks = list()
        if not os.path.isdir(SAVE_PATH):
            os.mkdir(SAVE_PATH)
        self.load()

    def _add(self, task: Task) -> None:
        if task.name not in self.task_names():
            self._tasks.append(task)
        else:
            raise ValueError("Task already exists")

    def _remove(self, task: Task) -> None:
        if task.name not in self.task_names():
            self._tasks.remove(task)
        else:
            raise ValueError("Task does not exist")

    @property
    def tasks(self) -> list[Task]:
        return self._tasks

    def _sort(self) -> None:
        if self.tasks:
            self._tasks.sort()

    @property
    def current_task(self) -> Optional[Task]:
        self._sort()
        if self.tasks:
            return self.tasks[0]
        else:
            return None

    def get_all_tasks(self) -> Generator[Tuple[str, int, int], None, None]:
        self._sort()
        if self.tasks:
            for task in self.tasks:
                yield task.name, task.priority, task.deadline
        else:
            return None

    def task_names(self) -> List[str]:
        self._sort()
        return list(map(lambda x: x.name, self.tasks))

    def create(self, name: str, priority: int, deadline: str | int) -> None:
        self._add(Task(name, priority, deadline))
        self._sort()
        self.save()

    def finish(self, name: str) -> None:
        for task in self.tasks:
            if task.name == name:
                self._remove(task)
                break
        else:
            raise ValueError(f"No task {name}")
        self.save()

    def reset(self) -> None:
        self._tasks = list()
        self.save()

    def get_task_by_name(self, name: str) -> Task:
        if name not in self.task_names():
            raise ValueError(f"Not such task {name}")
        else:
            for task in self.tasks:
                if task.name == name:
                    return task

    def _serialize(self) -> Serialized:
        self._sort()
        return {
            f"task_{i + 1}": task.serialize()
            for i, task in enumerate(self.tasks)
        }

    def save(self) -> None:
        with open(FILE_NAME, "w") as save_file:
            save_file.write(json.dumps(self._serialize()))

    def load(self) -> None:
        def get_task(t: Dict[str, str | int]):
            return (
                t.get("name", None),
                int(t.get("priority", 9)),
                int(t.get("deadline", 9)),
            )

        if os.path.isfile(FILE_NAME):
            with open(FILE_NAME, "r") as save_file:
                try:
                    _series: Serialized = json.load(save_file)
                    for name, task in _series.items():
                        self.create(*get_task(task))
                except JSONDecodeError:
                    pass
