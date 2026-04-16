import webbrowser

from textual.app import ComposeResult
from textual.containers import Grid, ScrollableContainer
from textual.screen import ModalScreen
from textual.widgets import Button, Footer, Header, Label, ListItem, ListView, Static

from heurams.context import *
from heurams.services.logger import get_logger

from .favmgr import FavoriteManagerScreen

logger = get_logger(__name__)


class NavigatorScreen(ModalScreen):
    """导航器模态窗口"""

    BINDINGS = [
        ("q", "go_back", "返回"),
        ("escape", "go_back", "返回"),
        ("n", "go_back", "切换"),
    ]

    SCREENS = [
        ("仪表盘", "dashboard"),
        #        ("创建仓库", "repo_creator"),
        ("缓存管理器", "precache_all"),
        ("收藏夹", FavoriteManagerScreen),
        # ("配置设置", "config"),
        # ("调试日志", "logviewer"),
        ("同步工具", "synctool"),
        ("关于此软件", "about"),
        #        ("仓库编辑器", "repo_editor"),
    ]

    OTHERS = [
        ("退出程序", "self.app.exit()"),
        ("项目主页", "webbrowser.open('https://ams.imwangzhiyu.xyz')"),
    ]

    def compose(self) -> ComposeResult:
        """组合界面组件"""
        with Grid(id="dialog"):
            yield Label(
                "[b]请选择要跳转的功能\n或记忆会话实例[/b]\n\n将在此处显示提示",
                classes="title-label",
            )
            yield ListView(
                *[ListItem(Label(title)) for title, _ in (self.SCREENS + self.OTHERS)],
                id="nav-list",
                classes="nav-list-view",
            )
            yield Static("按下回车以完成切换\n所有会话将被保存")
            yield Button(
                "关闭 (n)", id="close_button", variant="primary", classes="close-button", flat=True
            )

    def on_mount(self) -> None:
        # 设置焦点到列表
        nav_list = self.query_one("#nav-list", ListView)
        nav_list.focus()

    def on_list_view_selected(self, event) -> None:
        if not isinstance(event.item, ListItem):
            return
        selected_label = event.item.query_one(Label)
        label_text = str(selected_label.render())
        # 查找对应的屏幕标识
        for title, screen_id in self.SCREENS:
            if title == label_text:
                self.app.pop_screen()
                # 跳转到目标屏幕
                if isinstance(screen_id, str):
                    # 已注册的字符串标识符
                    self.app.push_screen(screen_id)
                else:
                    self.app.push_screen(screen_id())
                return
        for title, cmd in self.OTHERS:
            if title == label_text:
                exec(cmd)
                return
        return

    def on_button_pressed(self, event) -> None:
        event.stop()
        if event.button.id == "close_button":
            self.action_go_back()

    def action_go_back(self) -> None:
        self.app.pop_screen()
