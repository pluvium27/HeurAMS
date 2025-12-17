from enum import Enum, auto
from heurams.services.logger import get_logger

logger = get_logger(__name__)


class PhaserState(Enum):
    UNSURE = "unsure"
    QUICK_REVIEW = "quick_review"
    RECOGNITION = "recognition"
    FINAL_REVIEW = "final_review"
    FINISHED = "finished"


class ProcessionState(Enum):
    RUNNING = auto()
    FINISHED = auto()


logger.debug("状态枚举定义已加载")
