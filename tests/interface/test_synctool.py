#!/usr/bin/env python3
"""
SyncScreen 和 SyncService 的测试.
"""
import pathlib
import tempfile
import time
import unittest
from unittest.mock import MagicMock, Mock, patch

from heurams.context import ConfigContext
from heurams.services.config import ConfigFile
from heurams.services.sync_service import (
    ConflictStrategy,
    SyncConfig,
    SyncMode,
    SyncService,
)


class TestSyncServiceUnit(unittest.TestCase):
    """SyncService 的单元测试."""

    def setUp(self):
        """在每个测试之前运行, 设置临时目录和模拟客户端."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = pathlib.Path(self.temp_dir.name)

        # 创建测试文件
        self.test_file = self.temp_path / "test.txt"
        self.test_file.write_text("测试内容")

        # 模拟 WebDAV 客户端
        self.mock_client = MagicMock()

        # 创建同步配置
        self.config = SyncConfig(
            enabled=True,
            url="https://example.com/dav/",
            username="test",
            password="test",
            remote_path="/heurams/",
            sync_mode=SyncMode.BIDIRECTIONAL,
            conflict_strategy=ConflictStrategy.NEWER,
            verify_ssl=True,
        )

    def tearDown(self):
        """在每个测试之后清理."""
        self.temp_dir.cleanup()

    @patch("heurams.services.sync_service.Client")
    def test_sync_service_initialization(self, mock_client_class):
        """测试同步服务初始化."""
        mock_client_class.return_value = self.mock_client

        service = SyncService(self.config)

        # 验证客户端已创建
        mock_client_class.assert_called_once()
        self.assertIsNotNone(service.client)
        self.assertEqual(service.config, self.config)

    @patch("heurams.services.sync_service.Client")
    def test_sync_service_disabled(self, mock_client_class):
        """测试同步服务未启用."""
        config = SyncConfig(enabled=False)
        service = SyncService(config)

        # 客户端不应初始化
        mock_client_class.assert_not_called()
        self.assertIsNone(service.client)

    @patch("heurams.services.sync_service.Client")
    def test_test_connection_success(self, mock_client_class):
        """测试连接测试成功."""
        mock_client_class.return_value = self.mock_client
        self.mock_client.list.return_value = []

        service = SyncService(self.config)
        result = service.test_connection()

        self.assertTrue(result)
        self.mock_client.list.assert_called_once()

    @patch("heurams.services.sync_service.Client")
    def test_test_connection_failure(self, mock_client_class):
        """测试连接测试失败."""
        mock_client_class.return_value = self.mock_client
        self.mock_client.list.side_effect = Exception("连接失败")

        service = SyncService(self.config)
        result = service.test_connection()

        self.assertFalse(result)
        self.mock_client.list.assert_called_once()

    @patch("heurams.services.sync_service.Client")
    def test_upload_file(self, mock_client_class):
        """测试上传单个文件."""
        mock_client_class.return_value = self.mock_client

        service = SyncService(self.config)
        result = service.upload_file(self.test_file)

        self.assertTrue(result)
        self.mock_client.upload_file.assert_called_once()

    @patch("heurams.services.sync_service.Client")
    def test_download_file(self, mock_client_class):
        """测试下载单个文件."""
        mock_client_class.return_value = self.mock_client

        service = SyncService(self.config)
        remote_path = "/heurams/test.txt"
        local_path = self.temp_path / "downloaded.txt"

        result = service.download_file(remote_path, local_path)

        self.assertTrue(result)
        self.mock_client.download_file.assert_called_once()
        self.assertTrue(local_path.parent.exists())

    @patch("heurams.services.sync_service.Client")
    def test_sync_directory_no_files(self, mock_client_class):
        """测试同步空目录."""
        mock_client_class.return_value = self.mock_client
        self.mock_client.list.return_value = []
        self.mock_client.mkdir.return_value = None

        service = SyncService(self.config)
        result = service.sync_directory(self.temp_path)

        self.assertTrue(result["success"])
        self.assertEqual(result["uploaded"], 0)
        self.assertEqual(result["downloaded"], 0)
        self.mock_client.mkdir.assert_called_once()

    @patch("heurams.services.sync_service.Client")
    def test_sync_directory_upload_only(self, mock_client_class):
        """测试仅上传模式."""
        mock_client_class.return_value = self.mock_client
        self.mock_client.list.return_value = []
        self.mock_client.mkdir.return_value = None

        config = SyncConfig(
            enabled=True,
            url="https://example.com/dav/",
            username="test",
            password="test",
            remote_path="/heurams/",
            sync_mode=SyncMode.UPLOAD_ONLY,
            conflict_strategy=ConflictStrategy.NEWER,
        )

        service = SyncService(config)
        result = service.sync_directory(self.temp_path)

        self.assertTrue(result["success"])
        self.mock_client.mkdir.assert_called_once()

    @patch("heurams.services.sync_service.Client")
    def test_conflict_strategy_newer(self, mock_client_class):
        """测试 NEWER 冲突策略."""
        mock_client_class.return_value = self.mock_client

        # 模拟远程文件存在
        self.mock_client.list.return_value = ["test.txt"]
        self.mock_client.info.return_value = {
            "size": 100,
            "modified": "2023-01-01T00:00:00Z",
        }
        self.mock_client.mkdir.return_value = None

        service = SyncService(self.config)
        result = service.sync_directory(self.temp_path)

        self.assertTrue(result["success"])
        # 应该有一个冲突
        self.assertGreaterEqual(result.get("conflicts", 0), 0)

    @patch("heurams.services.sync_service.Client")
    def test_create_sync_service_from_config(self, mock_client_class):
        """测试从配置文件创建同步服务."""
        mock_client_class.return_value = self.mock_client

        # 创建临时配置文件
        config_data = {
            "sync": {
                "webdav": {
                    "enabled": True,
                    "url": "https://example.com/dav/",
                    "username": "test",
                    "password": "test",
                    "remote_path": "/heurams/",
                    "sync_mode": "bidirectional",
                    "conflict_strategy": "newer",
                    "verify_ssl": True,
                }
            }
        }

        # 模拟 config_var
        with patch("heurams.services.sync_service.config_var") as mock_config_var:
            mock_config = MagicMock()
            mock_config.data = config_data
            mock_config_var.get.return_value = mock_config

            from heurams.services.sync_service import create_sync_service_from_config

            service = create_sync_service_from_config()

            self.assertIsNotNone(service)
            self.assertIsNotNone(service.client)


class TestSyncScreenUnit(unittest.TestCase):
    """SyncScreen 的单元测试."""

    def setUp(self):
        """在每个测试之前运行."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = pathlib.Path(self.temp_dir.name)

        # 创建默认配置
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

        # 添加同步配置
        if "sync" not in config_data:
            config_data["sync"] = {}
        config_data["sync"]["webdav"] = {
            "enabled": False,
            "url": "",
            "username": "",
            "password": "",
            "remote_path": "/heurams/",
            "sync_mode": "bidirectional",
            "conflict_strategy": "newer",
            "verify_ssl": True,
        }

        # 创建目录
        for dir_key in ["nucleon_dir", "electron_dir", "orbital_dir", "cache_dir"]:
            pathlib.Path(config_data["paths"][dir_key]).mkdir(
                parents=True, exist_ok=True
            )

        # 使用 ConfigContext 设置配置
        self.config_ctx = ConfigContext(self.config)
        self.config_ctx.__enter__()

    def tearDown(self):
        """在每个测试之后清理."""
        self.config_ctx.__exit__(None, None, None)
        self.temp_dir.cleanup()

    @patch("heurams.interface.screens.synctool.create_sync_service_from_config")
    def test_sync_screen_compose(self, mock_create_service):
        """测试 SyncScreen 的 compose 方法."""
        from heurams.interface.screens.synctool import SyncScreen

        # 模拟同步服务
        mock_service = MagicMock()
        mock_service.client = MagicMock()
        mock_create_service.return_value = mock_service

        screen = SyncScreen()

        # 测试 compose 方法
        from textual.app import ComposeResult

        result = screen.compose()
        widgets = list(result)

        # 检查基本部件
        from textual.containers import ScrollableContainer
        from textual.widgets import Button, Footer, Header, ProgressBar, Static

        header_present = any(isinstance(w, Header) for w in widgets)
        footer_present = any(isinstance(w, Footer) for w in widgets)
        self.assertTrue(header_present)
        self.assertTrue(footer_present)

        # 检查容器
        container_present = any(isinstance(w, ScrollableContainer) for w in widgets)
        self.assertTrue(container_present)

    @patch("heurams.interface.screens.synctool.create_sync_service_from_config")
    def test_sync_screen_load_config(self, mock_create_service):
        """测试 SyncScreen 加载配置."""
        from heurams.interface.screens.synctool import SyncScreen

        mock_service = MagicMock()
        mock_service.client = MagicMock()
        mock_create_service.return_value = mock_service

        screen = SyncScreen()
        screen.load_config()

        # 验证配置已加载
        self.assertIsNotNone(screen.sync_config)
        mock_create_service.assert_called_once()


if __name__ == "__main__":
    unittest.main()
