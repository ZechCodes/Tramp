from tramp.singleton import singleton


def test_singleton_decorator():
    @singleton
    class MySingleton:
        def __init__(self):
            self.value = 42
    
    instance1 = MySingleton()
    instance2 = MySingleton()
    
    assert instance1 is instance2
    assert instance1.value == 42


def test_singleton_with_arguments():
    @singleton
    class ConfigSingleton:
        def __new__(cls, config_value="default"):
            instance = super().__new__(cls)
            instance.config = config_value
            return instance
    
    instance1 = ConfigSingleton("test_config")
    instance2 = ConfigSingleton("different_config")
    
    assert instance1 is instance2
    assert instance1.config == "test_config"


def test_singleton_state_persistence():
    @singleton
    class StatefulSingleton:
        def __init__(self):
            if not hasattr(self, 'counter'):
                self.counter = 0
        
        def increment(self):
            self.counter += 1
    
    instance1 = StatefulSingleton()
    instance1.increment()
    
    instance2 = StatefulSingleton()
    assert instance2.counter == 1
    
    instance2.increment()
    assert instance1.counter == 2


def test_multiple_singleton_classes():
    @singleton
    class Singleton1:
        pass
    
    @singleton
    class Singleton2:
        pass
    
    s1a = Singleton1()
    s1b = Singleton1()
    s2a = Singleton2()
    s2b = Singleton2()
    
    assert s1a is s1b
    assert s2a is s2b
    assert s1a is not s2a


def test_singleton_with_custom_new():
    @singleton
    class CustomNewSingleton:
        def __new__(cls):
            instance = super().__new__(cls)
            instance.created = True
            return instance
    
    instance1 = CustomNewSingleton()
    instance2 = CustomNewSingleton()
    
    assert instance1 is instance2
    assert hasattr(instance1, 'created')
    assert instance1.created is True


def test_singleton_inheritance():
    @singleton
    class BaseSingleton:
        def __init__(self):
            if not hasattr(self, 'base_value'):
                self.base_value = "base"
    
    # Different non-singleton class to test inheritance behavior
    class RegularClass:
        def __init__(self):
            self.regular_value = "regular"
    
    base1 = BaseSingleton()
    base2 = BaseSingleton()
    
    assert base1 is base2
    assert base1.base_value == "base"
    
    regular1 = RegularClass()
    regular2 = RegularClass()
    
    # These are different instances because RegularClass isn't decorated
    assert regular1 is not regular2


def test_singleton_decorated_inheritance():
    @singleton
    class BaseSingleton:
        def __init__(self):
            self.base_value = "base"
    
    @singleton
    class DerivedSingleton(BaseSingleton):
        def __init__(self):
            super().__init__()
            self.derived_value = "derived"
    
    base1 = BaseSingleton()
    base2 = BaseSingleton()
    derived1 = DerivedSingleton()
    derived2 = DerivedSingleton()
    
    assert base1 is base2
    assert derived1 is derived2
    assert base1 is not derived1