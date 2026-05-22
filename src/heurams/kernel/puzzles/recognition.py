# mcq.py

from heurams.services.logger import get_logger

from .base import BasePuzzle

logger = get_logger(__name__)


class RecognitionPuzzle(BasePuzzle):
    """识别占位符"""

    def __init__(self) -> None:
        super().__init__()

    def refresh(self):
        pass
