#!/usr/bin/env python3
from textual.app import ComposeResult
from textual.widgets import (
    Header,
    Footer,
    Label,
    Button,
    Static,
    ProgressBar,
)
from textual.containers import ScrollableContainer, Horizontal
from textual.containers import ScrollableContainer
from textual.screen import Screen
import pathlib

import heurams.kernel.particles as pt
import heurams.services.hasher as hasher
from heurams.context import *
from textual.worker import get_current_worker


class SyncScreen(Screen):

    BINDINGS = [("q", "go_back", "返回")]

    def __init__(self, nucleons: list = [], desc: str = ""):
        super().__init__(name=None, id=None, classes=None)

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with ScrollableContainer(id="sync_container"):
            pass
        yield Footer()

    def on_mount(self):
        """挂载时初始化状态"""

    def update_status(self, status, current_item="", progress=None):
        """更新状态显示"""

    def on_button_pressed(self, event: Button.Pressed) -> None:
        event.stop()

    def action_go_back(self):
        self.app.pop_screen()

    def action_quit_app(self):
        self.app.exit()
