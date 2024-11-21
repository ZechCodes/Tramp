"""
Batched Async Iterator yields results one at a time from batches. It takes a coroutine that fetches batches and returns
them as an iterable. The iterable can be of either type Iterable or AsyncIterable. The coroutine should accept a batch
index to determine which batch to return next.

The AsyncBatchIterator can be preloaded with a batch by passing it to the constructor along with a batch index.

Example:
    async def get_batch(batch_index: int) -> Iterable[int] | None:
        if batch_index > 1:
            return

        return range(batch_index * 2, (batch_index + 1) * 2)

    async for result in AsyncBatchIterator(get_batch):
        print(result)

    # Output:
    # 0
    # 1
    # 2
    # 3


Async Iterator Example:
    async def get_batch(batch_index: int) -> AsyncIterable[int] | None:
        if batch_index > 1:
            return

        return gen(batch_index * 2)

    async def gen(start: int) -> AsyncGenerator[int, None]:
        yield start
        yield start + 1

    async for result in AsyncBatchIterator(get_batch):
        print(result)

    # Output:
    # 0
    # 1
    # 2
    # 3
"""

from typing import (
    AsyncIterable,
    AsyncIterator,
    Awaitable,
    Callable,
    Generic, Iterable,
    Iterator,
    overload,
    Protocol,
    runtime_checkable,
    TypeAlias,
    TypeVar,
)

from tramp.sentinels import sentinel

T = TypeVar("T")
_NOT_SET = sentinel("_NOT_SET")

MaybeAsyncIterable: TypeAlias = Iterable[T] | AsyncIterable[T]
MaybeAsyncIterator: TypeAlias = Iterator[T] | AsyncIterator[T]


@runtime_checkable
class AsyncIterableProtocol(Protocol):
    def __aiter__(self):
        ...


@runtime_checkable
class AsyncIteratorProtocol(Protocol):
    async def __anext__(self):
        ...


@runtime_checkable
class IterableProtocol(Protocol):
    def __iter__(self):
        ...


@runtime_checkable
class IteratorProtocol(Protocol):
    def __next__(self):
        ...


def _get_iterator(iterable: MaybeAsyncIterable[T]) -> MaybeAsyncIterator[T]:
    match iterable:
        case AsyncIterableProtocol():
            return aiter(iterable)

        case IterableProtocol():
            return iter(iterable)

        case None:
            return _NullIterator()

        case _:
            raise ValueError(f"Unsupported iterable type: {type(iterable)}")



async def _get_next(iterator: MaybeAsyncIterator[T]) -> T:
    match iterator:
        case AsyncIteratorProtocol():
            return await anext(iterator)

        case IteratorProtocol():
            return _async_safe_next(iterator)

        case _:
            raise ValueError(f"Unsupported iterator type: {type(iterator)}")


def _async_safe_next(iterator: Iterator[T]) -> T:
    try:
        return next(iterator)
    except StopIteration:
        raise StopAsyncIteration


class _NullIterator:
    def __iter__(self):
        return self

    def __aiter__(self):
        return self

    def __next__(self):
        raise StopIteration

    async def __anext__(self):
        raise StopAsyncIteration


class AsyncBatchIterator(Generic[T]):
    """AsyncBatchIterator is an async iterator that yields results from batches one at a time, fetching new batches as
    needed. New batches are fetched using a provided coroutine that takes an index and returns an iterable of results.
    The iterable can either be an Iterable or an AsyncIterable."""

    @overload
    def __init__(self, get_batch: Callable[[int], Awaitable[MaybeAsyncIterable[T] | None]]):
        ...

    @overload
    def __init__(
        self,
        get_batch: Callable[[int], Awaitable[MaybeAsyncIterable[T] | None]],
        preload: MaybeAsyncIterable[T],
        index: int
    ):
        ...

    def __init__(
        self,
        get_batch: Callable[[int], Awaitable[MaybeAsyncIterable[T] | None]],
        preload: MaybeAsyncIterable[T] | None = None,
        index: int | None = None
    ):
        if preload is not None and index is None:
            raise ValueError("Preload requires a batch index")

        self._get_batch = get_batch
        self._batch: MaybeAsyncIterator = preload if preload is not None else _NullIterator()
        self._index = 0 if index is None else index

    def __aiter__(self):
        return self

    async def __anext__(self) -> T:
        try:
            return await _get_next(self._batch)
        except StopAsyncIteration:
            self._batch = await self._get_next_batch()
            try:
                return await _get_next(self._batch)
            except StopAsyncIteration:
                self._index -= 1 # Reset the index if the batch is empty
                raise StopAsyncIteration

    async def get(self, *, limit: int | None = None) -> list[T]:
        """Get all results from the iterator. If a limit is provided, the iterator will stop after the limit is reached.
        """
        match limit:
            case None:
                _limit = -1

            case int() if limit > 0:
                _limit = limit

            case int():
                raise ValueError("Limit must be greater than 0")

            case _:
                raise ValueError("Limit must be an integer")

        results = []
        async for result in self:
            results.append(result)
            if len(results) == limit:
                break

        return results

    async def one(self, *, default: T | _NOT_SET = _NOT_SET()) -> T:
        """Get one result from the iterator. If the iterator is empty, a ValueError is raised unless a default value is
        provided."""
        if default is _NOT_SET():
            try:
                return await anext(self)
            except StopAsyncIteration:
                raise ValueError("N`o results to return")

        try:
            return await anext(self)
        except StopAsyncIteration:
            return default

    async def _get_next_batch(self) -> MaybeAsyncIterator[T]:
        batch = _get_iterator(
            await self._get_batch(self._index)
        )
        self._index += 1
        return batch
