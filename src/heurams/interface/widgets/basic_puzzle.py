from textual.widgets import (
    Label,
    Static,
    Button,
)
from textual.containers import ScrollableContainer, Horizontal
from textual.widget import Widget
import heurams.kernel.particles as pt
from .base_puzzle_widget import BasePuzzleWidget
from textual.message import Message


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
            self.rating = rating  # 评分值 (0-5)
            super().__init__()

    # 反馈映射表
    feedback_mapping = {
        "feedback_5": {"rating": 5, "text": "完美回想"},
        "feedback_4": {"rating": 4, "text": "犹豫后正确"},
        "feedback_3": {"rating": 3, "text": "困难地正确"},
        "feedback_2": {"rating": 2, "text": "错误但熟悉"},
        "feedback_1": {"rating": 1, "text": "错误且不熟"},
        "feedback_0": {"rating": 0, "text": "完全空白"},
    }

    def compose(self):
        # 显示主要内容
        yield Label(self.atom.registry["nucleon"]["content"], id="main")

        # 显示评估说明（可选）
        yield Static("请评估你对这个内容的记忆程度: ", classes="instruction")

        # 按钮容器
        with ScrollableContainer(id="button_container"):
            btn = {}
            btn["5"] = Button(
                "完美回想", variant="success", id="feedback_5", classes="choice"
            )
            btn["4"] = Button(
                "犹豫后正确", variant="success", id="feedback_4", classes="choice"
            )
            btn["3"] = Button(
                "困难地正确", variant="warning", id="feedback_3", classes="choice"
            )
            btn["2"] = Button(
                "错误但熟悉", variant="warning", id="feedback_2", classes="choice"
            )
            btn["1"] = Button(
                "错误且不熟", variant="error", id="feedback_1", classes="choice"
            )
            btn["0"] = Button(
                "完全空白", variant="error", id="feedback_0", classes="choice"
            )

            # 布局按钮
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
