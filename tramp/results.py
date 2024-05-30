from typing import Generic, NoReturn, TypeVar, Type

V = TypeVar("V")


class ResultException(Exception):
    """Base exception for errors raised by a result object."""


class ResultTypeCannotBeInstantiated(ResultException):
    """Raised when attempting to instantiate a result type that is not a value type."""


class ResultWasAnErrorException(ResultException):
    """Raised when a result object wraps an error."""


class ResultWasNeverSetException(ResultException):
    """Raised when a result is never given a value and no errors were raised."""


class ResultBuilder(Generic[V]):
    def __init__(self):
        self._result: Result[V] | None = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            self._result = Result.Error(exc_val)

        elif self._result is None:
            raise ResultWasNeverSetException("No value was ever set on the result.")

        return True

    @property
    def result(self) -> "Result[V] | NoReturn":
        return self._result

    def set(self, value: V):
        self._result = Result.Value(value)


class Result(Generic[V]):
    Value: "Type[Result[V]]"
    Error: "Type[Error[V]]"

    def __new__(cls, *_):
        if cls is Result:
            raise ResultTypeCannotBeInstantiated(
                "You cannot instantiate the base result type."
            )

        return super().__new__(cls)

    def __bool__(self):
        return False

    @property
    def value(self) -> V | NoReturn:
        raise RuntimeError

    def error(self) -> Exception | None:
        return

    def value_or(self, default: V) -> V:
        pass

    @classmethod
    def build(cls) -> ResultBuilder[V]:
        return ResultBuilder()


class Value(Result[V]):
    __match_args__ = ("value",)

    def __init__(self, value: V):
        self._value = value

    def __repr__(self):
        return f"{Result.__name__}.{type(self).__name__}({self._value!r})"

    def __bool__(self):
        return True

    @property
    def value(self) -> V:
        return self._value


class Error(Result[V]):
    __match_args__ = ("error",)

    def __init__(self, error: Exception):
        self._error = error

    def __repr__(self):
        return f"{Result.__name__}.{type(self).__name__}({self._error!r})"

    @property
    def value(self) -> NoReturn:
        raise ResultWasAnErrorException("The result was an error.") from self.error

    @property
    def error(self) -> Exception:
        return self._error

    def value_or(self, default: V) -> V:
        return default


Result.Value = Value
Result.Error = Error
