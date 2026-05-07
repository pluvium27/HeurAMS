from time import sleep, perf_counter

# import gc
# gc.set_threshold(100, 1, 1)
print("欢迎使用基本用户界面!")
print("加载配置与上下文... ", end="", flush=True)
_start_all = perf_counter()
_start = _start_all
from heurams.context import rootdir, workdir, config_var

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
from . import shim

_end = perf_counter()
print(f"已完成! (耗时: {round(1000 * (_end - _start))}ms)")

print(f"组件目录: {rootdir}")
print(f"工作目录: {workdir}")
_end_all = perf_counter()
print(f"前置工作共计耗时: {round(1000 * (_end_all - _start_all))}ms")


class HeurAMSApp(App):
    TITLE = "潜进"
    CSS_PATH = rootdir / "interface" / "css" / "main.tcss"
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def on_mount(self) -> None:
        self.push_screen("dashboard")

    def action_go_back(self) -> None:
        self.exit()  # go_back 在最顶层是退出, Screen 会再次定义为返回, 键位都是 q, 免得不一样

    def action_do_nothing(
        self,
    ) -> None:  # 用来给没使用/禁用的快捷键占位, 因为 Binding 删除不了
        pass

    # 移除烦人的 "rich traceback"
    # Textual 官方不会管这破事, 写 Rich 写入脑了导致的
    # 不知道哪来的自信改标准库的 traceback
    # https://github.com/Textualize/textual/discussions/6255
    # NOTE: 进行 textual 版本升级时, 确保查看过上游代码, 尤其是 App 的 _exception
    # 如果行为变了就把下面的删了 (虽然有 fallback)
    def _fatal_error(self):
        if hasattr(self, "_exception"):
            self._close_messages_no_wait()
            raise self._exception
        super()._fatal_error()  # fallback

    def panic(self, *args):
        if hasattr("_exception"):
            self._close_messages_no_wait()
            raise self._exception
        super().panic(*args)  # ditto
