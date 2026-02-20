import pytest

from tramp.protected_strings import ProtectedString, ProtectedStringFormatError


def test_repr():
    assert repr(ProtectedString("value")) == "<Redacted>"


def test_repr_with_name():
    assert repr(ProtectedString("value", "name")) == "<Redacted Name>"


def test_repr_with_hidden_name():
    assert repr(ProtectedString("value", "name", hide_name=True)) == "<Redacted>"


def test_builder():
    assert (ProtectedString("value") + "other").render() == "<Redacted>other"


def test_builder_format_redacted():
    assert f"{ProtectedString('value') + 'other':***}" == "***other"


def test_builder_format_allowed():
    builder = ProtectedString('FOO', 'foo') + ProtectedString('BAR', 'bar') + 'other'
    assert f"{builder:$foo}" == "FOO<Redacted Bar>other"


def test_builder_format_allowed_and_redacted():
    builder = ProtectedString('FOO', 'foo') + ProtectedString('BAR', 'bar') + 'other'
    assert f"{builder:***$foo}" == "FOO***other"


def test_format_protected_string():
    assert f"{ProtectedString('value')}" == "<Redacted>"
    assert f"{ProtectedString('value', 'name')}" == "<Redacted Name>"
    assert f"{ProtectedString('value', 'name', hide_name=True)}" == "<Redacted>"
    assert f"{ProtectedString('value'):***}" == "***"
    assert f"{ProtectedString('value', 'name'):***}" == "***"
    assert f"{ProtectedString('value', 'name'):$name}" == "value"
    assert f"{ProtectedString('value', 'name'):***$name}" == "value"
    assert f"{ProtectedString('value', 'name'):***$wrong_name}" == "***"


def test_join():
    parts = [ProtectedString('FOO', 'foo'), ProtectedString('BAR', 'bar'), 'other']
    assert ProtectedString.join(parts) == "<Redacted Foo><Redacted Bar>other"
    assert ProtectedString.join(parts, allowed=['foo']) == "FOO<Redacted Bar>other"
    assert ProtectedString.join(parts, redact_with='***') == "******other"
    assert ProtectedString.join(parts, redact_with='***', allowed=['foo']) == "FOO***other"


def test_valid_format_spec():
    with pytest.raises(ProtectedStringFormatError, match="Invalid identifier"):
        f"{ProtectedString('value'):$^}"

    with pytest.raises(ProtectedStringFormatError, match="requires allowed names"):
        f"{ProtectedString('value'):$}"

    with pytest.raises(ProtectedStringFormatError, match="requires allowed names"):
        f"{ProtectedString('value'):***$}"


def test_builder_immutability():
    """Test that + operations return new builders without modifying originals."""
    from tramp.protected_strings import ProtectedStringBuilder
    
    # Test ProtectedString + operation creates builder
    ps1 = ProtectedString("secret1", "s1")
    builder1 = ps1 + "text"
    builder2 = builder1 + "more"
    
    # builder1 and builder2 should be different objects
    assert builder1 is not builder2
    assert len(builder1.strings) == 2  # ps1 + "text"
    assert len(builder2.strings) == 3  # ps1 + "text" + "more"
    
    # Test builder + builder
    ps2 = ProtectedString("secret2", "s2")
    builder3 = ps2 + "other"
    builder4 = builder1 + builder3
    
    assert builder1 is not builder4
    assert builder3 is not builder4
    assert len(builder1.strings) == 2  # Unchanged
    assert len(builder3.strings) == 2  # Unchanged
    assert len(builder4.strings) == 4  # Combined


def test_builder_iadd_mutating():
    """Test that += operations mutate the original builder."""
    from tramp.protected_strings import ProtectedStringBuilder
    
    ps = ProtectedString("secret", "s")
    builder = ps + "text"
    original_id = id(builder)
    
    builder += "more"
    
    # Should be the same object (mutated)
    assert id(builder) == original_id
    assert len(builder.strings) == 3  # ps + "text" + "more"


def test_improved_error_messages():
    """Test that error messages are clear and helpful."""
    ps = ProtectedString("secret", "test")
    
    # Test invalid identifier
    with pytest.raises(ProtectedStringFormatError, match="Invalid identifier.*123invalid"):
        f"{ps:$123invalid}"
    
    # Test empty names after filtering
    with pytest.raises(ProtectedStringFormatError, match="No valid names provided"):
        f"{ps:$   }"
    
    # Test format spec without names
    with pytest.raises(ProtectedStringFormatError, match="requires allowed names"):
        f"{ps:$}"


def test_whitespace_handling():
    """Test that whitespace in format specs is handled properly."""
    ps1 = ProtectedString("secret1", "name1")
    ps2 = ProtectedString("secret2", "name2")
    builder = ps1 + ps2
    
    # Should handle spaces around names
    assert f"{builder:$ name1 , name2 }" == "secret1secret2"
    
    # Should handle extra commas and spaces
    assert f"{builder:$name1,  name2,  }" == "secret1secret2"


def test_constructor_name_validation():
    """Test that constructor warns about invalid names."""
    import warnings
    
    # Valid name should not warn
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        ps = ProtectedString("secret", "valid_name")
        assert len(w) == 0
    
    # Invalid name should warn
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        ps = ProtectedString("secret", "invalid name")
        assert len(w) == 1
        assert "not a valid Python identifier" in str(w[0].message)
        
    # Empty name should not warn
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        ps = ProtectedString("secret", "")
        assert len(w) == 0


def test_unicode_and_edge_cases():
    """Test handling of unicode and edge cases."""
    # Unicode in value
    ps_unicode = ProtectedString("🔒secret🔑", "key")
    assert "🔒secret🔑" in ps_unicode.value
    
    # Very long strings
    long_value = "x" * 1000
    ps_long = ProtectedString(long_value, "long")
    assert ps_long.value == long_value
    assert len(repr(ps_long)) < 20  # Repr should be short regardless
    
    # Empty values
    ps_empty = ProtectedString("", "empty")
    assert ps_empty.value == ""
    assert repr(ps_empty) == "<Redacted Empty>"


def test_case_sensitivity():
    """Test that format spec matching is case-sensitive."""
    ps = ProtectedString("secret", "MyName")
    
    # Exact case should work
    assert f"{ps:$MyName}" == "secret"
    
    # Different cases should not work
    assert f"{ps:$myname}" == "<Redacted Myname>"
    assert f"{ps:$MYNAME}" == "<Redacted Myname>"
    assert f"{ps:$mynAme}" == "<Redacted Myname>"


def test_typing_behavior():
    """Test the documented typing behavior."""
    from tramp.protected_strings import ProtectedStringBuilder
    
    ps = ProtectedString("secret", "name")
    
    # + operator returns ProtectedStringBuilder which is also a ProtectedString
    result = ps + "text"
    assert isinstance(result, ProtectedStringBuilder)
    assert isinstance(result, ProtectedString)  # ProtectedStringBuilder inherits from ProtectedString
    
    # Chain operations work
    result2 = ps + "text" + "more"
    assert isinstance(result2, ProtectedStringBuilder)
    assert isinstance(result2, ProtectedString)
    
    # The original ProtectedString is unchanged and is NOT a builder
    assert isinstance(ps, ProtectedString)
    assert not isinstance(ps, ProtectedStringBuilder)


def test_pattern_matching_consistency():
    """Test that pattern matching works consistently for ProtectedString and ProtectedStringBuilder."""
    
    def process_secret(secret):
        match secret:
            case ProtectedString():
                return secret.value
            case _:
                return None
    
    ps = ProtectedString("secret", "name")
    builder = ps + ""  # Creates ProtectedStringBuilder
    
    # Both should match ProtectedString() pattern
    assert process_secret(ps) == "secret"
    assert process_secret(builder) == "secret"
    
    # Both should be instances of ProtectedString for pattern matching
    assert isinstance(ps, ProtectedString)
    assert isinstance(builder, ProtectedString)


def test_protected_string_add_unsupported_type():
    ps = ProtectedString("secret", "s")
    with pytest.raises(TypeError):
        ps + 42


def test_protected_string_radd_unsupported_type():
    ps = ProtectedString("secret", "s")
    with pytest.raises(TypeError):
        42 + ps


def test_protected_string_iadd_unsupported_type():
    ps = ProtectedString("secret", "s")
    with pytest.raises(TypeError):
        ps += 42


def test_builder_add_unsupported_type():
    builder = ProtectedString("a", "a") + "b"
    with pytest.raises(TypeError):
        builder + 42


def test_builder_radd_unsupported_type():
    builder = ProtectedString("a", "a") + "b"
    with pytest.raises(TypeError):
        42 + builder


def test_builder_iadd_unsupported_type():
    builder = ProtectedString("a", "a") + "b"
    with pytest.raises(TypeError):
        builder += 42


def test_builder_iadd_with_another_builder():
    from tramp.protected_strings import ProtectedStringBuilder

    builder1 = ProtectedString("a", "a") + "b"
    builder2 = ProtectedString("c", "c") + "d"
    original_id = id(builder1)

    builder1 += builder2

    assert id(builder1) == original_id
    assert len(builder1.strings) == 4
    assert f"{builder1:$a,c}" == "abcd"


def test_builder_add_method_with_name():
    from tramp.protected_strings import ProtectedStringBuilder

    builder = ProtectedStringBuilder()
    builder.add("secret_value", name="key")
    assert len(builder.strings) == 1
    assert isinstance(builder.strings[0], ProtectedString)
    assert f"{builder}" == "<Redacted Key>"
    assert f"{builder:$key}" == "secret_value"


def test_builder_add_method_with_hide_name():
    from tramp.protected_strings import ProtectedStringBuilder

    builder = ProtectedStringBuilder()
    builder.add("secret", name="hidden", hide_name=True)
    assert f"{builder}" == "<Redacted>"
    assert f"{builder:$hidden}" == "secret"


def test_builder_repr_all_plain_strings():
    from tramp.protected_strings import ProtectedStringBuilder

    builder = ProtectedStringBuilder("plain1", "plain2")
    assert repr(builder) == "<Redacted>"


def test_builder_value_with_mixed_types():
    from tramp.protected_strings import ProtectedStringBuilder

    ps1 = ProtectedString("secret1", "s1")
    ps2 = ProtectedString("secret2", "s2")
    builder = ps1 + "plain" + ps2
    assert builder.value == "secret1plainsecret2"


def test_readme_single_string_example():
    token = ProtectedString("sk-abc123", name="token")
    assert f"{token}" == "<Redacted Token>"
    assert f"{token:$token}" == "sk-abc123"
    assert f"{token:***}" == "***"
    assert f"{token:***$token}" == "sk-abc123"


def test_readme_builder_example():
    token = ProtectedString("sk-abc123", name="token")
    builder = ProtectedString("user", name="user") + ":" + token
    assert f"{builder}" == "<Redacted User>:<Redacted Token>"
    assert f"{builder:$user,token}" == "user:sk-abc123"
