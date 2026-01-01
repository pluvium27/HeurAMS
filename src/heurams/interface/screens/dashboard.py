"""仪表盘界面"""

import pathlib

from textual.app import ComposeResult
from textual.containers import ScrollableContainer
from textual.screen import Screen
from textual.widgets import (Button, Footer, Header, Label, ListItem, ListView,
                             Static)

import heurams.services.timer as timer
import heurams.services.version as version
from heurams.context import *
from heurams.kernel.particles import *
from heurams.services.logger import get_logger

from .about import AboutScreen
from .preparation import PreparationScreen

logger = get_logger(__name__)


class DashboardScreen(Screen):
    """主仪表盘屏幕"""

    SUB_TITLE = "仪表盘"

    def __init__(
        self,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        super().__init__(name, id, classes)
        self.nextdates = {}
        self.texts = {}
        self.stay_enabled = {}

    def compose(self) -> ComposeResult:
        """组合界面组件"""
        yield Header(show_clock=True)
        yield ScrollableContainer(
            Label('欢迎使用 "潜进" 启发式辅助记忆调度器', classes="title-label"),
            Label(f"当前 UNIX 日时间戳: {timer.get_daystamp()}"),
            Label(f'时区修正: UTC+{config_var.get()["timezone_offset"] / 3600}'),
            Label(f"使用算法: {config_var.get()['algorithm']['default']}"),
            Label("选择待学习或待修改的记忆单元集:", classes="title-label"),
            ListView(id="union-list", classes="union-list-view"),
            Label(
                f'"潜进" 启发式辅助记忆调度器 | 版本 {version.ver} '
                f"{version.codename.capitalize()} 2025"
            ),
        )
        yield Footer()

    def analyser(self, filename: str) -> dict:
        """分析文件状态以生成显示文本

        Args:
            filename: 要分析的文件名

        Returns:
            dict: 包含显示文本的字典，键为行号
        """
        from heurams.kernel.repository.particle_loader import (load_electron,
                                                               load_nucleon)

        result = {}
        filestem = pathlib.Path(filename).stem

        # 构建电子文件路径
        electron_dir = config_var.get()["paths"]["electron_dir"]
        electron_file_path = pathlib.Path(electron_dir) / f"{filestem}.json"

        logger.debug(f"电子文件路径: {electron_file_path}")

        # 确保电子文件存在
        if not electron_file_path.exists():
            electron_file_path.touch()
            electron_file_path.write_text("{}")

        # 加载电子数据
        electron_dict = load_electron(path=electron_file_path)
        logger.debug(f"电子数据: {electron_dict}")

        # 分析电子状态
        is_due = 0
        is_activated = 0
        nextdate = 0x3F3F3F3F

        for electron in electron_dict.values():
            logger.debug(f"{electron}, 是否到期: {electron.is_due()}")

            if electron.is_due():
                is_due = 1
            if electron.is_activated():
                is_activated = 1
            nextdate = min(nextdate, electron.nextdate())

        # 检查是否需要更多复习
        nucleon_dir = config_var.get()["paths"]["nucleon_dir"]
        nucleon_path = pathlib.Path(nucleon_dir) / f"{filestem}.toml"
        nucleon_count = len(load_nucleon(nucleon_path))
        electron_count = len(electron_dict)
        is_more = not (electron_count >= nucleon_count)

        logger.debug(f"是否需要更多复习: {is_more}")

        # 更新状态
        self.nextdates[filename] = nextdate
        self.stay_enabled[filename] = is_due or is_more

        # 构建返回结果
        result[0] = f"{filename}\0"

        if not is_activated:
            result[1] = "  尚未激活"
        else:
            status_text = "需要复习" if is_due else "当前无需复习"
            result[1] = f"下一次复习: {nextdate}\n{status_text}"

        return result

    def on_mount(self) -> None:
        """挂载组件时初始化"""
        union_list_widget = self.query_one("#union-list", ListView)
        probe = probe_all(0)

        # 分析所有文件
        for file in probe["nucleon"]:
            self.texts[file] = self.analyser(file)

        # 按下次复习时间排序
        nucleon_files = sorted(
            probe["nucleon"],
            key=lambda f: self.nextdates[f],
            reverse=True,
        )

        # 填充列表
        if not probe["nucleon"]:
            union_list_widget.append(
                ListItem(
                    Static(
                        "在 ./nucleon/ 中未找到任何内容源数据文件。\n"
                        "请放置文件后重启应用，或者新建空的单元集。"
                    )
                )
            )
            union_list_widget.disabled = True
            return

        for file in nucleon_files:
            text = self.texts[file]
            list_item = ListItem(Label(f"{text[0]}\n{text[1]}"))
            union_list_widget.append(list_item)

            if not self.stay_enabled[file]:
                list_item.disabled = True

    def on_list_view_selected(self, event) -> None:
        """处理列表项选择事件"""
        if not isinstance(event.item, ListItem):
            return

        selected_label = event.item.query_one(Label)
        label_text = str(selected_label.renderable)

        if "未找到任何 .toml 文件" in label_text:
            return

        # 提取文件名
        selected_filename = pathlib.Path(label_text.partition("\0")[0].replace("*", ""))

        # 构建文件路径
        nucleon_dir = config_var.get()["paths"]["nucleon_dir"]
        electron_dir = config_var.get()["paths"]["electron_dir"]

        nucleon_file_path = pathlib.Path(nucleon_dir) / selected_filename
        electron_file_path = (
            pathlib.Path(electron_dir) / f"{selected_filename.stem}.json"
        )

        # 跳转到准备屏幕
        self.app.push_screen(PreparationScreen(nucleon_file_path, electron_file_path))

    def on_button_pressed(self, event) -> None:
        """处理按钮点击事件"""
        button_id = event.button.id

        if button_id == "new_nucleon_button":
            from .repocreator import NucleonCreatorScreen

            new_screen = NucleonCreatorScreen()
            self.app.push_screen(new_screen)

        elif button_id == "precache_all_button":
            from .precache import PrecachingScreen

            precache_screen = PrecachingScreen()
            self.app.push_screen(precache_screen)

        elif button_id == "about_button":
            about_screen = AboutScreen()
            self.app.push_screen(about_screen)

    def action_quit_app(self) -> None:
        """退出应用程序"""
        self.app.exit()
