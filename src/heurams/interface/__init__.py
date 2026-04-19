from time import sleep, perf_counter
print("欢迎使用基本用户界面!")
print("加载配置与上下文... ", end="", flush=True)
_start1 = perf_counter()
_start = perf_counter()
from heurams.context import *
_end = perf_counter()
print(f"已完成! (耗时: {round(1000 * (_end - _start))}ms)")

print("加载用户界面框架... ", end="", flush=True)
_start = perf_counter()
from textual.app import App
from textual.widgets import Button
_end = perf_counter()
print(f"已完成! (耗时: {round(1000 * (_end - _start))}ms)")

print("加载用户界面布局... ", end="", flush=True)
_start = perf_counter()
from .screens.about import AboutScreen
from .screens.dashboard import DashboardScreen
from .screens.navigator import NavigatorScreen
from .screens.precache import PrecachingScreen
from .screens.setting import SettingScreen
from .screens.synctool import SyncScreen
_end = perf_counter()
print(f"已完成! (耗时: {round(1000 * (_end - _start))}ms)")

print(f"组件目录: {rootdir}")
print(f"工作目录: {workdir}")
_end1 = perf_counter()
print(f"前置工作共计耗时: {round(1000 * (_end1 - _start1))}ms")
class HeurAMSApp(App):
    TITLE = "潜进"
    CSS_PATH = "css/main.tcss"
    SUB_TITLE = "启发式辅助记忆调度器"
    BINDINGS = [
        ("q", "go_back", "退出"),
        ("d", "toggle_dark", "主题"),
        ("n", "app.push_screen('navigator')", "导航"),
        ("s", "app.push_screen('setting')", "设置"),
        ("z", "app.push_screen('about')", "关于"),
    ]
    SCREENS = {
        "dashboard": DashboardScreen,
        "precache_all": PrecachingScreen,
        "synctool": SyncScreen,
        "about": AboutScreen,
        "navigator": NavigatorScreen,
        "setting": SettingScreen,
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

    # 移除烦人的 "rich traceback"
    # Textual 官方不会管这破事, 写 Rich 写入脑了导致的
    # 不知道哪来的自信改标准库的 traceback
    # https://github.com/Textualize/textual/discussions/6255
    def _fatal_error(self):
        self._close_messages_no_wait()
        raise self._exception

    def panic(self, *args):
        self._close_messages_no_wait()
        raise self._exception