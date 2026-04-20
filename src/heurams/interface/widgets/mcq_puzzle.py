# 单项选择题
from typing import TypedDict

from textual.containers import Container, ScrollableContainer
from textual.widget import Widget
from textual.widgets import Button, Label

import heurams.kernel.particles as pt
import heurams.kernel.puzzles as pz
from heurams.services.hasher import hash
from heurams.services.logger import get_logger

from .base_puzzle_widget import BasePuzzleWidget

logger = get_logger(__name__)


class Setting(TypedDict):
    __origin__: str
    __hint__: str
    primary: str  # 显示的提示文本
    mapping: dict  # 谜题到答案的映射
    jammer: list  # 干扰项
    max_riddles_num: int  # 最大谜题数量
    prefix: str  # 提示词前缀


class MCQPuzzle(BasePuzzleWidget):
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
        self.inputlist = []
        self.alia = alia
        self.hashmap = dict()
        self.cursor = 0
        self.atom = atom
        self._load()

    def _load(self):
        cfg = self.atom.registry["nucleon"]["puzzles"][self.alia]
        if cfg["mapping"] == {}:
            self.screen.rating = 5  # type: ignore
        self.puzzle = pz.MCQPuzzle(
            cfg["mapping"], cfg["jammer"], int(cfg["max_riddles_num"]), cfg["prefix"]
        )
        self.puzzle.refresh()

    def compose(self):
        setting: Setting = self.atom.registry["nucleon"]["puzzles"][self.alia]
        if len(self.inputlist) > len(self.puzzle.options):
            logger.debug("ERR IDX")
            logger.debug(self.inputlist)
            logger.debug(self.puzzle.options)
        else:
            current_options = self.puzzle.options[len(self.inputlist)]
            yield Label(setting["primary"], id="sentence")
            yield Label(self.puzzle.wording[len(self.inputlist)], id="puzzle")
            yield Label(f"当前输入: {self.inputlist}", id="inputpreview")

        # 渲染当前问题的选项
        with Container(id="btn-container"):
            for i in current_options:
                self.hashmap[str(hash(i))] = i
                btnid = f"sel{str(self.cursor).zfill(3)}-{hash(i)}"
                logger.debug(f"建立按钮 {btnid}")
                yield Button(i, id=f"{btnid}")

        yield Button("退格", id="delete")

    def update_display(self, error=0):
        # 更新预览标签
        preview = self.query_one("#inputpreview")
        preview.update(f"当前输入: {self.inputlist}")  # type: ignore
        logger.debug("已经更新预览标签")
        # 更新问题标签
        puzzle_label = self.query_one("#puzzle")
        current_question_index = len(self.inputlist)
        if current_question_index < len(self.puzzle.wording):
            puzzle_label.update(self.puzzle.wording[current_question_index])  # type: ignore

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """处理按钮点击事件"""
        event.stop()
        button_id = event.button.id

        if button_id == "delete":
            # 退格处理
            if len(self.inputlist) > 0:
                self.inputlist.pop()
                self.refresh_buttons()
                self.update_display()

        elif button_id.startswith("sel"):  # type: ignore
            # 选项选择处理
            answer_text = self.hashmap[button_id[7:]]  # type: ignore
            self.inputlist.append(answer_text)
            logger.debug(f"{self.inputlist}")
            # 检查是否完成所有题目
            if len(self.inputlist) >= len(self.puzzle.answer):
                is_correct = self.inputlist == self.puzzle.answer
                rating = 4 if is_correct else 2

                self.screen.rating = rating  # type: ignore
                self.handler(rating)
                # 重置输入(如果回答错误)
                if not is_correct:
                    self.inputlist = []
                    self.refresh_buttons()
                    self.update_display()
            else:
                # 进入下一题
                self.refresh_buttons()
                self.update_display()

    def refresh_buttons(self):
        """刷新按钮显示(用于题目切换)"""
        # 移除所有选项按钮
        logger.debug("刷新按钮")
        self.cursor += 1
        container = self.query_one("#btn-container")
        buttons_to_remove = [
            child
            for child in container.children
            if hasattr(child, "id") and child.id and child.id.startswith("sel")
        ]

        for button in buttons_to_remove:
            logger.info(button)
            container.remove_children("#" + button.id)  # type: ignore

        # 添加当前题目的选项按钮
        current_question_index = len(self.inputlist)
        if current_question_index < len(self.puzzle.options):
            current_options = self.puzzle.options[current_question_index]
            for option in current_options:
                button_id = f"sel{str(self.cursor).zfill(3)}-{hash(option)}"
                if button_id not in self.hashmap:
                    self.hashmap[button_id[7:]] = option
                new_button = Button(option, id=button_id)
                container.mount(new_button)

    def handler(self, rating):
        if self.atom.lock():
            pass
        else:
            self.atom.minimize(rating)
