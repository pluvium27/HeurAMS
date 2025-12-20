from typing import Iterable

from textual.app import ComposeResult
from textual.widget import Widget

import heurams.kernel.particles as pt


class BasePuzzleWidget(Widget):
    def __init__(
        self,
        *children: Widget,
        atom: pt.Atom,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
        markup: bool = True
    ) -> None:
        super().__init__(
            *children,
            name=name,
            id=id,
            classes=classes,
            disabled=disabled,
            markup=markup
        )
        self.atom = atom

    def compose(self) -> Iterable[Widget]:
        return super().compose()

    def handler(self, rating) -> None:
        pass
