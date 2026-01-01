import copy
import random
from typing import TypedDict

from textual.containers import Container
from textual.message import Message
from textual.widget import Widget
from textual.widgets import Button, Label

import heurams.kernel.evaluators as pz
import heurams.kernel.particles as pt
from heurams.services.logger import get_logger

from .base_puzzle_widget import BasePuzzleWidget

logger = get_logger(__name__)


class Setting(TypedDict):
    __origin__: str
    __hint__: str
    text: str
    delimiter: str
    min_denominator: str


class ClozePuzzle(BasePuzzleWidget):

    def __init__(
        self,
        *children: Widget,
        atom: pt.Atom,
        alia: str = "",
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
        markup: bool = True,
    ) -> None:
        super().__init__(
            *children,
            atom=atom,
            name=name,
            id=id,
            classes=classes,
            disabled=disabled,
            markup=markup,
        )
        self.inputlist = list()
        self.hashtable = {}
        self.alia = alia
        self._load()
        self.hashmap = dict()

    def _load(self):
        setting = self.atom.registry["orbital"]["puzzles"][self.alia]
        self.puzzle = pz.ClozePuzzle(
            text=setting["text"],
            delimiter=setting["delimiter"],
            min_denominator=int(setting["min_denominator"]),
        )
        self.puzzle.refresh()
        self.ans = copy.copy(self.puzzle.answer)  # 乱序
        random.shuffle(self.ans)

    def compose(self):
        yield Label(self.puzzle.wording, id="sentence")
        yield Label(f"当前输入: {self.inputlist}", id="inputpreview")
        # 渲染当前问题的选项
        with Container(id="btn-container"):
            for i in self.ans:
                self.hashmap[str(hash(i))] = i
                btnid = f"sel000-{hash(i)}"
                logger.debug(f"建立按钮 {btnid}")
                yield Button(i, id=f"{btnid}")

        yield Button("退格", id="delete")

    def update_display(self):
        preview = self.query_one("#inputpreview")
        preview.update(f"当前输入: {self.inputlist}")  # type: ignore

    def on_button_pressed(self, event: Button.Pressed) -> None:
        button_id = event.button.id

        if button_id == "delete":
            if len(self.inputlist) > 0:
                self.inputlist.pop()
                self.update_display()
        else:
            answer_text = self.hashmap[button_id[7:]]  # type: ignore
            self.inputlist.append(answer_text)
            self.update_display()

            if len(self.inputlist) >= len(self.puzzle.answer):
                is_correct = self.inputlist == self.puzzle.answer
                rating = 4 if is_correct else 2
                self.handler(rating)
                self.screen.rating = rating  # type: ignore

                if not is_correct:
                    self.inputlist = []
                    self.update_display()

    def handler(self, rating):
        if self.atom.lock():
            pass
        else:
            self.atom.minimize(rating)
