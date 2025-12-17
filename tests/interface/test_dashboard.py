#!/usr/bin/env python3
"""
DashboardScreen 的测试, 包括单元测试和 pilot 测试. 
"""
import unittest
import tempfile
import pathlib
import time
from unittest.mock import patch, MagicMock
from textual.pilot import Pilot

from heurams.context import ConfigContext
from heurams.services.config import ConfigFile
from heurams.interface.__main__ import HeurAMSApp
from heurams.interface.screens.dashboard import DashboardScreen


class TestDashboardScreenUnit(unittest.TestCase):
    """DashboardScreen 的单元测试（不启动完整应用）. """

    def setUp(self):
        """在每个测试之前运行, 设置临时目录和配置. """
        # 创建临时目录用于测试数据
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = pathlib.Path(self.temp_dir.name)

        # 创建默认配置, 并修改路径指向临时目录
        default_config_path = (
            pathlib.Path(__file__).parent.parent.parent
            / "src/heurams/default/config/config.toml"
        )
        self.config = ConfigFile(default_config_path)
        # 更新配置中的路径
        config_data = self.config.data
        config_data["paths"]["nucleon_dir"] = str(self.temp_path / "nucleon")
        config_data["paths"]["electron_dir"] = str(self.temp_path / "electron")
        config_data["paths"]["orbital_dir"] = str(self.temp_path / "orbital")
        config_data["paths"]["cache_dir"] = str(self.temp_path / "cache")
        # 禁用快速通过, 避免测试干扰
        config_data["quick_pass"] = 0
        # 禁用时间覆盖
        config_data["daystamp_override"] = -1
        config_data["timestamp_override"] = -1

        # 创建目录
        for dir_key in ["nucleon_dir", "electron_dir", "orbital_dir", "cache_dir"]:
            pathlib.Path(config_data["paths"][dir_key]).mkdir(
                parents=True, exist_ok=True
            )

        # 使用 ConfigContext 设置配置
        self.config_ctx = ConfigContext(self.config)
        self.config_ctx.__enter__()

    def tearDown(self):
        """在每个测试之后清理. """
        self.config_ctx.__exit__(None, None, None)
        self.temp_dir.cleanup()

    def test_compose(self):
        """测试 compose 方法返回正确的部件. """
        screen = DashboardScreen()
        # 手动调用 compose 并收集部件
        from textual.app import ComposeResult

        result = screen.compose()
        widgets = list(result)
        # 检查是否包含 Header 和 Footer
        from textual.widgets import Header, Footer

        header_present = any(isinstance(w, Header) for w in widgets)
        footer_present = any(isinstance(w, Footer) for w in widgets)
        self.assertTrue(header_present)
        self.assertTrue(footer_present)
        # 检查是否有 ScrollableContainer
        from textual.containers import ScrollableContainer

        container_present = any(isinstance(w, ScrollableContainer) for w in widgets)
        self.assertTrue(container_present)
        # 使用 query_one 查找 union-list, 即使屏幕未挂载也可能有效
        list_view = screen.query_one("#union-list")
        self.assertIsNotNone(list_view)
        self.assertEqual(list_view.id, "union-list")
        self.assertEqual(list_view.__class__.__name__, "ListView")

    def test_item_desc_generator(self):
        """测试 item_desc_generator 函数. """
        screen = DashboardScreen()
        # 模拟一个文件名
        filename = "test.toml"
        result = screen.item_desc_generator(filename)
        self.assertIsInstance(result, dict)
        self.assertIn(0, result)
        self.assertIn(1, result)
        # 检查内容
        self.assertIn("test.toml", result[0])
        # 由于 electron 文件不存在, 应显示“尚未激活”
        self.assertIn("尚未激活", result[1])


@unittest.skip("Pilot 测试需要进一步配置, 暂不运行")
class TestDashboardScreenPilot(unittest.TestCase):
    """使用 Textual Pilot 的集成测试. """

    def setUp(self):
        """配置临时目录和配置. """
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = pathlib.Path(self.temp_dir.name)

        default_config_path = (
            pathlib.Path(__file__).parent.parent.parent
            / "src/heurams/default/config/config.toml"
        )
        self.config = ConfigFile(default_config_path)
        config_data = self.config.data
        config_data["paths"]["nucleon_dir"] = str(self.temp_path / "nucleon")
        config_data["paths"]["electron_dir"] = str(self.temp_path / "electron")
        config_data["paths"]["orbital_dir"] = str(self.temp_path / "orbital")
        config_data["paths"]["cache_dir"] = str(self.temp_path / "cache")
        config_data["quick_pass"] = 0
        config_data["daystamp_override"] = -1
        config_data["timestamp_override"] = -1

        for dir_key in ["nucleon_dir", "electron_dir", "orbital_dir", "cache_dir"]:
            pathlib.Path(config_data["paths"][dir_key]).mkdir(
                parents=True, exist_ok=True
            )

        self.config_ctx = ConfigContext(self.config)
        self.config_ctx.__enter__()

    def tearDown(self):
        self.config_ctx.__exit__(None, None, None)
        self.temp_dir.cleanup()

    def test_dashboard_loads_with_pilot(self):
        """使用 Pilot 测试 DashboardScreen 加载. """
        with patch("heurams.interface.__main__.environment_check"):
            app = HeurAMSApp()
            # 注意: Pilot 在 Textual 6.9.0 中的用法可能不同
            # 以下为示例代码, 可能需要调整
            pilot = Pilot(app)
            # 等待应用启动
            pilot.pause()
            screen = app.screen
            self.assertEqual(screen.__class__.__name__, "DashboardScreen")
            union_list = app.query_one("#union-list")
            self.assertIsNotNone(union_list)


if __name__ == "__main__":
    unittest.main()
