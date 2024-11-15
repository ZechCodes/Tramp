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


class _ResultBuilder(Generic[V]):
    def __init__(self):
        self._value = None
        self._error = None

    @property
    def value(self) -> V:
        return self._value

    @value.setter
    def value(self, value: V):
        self._value = value

    @property
    def error(self) -> Exception:
        return self._error

    def __enter__(self) -> "_ResultBuilder[V] | Result[V]":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            self.__class__ = Error
            self.__init__(exc_val)
            return True

        if self._value is None and self._error is None:
            with _ResultBuilder() as r:
                raise ResultWasNeverSetException("No result was ever set.")

            self.__class__ = Error
            self.__init__(r.error)
            return True

        self.__class__ = Value


class Result(Generic[V]):
    Value: "Type[Value[V]]"
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

    @property
    def error(self) -> Exception | None:
        return

    def value_or(self, default: V) -> V:
        pass

    @classmethod
    def build(cls) -> _ResultBuilder[V]:
        return _ResultBuilder()


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
