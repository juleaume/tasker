import datetime
from typing import Dict

from .utils import d_sigmoid


class NegativePriorityError(ValueError):
    def __init__(self) -> None:
        super().__init__("Cannot set negative priority")


class PastDeadlineError(ValueError):
    def __init__(self) -> None:
        super().__init__("Cannot set a deadline from the past")


class Task:
    def __init__(self, name: str, priority: int, deadline: str | int) -> None:
        self._name = name
        if priority < 0:
            raise NegativePriorityError
        self._priority = priority
        if isinstance(deadline, str):
            _deadline = datetime.date.fromisoformat(deadline)
            if _deadline < datetime.date.today():
                raise PastDeadlineError
        elif isinstance(deadline, int):
            _deadline = deadline
            if _deadline < 0:
                raise PastDeadlineError
        else:
            raise ValueError
        self._deadline = _deadline


    @property
    def name(self) -> str:
        return self._name

    @property
    def deadline(self) -> int:
        """
        Get the number of days before the due date
        :return:
        """
        if isinstance(self._deadline, datetime.date):
            return (self._deadline - datetime.date.today()).days
        elif isinstance(self._deadline, int):
            return self._deadline
        else:
            raise ValueError

    @deadline.setter
    def deadline(self, value: str | int) -> None:
        """
        Set the value of the dateline. Accepts both a date or a number of days
        before the due date.
        :param value:
        :return:
        """
        if isinstance(value, str):
            _deadline = datetime.date.fromisoformat(value)
            if _deadline < datetime.date.today():
                raise PastDeadlineError
            else:
                self._deadline = _deadline
        elif isinstance(value, int):
            if value < 0:
                raise PastDeadlineError
            else:
                self._deadline = value
        else:
            raise ValueError

    @property
    def priority(self) -> int:
        return self._priority

    @priority.setter
    def priority(self, value: int) -> None:
        if value >= 0:
            self._priority = value
        else:
            raise NegativePriorityError

    @property
    def urgency(self) -> float:
        return d_sigmoid(self.deadline + self.priority)

    def __lt__(self, other: "Task") -> bool:
        return self.urgency < other.urgency

    def __gt__(self, other: "Task") -> bool:
        return self.urgency > other.urgency

    def __eq__(self, other: "Task") -> bool:
        return self.urgency == other.urgency

    def __ge__(self, other: "Task") -> bool:
        return self.urgency >= other.urgency

    def __le__(self, other: "Task") -> bool:
        return self.urgency <= other.urgency

    def __repr__(self) -> str:
        return str(self)

    def __str__(self) -> str:
        return (
            f"{self.name} [{self.priority}]"
            f" -> {self.deadline} "
            f"day{'s' if self.deadline > 1 else ''} remaining"
        )

    def serialize(self) -> Dict[str, str | int]:
        return {
            "name": self.name,
            "priority": self.priority,
            "deadline": self.deadline,
        }
