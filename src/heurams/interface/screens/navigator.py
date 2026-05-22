from textual.app import ComposeResult
from textual.containers import Grid
from textual.screen import ModalScreen
from textual.widgets import Button, Label, ListItem, ListView, Static


from heurams.i18n import _
from heurams.services.logger import get_logger

from .favmgr import FavoriteManagerScreen

logger = get_logger(__name__)


class NavigatorScreen(ModalScreen):
    """Navigator modal screen"""

    BINDINGS = [
        ("q", "go_back", _("Back")),
        ("escape", "go_back", _("Back")),
        ("n", "go_back", _("Switch")),
    ]

    SCREENS = [
        (_("Dashboard"), "dashboard"),
        (_("Cache Manager"), "precache_all"),
        (_("Favorites"), FavoriteManagerScreen),
        (_("Settings Page"), "setting"),
        (_("Sync Tool"), "synctool"),
        (_("About"), "about"),
    ]

    OTHERS = [
        (_("Exit"), "self.app.exit()"),
        (_("Project Homepage"), "webbrowser.open('https://ams.pluv27.top')"),
    ]

    def compose(self) -> ComposeResult:
        """Compose UI components"""
        with Grid(id="dialog"):
            yield Label(
                _("[b]Select a function to navigate to\nor a memorization session instance[/b]\n\nTips will be displayed here"),
                classes="title-label",
            )
            yield ListView(
                *[ListItem(Label(title)) for title, _ in (self.SCREENS + self.OTHERS)],
                id="nav-list",
                classes="nav-list-view",
            )
            yield Static(_("Press Enter to switch\nAll sessions will be saved"))
            yield Button(
                _("Close (n)"),
                id="close_button",
                variant="primary",
                classes="close-button",
                flat=True,
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
