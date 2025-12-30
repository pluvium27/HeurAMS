# mcq.py
import random

from heurams.services.logger import get_logger

from .base import BaseEvaluator

logger = get_logger(__name__)


class RecognitionPuzzle(BaseEvaluator):
    """识别占位符"""

    def __init__(self) -> None:
        logger.debug("RecognitionPuzzle.__init__")
        super().__init__()

    def refresh(self):
        logger.debug("RecognitionPuzzle.refresh(空实现)")
        pass
