from textual.widget import Widget
from textual.widgets import Button, Label


class Finished(Widget):
    def __init__(
        self,
        *children: Widget,
        alia="",
        is_saved = 0,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
        markup: bool = True
    ) -> None:
        self.alia = alia
        self.is_saved = is_saved
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
        yield Label(f"算法数据{'已保存' if self.is_saved else "未能保存"}")
        yield Button("返回上一级", id="back-to-menu")

    def on_button_pressed(self, event):
        button_id = event.button.id
        if button_id == "back-to-menu":
            self.app.pop_screen()
