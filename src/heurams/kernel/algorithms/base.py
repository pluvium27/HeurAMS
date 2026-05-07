from typing import TypedDict

import heurams.services.timer as timer
from heurams.services.logger import get_logger

logger = get_logger(__name__)

_registry: dict[str, type["BaseAlgorithm"]] = {}


class BaseAlgorithm:
    algo_name = "BaseAlgorithm"
    desc = "算法基类"

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        _registry[cls.algo_name] = cls

    @classmethod
    def get_registry(cls) -> dict[str, type["BaseAlgorithm"]]:
        return dict(_registry)

    class AlgodataDict(TypedDict):
        real_rept: int
        rept: int
        interval: int
        last_date: int
        next_date: int
        is_activated: int
        last_modify: float

    defaults = {
        "real_rept": 0,
        "rept": 0,
        "interval": 0,
        "last_date": 0,
        "next_date": 0,
        "is_activated": 0,
        "last_modify": timer.get_timestamp(),
    }

    @classmethod
    def revisor(
        cls, algodata: dict, feedback: int = 5, is_new_activation: bool = False
    ) -> None:
        """迭代记忆数据"""
        logger.debug(
            "BaseAlgorithm.revisor 被调用, algodata keys: %s, feedback: %d, is_new_activation: %s",
            list(algodata.keys()) if algodata else [],
            feedback,
            is_new_activation,
        )

    @classmethod
    def is_due(cls, algodata) -> int:
        """是否应该复习"""
        logger.debug(
            "BaseAlgorithm.is_due 被调用, algodata keys: %s",
            list(algodata.keys()) if algodata else [],
        )
        return 1

    @classmethod
    def get_rating(cls, algodata) -> str:
        """获取评分信息"""
        logger.debug(
            "BaseAlgorithm.rate 被调用, algodata keys: %s",
            list(algodata.keys()) if algodata else [],
        )
        return ""

    @classmethod
    def nextdate(cls, algodata) -> int:
        """获取下一次记忆时间戳"""
        logger.debug(
            "BaseAlgorithm.nextdate 被调用, algodata keys: %s",
            list(algodata.keys()) if algodata else [],
        )
        return -1

    @classmethod
    def check_integrity(cls, algodata):
        try:
            cls.AlgodataDict(**algodata[cls.algo_name])
            return 1
        except:
            return 0
