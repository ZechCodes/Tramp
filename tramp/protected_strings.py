from mailbox import FormatError
from typing import Callable, Iterable, overload, Protocol, runtime_checkable, Union


@runtime_checkable
class CallableProtocol(Protocol):
    def __call__(self, *args, **kwargs):
        ...


@runtime_checkable
class ContainsProtocol(Protocol):
    def __contains__(self, item) -> bool:
        ...


class ProtectedString:
    """A string that can be selectively revealed in formatted output.
    
    Args:
        value: The protected string value
        name: Optional identifier for selective revelation (should be a valid Python identifier)
        hide_name: If True, don't show the name in the repr output
        
    Note:
        Names should be valid Python identifiers for best compatibility with format specs.
        Names with spaces or special characters will be title-cased in repr but may not
        work properly in format specifications.
        
        Format specification matching is case-sensitive: ProtectedString("x", "MyName") 
        will only match "$MyName", not "$myname" or "$MYNAME".
        
        Type Behavior:
        Both + and += operators return ProtectedStringBuilder, which inherits from 
        ProtectedString. This ensures consistent behavior in pattern matching:
        
        >>> ps = ProtectedString("secret")
        >>> builder = ps + "text"
        >>> isinstance(builder, ProtectedString)  # True - works in match/case
        True
        >>> isinstance(builder, ProtectedStringBuilder)  # True - is also a builder
        True
    """
    def __init__(self, value: str, name: str = "", *, hide_name: bool = False):
        self.value = value
        self.name = name
        self.hide_name = hide_name
        
        # Warn about potentially problematic names but don't enforce
        if name and not name.isidentifier():
            import warnings
            warnings.warn(
                f"Name '{name}' is not a valid Python identifier. "
                f"It may not work properly in format specifications.",
                UserWarning,
                stacklevel=2
            )

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


class ProtectedStringBuilder(ProtectedString):
    def __init__(self, *strings: str | ProtectedString):
        # Don't call super().__init__ as we override the behavior
        self.strings = list(strings)
        # Set attributes that ProtectedString expects but we don't use
        self._value = ""  # Placeholder - we override with property
        self.name = ""
        self.hide_name = False

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
            case ProtectedStringBuilder():
                return ProtectedStringBuilder(*self.strings, *other.strings)
                
            case ProtectedString() | str():
                return ProtectedStringBuilder(*self.strings, other)

            case _:
                return NotImplemented

    def __radd__(self, other):
        match other:
            case ProtectedString() | str():
                return ProtectedStringBuilder(other, *self.strings)

            case _:
                return NotImplemented

    def __iadd__(self, other):
        # Keep mutating behavior for += operator
        match other:
            case ProtectedStringBuilder():
                self.strings.extend(other.strings)
                return self
                
            case ProtectedString() | str():
                self.add(other)
                return self

            case _:
                return NotImplemented

    def __format__(self, format_spec):
        redact_with, sep, allowed_names = format_spec.partition("$")
        allowed = lambda _: False

        if sep and not allowed_names:
            raise FormatError("Format spec '$' requires allowed names.")

        filtered_names = set(name.strip() for name in allowed_names.split(",") if name.strip())
        
        if not filtered_names and allowed_names:
            raise FormatError("No valid names provided after filtering.")
        
        # Check for invalid identifiers and provide specific error messages
        invalid_names = [name for name in filtered_names if not name.isidentifier()]
        if invalid_names:
            raise FormatError(f"Invalid identifier(s) in allowed names: {', '.join(invalid_names)}")

        if allowed_names:
            allowed = lambda s: s.name in filtered_names

        return self.render(redact_with or None, allowed=allowed)
    
    def __repr__(self):
        # Use the first ProtectedString's repr if available, otherwise generic
        for item in self.strings:
            if isinstance(item, ProtectedString):
                return repr(item)
        return "<Redacted>"
    
    @property
    def value(self):
        """Return the actual concatenated value (not redacted)."""
        result = ""
        for item in self.strings:
            if isinstance(item, ProtectedString):
                result += item.value
            else:
                result += str(item)
        return result
