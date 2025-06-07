from tramp.sentinels import Sentinel, SentinelMCS, sentinel


def test_sentinel_singleton():
    class MySentinel(Sentinel):
        pass
    
    s1 = MySentinel()
    s2 = MySentinel()
    
    assert s1 is s2


def test_sentinel_repr():
    class MySentinel(Sentinel):
        pass
    
    s = MySentinel()
    repr_str = repr(s)
    assert "Sentinel:" in repr_str and "MySentinel" in repr_str


def test_sentinel_class_repr():
    class MySentinel(Sentinel):
        pass
    
    repr_str = repr(MySentinel)
    assert "sentinel class 'MySentinel'" in repr_str


def test_sentinel_function():
    MySentinel = sentinel("MySentinel")
    
    s1 = MySentinel()
    s2 = MySentinel()
    
    assert s1 is s2
    assert isinstance(s1, Sentinel)


def test_sentinel_function_repr():
    MySentinel = sentinel("TestSentinel")
    s = MySentinel()
    
    repr_str = repr(s)
    assert "Sentinel:TestSentinel" in repr_str


def test_sentinel_function_class_repr():
    MySentinel = sentinel("TestSentinel")
    
    repr_str = repr(MySentinel)
    assert "sentinel class 'TestSentinel'" in repr_str


def test_multiple_sentinels():
    Sentinel1 = sentinel("First")
    Sentinel2 = sentinel("Second")
    
    s1 = Sentinel1()
    s2 = Sentinel2()
    
    assert s1 is not s2
    assert type(s1) is not type(s2)


def test_sentinel_metaclass():
    assert isinstance(Sentinel, SentinelMCS)
    
    MySentinel = sentinel("MySentinel")
    assert isinstance(MySentinel, SentinelMCS)


def test_sentinel_inheritance():
    MySentinel = sentinel("MySentinel")
    s = MySentinel()
    
    assert isinstance(s, Sentinel)
    assert isinstance(s, MySentinel)


def test_sentinel_uniqueness():
    class UniqueSentinel(Sentinel):
        pass
    
    s = UniqueSentinel()
    
    assert s is not Sentinel()
    
    OtherSentinel = sentinel("Other")
    other = OtherSentinel()
    
    assert s is not other