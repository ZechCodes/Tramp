from mailbox import FormatError

import pytest

from tramp.protected_strings import ProtectedString


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
    with pytest.raises(FormatError):
        f"{ProtectedString('value'):$^}"

    with pytest.raises(FormatError):
        f"{ProtectedString('value'):$}"

    with pytest.raises(FormatError):
        f"{ProtectedString('value'):***$}"
