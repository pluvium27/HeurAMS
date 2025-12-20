from textual.widget import Widget
from textual.widgets import Button, Label


class Finished(Widget):
    def __init__(
        self,
        *children: Widget,
        alia="",
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
        markup: bool = True
    ) -> None:
        self.alia = alia
        super().__init__(
            *children,
            name=name,
            id=id,
            classes=classes,
            disabled=disabled,
            markup=markup
        )

    def compose(self):
        yield Label("本次记忆进程结束", id="finished_msg")
        yield Button("返回上一级", id="back-to-menu")

    def on_button_pressed(self, event):
        button_id = event.button.id
        if button_id == "back-to-menu":
            self.app.pop_screen()
