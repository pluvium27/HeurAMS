from typing import TypedDict

import heurams.services.timer as timer
from heurams.services.logger import get_logger

from .base import BaseAlgorithm

logger = get_logger(__name__)


class NSP0Algorithm(BaseAlgorithm):
    algo_name = "NSP-0"
    desc = "快速筛选用特殊调度器"

    class AlgodataDict(TypedDict):
        real_rept: int
        rept: int
        interval: int
        important: int
        last_date: int
        next_date: int
        is_activated: int
        last_modify: float

    defaults = {
        "real_rept": 0,
        "important": 0,
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
    ):
        """NSP-0 算法迭代决策机制实现
        根据 quality(0 ~ 5) 进行参数迭代最佳间隔
        quality 由主程序评估

        Args:
            quality (int): 记忆保留率量化参数
        """
        logger.debug(
            "NSP0.revisor 开始, feedback: %d, is_new_activation: %s",
            feedback,
            is_new_activation,
        )

        if feedback == -1:
            logger.debug("feedback 为 -1, 跳过更新")
            return
        algodata[cls.algo_name]["interval"] = 1 if feedback <= 3 else float("inf")
        if not algodata[cls.algo_name]["important"]:
            algodata[cls.algo_name]["important"] = (
                1 if feedback <= 3 else algodata[cls.algo_name]["important"]
            )
        algodata[cls.algo_name]["last_date"] = timer.get_daystamp()
        algodata[cls.algo_name]["next_date"] = (
            timer.get_daystamp() + algodata[cls.algo_name]["interval"]
        )
        algodata[cls.algo_name]["last_modify"] = timer.get_timestamp()

        logger.debug(
            "更新日期: last_date=%d, next_date=%d, last_modify=%f",
            algodata[cls.algo_name]["last_date"],
            algodata[cls.algo_name]["next_date"],
            algodata[cls.algo_name]["last_modify"],
        )

    @classmethod
    def is_due(cls, algodata):
        result = algodata[cls.algo_name]["next_date"] <= timer.get_daystamp()
        logger.debug(
            "NSP0.is_due: next_date=%d, current_daystamp=%d, result=%s",
            algodata[cls.algo_name]["next_date"],
            timer.get_daystamp(),
            result,
        )
        return result

    @classmethod
    def get_rating(cls, algodata):
        efactor = algodata[cls.algo_name]["efactor"]
        logger.debug("NSP0.rate: efactor=%f", efactor)
        return str(efactor)

    @classmethod
    def nextdate(cls, algodata) -> int:
        next_date = algodata[cls.algo_name]["next_date"]
        logger.debug("NSP0.nextdate: %d", next_date)
        return next_date
