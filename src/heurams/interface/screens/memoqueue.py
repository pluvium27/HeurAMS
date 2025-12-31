"""队列式记忆工作界面
"""
from enum import Enum, auto

from textual.app import ComposeResult
from textual.containers import Center, ScrollableContainer
from textual.reactive import reactive
from textual.screen import Screen
from textual.widgets import Button, Footer, Header, Label, Static

import heurams.kernel.particles as pt
import heurams.kernel.evaluators as pz
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
        ("q", "pop_screen", "返回"),
        #    ("p", "prev", "复习上一个"),
        ("d", "toggle_dark", ""),
        ("v", "play_voice", "朗读"),
        ("0,1,2,3", "app.push_screen('about')", ""),
    ]

    if config_var.get()["quick_pass"]:
        BINDINGS.append(("k", "quick_pass", "跳过"))
    rating = reactive(-1)

    def __init__(
        self,
        atoms: list,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        super().__init__(name, id, classes)
        self.atoms = atoms
        for i in self.atoms:
            i.do_eval()
        self.phaser = Phaser(atoms)
        # logger.debug(self.phaser.state)
        self.procession: Procession = self.phaser.current_procession()  # type: ignore
        self.atom: pt.Atom = self.procession.current_atom
        # logger.debug(self.phaser.state)
        # self.procession.forward(1)

    def on_mount(self):
        self.load_puzzle()
        pass

    def puzzle_widget(self):
        try:
            logger.debug(self.phaser.state)
            logger.debug(self.procession.cursor)
            logger.debug(self.atom)
            self.fission = Fission(self.atom, self.phaser.state)
            puzzle_debug = next(self.fission.generate())
            # logger.debug(puzzle_debug)
            return shim.puzzle2widget[puzzle_debug["puzzle"]](
                atom=self.atom, alia=puzzle_debug["alia"]
            )
        except (KeyError, StopIteration, AttributeError) as e:
            logger.debug(f"调度展开出错: {e}")
            return Static("无法生成谜题")
        # logger.debug(shim.puzzle2widget[puzzle_debug["puzzle"]])

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with ScrollableContainer():
            yield Label(self._get_progress_text(), id="progress")

            # self.mount(self.current_widget()) # type: ignore
            yield ScrollableContainer(id="puzzle-container")
        # yield Button("重新学习此单元", id="re-recognize", variant="warning")
        yield Footer()

    def _get_progress_text(self):
        return f"当前进度: {self.procession.process() + 1}/{self.procession.total_length()}"

    def update_display(self):
        progress_widget = self.query_one("#progress")
        progress_widget.update(self._get_progress_text())  # type: ignore

    def load_puzzle(self):
        self.atom: pt.Atom = self.procession.current_atom
        container = self.query_one("#puzzle-container")
        for i in container.children:
            i.remove()
        container.mount(self.puzzle_widget())

    def load_finished_widget(self):
        container = self.query_one("#puzzle-container")
        for i in container.children:
            i.remove()
        from heurams.interface.widgets.finished import Finished

        container.mount(Finished())

    def on_button_pressed(self, event):
        event.stop()

    def watch_rating(self, old_rating, new_rating) -> None:
        if self.procession == 0:
            return
        if new_rating == -1:
            return
        forwards = 1 if new_rating >= 4 else 0
        self.rating = -1
        logger.debug(f"试图前进: {"允许" if forwards else "禁止"}")
        if forwards:
            ret = self.procession.forward(1)
            if ret == 0:  # 若结束了此次队列
                self.procession = self.phaser.current_procession()  # type: ignore
                if self.procession == 0:  # 若所有队列都结束了
                    logger.debug(f"记忆进程结束")
                    for i in self.atoms:
                        i: pt.Atom
                        i.revise()
                        i.persist("electron")
                    self.load_finished_widget()
                    return
                else:
                    logger.debug(f"建立新队列 {self.procession.phase}")
            self.load_puzzle()
        else:  # 若不通过
            self.procession.append()
        self.update_display()

    def action_quick_pass(self):
        self.rating = 5
        self.atom.minimize(5)
        self.atom.registry["electron"].activate()
        self.atom.lock(1)

    def action_play_voice(self):
        self.run_worker(self.play_voice, exclusive=True, thread=True)

    def play_voice(self):
        """朗读当前内容"""
        from pathlib import Path

        from heurams.services.audio_service import play_by_path
        from heurams.services.hasher import get_md5

        path = Path(config_var.get()["paths"]["cache_dir"])
        path = (
            path
            / f"{get_md5(self.atom.registry['nucleon'].metadata["formation"]["tts_text"])}.wav"
        )
        if path.exists():
            play_by_path(path)
        else:
            from heurams.services.tts_service import convertor

            convertor(
                self.atom.registry["nucleon"].metadata["formation"]["tts_text"], path
            )
            play_by_path(path)

    def action_toggle_dark(self):
        self.app.action_toggle_dark()

    def action_pop_screen(self):
        self.app.pop_screen()
