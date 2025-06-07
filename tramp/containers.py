"""Container utilities for managing mutable references.

This module provides the Container class, which offers a way to create mutable
references to values. This is particularly useful in scenarios where you need
to share and modify state across different parts of your application, or when
you need to pass mutable references to functions.

Key Features:
    - Type-safe generic containers
    - Optional initialization with default values  
    - Safe value access with proper error handling
    - Fallback values with value_or() method
    - State tracking with never_set property

Common Use Cases:
    - Sharing mutable state between functions
    - Configuration objects that may be set later
    - Accumulator patterns in functional programming
    - Reference-like behavior in pure Python
"""
from typing import overload, TypeVar, Generic

T = TypeVar("T")


class Container(Generic[T]):
    """Containers are used to provide a reference to a changeable value.
    
    A Container provides a way to store and modify a value that can be shared
    across different parts of your code. It's particularly useful when you need
    to pass a mutable reference to a value, similar to how you might use a
    reference or pointer in other languages.
    
    Examples:
        Basic usage with initial value:
        
        >>> container = Container(42)
        >>> container.value
        42
        >>> container.set(100)
        >>> container.value
        100
        
        Creating an empty container and setting value later:
        
        >>> container = Container()
        >>> container.never_set
        True
        >>> container.set("hello")
        >>> container.never_set
        False
        >>> container.value
        'hello'
        
        Using value_or() to provide defaults:
        
        >>> empty_container = Container()
        >>> empty_container.value_or("default")
        'default'
        >>> 
        >>> filled_container = Container("actual")
        >>> filled_container.value_or("default")
        'actual'
        
        Type-safe containers with generics:
        
        >>> int_container: Container[int] = Container(0)
        >>> str_container: Container[str] = Container("initial")
        >>> int_container.set(42)  # Type checker knows this should be int
        >>> str_container.set("updated")  # Type checker knows this should be str
        
        Sharing containers between functions:
        
        >>> def increment_counter(counter: Container[int]) -> None:
        ...     current = counter.value_or(0)
        ...     counter.set(current + 1)
        ...
        >>> shared_counter = Container(5)
        >>> increment_counter(shared_counter)
        >>> shared_counter.value
        6
    """

    @overload
    def __init__(self):
        ...

    @overload
    def __init__(self, default: T):
        ...

    def __init__(self, *args, **kwargs):
        self._set, self._value = self._process_args(args, kwargs)

    @property
    def never_set(self) -> bool:
        return self._set is False

    @property
    def value(self):
        if self.never_set:
            raise ValueError("No value has been set on the container.")

        return self._value

    def set(self, value: T):
        self._value = value
        self._set = True

    def value_or(self, default: T) -> T:
        return self._value if self._set else default

    def _process_args(self, args, kwargs):
        if len(args):
            return True, args[0]

        if "default" in kwargs:
            return True, kwargs["default"]

        return False, None
