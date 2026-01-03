import re
from typing import Dict, List, TypedDict

from textual.containers import Center
from textual.message import Message
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Button, Label, Markdown, Static

import heurams.kernel.particles as pt
from heurams.services.logger import get_logger

from .base_puzzle_widget import BasePuzzleWidget

logger = get_logger(__name__)


class RecognitionConfig(TypedDict):
    __origin__: str
    __hint__: str
    primary: str
    secondary: List[str]
    top_dim: List[str]


class Recognition(BasePuzzleWidget):
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
        if alia == "":
            alia = "Recognition"
        self.alia = alia

    def compose(self):
        yield Button("我已知晓", id="ok")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        pass

    def handler(self, rating):
        pass