"""
Evaluator 模块 - 生成评估模块

提供多种类型的辅助评估生成器, 支持从字符串、字典等数据源导入题目
"""

from heurams.services.logger import get_logger

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
