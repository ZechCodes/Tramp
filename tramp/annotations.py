from typing import Type, Any, get_args, get_origin, Annotated, Union
from collections.abc import Mapping
from tramp.optionals import Optional


class Annotation:
    """Tramp's Annotation type allows for the evaluation of annotations as needed. It's lazy and is lax about names to
    allow for forward references. It takes an annotation that can be a string, a type, or any object along with the
    namespace to evaluate the annotation in.

    If the annotation is a string, it will be evaluated in the namespace using an EvaluationNamespace to prevent all
    name errors. Anytime the annotation references a name that is not in the namespace, a AnnotationForwardReference will be
    injected in its place.

    Evaluations happen every time that the annotation is accessed. This allows for the annotation to be evaluated in
    realtime, reflecting any changes in the namespace.

    A simple example
        import sys
        from inspect import get_annotations

        from tramp.annotations import Annotation
        from tramp.modules import get_module_namespace
        from tramp.optionals import Optional

        class Example:
            foo: "list[Bar]"

        annotation = Annotation(get_annotations(Example)["foo"], Optional.Some(get_module_namespace(__name__, True))
        print(annotation.type)  # <class 'list'>
        print(annotation.args)  # (<AnnotationForwardReference: 'Bar'>,)

        class Bar:
            ...

        print(annotation.type)  # <class 'list'>
        print(annotation.args)  # (<class 'Bar'>,)
    """
    def __init__(self, annotation: str | Type[Any] | Any, some_namespace: Optional[dict[str, Any]] = Optional.Nothing):
        self._annotation = annotation
        self._some_namespace = some_namespace

    @property
    def annotation(self) -> Type[Any] | Any:
        return self._get_annotation()

    @property
    def args(self) -> tuple[Type[Any] | Any, ...]:
        args = get_args(self.annotation)
        if self.is_annotated():
            return args[1:]

        return args

    @property
    def origin(self) -> Type[Any] | Any:
        return get_origin(self.annotation)

    @property
    def type(self) -> Type[Any]:
        if self.is_annotated():
            return Annotation(get_args(self.annotation)[0], self._some_namespace).type

        if self.is_generic():
            return self.origin

        if self.is_type():
            return self.annotation

        if self.args:
            return self.args[0]

        return self.annotation

    def is_annotated(self) -> bool:
        return self.origin is Annotated

    def is_generic(self) -> bool:
        return isinstance(self.origin, type)

    def is_optional(self) -> bool:
        return self.is_union() and type(None) in self.args

    def is_type(self) -> bool:
        return isinstance(self.annotation, type)

    def is_union(self) -> bool:
        return self.origin is Union

    def _get_annotation(self) -> Type[Any] | Any:
        match self._annotation:
            case str():
                return self._evaluate_annotation()

            case _:
                return self._annotation

    def _evaluate_annotation(self) -> Type[Any] | Any:
        return eval(self._annotation, {}, EvaluationNamespace(self._some_namespace.value_or({})))


class EvaluationNamespace(Mapping[str, Any]):
    def __init__(self, namespace: dict[str, Any]):
        self.namespace = namespace

    def __getitem__(self, item: str) -> Any:
        if item in self.namespace:
            return self.namespace[item]

        match self.namespace.get("__builtins__", __builtins__):
            case dict() as builtins if item in builtins:
                return builtins[item]

            case builtins if hasattr(builtins, item):
                return getattr(builtins, item)

        return AnnotationForwardReference(item, Optional.Some(self.namespace))

    def __iter__(self):
        return iter(self.namespace)

    def __len__(self):
        return len(self.namespace)


class AnnotationForwardReference:
    def __init__(self, annotation: str, some_namespace: Optional[dict[str, Any]]):
        self._annotation = annotation
        self._some_namespace = some_namespace

    def __evaluate__(self):
        return Annotation(self._annotation, self._some_namespace)

    def __getattr__(self, name: str) -> Any:
        if name == "__typing_is_unpacked_typevartuple__":
            raise AttributeError(name)

        return AnnotationForwardReference(f"{self._annotation}.{name}", self._some_namespace)

    def __call__(self, *args, **kwargs):
        arg_string = ", ".join(map(repr, args))
        kwarg_string = ", ".join(f"{key}={value!r}" for key, value in kwargs.items())
        return AnnotationForwardReference(f"{self._annotation}({arg_string}, {kwarg_string})", self._some_namespace)

    def __getitem__(self, item: Any):
        return AnnotationForwardReference(f"{self._annotation}[{item!r}]", self._some_namespace)

    def __repr__(self):
        return f"<{type(self).__name__}: {self._annotation!r}>"
