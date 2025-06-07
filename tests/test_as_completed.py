import asyncio
import pytest

from tramp.as_completed import AsCompleted


async def slow_task(value, delay=0.1):
    await asyncio.sleep(delay)
    return value


async def fast_task(value):
    return value


@pytest.mark.asyncio
async def test_async_iteration():
    task1 = asyncio.create_task(slow_task(1, 0.2))
    task2 = asyncio.create_task(fast_task(2))
    task3 = asyncio.create_task(slow_task(3, 0.1))
    
    results = []
    async for result in AsCompleted(task1, task2, task3):
        results.append(result)
    
    assert set(results) == {1, 2, 3}
    assert results[0] == 2


@pytest.mark.asyncio
async def test_sync_iteration():
    task1 = asyncio.create_task(slow_task(1, 0.2))
    task2 = asyncio.create_task(fast_task(2))
    task3 = asyncio.create_task(slow_task(3, 0.1))
    
    results = []
    for future in AsCompleted(task1, task2, task3):
        result = await future
        results.append(result)
    
    assert set(results) == {1, 2, 3}
    assert results[0] == 2


@pytest.mark.asyncio
async def test_empty_tasks():
    results = []
    async for result in AsCompleted():
        results.append(result)
    
    assert results == []


@pytest.mark.asyncio
async def test_single_task():
    task = asyncio.create_task(fast_task(42))
    
    results = []
    async for result in AsCompleted(task):
        results.append(result)
    
    assert results == [42]


@pytest.mark.asyncio
async def test_exception_handling():
    async def failing_task():
        raise ValueError("test error")
    
    task1 = asyncio.create_task(fast_task(1))
    task2 = asyncio.create_task(failing_task())
    
    results = []
    exceptions = []
    
    try:
        async for result in AsCompleted(task1, task2):
            results.append(result)
    except ValueError as e:
        exceptions.append(e)
    
    # Either we got one result and one exception, or the exception was raised
    assert len(results) == 1 or len(exceptions) == 1
    if results:
        assert results[0] == 1