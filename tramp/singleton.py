from typing import TypeVar, Type

T = TypeVar('T', bound='Singleton')


def singleton(cls: Type[T]) -> Type[T]:
    """A decorator to make a class a singleton."""
    old_new = cls.__new__
    def new(*args):
        inst = old_new(*args)
        cls.__new__ = lambda *_: inst
        return inst

    cls.__new__ = new
    return cls
