import unittest
from unittest.mock import MagicMock, patch

from heurams.kernel.particles.nucleon import Nucleon


class TestNucleon(unittest.TestCase):
    """测试 Nucleon 类"""

    def test_init(self):
        """测试初始化"""
        nucleon = Nucleon(
            "test_id", {"content": "hello", "note": "world"}, {"author": "test"}
        )
        self.assertEqual(nucleon.ident, "test_id")
        self.assertEqual(nucleon.payload, {"content": "hello", "note": "world"})
        self.assertEqual(nucleon.metadata, {"author": "test"})

    def test_init_default_metadata(self):
        """测试使用默认元数据初始化"""
        nucleon = Nucleon("test_id", {"content": "hello"})
        self.assertEqual(nucleon.ident, "test_id")
        self.assertEqual(nucleon.payload, {"content": "hello"})
        self.assertEqual(nucleon.metadata, {})

    def test_getitem(self):
        """测试 __getitem__ 方法"""
        nucleon = Nucleon("test_id", {"content": "hello", "note": "world"})
        self.assertEqual(nucleon["ident"], "test_id")
        self.assertEqual(nucleon["content"], "hello")
        self.assertEqual(nucleon["note"], "world")

        with self.assertRaises(KeyError):
            _ = nucleon["nonexistent"]

    def test_iter(self):
        """测试 __iter__ 方法"""
        nucleon = Nucleon("test_id", {"a": 1, "b": 2, "c": 3})
        keys = list(nucleon)
        self.assertCountEqual(keys, ["a", "b", "c"])

    def test_len(self):
        """测试 __len__ 方法"""
        nucleon = Nucleon("test_id", {"a": 1, "b": 2, "c": 3})
        self.assertEqual(len(nucleon), 3)

    def test_hash(self):
        """测试 __hash__ 方法"""
        nucleon1 = Nucleon("test_id", {})
        nucleon2 = Nucleon("test_id", {"different": "payload"})
        nucleon3 = Nucleon("different_id", {})
        self.assertEqual(hash(nucleon1), hash(nucleon2))  # 相同 ident
        self.assertNotEqual(hash(nucleon1), hash(nucleon3))

    def test_do_eval_simple(self):
        """测试 do_eval 处理简单 eval 表达式"""
        nucleon = Nucleon("test_id", {"result": "eval:1 + 2"})
        nucleon.do_eval()
        self.assertEqual(nucleon.payload["result"], "3")

    def test_do_eval_with_metadata_access(self):
        """测试 do_eval 访问元数据"""
        nucleon = Nucleon(
            "test_id",
            {"result": "eval:nucleon.metadata.get('value', 0)"},
            {"value": 42},
        )
        nucleon.do_eval()
        self.assertEqual(nucleon.payload["result"], "42")

    def test_do_eval_nested(self):
        """测试 do_eval 处理嵌套结构"""
        nucleon = Nucleon(
            "test_id",
            {
                "list": ["eval:2*3", "normal"],
                "dict": {"key": "eval:'hello' + ' world'"},
            },
        )
        nucleon.do_eval()
        self.assertEqual(nucleon.payload["list"][0], "6")
        self.assertEqual(nucleon.payload["list"][1], "normal")
        self.assertEqual(nucleon.payload["dict"]["key"], "hello world")

    def test_do_eval_error(self):
        """测试 do_eval 处理错误表达式"""
        nucleon = Nucleon("test_id", {"result": "eval:1 / 0"})
        nucleon.do_eval()
        self.assertIn("此 eval 实例发生错误", nucleon.payload["result"])

    def test_do_eval_no_eval(self):
        """测试 do_eval 不修改非 eval 字符串"""
        nucleon = Nucleon("test_id", {"text": "plain text", "number": 123})
        nucleon.do_eval()
        self.assertEqual(nucleon.payload["text"], "plain text")
        self.assertEqual(nucleon.payload["number"], 123)

    def test_placeholder(self):
        """测试静态方法 placeholder"""
        placeholder = Nucleon.placeholder()
        self.assertIsInstance(placeholder, Nucleon)
        self.assertEqual(placeholder.ident, "核子对象样例内容")
        self.assertEqual(placeholder.payload, {})
        self.assertEqual(placeholder.metadata, {})


if __name__ == "__main__":
    unittest.main()
