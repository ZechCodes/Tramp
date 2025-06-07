import sys
from unittest.mock import MagicMock

from tramp.modules import get_module_namespace


def test_get_module_namespace():
    mock_module = MagicMock()
    mock_module.some_var = "test_value"
    mock_module.some_func = lambda: "test_func"
    
    sys.modules['test_module'] = mock_module
    
    try:
        namespace = get_module_namespace('test_module')
        
        assert 'some_var' in namespace
        assert namespace['some_var'] == "test_value"
        assert 'some_func' in namespace
        assert callable(namespace['some_func'])
        
    finally:
        if 'test_module' in sys.modules:
            del sys.modules['test_module']


def test_get_module_namespace_builtin():
    namespace = get_module_namespace('sys')
    
    assert 'modules' in namespace
    assert 'path' in namespace
    assert namespace['modules'] is sys.modules


def test_get_module_namespace_current_module():
    namespace = get_module_namespace(__name__)
    
    assert 'test_get_module_namespace' in namespace
    assert callable(namespace['test_get_module_namespace'])