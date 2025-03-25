from typing import Protocol, runtime_checkable


@runtime_checkable
class AsyncContextManager(Protocol):
    async def __aenter__(self):
        ...

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        ...


@runtime_checkable
class AsyncIterable(Protocol):
    def __aiter__(self):
        ...


@runtime_checkable
class AsyncIterator(Protocol):
    async def __anext__(self):
        ...


@runtime_checkable
class Awaitable(Protocol):
    def __await__(self):
        ...


@runtime_checkable
class Callable(Protocol):
    def __call__(self, *args, **kwargs):
        ...


@runtime_checkable
class ContextManager(Protocol):
    def __enter__(self):
        ...

    def __exit__(self, exc_type, exc_val, exc_tb):
        ...


@runtime_checkable
class Iterable(Protocol):
    def __iter__(self):
        ...


@runtime_checkable
class Iterator(Protocol):
    def __next__(self):
        ...
