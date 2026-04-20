"""设置页面"""

from functools import reduce
import pathlib
from pathlib import Path
import os

from textual.app import ComposeResult
from textual.containers import ScrollableContainer, Container, Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import (
    Button,
    Footer,
    Header,
    Label,
    ListItem,
    ListView,
    Static,
    Collapsible,
    Input,
    Switch,
    Select,
)
from textual.layouts import horizontal

import heurams.kernel.particles as pt
import heurams.services.timer as timer
import heurams.services.version as version
from heurams.context import *
from heurams.kernel.particles import *
from heurams.kernel.repolib import *
from heurams.kernel.algorithms import algorithms
from heurams.services.logger import get_logger
from heurams.services.textproc import domize, undomize
from heurams.services.epath import epath

logger = get_logger(__name__)


class SettingScreen(Screen):
    """设置页面屏幕"""

    SUB_TITLE = "设置"
    BINDINGS = [
        ("q", "go_back", "返回"),
    ]
    CSS_PATH = rootdir / "interface" / "css" / "screens" / "setting.tcss"

    def __init__(
        self,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        super().__init__(name, id, classes)

    def compose(self) -> ComposeResult:
        """组合界面组件"""
        yield Header(show_clock=True)
        with ScrollableContainer():
            yield Label("[b]设置页面[/b]")
            for i in config_var.get():
                if i.startswith("_"):
                    continue
                a = self._get_subcfg(f"{i}")
                if a:
                    yield Collapsible(
                        *a, title=i + f'\n{config_var.get().get(f"_{i}_desc", "")}'
                    )
        yield Label(
            "退出页面时, 所作的更改会立即保存, 但仍建议重启软件以确保新的配置得到应用",
            classes="foot",
        )
        yield Footer()

    def _get_subcfg(self, parent_epath: str):
        parent = epath(config_var.get(), parent_epath)
        if isinstance(parent, ConfigDict):
            if parent.is_dir:
                lst = list()
                for i in parent:
                    if i.startswith("_"):
                        continue
                    a = self._get_subcfg(f"{parent_epath}.{i}")
                    if a:
                        lst.append(
                            Collapsible(
                                *a, title=i + f'\n{parent.get(f"_{i}_desc", "")}'
                            )
                        )
                return lst
        if isinstance(parent, dict) or (
            isinstance(parent, ConfigDict) and not parent.is_dir
        ):
            lst = list()
            for i in parent:
                if i.startswith("_"):
                    continue
                if isinstance(parent[i], dict):
                    a = self._get_subcfg(f"{parent_epath}.{i}")
                    if a:
                        lst.append(
                            Collapsible(
                                *a, title=i + f'\n{parent.get(f"_{i}_desc", "")}'
                            )
                        )
                elif f"_{i}_candidate" in parent:  # 选择框模式
                    if isinstance(parent[f"_{i}_candidate"], dict):
                        lst.append(
                            Horizontal(
                                Label(i + f'\n{parent.get(f"_{i}_desc", "")}'),
                                Select(
                                    (
                                        (f"{j} ({k})", j)
                                        for j, k in parent[f"_{i}_candidate"].items()
                                    ),
                                    prompt=f'{parent.get(f"{i}", "")}',
                                    id=domize(f"{parent_epath}.{i}"),
                                ),
                            )
                        )
                    elif isinstance(parent[f"_{i}_candidate"], list):
                        lst.append(
                            Horizontal(
                                Label(i + f'\n{parent.get(f"_{i}_desc", "")}'),
                                Select(
                                    ((j, j) for j in parent[f"_{i}_candidate"]),
                                    prompt=f'{parent.get(f"{i}", "")}',
                                    id=domize(f"{parent_epath}.{i}"),
                                ),
                            )
                        )
                else:
                    if isinstance(parent[i], float):
                        lst.append(
                            Horizontal(
                                Label(i + f'\n{parent.get(f"_{i}_desc", "")}'),
                                Input(
                                    value=str(parent[i]),
                                    placeholder="要求一个浮点数",
                                    type="number",
                                    id=domize(f"{parent_epath}.{i}"),
                                ),
                            )
                        )
                    elif isinstance(parent[i], str):
                        lst.append(
                            Horizontal(
                                Label(i + f'\n{parent.get(f"_{i}_desc", "")}'),
                                Input(
                                    value=parent[i],
                                    placeholder="要求一个字符串",
                                    type="text",
                                    id=domize(f"{parent_epath}.{i}"),
                                ),
                            )
                        )
                    elif isinstance(parent[i], bool):
                        lst.append(
                            Horizontal(
                                Label(i + f'\n{parent.get(f"_{i}_desc", "")}'),
                                Switch(
                                    value=parent[i], id=domize(f"{parent_epath}.{i}")
                                ),
                            )
                        )
                    elif isinstance(parent[i], int):
                        lst.append(
                            Horizontal(
                                Label(i + f'\n{parent.get(f"_{i}_desc", "")}'),
                                Input(
                                    value=str(parent[i]),
                                    placeholder="要求一个整数",
                                    type="integer",
                                    id=domize(f"{parent_epath}.{i}"),
                                ),
                            )
                        )
                    elif isinstance(parent[i], list):
                        pass
                    else:
                        lst.append(Label("未知类型"))
            return lst
        return [Label("无子项")]

    def on_mount(self) -> None:
        """挂载组件时初始化"""
        pass

    def action_go_back(self) -> None:
        """返回上一屏幕"""
        config_var.get().persist()
        self.app.pop_screen()

    def action_quit_app(self) -> None:
        """退出应用程序"""
        self.app.exit()

    def action_open_navigator(self) -> None:
        """打开导航器"""
        self.app.push_screen(NavigatorScreen())

    def on_input_changed(self, event: Input.Changed) -> None:
        widget_id = event.input.id
        if not widget_id:
            return
        eepath = undomize(widget_id)
        value = event.value
        epath(
            config_var.get(),
            eepath,
            enable_modify=True,
            new_value=type(epath(config_var.get(), eepath))(value),
        )

    def on_switch_changed(self, event: Switch.Changed) -> None:
        widget_id = event.switch.id
        if not widget_id:
            return
        eepath = undomize(widget_id)
        value = event.value
        epath(
            config_var.get(),
            eepath,
            enable_modify=True,
            new_value=type(epath(config_var.get(), eepath))(value),
        )

    def on_select_changed(self, event: Select.Changed) -> None:
        widget_id = event.select.id
        if not widget_id:
            return
        eepath = undomize(widget_id)
        value = event.value
        epath(
            config_var.get(),
            eepath,
            enable_modify=True,
            new_value=type(epath(config_var.get(), eepath))(value),
        )
