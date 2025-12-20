from heurams.services.logger import get_logger

from .sm2 import SM2Algorithm
from .sm15m import SM15MAlgorithm

logger = get_logger(__name__)

__all__ = [
    "SM2Algorithm",
]

algorithms = {
    "SM-2": SM2Algorithm,
    "SM-15M": SM15MAlgorithm,
    # "SM-15M": SM15MAlgorithm,
}

logger.debug("算法模块初始化完成, 注册的算法: %s", list(algorithms.keys()))
