"""队列式记忆工作界面"""

from enum import Enum, auto

from textual.app import ComposeResult
from textual.containers import Center, ScrollableContainer
from textual.reactive import reactive
from textual.screen import Screen
from textual.widgets import Button, Footer, Header, Label, Static

import heurams.kernel.puzzles as pz
import heurams.kernel.particles as pt
from heurams.context import config_var
from heurams.kernel.reactor import *
from heurams.services.logger import get_logger

from .. import shim


class AtomState(Enum):
    FAILED = auto()
    NORMAL = auto()


logger = get_logger(__name__)


class MemScreen(Screen):
    BINDINGS = [
        ("q", "go_back", "返回"),
        ("p", "prev", "查看上一个"),
        ("d", "toggle_dark", ""),
        ("v", "play_voice", "朗读"),
        ("0,1,2,3", "app.push_screen('about')", ""),
    ]

    if config_var.get()["quick_pass"]:
        BINDINGS.append(("k", "quick_pass", "正确应答"))
        BINDINGS.append(("f", "quick_fail", "错误应答"))
    rating = reactive(-1)

    def __init__(
        self,
        phaser: Phaser,
        name=None,
        id=None,
        classes=None,
    ) -> None:
        super().__init__(name, id, classes)
        self.phaser = phaser
        self.update_state()
        self.fission: Fission

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with ScrollableContainer():
            yield Label(self._get_progress_text(), id="progress")
            yield ScrollableContainer(id="puzzle-container")
        yield Footer()

    def update_state(self):
        """更新状态机"""
        self.procession: Procession = self.phaser.current_procession()  # type: ignore
        self.atom: pt.Atom = self.procession.current_atom  # type: ignore

    def on_mount(self):
        self.fission = self.procession.get_fission()
        self.mount_puzzle()
        self.update_display()

    def puzzle_widget(self):
        try:
            puzzle = self.fission.get_current_puzzle_inf()
            return shim.puzzle2widget[puzzle["puzzle"]](  # type: ignore
                atom=self.atom, alia=puzzle["alia"]  # type: ignore
            )
        except Exception as e:
            logger.debug(f"调度展开出错: {e}")
            return Static(f"无法生成谜题 {e}")

    def _get_progress_text(self):
        s = f"阶段: {self.procession.phase.name}\n"
        if config_var.get().get("debug_topline", 0):
            try:
                alia = self.fission.get_current_puzzle_inf()["alia"]  # type: ignore
                s += f"谜题: {alia}\n"
            except:
                pass
            try:
                stat = self.phaser.__repr__("simple", "")
                s += f"{stat}\n"
            except:
                pass
            try:
                stat = self.procession.__repr__("simple", "")
                s += f"{stat}\n"
            except:
                pass
            try:
                stat = self.fission.__repr__("simple", "")
                s += f"{stat}\n"
            except Exception as e:
                s = str(e)
            # s += f"当前进度: {self.procession.process() + 1}/{self.procession.total_length()}"
        return s

    def update_display(self):
        """更新进度显示"""
        progress_widget = self.query_one("#progress")
        progress_widget.update(self._get_progress_text())  # type: ignore

    def mount_puzzle(self):
        """挂载当前谜题组件"""
        if self.procession.phase == PhaserState.FINISHED:
            self.mount_finished_widget()
            return
        container = self.query_one("#puzzle-container")
        for i in container.children:
            i.remove()
        container.mount(self.puzzle_widget())

    def mount_finished_widget(self):
        """挂载已完成组件"""
        container = self.query_one("#puzzle-container")
        for i in container.children:
            i.remove()
        from heurams.interface.widgets.finished import Finished

        container.mount(Finished())

    def on_button_pressed(self, event):
        event.stop()

    def action_play_voice(self):
        self.run_worker(self.play_voice, exclusive=True, thread=True)

    def play_voice(self):
        """朗读当前内容"""
        from pathlib import Path

        from heurams.services.audio_service import play_by_path
        from heurams.services.hasher import get_md5

        path = Path(config_var.get()["paths"]["data"]) / "cache" / "voice"
        path = path / f"{get_md5(self.atom.registry['nucleon']["tts_text"])}.wav"
        if path.exists():
            play_by_path(path)
        else:
            from heurams.services.tts_service import convertor

            convertor(self.atom.registry["nucleon"]["tts_text"], path)
            play_by_path(path)

    def watch_rating(self, old_rating, new_rating) -> None:
        if new_rating == -1:  # 安全值
            return
        self.update_state()
        if self.procession.phase == PhaserState.FINISHED:
            rating = -1
            return
        self.fission.report(new_rating)
        self.forward(new_rating)
        self.rating = -1

    def forward(self, rating):
        self.update_state()
        allow_forward = 1 if rating >= 4 else 0
        if allow_forward:
            self.fission.forward()
        if self.fission.state == "retronly":
            self.forward_atom(self.fission.get_quality())
        self.update_state()
        self.mount_puzzle()
        self.update_display()

    def forward_atom(self, quality):
        logger.debug(f"Quality: {quality}")
        if quality <= 3:
            self.procession.append()
            self.update_state()  # 刷新状态
        self.procession.forward(1)
        self.update_state()  # 刷新状态
        self.fission = self.procession.get_fission()

    def action_go_back(self):
        self.app.pop_screen()

    def action_quick_pass(self):
        self.rating = 5

    def action_quick_fail(self):
        self.rating = 3
