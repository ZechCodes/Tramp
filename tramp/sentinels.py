from typing import Type, cast


class SentinelMCS(type):
    def __repr__(self):
        return f"<sentinel class '{self.__name__}'>"


class Sentinel(metaclass=SentinelMCS):
    def __new__(cls):
        inst = super().__new__(cls)
        cls.__new__ = lambda _: inst
        return inst

    def __repr__(self):
        return f"<Sentinel:{type(self).__qualname__}>"


def sentinel(name: str) -> Type[Sentinel]:
    """Create a new sentinel type."""

    return cast(Type[Sentinel], SentinelMCS(name, (Sentinel,), {}))
