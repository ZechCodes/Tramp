from typing import Type, Any, get_args, get_origin
from collections.abc import Mapping
from tramp.optionals import Optional


class Annotation:
    def __init__(self, annotation: str | Type[Any] | Any, namespace: Optional[dict[str, Any]] = Optional.Nothing):
        self._annotation = annotation
        self._namespace = namespace.value_or({})

    @property
    def annotation(self) -> Type[Any] | Any:
        return self._get_annotation()

    @property
    def args(self) -> tuple[Type[Any] | Any, ...]:
        return get_args(self.annotation)

    @property
    def origin(self) -> Type[Any] | Any:
        return get_origin(self.annotation)

    @property
    def type(self) -> Type[Any]:
        if isinstance(self.annotation, type):
            return self.annotation

        return self.args[0]

    def _get_annotation(self) -> Type[Any] | Any:
        match self._annotation:
            case str():
                return self._evaluate_annotation()

            case _:
                return self._annotation

    def _evaluate_annotation(self) -> Type[Any] | Any:
        return eval(self._annotation, {}, EvaluationNamespace(self._namespace))


class EvaluationNamespace(Mapping[str, Any]):
    def __init__(self, namespace: dict[str, Any]):
        self.namespace = namespace

    def __getitem__(self, item: str) -> Any:
        if item in self.namespace:
            return self.namespace[item]

        if hasattr(__builtins__, item):
            return getattr(__builtins__, item)

        return ForwardReferenceObject()

    def __iter__(self):
        return iter(self.namespace)

    def __len__(self):
        return len(self.namespace)


class ForwardReferenceObject:
    def __getattr__(self, name: str) -> Any:
        if name == "__typing_is_unpacked_typevartuple__":
            raise AttributeError(name)

        return self

    def __call__(self, *_, **__):
        return self

    def __getitem__(self, _):
        return self
