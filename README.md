from tramp.as_completed import AsCompleted

# Tramp

A collection of useful utilities that can be used in any project.

## Installation

```python
pip install tramp
```

## Annotations

A utility for evaluating string annotations with support for forward references when a name cannot be evaluated. Forward references can be evaluated later by calling the forward reference's `evaluate` method. This is a similar API to [PEP 649](https://peps.python.org/pep-0649/), although it is not fully compatible and only emulates the behavior of `Format.FORWARDREF`. Certain things are not possible (at least not without some serious hacking) such as using `ForwardRef` instances as that would break many annotation types from the `typing` module. To help with this limitation the `tramp.annotations.ForwardRefMeta` type overrides the `isinstance` check to return `True` when Tramp's version of the `ForwardRef` class is used in an instance check (`isinstance` or a match/case). The goal is to implement the most essential parts of the PEP to begin reaping the benefits of forward references now with the least necessary refactoring later.

On Python 3.14 Tramp falls through to the PEP 649 implementation.

```python
from tramp.annotations import get_annotations


class Foo:
    bar: "Bar"


annotations = get_annotations(Foo)  # {'bar': <ForwardRef 'Bar'>}


class Bar:
    pass


annotations["bar"].evaluate()  # <class '__main__.Bar'>
```
It supports generic types, metadata, function calls/class instantiation, etc.
```python
class Foo:
    bar: "list[int]"
    baz: "Callable[[int], str]"
    qux: "Annotated[int, Bar('baz')]"
```

## As Completed

The `AsCompleted` type is a wrapper around `asyncio.as_completed` that adds an async iterator over the results from each task. This simplifies iterating over tasks, eliminating the need to await the next result.

```py
from tramp.as_completed import AsCompleted
...
tasks = [...]
async for result in AsCompleted(*tasks):
    ...
```

Additionally it is possible to use `AsCompleted` in the same way that `as_completed` operates.

```py
for next_result in AsCompleted(*tasks):
    result = await next_result
```

## Containers

A container acts a reference to a changable value.

```python
from tramp import Container

container = Container[int](0)
container.set(1)

print(container.value)  # 1
```

## Modules

Helper functions for working with modules

```python
from tramp import modules
from typing import Any

ns: dict[str, Any] = modules.get_module_namespace("some_module")
```

## Optionals

An optional type that can be used with match statements.

```python
from tramp.optionals import Optional

def foo(x: int) -> Optional[int]:
    if x > 0:
        return Optional.Some(x)
        
    return Optional.Nothing()

result = foo(1)
print(result.value) # 1

result = foo(-1)
print(result.value) # Raises an exception

result = foo(-1)
print(result.value_or(0)) # 0

...

match foo(1):
    case Optional.Some(x):
        print(x)

    case Optional.Nothing():
        print("Nothing")

# Output: 1

match foo(-1):
    case Optional.Some(x):
        print(x)

    case Optional.Nothing():
        print("Nothing")

# Output: Nothing
```

## Results

A result type that can be used with match statements. Works the same as Optionals with an added `error` property.

```python
from tramp.results import Result

with Result.build() as result:
    result.set(1)

print(result.value) # 1
print(result.error) # None

with Result.build() as result:
    raise Execption("Error")

print(result.value) # Raises an exception
print(result.value_or(0)) # 0
print(result.error) # Exception("Error")
```

## Sentinel

A sentinel value that can be used to represent a unique value. Useful for creating `NotSet` types. Instantiating any
sentinel type will always return the same singleton instance of that type allowing for `is` checks.

```python
from tramp.sentinels import sentinel

NotSet = sentinel("NotSet")


def foo(x: int | NotSet = NotSet()) -> int:
    if x is NotSet():
        return 0

    return x
```
