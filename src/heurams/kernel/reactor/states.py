from enum import Enum

from heurams.services.logger import get_logger

logger = get_logger(__name__)


class RouterState(Enum):
    UNSURE = "unsure"
    QUICK_REVIEW = "quick_review"
    RECOGNITION = "recognition"
    FINAL_REVIEW = "final_review"
    FINISHED = "finished"


class ProcessionState(Enum):
    ACTIVE = "active"
    FINISHED = "finished"


class ExpanderState(Enum):
    EXAMMODE = "exammode"
    RETRONLY = "retronly"