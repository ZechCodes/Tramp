import pytest

from tramp.results import (
    Result, Value, Error, ResultException, ResultTypeCannotBeInstantiated,
    ResultWasAnErrorException, ResultWasNeverSetException
)


def test_result_cannot_be_instantiated():
    with pytest.raises(ResultTypeCannotBeInstantiated):
        Result()


def test_value_creation():
    value = Value(42)
    assert value.value == 42
    assert bool(value) is True
    assert value.error is None


def test_value_repr():
    value = Value("hello")
    assert repr(value) == "Result.Value('hello')"


def test_value_match_args():
    value = Value(42)
    match value:
        case Value(val):
            assert val == 42
        case _:
            pytest.fail("Should match Value pattern")


def test_error_creation():
    error = ValueError("test error")
    result = Error(error)
    assert result.error is error
    assert bool(result) is False


def test_error_repr():
    error = ValueError("test error")
    result = Error(error)
    assert repr(result) == f"Result.Error({error!r})"


def test_error_value_access():
    error = ValueError("test error")
    result = Error(error)
    with pytest.raises(ResultWasAnErrorException):
        _ = result.value


def test_error_value_or():
    error = ValueError("test error")
    result = Error(error)
    assert result.value_or(42) == 42


def test_error_match_args():
    error = ValueError("test error")
    result = Error(error)
    match result:
        case Error(err):
            assert err is error
        case _:
            pytest.fail("Should match Error pattern")


def test_result_class_attributes():
    assert Result.Value is Value
    assert Result.Error is Error


def test_result_builder_success():
    with Result.build() as result:
        result.value = 42
    
    assert isinstance(result, Value)
    assert result.value == 42


def test_result_builder_exception():
    with Result.build() as result:
        raise ValueError("test error")
    
    assert isinstance(result, Error)
    assert isinstance(result.error, ValueError)
    assert str(result.error) == "test error"


def test_result_builder_never_set():
    with Result.build() as result:
        pass
    
    assert isinstance(result, Error)
    assert isinstance(result.error, ResultWasNeverSetException)


def test_result_builder_exception_chaining():
    original_error = ValueError("original")
    
    with Result.build() as result:
        raise original_error
    
    assert result.error is original_error


def test_base_result_bool():
    value = Value(42)
    assert bool(Result.__bool__(value)) is False


def test_pattern_matching():
    def process_result(result):
        match result:
            case Value(val):
                return f"Success: {val}"
            case Error(err):
                return f"Error: {err}"
    
    assert process_result(Value(42)) == "Success: 42"
    error = ValueError("test")
    assert process_result(Error(error)) == f"Error: {error}"


def test_value_truthiness():
    assert Value(42)
    assert Value(0)
    assert Value("")
    assert Value(False)
    assert Value(None)


def test_error_truthiness():
    assert not Error(ValueError("test"))
    assert not Error(RuntimeError("test"))


def test_value_value_or():
    assert Value(42).value_or(0) == 42


def test_readme_build_and_match_example():
    with Result.build() as result:
        result.value = 42

    match result:
        case Result.Value(v):
            assert v == 42
        case _:
            pytest.fail("Should match Result.Value")

    with Result.build() as err_result:
        raise ValueError("oops")

    match err_result:
        case Result.Error(e):
            assert isinstance(e, ValueError)
        case _:
            pytest.fail("Should match Result.Error")


def test_result_build_with_none_value():
    with Result.build() as result:
        result.value = None

    assert isinstance(result, Value)
    assert result.value is None


def test_result_build_with_falsy_values():
    for falsy in (0, False, ""):
        with Result.build() as result:
            result.value = falsy

        assert isinstance(result, Value)
        assert result.value == falsy


def test_error_value_exception_chaining():
    original = ValueError("original")
    error_result = Error(original)

    with pytest.raises(ResultWasAnErrorException) as exc_info:
        _ = error_result.value

    assert exc_info.value.__cause__ is original


def test_value_none_access():
    v = Value(None)
    assert v.value is None


def test_value_value_or_with_falsy():
    assert Value(0).value_or(99) == 0
    assert Value(False).value_or(True) is False
    assert Value("").value_or("default") == ""


def test_result_build_value_then_exception():
    """When value is set but then an exception is raised, Error wins."""
    with Result.build() as result:
        result.value = 42
        raise RuntimeError("oops")

    assert isinstance(result, Error)
    assert isinstance(result.error, RuntimeError)


def test_base_result_value_raises():
    v = Value(42)
    with pytest.raises(RuntimeError):
        Result.value.fget(v)