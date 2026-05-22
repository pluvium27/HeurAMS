from textual.widget import Widget
from textual.widgets import Button, Label

from heurams.i18n import _


class Placeholder(Widget):
    def __init__(
        self,
        *children: Widget,
        name: str | None = None,
        alia: str = "",
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
        markup: bool = True,
    ) -> None:
        super().__init__(
            *children,
            name=name,
            id=id,
            classes=classes,
            disabled=disabled,
            markup=markup,
        )

    def compose(self):
        yield Label(_("Sample Label"), id="testlabel")
        yield Button(_("Sample Button"), id="testbtn", classes="choice")

    def on_button_pressed(self, event):
        pass
