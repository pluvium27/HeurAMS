import json
import pathlib
import tempfile
import unittest
from unittest.mock import MagicMock, patch

import toml

from heurams.context import ConfigContext
from heurams.kernel.particles.atom import Atom, atom_registry
from heurams.kernel.particles.electron import Electron
from heurams.kernel.particles.nucleon import Nucleon
from heurams.kernel.particles.orbital import Orbital
from heurams.services.config import ConfigFile


class TestAtom(unittest.TestCase):
    """测试 Atom 类"""

    def setUp(self):
        """在每个测试之前运行"""
        # 创建临时目录用于持久化测试
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = pathlib.Path(self.temp_dir.name)

        # 创建默认配置
        self.config = ConfigFile(
            pathlib.Path(__file__).parent.parent.parent.parent
            / "src/heurams/default/config/config.toml"
        )

        # 使用 ConfigContext 设置配置
        self.config_ctx = ConfigContext(self.config)
        self.config_ctx.__enter__()

        # 清空全局注册表
        atom_registry.clear()

    def tearDown(self):
        """在每个测试之后运行"""
        self.config_ctx.__exit__(None, None, None)
        self.temp_dir.cleanup()
        atom_registry.clear()

    def test_init(self):
        """测试 Atom 初始化"""
        atom = Atom("test_atom")
        self.assertEqual(atom.ident, "test_atom")
        self.assertIn("test_atom", atom_registry)
        self.assertEqual(atom_registry["test_atom"], atom)

        # 检查 registry 默认值
        self.assertIsNone(atom.registry["nucleon"])
        self.assertIsNone(atom.registry["electron"])
        self.assertIsNone(atom.registry["orbital"])
        self.assertEqual(atom.registry["nucleon_fmt"], "toml")
        self.assertEqual(atom.registry["electron_fmt"], "json")
        self.assertEqual(atom.registry["orbital_fmt"], "toml")

    def test_link(self):
        """测试 link 方法"""
        atom = Atom("test_link")
        nucleon = Nucleon("test_nucleon", {"content": "test content"})

        atom.link("nucleon", nucleon)
        self.assertEqual(atom.registry["nucleon"], nucleon)

        # 测试链接不支持的键
        with self.assertRaises(ValueError):
            atom.link("invalid_key", "value")

    def test_link_triggers_do_eval(self):
        """测试 link 后触发 do_eval"""
        atom = Atom("test_eval_trigger")
        nucleon = Nucleon("test_nucleon", {"content": "eval:1+1"})

        with patch.object(atom, "do_eval") as mock_do_eval:
            atom.link("nucleon", nucleon)
            mock_do_eval.assert_called_once()

    def test_persist_toml(self):
        """测试 TOML 持久化"""
        atom = Atom("test_persist_toml")
        nucleon = Nucleon("test_nucleon", {"content": "test"})
        atom.link("nucleon", nucleon)

        # 设置路径
        test_path = self.temp_path / "test.toml"
        atom.link("nucleon_path", test_path)

        atom.persist("nucleon")

        # 验证文件存在且内容正确
        self.assertTrue(test_path.exists())
        with open(test_path, "r") as f:
            data = toml.load(f)
        self.assertEqual(data["ident"], "test_nucleon")
        self.assertEqual(data["payload"]["content"], "test")

    def test_persist_json(self):
        """测试 JSON 持久化"""
        atom = Atom("test_persist_json")
        electron = Electron("test_electron", {})
        atom.link("electron", electron)

        test_path = self.temp_path / "test.json"
        atom.link("electron_path", test_path)

        atom.persist("electron")

        self.assertTrue(test_path.exists())
        with open(test_path, "r") as f:
            data = json.load(f)
        self.assertIn("supermemo2", data)

    def test_persist_invalid_format(self):
        """测试无效持久化格式"""
        atom = Atom("test_invalid_format")
        nucleon = Nucleon("test_nucleon", {})
        atom.link("nucleon", nucleon)
        atom.link("nucleon_path", self.temp_path / "test.txt")
        atom.registry["nucleon_fmt"] = "invalid"

        with self.assertRaises(KeyError):
            atom.persist("nucleon")

    def test_persist_no_path(self):
        """测试未初始化路径的持久化"""
        atom = Atom("test_no_path")
        nucleon = Nucleon("test_nucleon", {})
        atom.link("nucleon", nucleon)
        # 不设置 nucleon_path

        with self.assertRaises(TypeError):
            atom.persist("nucleon")

    def test_getitem_setitem(self):
        """测试 __getitem__ 和 __setitem__"""
        atom = Atom("test_getset")
        nucleon = Nucleon("test_nucleon", {})

        atom["nucleon"] = nucleon
        self.assertEqual(atom["nucleon"], nucleon)

        # 测试不支持的键
        with self.assertRaises(KeyError):
            _ = atom["invalid_key"]

        with self.assertRaises(KeyError):
            atom["invalid_key"] = "value"

    def test_do_eval_with_eval_string(self):
        """测试 do_eval 处理 eval: 字符串"""
        atom = Atom("test_do_eval")
        nucleon = Nucleon(
            "test_nucleon",
            {"content": "eval:'hello' + ' world'", "number": "eval:2 + 3"},
        )
        atom.link("nucleon", nucleon)

        # do_eval 应该在链接时自动调用
        # 检查 eval 表达式是否被求值
        self.assertEqual(nucleon.payload["content"], "hello world")
        self.assertEqual(nucleon.payload["number"], "5")

    def test_do_eval_with_config_access(self):
        """测试 do_eval 访问配置"""
        atom = Atom("test_eval_config")
        nucleon = Nucleon(
            "test_nucleon", {"max_riddles": "eval:default['mcq']['max_riddles_num']"}
        )
        atom.link("nucleon", nucleon)

        # 配置中 puzzles.mcq.max_riddles_num = 2
        self.assertEqual(nucleon.payload["max_riddles"], 2)

    def test_placeholder(self):
        """测试静态方法 placeholder"""
        placeholder = Atom.placeholder()
        self.assertIsInstance(placeholder, tuple)
        self.assertEqual(len(placeholder), 3)
        self.assertIsInstance(placeholder[0], Electron)
        self.assertIsInstance(placeholder[1], Nucleon)
        self.assertIsInstance(placeholder[2], dict)

    def test_atom_registry_management(self):
        """测试全局注册表管理"""
        # 创建多个 Atom
        atom1 = Atom("atom1")
        atom2 = Atom("atom2")

        self.assertEqual(len(atom_registry), 2)
        self.assertEqual(atom_registry["atom1"], atom1)
        self.assertEqual(atom_registry["atom2"], atom2)

        # 测试 bidict 的反向查找
        self.assertEqual(atom_registry.inverse[atom1], "atom1")
        self.assertEqual(atom_registry.inverse[atom2], "atom2")


if __name__ == "__main__":
    unittest.main()
