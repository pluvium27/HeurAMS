"""LLM 聊天界面"""

import asyncio
from pathlib import Path
from typing import Optional

from textual.app import ComposeResult
from textual.containers import Container, Horizontal
from textual.screen import Screen
from textual.widgets import Button, Footer, Header, Input, Label, RichLog, Static

from heurams.context import *
from heurams.services.llm_service import ChatSession, get_chat_manager
from heurams.services.logger import get_logger

logger = get_logger(__name__)


class LLMChatScreen(Screen):
    """LLM 聊天屏幕"""

    SUB_TITLE = "AI 聊天"
    BINDINGS = [
        ("q", "go_back", "返回"),
        ("ctrl+s", "save_session", "保存会话"),
        ("ctrl+l", "load_session", "加载会话"),
        ("ctrl+n", "new_session", "新建会话"),
        ("ctrl+c", "clear_history", "清空历史"),
        ("escape", "focus_input", "聚焦输入"),
    ]

    def __init__(
        self,
        session_id: Optional[str] = None,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        super().__init__(name, id, classes)
        self.session_id = session_id
        self.chat_manager = get_chat_manager()
        self.current_session: Optional[ChatSession] = None
        self.is_streaming = False

    def compose(self) -> ComposeResult:
        """组合界面组件"""
        yield Header(show_clock=True)

        with Container(id="chat-container"):
            # 顶部工具栏
            with Horizontal(id="toolbar"):
                yield Button("新建会话", id="new-session", variant="primary")
                yield Button("保存会话", id="save-session", variant="default")
                yield Button("加载会话", id="load-session", variant="default")
                yield Button("清空历史", id="clear-history", variant="default")
                yield Button("设置系统提示", id="set-system-prompt", variant="default")
                yield Static(" | ", classes="separator")
                yield Label("当前会话:", classes="label")
                yield Static(id="current-session-label", classes="session-label")

            # 聊天记录显示区域
            yield RichLog(
                id="chat-log",
                wrap=True,
                highlight=True,
                markup=True,
                classes="chat-log",
            )

            # 输入区域
            with Horizontal(id="input-container"):
                yield Input(
                    id="message-input",
                    placeholder="输入消息... (按 Ctrl+Enter 发送, Esc 聚焦)",
                    classes="message-input",
                )
                yield Button(
                    "发送", id="send-button", variant="primary", classes="send-button"
                )

            # 状态栏
            yield Static(id="status-bar", classes="status-bar")

        yield Footer()

    def on_mount(self) -> None:
        """挂载组件时初始化"""
        # 获取或创建会话
        self.current_session = self.chat_manager.get_session(self.session_id)
        if self.current_session is None:
            self.notify("无法创建 LLM 会话，请检查配置", severity="error")
            return

        # 更新会话标签
        self.query_one("#current-session-label", Static).update(
            f"{self.current_session.session_id}"
        )

        # 加载历史消息到聊天记录
        self._display_history()

        # 聚焦输入框
        self.query_one("#message-input", Input).focus()

        # 检查配置
        self._check_config()

    def _check_config(self):
        """检查 LLM 配置"""
        config = config_var.get()
        provider_name = config["services"]["llm"]
        provider_config = config["providers"]["llm"][provider_name]

        if provider_name == "openai":
            if not provider_config.get("key") and not provider_config.get("url"):
                self.notify(
                    "未配置 OpenAI API key 或 URL，请在 config.toml 中配置 [providers.llm.openai]",
                    severity="warning",
                )

    def _display_history(self):
        """显示当前会话的历史消息"""
        if not self.current_session:
            return

        chat_log = self.query_one("#chat-log", RichLog)
        chat_log.clear()

        for msg in self.current_session.get_history():
            role = msg["role"]
            content = msg["content"]

            if role == "user":
                chat_log.write(f"[bold cyan]你:[/bold cyan] {content}")
            elif role == "assistant":
                chat_log.write(f"[bold green]AI:[/bold green] {content}")
            elif role == "system":
                # 系统消息不显示在聊天记录中
                pass

    def _add_message_to_log(self, role: str, content: str):
        """添加消息到聊天记录显示"""
        chat_log = self.query_one("#chat-log", RichLog)
        if role == "user":
            chat_log.write(f"[bold cyan]你:[/bold cyan] {content}")
        elif role == "assistant":
            chat_log.write(f"[bold green]AI:[/bold green] {content}")
        chat_log.scroll_end()

    async def on_input_submitted(self, event: Input.Submitted):
        """处理输入提交"""
        if event.input.id == "message-input":
            await self._send_message()

    async def on_button_pressed(self, event: Button.Pressed):
        """处理按钮点击"""
        button_id = event.button.id

        if button_id == "send-button":
            await self._send_message()
        elif button_id == "new-session":
            self.action_new_session()
        elif button_id == "save-session":
            self.action_save_session()
        elif button_id == "load-session":
            self.action_load_session()
        elif button_id == "clear-history":
            self.action_clear_history()
        elif button_id == "set-system-prompt":
            self.action_set_system_prompt()

    async def _send_message(self):
        """发送当前输入的消息"""
        if not self.current_session or self.is_streaming:
            return

        input_widget = self.query_one("#message-input", Input)
        message = input_widget.value.strip()

        if not message:
            return

        # 清空输入框
        input_widget.value = ""

        # 显示用户消息
        self._add_message_to_log("user", message)

        # 禁用输入和按钮
        self._set_input_state(disabled=True)
        self.is_streaming = True

        # 更新状态
        self.query_one("#status-bar", Static).update("AI 正在思考...")

        try:
            # 发送消息并获取响应
            response = await self.current_session.send_message(message)

            # 显示AI响应
            self._add_message_to_log("assistant", response)

        except Exception as e:
            error_msg = f"请求失败: {str(e)}"
            logger.error(error_msg)
            self._add_message_to_log("assistant", f"[red]{error_msg}[/red]")
            self.notify(error_msg, severity="error")

        finally:
            # 恢复输入和按钮
            self._set_input_state(disabled=False)
            self.is_streaming = False
            self.query_one("#status-bar", Static).update("就绪")
            input_widget.focus()

    def _set_input_state(self, disabled: bool):
        """设置输入控件状态"""
        self.query_one("#message-input", Input).disabled = disabled
        self.query_one("#send-button", Button).disabled = disabled

    async def action_save_session(self):
        """保存当前会话到文件"""
        if not self.current_session:
            self.notify("无当前会话", severity="error")
            return

        # 默认保存到 data/chat_sessions/ 目录
        save_dir = Path(config_var.get()["paths"]["data"]) / "chat_sessions"
        save_dir.mkdir(exist_ok=True, parents=True)

        file_path = save_dir / f"{self.current_session.session_id}.json"
        self.current_session.save_to_file(file_path)

        self.notify(f"会话已保存到 {file_path}", severity="information")

    async def action_load_session(self):
        """从文件加载会话"""
        # 简化实现：加载默认目录下的第一个会话文件
        save_dir = Path(config_var.get()["paths"]["data"]) / "chat_sessions"
        if not save_dir.exists():
            self.notify(f"目录不存在: {save_dir}", severity="error")
            return

        session_files = list(save_dir.glob("*.json"))
        if not session_files:
            self.notify("未找到会话文件", severity="error")
            return

        # 使用第一个文件（在实际应用中可以让用户选择）
        file_path = session_files[0]

        try:
            # 获取 LLM 提供者
            provider_name = config_var.get()["services"]["llm"]
            provider_config = config_var.get()["providers"]["llm"][provider_name]
            from heurams.providers.llm import providers as prov

            llm_provider = prov[provider_name](provider_config)

            # 加载会话
            self.current_session = ChatSession.load_from_file(file_path, llm_provider)

            # 更新聊天管理器
            self.chat_manager.sessions[self.current_session.session_id] = (
                self.current_session
            )

            # 更新UI
            self.query_one("#current-session-label", Static).update(
                f"{self.current_session.session_id}"
            )
            self._display_history()

            self.notify(f"已加载会话: {file_path.name}", severity="information")

        except Exception as e:
            logger.error("加载会话失败: %s", e)
            self.notify(f"加载失败: {str(e)}", severity="error")

    async def action_new_session(self):
        """创建新会话"""
        # 简单实现：使用时间戳作为会话ID
        import time

        new_session_id = f"session_{int(time.time())}"

        self.current_session = self.chat_manager.get_session(new_session_id)

        # 更新UI
        self.query_one("#current-session-label", Static).update(
            f"{self.current_session.session_id}"
        )
        self._display_history()

        self.notify(f"已创建新会话: {new_session_id}", severity="information")
        self.query_one("#message-input", Input).focus()

    async def action_clear_history(self):
        """清空当前会话历史"""
        if not self.current_session:
            return

        self.current_session.clear_history()
        self._display_history()
        self.notify("历史已清空", severity="information")

    async def action_set_system_prompt(self):
        """设置系统提示词"""
        if not self.current_session:
            return

        # 使用输入框获取新提示词
        input_widget = self.query_one("#message-input", Input)
        current_value = input_widget.value

        # 临时修改输入框提示
        input_widget.placeholder = "输入系统提示词... (按 Enter 确认, Esc 取消)"
        input_widget.value = self.current_session.system_prompt

        # 等待用户输入
        self.notify("请输入系统提示词，按 Enter 确认", severity="information")

        # 实际应用中需要更复杂的交互，这里简化处理
        # 用户手动输入后按 Enter 会触发 on_input_submitted
        # 这里我们只修改占位符，实际系统提示词设置需要额外界面

    def action_focus_input(self):
        """聚焦到输入框"""
        self.query_one("#message-input", Input).focus()

    def action_go_back(self):
        """返回上级屏幕"""
        self.app.pop_screen()
