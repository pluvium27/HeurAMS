from textual.widget import Widget
from textual.widgets import Button, Label

from heurams.i18n import _


class Finished(Widget):
    def __init__(
        self,
        *children: Widget,
        alia="",
        is_saved=0,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
        markup: bool = True,
    ) -> None:
        self.alia = alia
        self.is_saved = is_saved
        super().__init__(
            *children,
            name=name,
            id=id,
            classes=classes,
            disabled=disabled,
            markup=markup,
        )

    def compose(self):
        yield Label(_("This memorization session is finished"), id="finished_msg")
        yield Label(_("Algorithm data {}").format(_("saved") if self.is_saved else _("not saved")))
        yield Button(_("Back to Menu"), flat=True, id="back-to-menu")

    def on_button_pressed(self, event):
        button_id = event.button.id
        if button_id == "back-to-menu":
            self.app.pop_screen()
