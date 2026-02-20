# Tramp

[![PyPI](https://img.shields.io/pypi/v/tramp)](https://pypi.org/project/tramp/)
[![Python](https://img.shields.io/pypi/pyversions/tramp)](https://pypi.org/project/tramp/)
[![License](https://img.shields.io/pypi/l/tramp)](https://github.com/ZechCodes/Tramp/blob/main/LICENSE)
[![CI](https://github.com/ZechCodes/Tramp/actions/workflows/ci.yaml/badge.svg)](https://github.com/ZechCodes/Tramp/actions/workflows/ci.yaml)

A collection of useful Python utilities for annotations, async iteration, containers, optionals, protected strings, results, sentinels, and singletons.

## Installation

```
pip install tramp
```

## Annotations

Forward-reference-aware annotation evaluation. On Python < 3.14 it provides a [PEP 649](https://peps.python.org/pep-0649/)-style API for resolving string annotations into `ForwardRef` objects that can be evaluated later. On Python 3.14+ it falls through to the stdlib `annotationlib`.

- `get_annotations(obj, *, format=Format.FORWARDREF)` — evaluate annotations on a class, function, or module
- `ForwardRef` — a lazy reference that resolves when `.evaluate()` is called
- `Format` — enum selecting evaluation mode (`FORWARDREF`, `VALUE`, `STRING`)

```python
from tramp.annotations import get_annotations

class Foo:
    bar: "Bar"

annotations = get_annotations(Foo)  # {'bar': <ForwardRef 'Bar'>}

class Bar:
    pass

annotations["bar"].evaluate()  # <class '__main__.Bar'>
```

## Async Batch Iterator

An async iterator that pages through batches, yielding items one at a time. Accepts a coroutine that returns an `Iterable`, `AsyncIterable`, or `None` (to signal completion) for each batch index.

- `AsyncBatchIterator[T](get_batch)` — create an iterator from a batch-fetching coroutine
- `.get(*, limit=None)` — collect all (or up to `limit`) results into a list
- `.one(*, default=)` — return a single result, or `default` / raise if empty

```python
from tramp.async_batch_iterator import AsyncBatchIterator

async def get_batch(index: int) -> list[int] | None:
    if index > 1:
        return None
    return list(range(index * 2, (index + 1) * 2))

async def main():
    async for item in AsyncBatchIterator(get_batch):
        print(item)  # 0, 1, 2, 3
```

## Containers

A mutable reference wrapper. Useful for sharing changeable state across functions or deferring initialization.

- `Container[T](default?)` — create a container, optionally with an initial value
- `.value` — access the stored value (raises `ValueError` if never set)
- `.set(value)` — update the stored value
- `.value_or(default)` — return the value or a fallback if never set
- `.never_set` — `True` if no value has been assigned

```python
from tramp.containers import Container

config = Container[str]()
print(config.never_set)      # True
print(config.value_or("N/A")) # N/A

config.set("production")
print(config.value)           # production
```

## Optionals

A pattern-matchable optional type with `Some` and `Nothing` variants.

- `Optional[V]` — base type (not instantiable directly)
- `Optional.Some(value)` / `Optional.Nothing()` — construct variants
- `.value` — unwrap or raise `OptionalHasNoValueException`
- `.value_or(default)` — unwrap or return a fallback
- `Optional.wrap(obj)` — convert `None` to `Nothing`, anything else to `Some`

```python
from tramp.optionals import Optional

result = Optional.wrap(42)

match result:
    case Optional.Some(x):
        print(f"Got {x}")    # Got 42
    case Optional.Nothing():
        print("Nothing")
```

## Protected Strings

Strings that redact themselves when rendered, with selective f-string revelation via `$name` format specs.

- `ProtectedString(value, name="", *, hide_name=False)` — create a redacted string
- `ProtectedStringBuilder` — built automatically when concatenating protected and plain strings
- `ProtectedStringFormatError` — raised on invalid format specs

```python
from tramp.protected_strings import ProtectedString

token = ProtectedString("sk-abc123", name="token")
print(f"{token}")             # <Redacted Token>
print(f"{token:$token}")      # sk-abc123
print(f"{token:***}")         # ***
print(f"{token:***$token}")   # sk-abc123

builder = ProtectedString("user", name="user") + ":" + token
print(f"{builder}")           # <Redacted User>:<Redacted Token>
print(f"{builder:$user,token}") # user:sk-abc123
```

## Results

A context-manager-based result type with `Value` and `Error` variants, supporting pattern matching.

- `Result[V]` — base type (not instantiable directly)
- `Result.build()` — context manager that captures exceptions into `Error`, or a set `.value` into `Value`
- `.value` — unwrap or raise `ResultWasAnErrorException`
- `.value_or(default)` — unwrap or return a fallback
- `.error` — the captured exception, or `None`

```python
from tramp.results import Result

with Result.build() as result:
    result.value = 42

match result:
    case Result.Value(v):
        print(f"Success: {v}")  # Success: 42
    case Result.Error(e):
        print(f"Failed: {e}")
```

## Sentinels

Create singleton sentinel types for use as default-value markers or unique tokens.

- `sentinel(name)` — return a new sentinel type whose instances are always the same object

```python
from tramp.sentinels import sentinel

NotSet = sentinel("NotSet")

def get(key: str, default: int | NotSet = NotSet()) -> int:
    if default is NotSet():
        raise KeyError(key)
    return default
```

## Singleton

A decorator that makes a class a singleton — all instantiations return the same object.

- `@singleton` — decorate a class to enforce a single instance

```python
from tramp.singleton import singleton

@singleton
class Config:
    def __init__(self):
        self.debug = False

a = Config()
b = Config()
assert a is b  # True
```
