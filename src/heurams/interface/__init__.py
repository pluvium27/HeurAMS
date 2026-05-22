from time import sleep, perf_counter

# import gc
# gc.set_threshold(100, 1, 1)
from heurams.i18n import _

print(_("Welcome to the basic user interface!"))
print(_("Loading config and context... "), end="", flush=True)
_start_all = perf_counter()
_start = _start_all
from heurams.context import rootdir, workdir, config_var

_end = perf_counter()
print(_("Done! ({time}ms)").format(time=round(1000 * (_end - _start))))

print(_("Loading UI framework... "), end="", flush=True)
_start = perf_counter()
from textual.app import App

_end = perf_counter()
print(_("Done! ({time}ms)").format(time=round(1000 * (_end - _start))))

print(_("Loading UI layout... "), end="", flush=True)
_start = perf_counter()
from .screens.dashboard import DashboardScreen
from .screens.navigator import NavigatorScreen
from .screens.precache import PrecachingScreen
from .screens.setting import SettingScreen
from .screens.synctool import SyncScreen
from .screens.about import AboutScreen
from . import shim

_end = perf_counter()
print(_("Done! ({time}ms)").format(time=round(1000 * (_end - _start))))

print(_("Component directory: {path}").format(path=rootdir))
print(_("Working directory: {path}").format(path=workdir))
_end_all = perf_counter()
print(_("Pre-work total: {time}ms").format(time=round(1000 * (_end_all - _start_all))))


class HeurAMSApp(App):
    TITLE = "HeurAMS"
    CSS_PATH = rootdir / "interface" / "css" / "main.tcss"
    SUB_TITLE = _("Heuristic Auxiliary Memorizing Scheduler")
    BINDINGS = [
        ("q", "go_back", _("Quit")),
        ("d", "toggle_dark", _("Theme")),
        ("n", "app.push_screen('navigator')", _("Navigate")),
        ("s", "app.push_screen('setting')", _("Settings")),
        ("z", "app.push_screen('about')", _("About")),
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

'''
    # 移除烦人的 "rich traceback", 但可能导致未定义行为出现, 所以注释掉
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
'''