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