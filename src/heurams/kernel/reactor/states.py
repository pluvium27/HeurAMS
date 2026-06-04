"""状态枚举定义

定义反应器三层状态机的所有状态值. 
"""

from enum import Enum

from heurams.services.logger import get_logger

logger = get_logger(__name__)


class RouterState(Enum):
    """路由器状态: 全局复习阶段"""

    UNSURE = "unsure"
    QUICK_REVIEW = "quick_review"
    RECOGNITION = "recognition"
    FINAL_REVIEW = "final_review"
    FINISHED = "finished"


class ProcessionState(Enum):
    """队列状态: 单阶段进度"""

    ACTIVE = "active"
    FINISHED = "finished"


class ExpanderState(Enum):
    """展开器状态: 单原子调度模式"""

    EXAMMODE = "exammode"
    RETRONLY = "retronly"


logger.debug("状态枚举定义已加载")
