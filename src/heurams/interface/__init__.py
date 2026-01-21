from time import sleep
print("欢迎使用基本用户界面!")
print("加载配置... ", end="", flush=True)
from heurams.context import *
print("已完成!")

print("加载用户界面框架... ", end="", flush=True)
from textual.app import App
from textual.widgets import Button
print("已完成!")

print("加载用户界面布局... ", end="", flush=True)
from .screens.about import AboutScreen
from .screens.dashboard import DashboardScreen
from .screens.llmchat import LLMChatScreen
from .screens.navigator import NavigatorScreen
from .screens.precache import PrecachingScreen
from .screens.radio import RadioScreen
from .screens.repocreator import RepoCreatorScreen
from .screens.repoeditor import RepoEditorScreen
from .screens.synctool import SyncScreen
print("已完成!")
print(f"组件目录: {rootdir}")
print(f"工作目录: {workdir}")
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
        self.push_screen("dashboard")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        pass
        # self.exit(event.button.id)

    def action_go_back(self) -> None:
        quit()

    def action_do_nothing(self):
        self.refresh()
