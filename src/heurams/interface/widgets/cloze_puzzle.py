import copy
import random
from typing import TypedDict

from textual.containers import ScrollableContainer, Horizontal
from textual.widget import Widget
from textual.widgets import Button, Label, Markdown
from textual.events import Key

import heurams.kernel.particles as pt
import heurams.kernel.puzzles as pz
from heurams.services.hasher import hash
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
        self.btn_shortcuts = {}
        self.hashmap = dict()

    def _load(self):
        setting = self.atom.registry["nucleon"]["puzzles"][self.alia]
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
        yield Markdown(f"> {self.listprint(self.inputlist)}", id="inputpreview")
        # 渲染当前问题的选项
        with ScrollableContainer(id="btn-container") as s:
            c = 0
            btns = []
            for i in self.ans:
                h = str(hash(i))
                if hash(i) in self.hashmap.keys():
                    continue
                c += 1
                self.hashmap[h] = i
                btnid = f"sel000-{h}"
                logger.debug(f"建立按钮 {btnid}")
                self.btn_shortcuts[f"{c}"] = btnid
                btns.append(Button(f"{i}", id=f"{btnid}", classes='cloze-option-btn'))
            for i in range((len(btns)+1)//2):
                if 2 * i + 1 + 1 <= len(btns):
                    yield Horizontal(btns[i], btns[len(btns) - 1 - i], classes='hori')
                else:
                    yield btns[i]
            s.focus()

        yield Button("退格", id="delete")
        self.btn_shortcuts[f"0"] = "delete"
        self.btn_shortcuts[f"backspace"] = "delete"
        self.btn_shortcuts[f"delete"] = "delete"

    def listprint(self, lst):
        s = ""
        if lst:
            lastone = lst[-1]
            for i in lst[:-1]:
                s += i + " "
            s += f" `{lastone}`"
        return s

    def update_display(self):
        preview = self.query_one("#inputpreview")
        preview.update(f"> {self.listprint(self.inputlist)}")  # type: ignore

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

    def on_key(self, event: Key) -> None:
        #self.notify(event.key)
        if event.key in self.btn_shortcuts:
            btn_id = self.btn_shortcuts.get(event.key)
            btn_id = "#" + btn_id
            self.query_one(btn_id, Button).press()
