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