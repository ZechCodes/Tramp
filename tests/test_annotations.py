import pytest
from unittest.mock import patch, MagicMock

from tramp.annotations import get_annotations, Format, ForwardRef


def test_fallback_import():
    import sys
    original_modules = sys.modules.copy()
    
    # Force ImportError for annotationlib
    if 'annotationlib' in sys.modules:
        del sys.modules['annotationlib']
    if 'tramp.annotations' in sys.modules:
        del sys.modules['tramp.annotations']
    
    # Block import of annotationlib
    sys.modules['annotationlib'] = None
    
    try:
        # Import should fall back to _annotations
        import tramp.annotations
        from tramp._annotations import get_annotations as fallback_get_annotations
        from tramp._annotations import Format as fallback_Format
        from tramp._annotations import ForwardRef as fallback_ForwardRef
        
        assert tramp.annotations.get_annotations is fallback_get_annotations
        assert tramp.annotations.Format is fallback_Format
        assert tramp.annotations.ForwardRef is fallback_ForwardRef
    finally:
        # Restore original modules
        sys.modules.clear()
        sys.modules.update(original_modules)


def test_format_enum():
    assert Format.VALUE == 1
    assert Format.FORWARDREF == 2
    assert Format.STRING == 3


def test_get_annotations_only_supports_forwardref():
    class TestClass:
        __annotations__ = {'x': 'int', 'y': str}
        __module__ = 'test_module'
    
    with pytest.raises(ValueError, match="Tramp only supports"):
        get_annotations(TestClass, Format.VALUE)


def test_get_annotations_with_string_annotations():
    with patch('sys.modules', {'test_module': MagicMock()}):
        class TestClass:
            __annotations__ = {'x': 'int', 'y': str}
            __module__ = 'test_module'
        
        result = get_annotations(TestClass, Format.FORWARDREF)
        assert 'x' in result
        assert 'y' in result
        assert result['y'] is str


def test_forward_ref_evaluation():
    mock_module = MagicMock()
    mock_module.SomeClass = int
    
    with patch('sys.modules', {'test_module': mock_module}):
        from tramp._annotations import ForwardReferencableNamespace
        
        ns = ForwardReferencableNamespace('test_module')
        
        # Check if 'SomeClass' is in namespace (should be True since it's in mock_module)
        assert 'SomeClass' in ns
        
        # When we access it directly, it should return the int class
        assert ns['SomeClass'] is int


def test_forward_ref_namespace_contains():
    # Test the namespace containment check
    from tramp._annotations import ForwardReferencableNamespace
    
    # Use this test module which has known attributes
    ns = ForwardReferencableNamespace(__name__)
    
    # Should find functions defined in this module
    assert 'test_forward_ref_namespace_contains' in ns


def test_readme_get_annotations_returns_forward_refs():
    class Foo:
        bar: "Bar"

    annotations = get_annotations(Foo, Format.FORWARDREF)
    ref = annotations["bar"]
    assert issubclass(ref, ForwardRef)
    assert repr(ref) == "<ForwardRef 'Bar'>"


def test_readme_forward_ref_evaluate_resolves():
    import sys

    class Foo:
        bar: "Bar"

    annotations = get_annotations(Foo, Format.FORWARDREF)

    class Bar:
        pass

    module = sys.modules[Foo.__module__]
    module.Bar = Bar
    try:
        resolved = annotations["bar"].evaluate()
        assert resolved is Bar
    finally:
        del module.Bar


def test_forward_ref_instancecheck_non_type():
    """ForwardRefMeta.__instancecheck__ returns False for non-type instances."""
    from tramp._annotations import ForwardReferencableNamespace
    ns = ForwardReferencableNamespace(__name__)
    ref = ns["Unknown"]
    assert not isinstance(42, ref)
    assert not isinstance("hello", ref)


def test_forward_ref_class_getitem_iterable():
    """__class_getitem__ with iterable args stores them directly."""
    from tramp._annotations import ForwardReferencableNamespace
    ns = ForwardReferencableNamespace(__name__)
    ref = ns["SomeType"]
    ref[int, str]
    assert ref.args == (int, str)


def test_forward_ref_class_getitem_non_iterable():
    """__class_getitem__ with non-iterable wraps in tuple."""
    from tramp._annotations import ForwardReferencableNamespace
    ns = ForwardReferencableNamespace(__name__)
    ref = ns["SomeType"]
    ref[int]
    assert ref.args == (int,)


def test_forward_ref_repr_with_subscript_args():
    from tramp._annotations import ForwardReferencableNamespace
    ns = ForwardReferencableNamespace(__name__)
    ref = ns["SomeType"]
    ref[int, str]
    assert repr(ref) == "<ForwardRef 'SomeType'>[<class 'int'>, <class 'str'>]"


def test_forward_ref_repr_with_call_args():
    from tramp._annotations import ForwardReferencableNamespace
    ns = ForwardReferencableNamespace(__name__)
    ref = ns["SomeType"]
    ref(1, key=2)
    assert repr(ref) == "<ForwardRef 'SomeType'>(1, key=2)"


def test_forward_ref_repr_with_args_and_call_args():
    from tramp._annotations import ForwardReferencableNamespace
    ns = ForwardReferencableNamespace(__name__)
    ref = ns["SomeType"]
    ref[int, str]
    ref(1, key=2)
    assert repr(ref) == "<ForwardRef 'SomeType'>[<class 'int'>, <class 'str'>](1, key=2)"


def test_forward_ref_evaluate_with_subscript():
    import sys
    from tramp._annotations import ForwardReferencableNamespace
    ns = ForwardReferencableNamespace(__name__)
    ref = ns["_TestSubscriptable"]
    ref[int, str]

    module = sys.modules[__name__]

    class _TestSubscriptable:
        def __class_getitem__(cls, item):
            return ("subscripted", item)

    module._TestSubscriptable = _TestSubscriptable
    try:
        result = ref.evaluate()
        assert result == ("subscripted", (int, str))
    finally:
        del module._TestSubscriptable


def test_forward_ref_evaluate_with_call_args():
    import sys
    from tramp._annotations import ForwardReferencableNamespace
    ns = ForwardReferencableNamespace(__name__)
    ref = ns["_TestCallable"]
    ref(10, name="test")

    module = sys.modules[__name__]
    module._TestCallable = lambda *args, **kwargs: (args, kwargs)
    try:
        result = ref.evaluate()
        assert result == ((10,), {"name": "test"})
    finally:
        del module._TestCallable


def test_builtin_name_becomes_forward_ref():
    """Builtin names are not resolved because __builtins__ is a dict in non-main
    modules, making the hasattr check in ForwardReferencableNamespace a no-op."""
    from tramp._annotations import ForwardReferencableNamespace
    ns = ForwardReferencableNamespace(__name__)
    ref = ns["int"]
    assert issubclass(ref, ForwardRef)


def test_string_annotation_with_builtin_becomes_forward_ref():
    """String annotations referencing builtins become ForwardRef, not the actual type."""
    class Foo:
        x: "int"

    annotations = get_annotations(Foo, Format.FORWARDREF)
    assert issubclass(annotations["x"], ForwardRef)


def test_get_annotations_format_string_raises():
    class Foo:
        x: "int"

    with pytest.raises(ValueError, match="Tramp only supports"):
        get_annotations(Foo, Format.STRING)