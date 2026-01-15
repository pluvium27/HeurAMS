from typing import Type

from textual.app import App
from textual.driver import Driver
from textual.widgets import Button

from heurams.context import config_var
from heurams.services.logger import get_logger

from .screens.about import AboutScreen
from .screens.dashboard import DashboardScreen
from .screens.llmchat import LLMChatScreen
from .screens.navigator import NavigatorScreen
from .screens.precache import PrecachingScreen
from .screens.radio import RadioScreen
from .screens.repocreator import RepoCreatorScreen
from .screens.repoeditor import RepoEditorScreen
from .screens.synctool import SyncScreen

logger = get_logger(__name__)


def environment_check():
    from pathlib import Path

    logger.debug("检查环境路径")
    subdir = ["cache/voice", "repo", "global", "config"]
    for i in subdir:
        i = Path(config_var.get()["paths"]["data"]) / i
        if not i.exists():
            logger.info("创建目录: %s", i)
            print(f"创建 {i}")
            i.mkdir(exist_ok=True, parents=True)
        else:
            logger.debug("目录已存在: %s", i)
            print(f"找到 {i}")
    logger.debug("环境检查完成")


class HeurAMSApp(App):
    TITLE = "潜进"
    CSS_PATH = "css/main.tcss"
    SUB_TITLE = "启发式辅助记忆调度器"
    BINDINGS = [
        ("q", "go_back", "退出"),
        ("d", "toggle_dark", "主题"),
        ("n", "app.push_screen('navigator')", "导航"),
        ("z", "app.push_screen('about')", "关于"),
    ]
    SCREENS = {
        "dashboard": DashboardScreen,
        "repo_creator": RepoCreatorScreen,
        "precache_all": PrecachingScreen,
        "synctool": SyncScreen,
        "about": AboutScreen,
        "navigator": NavigatorScreen,
        "radio": RadioScreen,
        "repo_editor": RepoEditorScreen,
        "llmchat": LLMChatScreen,
#        "config": ConfigScreen,
    }

    def on_mount(self) -> None:
        environment_check()
        self.push_screen("dashboard")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        pass
        # self.exit(event.button.id)

    def action_go_back(self) -> None:
        quit()

    def action_do_nothing(self):
        self.refresh()
