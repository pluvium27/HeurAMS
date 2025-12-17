from textual.reactive import reactive
from textual.widgets import (
    Markdown,
    Label,
    Static,
    Button,
)
from textual.containers import Center
from textual.widget import Widget
from typing import Dict
import heurams.kernel.particles as pt
import re
from .base_puzzle_widget import BasePuzzleWidget
from typing import TypedDict, List
from textual.message import Message
from heurams.services.logger import get_logger

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
        cfg: RecognitionConfig = self.atom.registry["orbital"]["puzzles"][self.alia]
        delim = self.atom.registry["nucleon"].metadata["formation"]["delimiter"]
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
        metadata = self.atom.registry["nucleon"].metadata
        primary = cfg["primary"]

        with Center():
            yield Static(f"[dim]{cfg['top_dim']}[/]")
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
