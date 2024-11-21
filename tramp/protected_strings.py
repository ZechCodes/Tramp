from mailbox import FormatError
from typing import Callable, Iterable, overload, Protocol, runtime_checkable


@runtime_checkable
class CallableProtocol(Protocol):
    def __call__(self, *args, **kwargs):
        ...


@runtime_checkable
class ContainsProtocol(Protocol):
    def __contains__(self, item) -> bool:
        ...


class ProtectedString:
    def __init__(self, value: str, name: str = "", *, hide_name: bool = False):
        self.value = value
        self.name = name
        self.hide_name = hide_name

    def __add__(self, other) -> "ProtectedStringBuilder":
        match other:
            case ProtectedString() | str():
                return ProtectedStringBuilder(self, other)

            case _:
                return NotImplemented

    def __radd__(self, other) -> "ProtectedStringBuilder":
        match other:
            case ProtectedString() | str():
                return ProtectedStringBuilder(other, self)

            case _:
                return NotImplemented

    def __iadd__(self, other) -> "ProtectedStringBuilder":
        match other:
            case ProtectedString() | str():
                return self + other

            case _:
                return NotImplemented

    def __format__(self, format_spec):
        return format(ProtectedStringBuilder(self), format_spec)

    def __repr__(self):
        if self.name and not self.hide_name:
            return f"<Redacted {self.name.title()}>"

        return f"<Redacted>"

    @classmethod
    def join(
        cls,
        parts: "list[ProtectedString | str]",
        redact_with: str | None = None,
        *,
        allowed: "Callable[[ProtectedString], bool] | Iterable[str] | None" = None
    ) -> str:
        builder = ProtectedStringBuilder(*parts)
        return builder.render(redact_with, allowed=allowed)


class ProtectedStringBuilder:
    def __init__(self, *strings: str | ProtectedString):
        self.strings = list(strings)

    @overload
    def add(self, string: str | ProtectedString):
        ...

    @overload
    def add(self, string: str, name: str, *, hide_name: bool = False):
        ...

    def add(self, string: str | ProtectedString, name: str = "", *, hide_name: bool = False):
        if name:
            string = ProtectedString(string, name, hide_name=hide_name)

        self.strings.append(string)

    def render(
        self,
        redact_with: str | None = None,
        *,
        allowed: Callable[[ProtectedString], bool] | Iterable[str] | None = None
    ) -> str:
        return "".join(
            self._redact(value, redact_with, allowed) if isinstance(value, ProtectedString) else value
            for value in self.strings
        )

    def _redact(
        self,
        string: ProtectedString,
        redact_with: str | None,
        allowed: Callable[[ProtectedString], bool] | Iterable[str] | None) -> str:
        match allowed:
            case CallableProtocol() if allowed(string):
                return string.value

            case ContainsProtocol() if string.name in allowed:
                return string.value

            case _:
                return repr(string) if redact_with is None else redact_with

    def __add__(self, other):
        match other:
            case ProtectedString() | str():
                self.add(other)
                return self

            case ProtectedStringBuilder():
                self.strings.extend(other.strings)
                return self

            case _:
                return NotImplemented

    def __radd__(self, other):
        match other:
            case ProtectedString() | str():
                return ProtectedStringBuilder(other, *self.strings)

            case _:
                return NotImplemented

    def __iadd__(self, other):
        return self + other

    def __format__(self, format_spec):
        redact_with, sep, allowed_names = format_spec.partition("$")
        allowed = lambda _: False

        if sep and not allowed_names:
            raise FormatError("No allowed names provided.")

        filtered_names = set(name for name in allowed_names.split(",") if name.strip())
        if not all(name.isidentifier() for name in filtered_names):
            raise FormatError("Allowed names provided.")

        if allowed_names:
            allowed = lambda s: s.name in filtered_names

        return self.render(redact_with or None, allowed=allowed)
