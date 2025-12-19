from textual.app import App
from textual.widgets import Button

from heurams.services.logger import get_logger

from .screens.about import AboutScreen
from .screens.dashboard import DashboardScreen
from .screens.nucreator import NucleonCreatorScreen
from .screens.precache import PrecachingScreen

logger = get_logger(__name__)


class HeurAMSApp(App):
    TITLE = "潜进"
    CSS_PATH = "css/main.tcss"
    SUB_TITLE = "启发式辅助记忆调度器"
    BINDINGS = [
        ("q", "quit", "退出"),
        ("d", "toggle_dark", "切换色调"),
        ("1", "app.push_screen('dashboard')", "仪表盘"),
        ("2", "app.push_screen('precache_all')", "缓存管理器"),
        ("3", "app.push_screen('nucleon_creator')", "创建新单元"),
        ("0", "app.push_screen('about')", "版本信息"),
    ]
    SCREENS = {
        "dashboard": DashboardScreen,
        "nucleon_creator": NucleonCreatorScreen,
        "precache_all": PrecachingScreen,
        "about": AboutScreen,
    }

    def on_mount(self) -> None:
        self.push_screen("dashboard")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.exit(event.button.id)

    def action_do_nothing(self):
        print("DO NOTHING")
        self.refresh()


def environment_check():
    from pathlib import Path

    logger.debug("检查环境路径")

    for i in config_var.get()["paths"].values():
        i = Path(i)
        if not i.exists():
            logger.info("创建目录: %s", i)
            print(f"创建 {i}")
            i.mkdir(exist_ok=True, parents=True)
        else:
            logger.debug("目录已存在: %s", i)
            print(f"找到 {i}")
    logger.debug("环境检查完成")


def is_subdir(parent, child):
    try:
        child.relative_to(parent)
        logger.debug("is_subdir: %s 是 %s 的子目录", child, parent)
        return 1
    except:
        logger.debug("is_subdir: %s 不是 %s 的子目录", child, parent)
        return 0


import os
from pathlib import Path

# 开发模式
from heurams.context import config_var, rootdir, workdir

if is_subdir(Path(rootdir), Path(os.getcwd())):
    os.chdir(Path(rootdir) / ".." / "..")
    print(f'转入开发数据目录: {Path(rootdir)/".."/".."}')

environment_check()

app = HeurAMSApp()
if __name__ == "__main__":
    app.run()


def main():
    app.run()
