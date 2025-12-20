#!/usr/bin/env python3
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
    SUB_TITLE = "仪表盘"

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield ScrollableContainer(
            Label(f'欢迎使用 "潜进" 启发式辅助记忆调度器', classes="title-label"),
            Label(f"当前 UNIX 日时间戳: {timer.get_daystamp()}"),
            Label(f'时区修正: UTC+{config_var.get()["timezone_offset"] / 3600}'),
            Label("选择待学习或待修改的记忆单元集:", classes="title-label"),
            ListView(id="union-list", classes="union-list-view"),
            Label(
                f'"潜进" 启发式辅助记忆调度器 | 版本 {version.ver} {version.codename.capitalize()} 2025'
            ),
        )
        yield Footer()

    def item_desc_generator(self, filename) -> dict:
        """简单分析以生成项目项显示文本

        Returns:
            dict: 以数字为列表, 分别呈现单行字符串
        """
        res = dict()
        filestem = pathlib.Path(filename).stem
        res[0] = f"{filename}\0"
        import heurams.kernel.particles as pt
        from heurams.kernel.particles.loader import load_electron

        electron_file_path = pathlib.Path(config_var.get()["paths"]["electron_dir"]) / (
            filestem + ".json"
        )

        logger.debug(f"电子文件路径: {electron_file_path}")

        if electron_file_path.exists():  # 未找到则创建电子文件 (json)
            pass
        else:
            electron_file_path.touch()
            with open(electron_file_path, "w") as f:
                f.write("{}")
        electron_dict = load_electron(path=electron_file_path)  # TODO: 取消硬编码扩展名
        logger.debug(electron_dict)
        is_due = 0
        is_activated = 0
        nextdate = 0x3F3F3F3F
        for i in electron_dict.values():
            i: pt.Electron
            logger.debug(i, i.is_due())
            if i.is_due():
                is_due = 1
            if i.is_activated():
                is_activated = 1
            nextdate = min(nextdate, i.nextdate())
        res[1] = f"下一次复习: {nextdate}\n"
        res[1] += f"{is_due if "需要复习" else "当前无需复习"}"
        if not is_activated:
            res[1] = "  尚未激活"
        return res

    def on_mount(self) -> None:
        union_list_widget = self.query_one("#union-list", ListView)

        probe = probe_all(0)

        if len(probe["nucleon"]):
            for file in probe["nucleon"]:
                text = self.item_desc_generator(file)
                union_list_widget.append(
                    ListItem(
                        Label(text[0] + "\n" + text[1]),
                    )
                )
        else:
            union_list_widget.append(
                ListItem(
                    Static(
                        "在 ./nucleon/ 中未找到任何内容源数据文件.\n请放置文件后重启应用.\n或者新建空的单元集."
                    )
                )
            )
            union_list_widget.disabled = True

    def on_list_view_selected(self, event) -> None:
        if not isinstance(event.item, ListItem):
            return

        selected_label = event.item.query_one(Label)
        if "未找到任何 .toml 文件" in str(selected_label.renderable):  # type: ignore
            return

        selected_filename = pathlib.Path(
            str(selected_label.renderable)
            .partition("\0")[0]  # 文件名末尾截断, 保留文件名
            .replace("*", "")
        )  # 去除markdown加粗

        nucleon_file_path = (
            pathlib.Path(config_var.get()["paths"]["nucleon_dir"]) / selected_filename
        )
        electron_file_path = pathlib.Path(config_var.get()["paths"]["electron_dir"]) / (
            str(selected_filename.stem) + ".json"
        )
        self.app.push_screen(PreparationScreen(nucleon_file_path, electron_file_path))

    def on_button_pressed(self, event) -> None:
        if event.button.id == "new_nucleon_button":
            # 切换到创建单元
            from .nucreator import NucleonCreatorScreen

            newscr = NucleonCreatorScreen()
            self.app.push_screen(newscr)
        elif event.button.id == "precache_all_button":
            # 切换到缓存管理器
            from .precache import PrecachingScreen

            precache_screen = PrecachingScreen()
            self.app.push_screen(precache_screen)
        elif event.button.id == "about_button":
            from .about import AboutScreen

            about_screen = AboutScreen()
            self.app.push_screen(about_screen)

    def action_quit_app(self) -> None:
        self.app.exit()
