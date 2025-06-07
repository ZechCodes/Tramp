import pytest

from tramp.optionals import (
    Optional, Some, Nothing, OptionalException, OptionalTypeCannotBeInstantiated, 
    OptionalHasNoValueException
)


def test_optional_cannot_be_instantiated():
    with pytest.raises(OptionalTypeCannotBeInstantiated):
        Optional()


def test_some_creation():
    some = Some(42)
    assert some.value == 42
    assert bool(some) is True


def test_some_match_args():
    some = Some(42)
    match some:
        case Some(value):
            assert value == 42
        case _:
            pytest.fail("Should match Some pattern")


def test_nothing_singleton():
    nothing1 = Nothing()
    nothing2 = Nothing()
    assert nothing1 is nothing2


def test_nothing_no_value():
    nothing = Nothing()
    with pytest.raises(OptionalHasNoValueException):
        _ = nothing.value
    assert bool(nothing) is False


def test_nothing_value_or():
    nothing = Nothing()
    assert nothing.value_or(42) == 42


def test_some_value_or():
    some = Some(10)
    assert some.value_or(42) == 10


def test_optional_wrap_with_value():
    result = Optional.wrap("hello")
    assert isinstance(result, Some)
    assert result.value == "hello"


def test_optional_wrap_with_none():
    result = Optional.wrap(None)
    assert isinstance(result, Nothing)


def test_optional_class_attributes():
    assert Optional.Some is Some
    assert Optional.Nothing is Nothing


def test_base_optional_value_access():
    some = Some(42)
    with pytest.raises(OptionalHasNoValueException):
        _ = Optional.value.fget(some)


def test_base_optional_bool():
    some = Some(42)
    assert bool(Optional.__bool__(some)) is False


def test_nothing_repr():
    nothing = Nothing()
    repr_str = repr(nothing)
    assert "Nothing" in repr_str


def test_some_repr():
    some = Some(42)
    repr_str = repr(some)
    assert "Some" in repr_str


def test_optional_pattern_matching():
    def process_optional(opt):
        match opt:
            case Some(value):
                return f"Got value: {value}"
            case Nothing():
                return "Got nothing"
    
    assert process_optional(Some(42)) == "Got value: 42"
    assert process_optional(Nothing()) == "Got nothing"


def test_optional_truthiness():
    assert Some(42)
    assert Some(0)
    assert Some("")
    assert Some(False)
    assert not Nothing()


def test_wrap_various_types():
    assert isinstance(Optional.wrap(42), Some)
    assert isinstance(Optional.wrap(""), Some)
    assert isinstance(Optional.wrap([]), Some)
    assert isinstance(Optional.wrap(False), Some)
    assert isinstance(Optional.wrap(None), Nothing)