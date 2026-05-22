from textual.containers import Horizontal, ScrollableContainer
from textual.message import Message
from textual.widget import Widget
from textual.widgets import Button, Label, Static

import heurams.kernel.particles as pt

from heurams.i18n import _
from .base_puzzle_widget import BasePuzzleWidget


class BasicEvaluation(BasePuzzleWidget):
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

    class RatingChanged(Message):
        def __init__(self, rating: int) -> None:
            self.rating = rating  # Rating value (0-5)
            super().__init__()

    # Feedback mapping
    feedback_mapping = {
        "feedback_5": {"rating": 5, "text": _("Perfect recall")},
        "feedback_4": {"rating": 4, "text": _("Correct after hesitation")},
        "feedback_3": {"rating": 3, "text": _("Correct with difficulty")},
        "feedback_2": {"rating": 2, "text": _("Wrong but familiar")},
        "feedback_1": {"rating": 1, "text": _("Wrong and unfamiliar")},
        "feedback_0": {"rating": 0, "text": _("Complete blank")},
    }

    def compose(self):
        # Show main content
        yield Label(self.atom.registry["nucleon"]["content"], id="main")

        # Show instruction (optional)
        yield Static(_("Evaluate how well you remember this content: "), classes="instruction")

        # Button container
        with ScrollableContainer(id="button_container"):
            btn = {}
            btn["5"] = Button(
                _("Perfect recall"), variant="success", id="feedback_5", classes="choice"
            )
            btn["4"] = Button(
                _("Correct after hesitation"), variant="success", id="feedback_4", classes="choice"
            )
            btn["3"] = Button(
                _("Correct with difficulty"), variant="warning", id="feedback_3", classes="choice"
            )
            btn["2"] = Button(
                _("Wrong but familiar"), variant="warning", id="feedback_2", classes="choice"
            )
            btn["1"] = Button(
                _("Wrong and unfamiliar"), variant="error", id="feedback_1", classes="choice"
            )
            btn["0"] = Button(
                _("Complete blank"), variant="error", id="feedback_0", classes="choice"
            )

            # Layout buttons
            yield Horizontal(btn["5"], btn["4"])
            yield Horizontal(btn["3"], btn["2"])
            yield Horizontal(btn["1"], btn["0"])

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """处理按钮点击事件"""
        button_id = event.button.id

        if button_id in self.feedback_mapping:
            feedback_info = self.feedback_mapping[button_id]

            self.post_message(
                self.RatingChanged(
                    rating=feedback_info["rating"],
                )
            )

            event.button.add_class("selected")

            self.disable_other_buttons(button_id)

    def disable_other_buttons(self, selected_button_id: str) -> None:
        for button in self.query("Button.choice"):
            if button.id != selected_button_id:
                button.disabled = True

    def enable_all_buttons(self) -> None:
        for button in self.query("Button.choice"):
            button.disabled = False

    def on_key(self, event) -> None:
        if event.key in ["0", "1", "2", "3", "4", "5"]:
            button_id = f"feedback_{event.key}"
            if button_id in self.feedback_mapping:
                # 模拟按钮点击
                self.post_message(
                    self.RatingChanged(
                        rating=self.feedback_mapping[button_id]["rating"],
                    )
                )
