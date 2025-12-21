#!/usr/bin/env python3
import pathlib
import time

from textual.app import ComposeResult
from textual.containers import Horizontal, ScrollableContainer
from textual.screen import Screen
from textual.widgets import Button, Footer, Header, Label, ProgressBar, Static
from textual.worker import get_current_worker

import heurams.kernel.particles as pt
import heurams.services.hasher as hasher
from heurams.context import *


class SyncScreen(Screen):

    BINDINGS = [("q", "go_back", "返回")]

    def __init__(self, nucleons: list = [], desc: str = ""):
        super().__init__(name=None, id=None, classes=None)
        self.sync_service = None
        self.is_syncing = False
        self.is_paused = False
        self.log_messages = []
        self.max_log_lines = 50

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with ScrollableContainer(id="sync_container"):
            # 标题和连接状态
            yield Static("同步工具", classes="title")
            yield Static("", id="status_label", classes="status")

            # 配置信息
            yield Static(f"同步协议: {config_var.get()['services']['sync']}")
            yield Static("服务器配置:", classes="section_title")
            with Horizontal(classes="config_info"):
                yield Static("远程服务器:", classes="config_label")
                yield Static("", id="server_url", classes="config_value")
            with Horizontal(classes="config_info"):
                yield Static("远程路径:", classes="config_label")
                yield Static("", id="remote_path", classes="config_value")

            with Horizontal(classes="control_buttons"):
                yield Button("测试连接", id="test_connection", variant="primary")
                yield Button("开始同步", id="start_sync", variant="success")
                yield Button("暂停", id="pause_sync", variant="warning", disabled=True)
                yield Button("取消", id="cancel_sync", variant="error", disabled=True)

            yield Static("同步进度", classes="section_title")
            yield ProgressBar(id="progress_bar", show_percentage=True, total=100)
            yield Static("", id="progress_label", classes="progress_text")

            yield Static("同步日志", classes="section_title")
            yield Static("", id="log_output", classes="log_output")

        yield Footer()

    def on_mount(self):
        """挂载时初始化状态"""
        self.update_ui_from_config()
        self.log_message("同步工具已启动")

    def update_ui_from_config(self):
        """更新 UI 显示配置信息"""
        try:
            sync_cfg: dict = config_var.get()['providers']['sync']['webdav']
            # 更新服务器 URL
            url = sync_cfg.get("url", "未配置")
            url_widget = self.query_one("#server_url")
            url_widget.update(url)  # type: ignore
            # 更新远程路径
            remote_path = sync_cfg.get("remote_path", "/")
            path_widget = self.query_one("#remote_path")
            path_widget.update(remote_path)  # type: ignore

            # 更新状态标签
            status_widget = self.query_one("#status_label")
            if self.sync_service and self.sync_service.client:
                status_widget.update("✅ 同步服务已就绪")  # type: ignore
                status_widget.add_class("ready")
            else:
                status_widget.update("❌ 同步服务未配置或未启用")  # type: ignore
                status_widget.add_class("error")

        except Exception as e:
            self.log_message(f"更新 UI 失败: {e}", is_error=True)

    def update_status(self, status, current_item="", progress=None):
        """更新状态显示"""
        try:
            status_widget = self.query_one("#status_label")
            status_widget.update(status)  # type: ignore

            if progress is not None:
                progress_bar = self.query_one("#progress_bar")
                progress_bar.progress = progress  # type: ignore

                progress_label = self.query_one("#progress_label")
                progress_label.update(f"{progress}% - {current_item}" if current_item else f"{progress}%")  # type: ignore

        except Exception as e:
            self.log_message(f"更新状态失败: {e}", is_error=True)

    def log_message(self, message: str, is_error: bool = False):
        """添加日志消息并更新显示"""
        timestamp = time.strftime("%H:%M:%S")
        prefix = "[ERROR]" if is_error else "[INFO]"
        log_line = f"{timestamp} {prefix} {message}"

        self.log_messages.append(log_line)
        # 保持日志行数不超过最大值
        if len(self.log_messages) > self.max_log_lines:
            self.log_messages = self.log_messages[-self.max_log_lines :]

        # 更新日志显示
        try:
            log_widget = self.query_one("#log_output")
            log_widget.update("\n".join(self.log_messages))  # type: ignore
        except Exception:
            pass  # 如果组件未就绪，忽略错误

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """处理按钮点击事件"""
        button_id = event.button.id

        if button_id == "test_connection":
            self.test_connection()
        elif button_id == "start_sync":
            self.start_sync()
        elif button_id == "pause_sync":
            self.pause_sync()
        elif button_id == "cancel_sync":
            self.cancel_sync()

        event.stop()

    def test_connection(self):
        """测试 WebDAV 服务器连接"""
        if not self.sync_service:
            self.log_message("同步服务未初始化，请检查配置", is_error=True)
            self.update_status("❌ 同步服务未初始化")
            return

        self.log_message("正在测试 WebDAV 连接...")
        self.update_status("正在测试连接...")

        try:
            success = self.sync_service.test_connection()
            if success:
                self.log_message("连接测试成功")
                self.update_status("✅ 连接正常")
            else:
                self.log_message("连接测试失败", is_error=True)
                self.update_status("❌ 连接失败")
        except Exception as e:
            self.log_message(f"连接测试异常: {e}", is_error=True)
            self.update_status("❌ 连接异常")

    def start_sync(self):
        """开始同步"""
        if not self.sync_service:
            self.log_message("同步服务未初始化，无法开始同步", is_error=True)
            return

        if self.is_syncing:
            self.log_message("同步已在进行中", is_error=True)
            return

        self.is_syncing = True
        self.is_paused = False
        self.update_button_states()

        self.log_message("开始同步数据...")
        self.update_status("正在同步...", progress=0)

        # 启动后台同步任务
        self.run_worker(self.perform_sync, thread=True)

    def perform_sync(self):
        """执行同步任务（在后台线程中运行）"""
        worker = get_current_worker()

        try:
            # 获取需要同步的本地目录
            from heurams.context import config_var

            config = config_var.get()
            paths = config.get("paths", {})

            # 同步 nucleon 目录
            nucleon_dir = pathlib.Path(paths.get("nucleon_dir", "./data/nucleon"))
            if nucleon_dir.exists():
                self.log_message(f"同步 nucleon 目录: {nucleon_dir}")
                self.update_status(f"同步 nucleon 目录...", progress=10)

                result = self.sync_service.sync_directory(nucleon_dir)  # type: ignore
                if result.get("success"):
                    self.log_message(
                        f"nucleon 同步完成: 上传 {result.get('uploaded', 0)} 个, 下载 {result.get('downloaded', 0)} 个"
                    )
                else:
                    self.log_message(
                        f"nucleon 同步失败: {result.get('error', '未知错误')}",
                        is_error=True,
                    )

            # 同步 electron 目录
            electron_dir = pathlib.Path(paths.get("electron_dir", "./data/electron"))
            if electron_dir.exists():
                self.log_message(f"同步 electron 目录: {electron_dir}")
                self.update_status(f"同步 electron 目录...", progress=60)

                result = self.sync_service.sync_directory(electron_dir)  # type: ignore
                if result.get("success"):
                    self.log_message(
                        f"electron 同步完成: 上传 {result.get('uploaded', 0)} 个, 下载 {result.get('downloaded', 0)} 个"
                    )
                else:
                    self.log_message(
                        f"electron 同步失败: {result.get('error', '未知错误')}",
                        is_error=True,
                    )

            # 同步 orbital 目录（如果存在）
            orbital_dir = pathlib.Path(paths.get("orbital_dir", "./data/orbital"))
            if orbital_dir.exists():
                self.log_message(f"同步 orbital 目录: {orbital_dir}")
                self.update_status(f"同步 orbital 目录...", progress=80)

                result = self.sync_service.sync_directory(orbital_dir)  # type: ignore
                if result.get("success"):
                    self.log_message(
                        f"orbital 同步完成: 上传 {result.get('uploaded', 0)} 个, 下载 {result.get('downloaded', 0)} 个"
                    )
                else:
                    self.log_message(
                        f"orbital 同步失败: {result.get('error', '未知错误')}",
                        is_error=True,
                    )

            # 同步完成
            self.update_status("同步完成", progress=100)
            self.log_message("所有目录同步完成")

        except Exception as e:
            self.log_message(f"同步过程中发生错误: {e}", is_error=True)
            self.update_status("同步失败")
        finally:
            # 重置同步状态
            self.is_syncing = False
            self.is_paused = False
            self.update_button_states()  # type: ignore

    def pause_sync(self):
        """暂停同步"""
        if not self.is_syncing:
            return

        self.is_paused = not self.is_paused
        self.update_button_states()

        if self.is_paused:
            self.log_message("同步已暂停")
            self.update_status("同步已暂停")
        else:
            self.log_message("同步已恢复")
            self.update_status("正在同步...")

    def cancel_sync(self):
        """取消同步"""
        if not self.is_syncing:
            return

        self.is_syncing = False
        self.is_paused = False
        self.update_button_states()

        self.log_message("同步已取消")
        self.update_status("同步已取消")

    def update_button_states(self):
        """更新按钮状态"""
        try:
            start_button = self.query_one("#start_sync")
            pause_button = self.query_one("#pause_sync")
            cancel_button = self.query_one("#cancel_sync")

            if self.is_syncing:
                start_button.disabled = True
                pause_button.disabled = False
                cancel_button.disabled = False
                pause_button.label = "继续" if self.is_paused else "暂停"  # type: ignore
            else:
                start_button.disabled = False
                pause_button.disabled = True
                cancel_button.disabled = True

        except Exception as e:
            self.log_message(f"更新按钮状态失败: {e}", is_error=True)

    def action_go_back(self):
        self.app.pop_screen()

    def action_quit_app(self):
        self.app.exit()
