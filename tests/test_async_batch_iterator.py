import pytest

from tramp.async_batch_iterator import AsyncBatchIterator


async def get_async_batch(batch_index):
    if batch_index == 2:
        return

    return gen(batch_index * 2)


async def gen(start):
    yield start
    yield start + 1


async def get_batch(batch_index):
    if batch_index == 2:
        return

    return (batch_index * 2 + i for i in range(2))


@pytest.mark.asyncio
async def test_async_iterator():
    result = [r async for r in AsyncBatchIterator(get_async_batch)]
    assert result == [0, 1, 2, 3]


@pytest.mark.asyncio
async def test_iterator():
    result = [r async for r in AsyncBatchIterator(get_batch)]
    assert result == [0, 1, 2, 3]


@pytest.mark.asyncio
async def test_get():
    result = await AsyncBatchIterator(get_batch).get()
    assert result == [0, 1, 2, 3]


@pytest.mark.asyncio
async def test_get_limit():
    result = await AsyncBatchIterator(get_batch).get(limit=2)
    assert result == [0, 1]


@pytest.mark.asyncio
async def test_get_limit_zero():
    with pytest.raises(ValueError):
        await AsyncBatchIterator(get_batch).get(limit=0)


@pytest.mark.asyncio
async def test_get_one():
    result = await AsyncBatchIterator(get_batch).one()
    assert result == 0


@pytest.mark.asyncio
async def test_get_one_no_default():
    batcher = AsyncBatchIterator(get_batch)
    await batcher.get()
    with pytest.raises(ValueError):
        await batcher.one()


@pytest.mark.asyncio
async def test_get_one_default():
    batcher = AsyncBatchIterator(get_batch)
    await batcher.get()
    assert await batcher.one(default=1) == 1