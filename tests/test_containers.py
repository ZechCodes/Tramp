import pytest

from tramp.containers import Container


def test_container_with_default():
    container = Container(42)
    assert container.value == 42
    assert not container.never_set


def test_container_with_default_keyword():
    container = Container(default=42)
    assert container.value == 42
    assert not container.never_set


def test_container_without_default():
    container = Container()
    assert container.never_set
    with pytest.raises(ValueError, match="No value has been set on the container"):
        _ = container.value


def test_container_set_value():
    container = Container()
    assert container.never_set
    
    container.set(100)
    assert not container.never_set
    assert container.value == 100


def test_container_value_or_with_set_value():
    container = Container(42)
    assert container.value_or(999) == 42


def test_container_value_or_with_unset_value():
    container = Container()
    assert container.value_or(999) == 999


def test_container_overwrite_value():
    container = Container(42)
    assert container.value == 42
    
    container.set(100)
    assert container.value == 100


def test_container_type_hints():
    container: Container[str] = Container("hello")
    assert container.value == "hello"
    
    container.set("world")
    assert container.value == "world"


def test_container_never_set_property():
    container = Container()
    assert container.never_set is True
    
    container.set(1)
    assert container.never_set is False


def test_container_value_or_never_set():
    container = Container()
    assert container.never_set
    assert container.value_or("default") == "default"
    
    container.set("actual")
    assert not container.never_set
    assert container.value_or("default") == "actual"


def test_container_with_none_default():
    container = Container(None)
    assert container.never_set is False
    assert container.value is None
    assert container.value_or("fallback") is None


def test_container_set_none():
    container = Container()
    container.set(None)
    assert container.never_set is False
    assert container.value is None
    assert container.value_or("fallback") is None


def test_container_with_falsy_defaults():
    for falsy in (0, False, "", []):
        container = Container(falsy)
        assert container.never_set is False
        assert container.value == falsy
        assert container.value_or("fallback") == falsy


def test_container_positional_arg_takes_priority():
    container = Container(42, default=99)
    assert container.value == 42


def test_container_extra_positional_args_ignored():
    container = Container(1, 2, 3)
    assert container.value == 1


def test_readme_example():
    config = Container[str]()
    assert config.never_set is True
    assert config.value_or("N/A") == "N/A"

    config.set("production")
    assert config.value == "production"