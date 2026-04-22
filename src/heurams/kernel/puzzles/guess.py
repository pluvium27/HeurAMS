from heurams.services.logger import get_logger

from .base import BasePuzzle

logger = get_logger(__name__)


class GuessPuzzle(BasePuzzle):
    def __init__(self):
        super().__init__()
