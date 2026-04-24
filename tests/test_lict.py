"""Tests for heurams.kernel.auxiliary.lict.Lict"""

import pytest

from heurams.kernel.auxiliary.lict import Lict


class TestLictInit:
    def test_empty(self):
        l = Lict()
        assert len(l) == 0
        assert list(l) == []

    def test_from_list(self):
        l = Lict(initlist=[("a", 1), ("b", 2)])
        assert l["a"] == 1
        assert l["b"] == 2
        assert len(l) == 2

    def test_from_dict(self):
        l = Lict(initdict={"x": 10, "y": 20})
        assert l["x"] == 10
        assert l["y"] == 20
        assert len(l) == 2


class TestLictListInterface:
    def test_list_getitem(self):
        l = Lict(initlist=[("a", 1), ("b", 2)])
        assert l[0] == ("a", 1)
        assert l[1] == ("b", 2)

    def test_list_setitem(self):
        l = Lict(initlist=[("a", 1), ("b", 2)])
        l[0] = ("c", 3)
        assert l["c"] == 3
        assert l[0] == ("c", 3)

    def test_list_delitem(self):
        l = Lict(initlist=[("a", 1), ("b", 2)])
        del l[0]
        assert "a" not in l
        assert len(l) == 1

    def test_append(self):
        l = Lict()
        l.append(("k", "v"))
        assert l["k"] == "v"
        assert l[0] == ("k", "v")

    def test_insert(self):
        l = Lict(initlist=[("a", 1), ("c", 3)])
        l.insert(1, ("b", 2))
        assert l[1] == ("b", 2)
        assert l["b"] == 2
        assert len(l) == 3

    def test_pop(self):
        l = Lict(initlist=[("a", 1), ("b", 2)])
        item = l.pop()
        assert item == ("b", 2)
        assert "b" not in l

    def test_remove_by_key(self):
        l = Lict(initlist=[("a", 1), ("b", 2)])
        l.remove("a")
        assert "a" not in l
        assert len(l) == 1

    def test_remove_by_tuple(self):
        l = Lict(initlist=[("a", 1), ("b", 2)])
        l.remove(("a", 1))
        assert "a" not in l

    def test_clear(self):
        l = Lict(initlist=[("a", 1)])
        l.clear()
        assert len(l) == 0
        assert list(l) == []


class TestLictDictInterface:
    def test_dict_getitem(self):
        l = Lict(initlist=[("a", 1)])
        assert l["a"] == 1

    def test_dict_setitem(self):
        l = Lict()
        l["k"] = "v"
        assert l["k"] == "v"
        # dict set marks list dirty — sync on access
        assert l[0] == ("k", "v")

    def test_dict_delitem(self):
        l = Lict(initlist=[("a", 1), ("b", 2)])
        del l["a"]
        assert "a" not in l
        assert len(l) == 1

    def test_keys(self):
        l = Lict(initlist=[("a", 1), ("b", 2)])
        assert set(l.keys()) == {"a", "b"}

    def test_values(self):
        l = Lict(initlist=[("a", 1), ("b", 2)])
        assert set(l.values()) == {1, 2}

    def test_items(self):
        l = Lict(initlist=[("a", 1), ("b", 2)])
        assert set(l.items()) == {("a", 1), ("b", 2)}

    def test_get_itemic_unit(self):
        l = Lict(initlist=[("a", 1)])
        assert l.get_itemic_unit("a") == ("a", 1)


class TestLictSync:
    def test_dict_to_list_sync(self):
        """After dict modification, list access triggers sync."""
        l = Lict(initdict={"a": 1})
        assert l[0] == ("a", 1)

    def test_list_to_dict_sync(self):
        """After list modification, dict access triggers sync."""
        l = Lict(initlist=[("a", 1)])
        assert l["a"] == 1

    def test_append_list_maintained(self):
        l = Lict()
        l.append(("x", 100))
        l.append(("y", 200))
        # List order preserved
        assert list(l) == [("x", 100), ("y", 200)]


class TestLictEdgeCases:
    def test_append_non_tuple_raises(self):
        l = Lict()
        with pytest.raises(NotImplementedError):
            l.append("not_a_tuple")  # type: ignore

    def test_append_bad_tuple_raises(self):
        l = Lict()
        with pytest.raises(NotImplementedError):
            l.append((1, 2, 3))  # type: ignore

    def test_contains_by_key(self):
        l = Lict(initlist=[("a", 1)])
        assert "a" in l

    def test_contains_by_value(self):
        l = Lict(initlist=[("a", 1)])
        assert 1 in l

    def test_contains_by_tuple(self):
        l = Lict(initlist=[("a", 1)])
        assert ("a", 1) in l

    def test_not_contains(self):
        l = Lict(initlist=[("a", 1)])
        assert "z" not in l

    def test_forced_order(self):
        l = Lict(initlist=[("b", 2), ("a", 1)], forced_order=True)
        assert l[0] == ("a", 1)
        assert l[1] == ("b", 2)

    def test_append_if_not_exists(self):
        l = Lict()
        l.append_if_it_doesnt_exist_before(("k", "v"))
        assert l["k"] == "v"
        l.append_if_it_doesnt_exist_before(("k", "v"))
        assert len(l) == 1

    def test_keys_equal_with(self):
        a = Lict(initlist=[("x", 1), ("y", 2)])
        b = Lict(initlist=[("y", 3), ("x", 4)])
        assert a.keys_equal_with(b)

    def test_index_raises(self):
        l = Lict()
        with pytest.raises(NotImplementedError):
            l.index()

    def test_extend_raises(self):
        l = Lict()
        with pytest.raises(NotImplementedError):
            l.extend()

    def test_sort_raises(self):
        l = Lict()
        with pytest.raises(NotImplementedError):
            l.sort()

    def test_reverse_raises(self):
        l = Lict()
        with pytest.raises(NotImplementedError):
            l.reverse()
