"""
Evaluator 模块 - 生成评估模块

提供多种类型的辅助评估生成器, 支持从字符串、字典等数据源导入题目
"""

from heurams.services.logger import get_logger

logger = get_logger(__name__)

from .base import BaseEvaluator
from .cloze import ClozePuzzle
from .mcq import MCQPuzzle
from .recognition import RecognitionPuzzle

__all__ = [
    "BaseEvaluator",
    "ClozePuzzle",
    "MCQPuzzle",
    "RecognitionPuzzle",
]

puzzles = {
    "mcq": MCQPuzzle,
    "cloze": ClozePuzzle,
    "recognition": RecognitionPuzzle,
    "base": BaseEvaluator,
}


@staticmethod
def create_by_dict(config_dict: dict) -> BaseEvaluator:
    """
    根据配置字典创建谜题

    Args:
        config_dict: 配置字典, 包含谜题类型和参数

    Returns:
        BasePuzzle: 谜题实例

    Raises:
        ValueError: 当配置无效时抛出
    """
    logger.debug(
        "puzzles.create_by_dict: config_dict keys=%s", list(config_dict.keys())
    )
    puzzle_type = config_dict.get("type")

    if puzzle_type == "cloze":
        return puzzles["cloze"](
            text=config_dict["text"],
            min_denominator=config_dict.get("min_denominator", 7),
        )
    elif puzzle_type == "mcq":
        return puzzles["mcq"](
            mapping=config_dict["mapping"],
            jammer=config_dict.get("jammer", []),
            max_riddles_num=config_dict.get("max_riddles_num", 2),
            prefix=config_dict.get("prefix", ""),
        )
    else:
        raise ValueError(f"未知的谜题类型: {puzzle_type}")
