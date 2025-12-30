# mcq.py
import random
from typing import Dict, List, Optional, Union

from heurams.services.logger import get_logger

from .base import BaseEvaluator

logger = get_logger(__name__)


class MCQPuzzle(BaseEvaluator):
    """选择题谜题生成器

    该类用于生成和管理选择题谜题, 支持多个题目同时生成,
    每个题目包含问题, 正确答案和干扰项选项.

    Attributes:
        prefix (str): 题目前缀文本
        mapping (Dict[str, str]): 问题和正确答案的映射字典
        jammer (List[str]): 干扰项列表
        max_riddles_num (int): 最大题目数量限制
        wording (Union[str, List[str]]): 题目文本内容
        answer (Union[str, List[str]]): 正确答案列表
        options (List[List[str]]): 每个题目的选项列表
    """

    def __init__(
        self,
        mapping: Dict[str, str],
        jammer: List[str],
        max_riddles_num: int = 2,
        prefix: str = "",
    ) -> None:
        """初始化选择题谜题生成器

        Args:
            mapping: 问题和正确答案的映射字典, 键为问题, 值为正确答案
            jammer: 干扰项列表, 用于生成错误选项
            max_riddles_num: 每次生成的最大题目数量, 范围限制在1-5之间
            prefix: 题目前缀文本, 会显示在每个题目之前
        """
        logger.debug(
            "MCQPuzzle.__init__: mapping size=%d, jammer size=%d, max_riddles_num=%d",
            len(mapping),
            len(jammer),
            max_riddles_num,
        )
        self.prefix = prefix
        self.mapping = mapping
        self.max_riddles_num = max(1, min(max_riddles_num, 5))

        # 初始化干扰项, 确保至少有4个选项
        self._init_jammer(jammer)

        # 初始化题目状态
        self._reset_puzzle_state()

    def _init_jammer(self, jammer: List[str]) -> None:
        """初始化干扰项列表

        合并传入的干扰项和所有正确答案, 确保去重后至少有4个干扰项.

        Args:
            jammer: 传入的干扰项列表
        """
        # 合并正确答案和传入的干扰项, 并去重
        logger.debug(f"答案映射: {self.mapping}, {type(self.mapping)}")
        logger.debug(f"干扰项: {jammer}, {type(jammer)}")
        unique_jammers = set(jammer + list(self.mapping.values()))
        self.jammer = list(unique_jammers)

        # 确保至少有4个干扰项
        while len(self.jammer) < 4:
            self.jammer.append(" " * (4 - len(self.jammer)))

        unique_jammers = set(jammer + list(self.mapping.values()))

    def _reset_puzzle_state(self) -> None:
        """重置谜题状态为初始值

        将题目文本, 答案和选项重置为默认状态.
        """
        self.wording: Union[str, List[str]] = "选择题 - 尚未刷新谜题"
        self.answer: Union[str, List[str]] = ["选择题 - 尚未刷新谜题"]
        self.options: List[List[str]] = []

    def refresh(self) -> None:
        """刷新谜题, 生成指定数量的选择题

        从mapping中随机选择指定数量的问题, 为每个问题生成包含正确答案
        和干扰项的选项列表, 并更新谜题状态.

        Raises:
            ValueError: 当mapping为空时不会抛出异常, 但会设置空谜题状态
        """
        logger.debug("MCQPuzzle.refresh 开始, mapping size=%d", len(self.mapping))
        if not self.mapping:
            self._set_empty_puzzle()
            return

        num_questions = min(self.max_riddles_num, len(self.mapping))
        selected_questions = random.sample(list(self.mapping.items()), num_questions)

        puzzles: List[str] = []
        answers: List[str] = []
        all_options: List[List[str]] = []

        for question, correct_answer in selected_questions:
            options = self._generate_options(correct_answer)
            puzzles.append(question)
            answers.append(correct_answer)
            all_options.append(options)

        self.wording = self._format_questions(puzzles)
        self.answer = answers
        self.options = all_options

    def _set_empty_puzzle(self) -> None:
        """设置为空谜题状态

        当没有可用的题目时, 设置相应的提示信息.
        """
        self.wording = "无可用题目"
        self.answer = ["无答案"]
        self.options = []

    def _generate_options(self, correct_answer: str) -> List[str]:
        """为单个问题生成选项列表(包含正确答案和干扰项)

        Args:
            correct_answer: 当前问题的正确答案

        Returns:
            包含4个选项的列表, 其中一个是正确答案, 三个是干扰项

        Note:
            如果可用干扰项不足3个, 会使用重复的干扰项填充
        """
        options = [correct_answer]

        # 获取可用的干扰项(排除正确答案)
        available_jammers = [
            jammer for jammer in self.jammer if jammer != correct_answer
        ]

        # 选择3个干扰项
        if len(available_jammers) >= 3:
            selected_jammers = random.sample(available_jammers, 3)
        else:
            selected_jammers = random.choices(available_jammers, k=3)

        options.extend(selected_jammers)
        random.shuffle(options)

        return options

    def _format_questions(self, puzzles: List[str]) -> List[str]:
        """格式化问题列表为可读的文本

        Args:
            puzzles: 原始问题文本列表

        Returns:
            格式化后的问题文本列表, 包含编号和前缀

        Example:
            输入: ["问题1", "问题2"]
            输出: ["前缀:\\n  1. 问题1", "前缀:\\n  2. 问题2"]
        """
        if not puzzles:
            return []

        formatted_questions = []
        for i, puzzle in enumerate(puzzles, 1):
            question_text = (
                f"{self.prefix}:\n  {i}. {puzzle}" if self.prefix else f"{i}. {puzzle}"
            )
            formatted_questions.append(question_text)

        return formatted_questions

    def __str__(self) -> str:
        """返回谜题的字符串表示

        Returns:
            包含所有问题和正确答案的格式化字符串

        Example:
            选择题 - 尚未刷新谜题
            正确答案: 选择题 - 尚未刷新谜题
        """
        if isinstance(self.wording, list):
            question_text = "\n".join(self.wording)
        else:
            question_text = self.wording

        if isinstance(self.answer, list):
            answer_text = ", ".join(self.answer)
        else:
            answer_text = str(self.answer)

        return f"{question_text}\n正确答案: {answer_text}"

    def get_question_count(self) -> int:
        """获取当前生成的题目数量

        Returns:
            当前题目的数量, 如果尚未刷新则返回 0
        """
        if isinstance(self.wording, list):
            return len(self.wording)
        elif self.wording == "选择题 - 尚未刷新谜题" or self.wording == "无可用题目":
            return 0
        else:
            return 1

    def get_correct_answer_for_question(self, question_index: int) -> Optional[str]:
        """获取指定题目的正确答案

        Args:
            question_index: 题目索引(从0开始)

        Returns:
            指定题目的正确答案, 如果索引无效则返回None
        """
        if not isinstance(self.answer, list):
            return None
        if 0 <= question_index < len(self.answer):
            return self.answer[question_index]
        return None

    def get_options_for_question(self, question_index: int) -> Optional[List[str]]:
        """获取指定题目的选项列表

        Args:
            question_index: 题目索引(从0开始)

        Returns:
            指定题目的选项列表, 如果索引无效则返回None
        """
        if 0 <= question_index < len(self.options):
            return self.options[question_index]
        return None
