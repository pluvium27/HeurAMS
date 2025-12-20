from textual.widget import Widget
from textual.widgets import Button, Label


class Placeholder(Widget):
    def __init__(
        self,
        *children: Widget,
        name: str | None = None,
        alia: str = "",
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

    def compose(self):
        yield Label("示例标签", id="testlabel")
        yield Button("示例按钮", id="testbtn", classes="choice")

    def on_button_pressed(self, event):
        pass
