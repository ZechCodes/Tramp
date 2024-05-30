from typing import TypeVar, Generic

T = TypeVar("T")


class Container(Generic[T]):
    """Containers are used to provide a reference to a changeable value."""

    def __init__(self, default: T | None = None):
        self._value = default

    @property
    def value(self):
        return self._value

    def set(self, value: T) -> None:
        self._value = value
