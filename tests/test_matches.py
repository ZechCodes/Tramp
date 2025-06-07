from tramp.matches import (
    AsyncContextManager, AsyncIterable, AsyncIterator, Awaitable, Callable, ContextManager,
    Iterable, Iterator,
)


def test_async_context_manager():
    class Foo:
        async def __aenter__(self):
            pass

        async def __aexit__(self, exc_type, exc_val, exc_tb):
            pass

    assert isinstance(Foo(), AsyncContextManager)


def test_not_async_context_manager():
    class Foo:
        def __enter__(self):
            pass

    class Bar:
        def __exit__(self, exc_type, exc_val, exc_tb):
            pass

    assert not isinstance(Foo(), AsyncContextManager)
    assert not isinstance(Bar(), AsyncContextManager)


def test_async_iterable():
    class Foo:
        def __aiter__(self):
            pass

    assert isinstance(Foo(), AsyncIterable)


def test_async_iterator():
    class Foo:
        async def __anext__(self):
            pass

    assert isinstance(Foo(), AsyncIterator)


def test_awaitable():
    async def foo():
        pass

    coro = foo()
    try:
        assert isinstance(coro, Awaitable)
    finally:
        coro.close()  # Clean up the coroutine to avoid warning


def test_callable():
    def foo():
        pass

    class Foo:
        def __call__(self):
            pass

    assert isinstance(foo, Callable)
    assert isinstance(Foo(), Callable)


def test_context_manager():
    class Foo:
        def __enter__(self):
            pass

        def __exit__(self, exc_type, exc_val, exc_tb):
            pass

    assert isinstance(Foo(), ContextManager)


def test_not_context_manager():
    class Foo:
        def __aenter__(self):
            pass

    class Bar:
        def __aexit__(self, exc_type, exc_val, exc_tb):
            pass

    assert not isinstance(Foo(), ContextManager)
    assert not isinstance(Bar(), ContextManager)


def test_iterable():
    class Foo:
        def __iter__(self):
            pass

    assert isinstance(Foo(), Iterable)


def test_iterator():
    class Foo:
        def __next__(self):
            pass

    assert isinstance(Foo(), Iterator)
