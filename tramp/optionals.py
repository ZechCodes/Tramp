from typing import Generic, NoReturn, TypeVar, Type


V = TypeVar("V")


class OptionalException(Exception):
    """Base exception for errors raised by an Optional object."""


class OptionalTypeCannotBeInstantiated(OptionalException):
    """Raised when attempting to instantiate an Optional type that is not a type of Some."""


class OptionalHasNoValueException(OptionalException):
    """Raised when an Optional object has no value."""


class Optional(Generic[V]):
    Some: "Type[Optional[V]]"
    Nothing: "Optional[V]"

    def __new__(cls, *_):
        if cls is Optional:
            raise OptionalTypeCannotBeInstantiated(
                "You cannot instantiate the base Optional type."
            )

        return super().__new__(cls)

    @property
    def value(self) -> V | NoReturn:
        raise OptionalHasNoValueException(
            "You cannot access Optional directly, you must use either Optional.Some or Optional.Nothing"
        )

    def value_or(self, default: V) -> V:
        return self.value

    def __bool__(self):
        return False


class Some(Optional):
    __match_args__ = ("value",)

    def __init__(self, value: V):
        self._value = value

    @property
    def value(self) -> V:
        return self._value

    def __bool__(self):
        return True


class Nothing(Optional):
    def __new__(cls, *_):
        if not hasattr(Optional, "Nothing"):
            return super().__new__(cls)

        return Optional.Nothing

    @property
    def value(self) -> NoReturn:
        raise OptionalHasNoValueException("No value was set, this is Nothing")

    def value_or(self, default: V) -> V:
        return default


Optional.Some = Some
Optional.Nothing = Nothing()
