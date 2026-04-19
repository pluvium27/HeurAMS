"""设置页面"""

from functools import reduce
import pathlib
from pathlib import Path
import os

from textual.app import ComposeResult
from textual.containers import ScrollableContainer, Container, Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Button, Footer, Header, Label, ListItem, ListView, Static, Collapsible, Input, Switch
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
            yield Label('设置页面')
            for i in config_var.get():
                yield Collapsible(*self._get_subcfg(f'{i}'), title=i)
        yield Footer()

    def _get_subcfg(self, parent_epath: str):
        parent = epath(config_var.get(), parent_epath)
        if isinstance(parent, ConfigDict):
            if parent.is_dir:
                lst = list()
                for i in parent:
                    lst.append(Collapsible(*self._get_subcfg(f"{parent_epath}.{i}"), title=i))
                return lst
        if isinstance(parent, dict) or (isinstance(parent, ConfigDict) and not parent.is_dir):
            lst = list()
            for i in parent:
                if i.startswith('_'):
                    continue
                if isinstance(parent[i], dict):
                    lst.append(Collapsible(*self._get_subcfg(f"{parent_epath}.{i}"), title=i))
                elif isinstance(parent[i], float):
                    lst.extend([
                        Label(i),
                        Input(value=str(parent[i]), placeholder='要求一个浮点数', type='number', id=domize(f"{parent_epath}.{i}"))
                    ])
                elif isinstance(parent[i], str):
                    lst.extend([
                        Label(i),
                        Input(value=parent[i], placeholder='要求一个字符串', type='text', id=domize(f"{parent_epath}.{i}"))
                    ])
                elif isinstance(parent[i], bool):
                    lst.extend([
                        Label(i),
                        Switch(value=str(parent[i]), id=domize(f"{parent_epath}.{i}"))
                    ])
                elif isinstance(parent[i], int):
                    lst.extend([
                        Label(i),
                        Input(value=str(parent[i]), placeholder='要求一个整数', type='integer', id=domize(f"{parent_epath}.{i}"))
                    ])
                elif isinstance(parent[i], list):
                    pass
                else:
                    lst.append(Label('未知类型'))

            return lst
        return [Label('无子项')]

    def on_mount(self) -> None:
        """挂载组件时初始化"""
        pass

    def action_quit_app(self) -> None:
        """退出应用程序"""
        self.app.exit()

    def action_open_navigator(self) -> None:
        """打开导航器"""
        self.app.push_screen(NavigatorScreen())

    def on_button_pressed(self, event: Button.Pressed) -> None:
        logger.debug(f"event.button.id: {event.button.id}")
        """处理按钮点击事件"""
        if str(event.button.id) == 'apply':
            pass
        if str(event.button.id) == 'openfolder':
            pass
        if str(event.button.id) == 'cancel':
            pass
