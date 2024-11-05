import sys
from typing import Any, Callable, Type

from enum import IntEnum


class Format(IntEnum):
    VALUE = 1
    FORWARDREF = 2
    STRING = 3


class ForwardReferencableNamespace:
    def __init__(self, module):
        self.module = module

    def __getitem__(self, item):
        if hasattr(sys.modules[self.module], item):
            return getattr(sys.modules[self.module], item)
        elif hasattr(__builtins__, item):
            return getattr(__builtins__, item)
        else:
            return ForwardRefMeta(
                f"ForwardReferenceTo_{item}",
                (ForwardRef,),
                {"name": item, "namespace": self}
            )

    def __contains__(self, item):
        return hasattr(sys.modules[self.module], item) or hasattr(__builtins__, item)


class ForwardRefMeta(type):
    def __instancecheck__(self, instance):
        if isinstance(instance, type) and issubclass(instance, ForwardRef):
            return True

        return False

    def __repr__(cls):
        annotation = f"<ForwardRef {cls.name!r}>"
        if args := getattr(cls, "args", None):
            annotation += f"[{', '.join(map(repr, args))}]"

        if call_args := getattr(cls, "call_args", None):
            args, kwargs = call_args
            arg_string = ", ".join(map(repr, args))
            kwarg_string = ", ".join(f"{k}={v!r}" for k, v in kwargs.items())
            annotation += f"({', '.join((arg_string, kwarg_string))})"

        return annotation


class ForwardRef(metaclass=ForwardRefMeta):
    name: str
    namespace: ForwardReferencableNamespace
    args: tuple[Any]
    call_args: tuple[tuple[Any, ...], dict[str, Any]]

    def __new__(cls, *args, **kwargs):
        cls.call_args = (args, kwargs)
        return cls

    def __class_getitem__(cls, item):
        cls.args = item if hasattr(item, "__iter__") else (item,)
        return cls

    @classmethod
    def evaluate(cls):
        obj = cls.namespace[cls.name]
        if hasattr(cls, "args"):
            obj = obj[cls.args]

        if hasattr(cls, "call_args"):
            args, kwargs = cls.call_args
            obj = obj(*args, **kwargs)

        return obj


def get_annotations(obj: Type | Callable, annotation_format: Format) -> dict[str, Any]:
    if annotation_format is not Format.FORWARDREF:
        raise ValueError(f"Tramp only supports {Format.FORWARDREF}.")

    forward_reference_ns = ForwardReferencableNamespace(obj.__module__)
    return {
        name: eval(anno, {}, forward_reference_ns) if isinstance(anno, str) else anno
        for name, anno in obj.__annotations__.items()
    }


def testing(foo: "Bar"):
    pass
