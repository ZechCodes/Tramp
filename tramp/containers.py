from typing import overload, TypeVar, Generic

T = TypeVar("T")


class Container(Generic[T]):
    """Containers are used to provide a reference to a changeable value."""

    @overload
    def __init__(self):
        ...

    @overload
    def __init__(self, default: T):
        ...

    def __init__(self, *args, **kwargs):
        self._set, self._value = self._process_args(args, kwargs)

    @property
    def never_set(self) -> bool:
        return self._set is False

    @property
    def value(self):
        if self.never_set:
            raise ValueError("No value has been set on the container.")

        return self._value

    def set(self, value: T):
        self._value = value
        self._set = True

    def value_or(self, default: T) -> T:
        return self._value if self._set else default

    def _process_args(self, args, kwargs):
        if len(args):
            return True, args[0]

        if "default" in kwargs:
            return True, kwargs["default"]

        return False, None
