# base.py
from heurams.services.logger import get_logger

logger = get_logger(__name__)


class BasePuzzle:
    """谜题基类"""

    def refresh(self):
        raise NotImplementedError("Method refresh not implemented")

    def __str__(self):
        return f"Puzzle: {type(self).__name__}"
