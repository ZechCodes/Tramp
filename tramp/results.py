from typing import Generic, NoReturn, TypeVar, Type

from tramp.containers import Container


V = TypeVar("V")


class ResultException(Exception):
    """Base exception for errors raised by a result object."""


class ResultTypeCannotBeInstantiated(ResultException):
    """Raised when attempting to instantiate a result type that is not a value type."""


class ResultWasAnErrorException(ResultException):
    """Raised when a result object wraps an error."""


class ResultWasNeverSetException(ResultException):
    """Raised when a result is never given a value and no errors were raised."""


class Result(Generic[V]):
    Value: "Type[Result[V]]"
    Error: "Type[Error[V]]"

    def __new__(cls, *_):
        if cls is Result:
            raise ResultTypeCannotBeInstantiated(
                "You cannot instantiate the base result type."
            )

        return super().__new__(cls)

    @property
    def value(self) -> V | NoReturn:
        pass

    def value_or(self, default: V) -> V:
        pass

    def __bool__(self):
        return False

    @classmethod
    def build(cls) -> "ResultBuilder":
        return ResultBuilder()


class ResultBuilder:
    def __init__(self):
        self._result = Container()

    def __enter__(self):
        return self._result

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            self._result.set(Result.Error(exc_val))

        elif self._result.value is None:
            raise ResultWasNeverSetException("No value was ever set on the result.")

        return True


class Value(Result):
    __match_args__ = ("value",)

    def __init__(self, value: V):
        self._value = value

    @property
    def value(self) -> V:
        return self._value

    def __bool__(self):
        return True


class Error(Result):
    def __init__(self, error: Exception):
        self._error = error

    @property
    def value(self) -> NoReturn:
        raise ResultWasAnErrorException("The result was an error.") from self.error

    def value_or(self, default: V) -> V:
        return default

    def error(self) -> Exception:
        return self._error


Result.Value = Value
Result.Error = Error
