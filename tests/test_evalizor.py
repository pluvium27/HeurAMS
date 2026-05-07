"""Tests for heurams.kernel.auxiliary.evalizor.Evalizer"""

from heurams.kernel.auxiliary.evalizor import Evalizer


class TestEvalizer:
    def test_noop_on_plain_string(self):
        e = Evalizer({"x": 42})
        assert e("hello") == "hello"

    def test_eval_expression(self):
        e = Evalizer({"x": 42})
        assert e("eval: x") == 42

    def test_eval_arithmetic(self):
        e = Evalizer({"a": 10, "b": 20})
        assert e("eval: a + b") == 30

    def test_traverses_dict(self):
        e = Evalizer({"val": 99})
        data = {"key_a": "plain", "key_b": "eval: val + 1"}
        result = e(data)
        assert result == {"key_a": "plain", "key_b": 100}

    def test_traverses_list(self):
        e = Evalizer({"val": 5})
        data = ["eval: val", "plain", "eval: val * 2"]
        result = e(data)
        assert result == [5, "plain", 10]

    def test_traverses_nested(self):
        e = Evalizer({"val": 3})
        data = {"outer": {"inner": "eval: val ** 2"}}
        result = e(data)
        assert result == {"outer": {"inner": 9}}

    def test_traverses_tuple(self):
        e = Evalizer({"val": 7})
        data = ("eval: val", "other")
        result = e(data)
        assert result == (7, "other")

    def test_non_string_passthrough(self):
        e = Evalizer({})
        assert e(42) == 42
        assert e(None) is None
        assert e([1, 2, 3]) == [1, 2, 3]
