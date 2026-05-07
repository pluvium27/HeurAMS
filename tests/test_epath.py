"""Tests for heurams.services.epath"""

from heurams.services.epath import epath


class TestEpathRead:
    def test_empty_path_returns_self(self):
        d = {"a": 1}
        assert epath(d, "") is d

    def test_simple_key(self):
        d = {"a": 1}
        assert epath(d, "a") == 1

    def test_nested_key(self):
        d = {"a": {"b": {"c": 42}}}
        assert epath(d, "a.b.c") == 42

    def test_missing_key_returns_default(self):
        d = {"a": 1}
        assert epath(d, "b", default=None) is None

    def test_missing_key_no_default(self):
        d = {"a": 1}
        assert epath(d, "b") is None

    def test_list_index_access(self):
        d = {"items": [10, 20, 30]}
        assert epath(d, "items.[1]") == 20

    def test_leading_dot_stripped(self):
        d = {"a": 1}
        assert epath(d, ".a") == 1

    def test_trailing_dot_stripped(self):
        d = {"a": 1}
        assert epath(d, "a.") == 1


class TestEpathParents:
    def test_parents_creates_missing_dict_keys(self):
        d = {}
        result = epath(d, "a.b.c", parents=True, default=None)
        # parents=True creates all intermediate keys including the leaf
        assert result == {}
        assert d == {"a": {"b": {"c": {}}}}


class TestEpathModify:
    def test_modify_dict_key(self):
        d = {"a": 1}
        result = epath(d, "a", enable_modify=True, new_value=99)
        assert result == 99
        assert d["a"] == 99

    def test_modify_nested_key(self):
        d = {"a": {"b": 2}}
        epath(d, "a.b", enable_modify=True, new_value=42)
        assert d["a"]["b"] == 42

    def test_modify_list_index(self):
        d = {"items": [10, 20]}
        epath(d, "items.[0]", enable_modify=True, new_value=99)
        assert d["items"][0] == 99

    def test_modify_list_index_with_parents(self):
        d = {"items": []}
        result = epath(d, "items.[3]", enable_modify=True, new_value=42, parents=True)
        assert result == 42
        assert d["items"] == [None, None, None, 42]
