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