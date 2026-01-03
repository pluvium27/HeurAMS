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
        from heurams.context import config_var

        autovoice = config_var.get()["interface"]["memorizor"]["autovoice"]
        if autovoice:
            self.screen.action_play_voice()  # type: ignore
        cfg: RecognitionConfig = self.atom.registry["nucleon"]["puzzles"][self.alia]
        delim = self.atom.registry["nucleon"]["delimiter"]
        replace_dict = {
            ", ": ",",
            ". ": ".",
            "; ": ";",
            ": ": ":",
            f"{delim},": ",",
            f".{delim}": ".",
            f"{delim};": ";",
            f";{delim}": ";",
            f":{delim}": ":",
        }

        nucleon = self.atom.registry["nucleon"]
        metadata = self.atom.registry["nucleon"]
        primary = cfg["primary"]

        with Center():
            for i in cfg["top_dim"]:
                yield Static(f"[dim]{i}[/]")
            yield Label("")

        for old, new in replace_dict.items():
            primary = primary.replace(old, new)
        primary_splited = re.split(r"(?<=[,;:|])", cfg["primary"])
        for item in primary_splited:
            with Center():
                yield Label(
                    f"[b][b]{item.replace(delim, ' ')}[/][/]",
                    id="sentence" + str(hash(item)),
                )

        for item in cfg["secondary"]:
            if isinstance(item, list):
                for j in item:
                    yield Markdown(f"### {metadata['annotation'][item]}: {j}")
                    continue
            if isinstance(item, Dict):
                total = ""
                for j, k in item.items():  # type: ignore
                    total += f"> **{j}**: {k}  \n"
                yield Markdown(total)
            if isinstance(item, str):
                yield Markdown(item)

        with Center():
            yield Button("我已知晓", id="ok")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "ok":
            self.screen.rating = 5  # type: ignore
            self.handler(5)

    def handler(self, rating):
        if not self.atom.registry["runtime"]["locked"]:
            if not self.atom.registry["electron"].is_activated():
                self.atom.registry["electron"].activate()
                logger.debug(f"激活原子 {self.atom}")
                self.atom.lock(1)
                self.atom.minimize(5)
        else:
            pass
