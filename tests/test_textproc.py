"""Tests for heurams.services.textproc"""

from heurams.services.textproc import domize, truncate, undomize


class TestTruncate:
    def test_short_string_unchanged(self):
        assert truncate("ab") == "ab"

    def test_three_char_unchanged(self):
        assert truncate("abc") == "abc"

    def test_longer_string_truncated(self):
        assert truncate("abcd") == "abc>"

    def test_empty_string(self):
        assert truncate("") == ""


class TestDomizeUndomize:
    def test_domize_replaces_dot(self):
        assert domize("a.b.c") == "a--DOT--b--DOT--c"

    def test_domize_no_dot(self):
        assert domize("abc") == "abc"

    def test_undomize_restores_dot(self):
        assert undomize("a--DOT--b") == "a.b"

    def test_undomize_no_marker(self):
        assert undomize("abc") == "abc"

    def test_roundtrip(self):
        original = "config.key.subkey"
        assert undomize(domize(original)) == original
