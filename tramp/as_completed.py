"""Tramp's AsCompleted is a simple wrapper around asyncio.as_completed that provides an async iterator that yields the
result of each task as they complete. It can also be used as a standard iterator to access the next result future.

Simple example:

    async for result in AsCompleted(*tasks):

And here's an example falling through to the as_completed iterator:

    for next_result in AsCompleted(*tasks):
        result = await next_result
"""
import asyncio


class AsCompleted:
    """A simple wrapper around asyncio.as_completed that provides an async iterator that yields the result of each task
    as they complete. It can also be used as a standard iterator to access the next result future."""
    def __init__(self, *tasks: asyncio.Task):
        self._tasks = asyncio.as_completed(tasks)

    async def __aiter__(self):
        for next_result in self._tasks:
            yield await next_result

    def __iter__(self):
        return iter(self._tasks)
