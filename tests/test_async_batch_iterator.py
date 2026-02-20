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


@pytest.mark.asyncio
async def test_readme_example_list_batches():
    async def get_batch(index: int):
        if index > 1:
            return None
        return list(range(index * 2, (index + 1) * 2))

    result = [item async for item in AsyncBatchIterator(get_batch)]
    assert result == [0, 1, 2, 3]


@pytest.mark.asyncio
async def test_none_signals_completion():
    async def get_batch(index: int):
        return None

    result = [item async for item in AsyncBatchIterator(get_batch)]
    assert result == []


@pytest.mark.asyncio
async def test_preload_without_index_raises():
    async def get_batch(index: int):
        return None

    with pytest.raises(ValueError, match="Preload requires a batch index"):
        AsyncBatchIterator(get_batch, preload=[1, 2, 3])


@pytest.mark.asyncio
async def test_preload_with_index():
    async def get_batch(index: int):
        if index > 1:
            return None
        return list(range(index * 2, (index + 1) * 2))

    result = [item async for item in AsyncBatchIterator(get_batch, preload=[10, 11], index=0)]
    assert result == [10, 11, 0, 1, 2, 3]


@pytest.mark.asyncio
async def test_get_negative_limit_raises():
    async def get_batch(index: int):
        return [1, 2, 3] if index == 0 else None

    with pytest.raises(ValueError, match="greater than 0"):
        await AsyncBatchIterator(get_batch).get(limit=-1)


@pytest.mark.asyncio
async def test_get_non_integer_limit_raises():
    async def get_batch(index: int):
        return [1, 2, 3] if index == 0 else None

    with pytest.raises(ValueError, match="must be an integer"):
        await AsyncBatchIterator(get_batch).get(limit=3.5)


@pytest.mark.asyncio
async def test_get_iterator_unsupported_type_raises():
    async def get_batch(index: int):
        return 42  # Not iterable, not None

    with pytest.raises(ValueError, match="Unsupported iterable type"):
        async for _ in AsyncBatchIterator(get_batch):
            pass