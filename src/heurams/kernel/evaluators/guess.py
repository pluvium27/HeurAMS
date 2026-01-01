import random

from heurams.services.logger import get_logger

from .base import BaseEvaluator

logger = get_logger(__name__)


class GuessEvaluator(BaseEvaluator):
    def __init__(self):
        super().__init__()
