import random

from heurams.services.logger import get_logger

from .base import BasePuzzle

logger = get_logger(__name__)


class ClozePuzzle(BasePuzzle):
    """填空题谜题生成器

    Args:
        text: 原始字符串(需要 delimiter 分割句子, 末尾应有 delimiter)
        min_denominator: 最小概率倒数(如占所有可生成填空数的 1/7 中的 7, 若期望值小于 1, 则取 1)
    """

    def __init__(self, text: str, min_denominator: int, delimiter: str = "/"):
        logger.debug(
            "ClozePuzzle.__init__: text length=%d, min_denominator=%d, delimiter='%s'",
            len(text),
            min_denominator,
            delimiter,
        )
        self.text = text
        self.min_denominator = min_denominator
        self.wording = "填空题 - 尚未刷新谜题"
        self.answer = ["填空题 - 尚未刷新谜题"]
        self.delimiter = delimiter
        logger.debug("ClozePuzzle 初始化完成")

    def refresh(self):  # 刷新谜题
        logger.debug("ClozePuzzle.refresh 开始")
        placeholder = "___SLASH___"
        tmp_text = self.text.replace(self.delimiter, placeholder)
        words = tmp_text.split(placeholder)
        if not words:
            logger.warning("ClozePuzzle.refresh: 无单词可处理")
            return
        words = [word for word in words if word]
        logger.debug("ClozePuzzle.refresh: 分割出 %d 个单词", len(words))
        num_blanks = min(max(1, len(words) // self.min_denominator), len(words))
        logger.debug("ClozePuzzle.refresh: 需要生成 %d 个填空", num_blanks)
        indices_to_blank = random.sample(range(len(words)), num_blanks)
        indices_to_blank.sort()
        blanked_words = list(words)
        answer = list()
        for index in indices_to_blank:
            blanked_words[index] = "__" * len(words[index])
            answer.append(words[index])
        self.answer = answer
        self.wording = "".join(blanked_words)
        logger.debug("ClozePuzzle.refresh 完成, 生成 %d 个填空", len(answer))

    def __str__(self):
        logger.debug("ClozePuzzle.__str__ 被调用")
        return f"{self.wording}\n{str(self.answer)}"
