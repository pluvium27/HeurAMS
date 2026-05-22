from typing import TypedDict

import heurams.services.timer as timer
from heurams.services.logger import get_logger

from .base import BaseAlgorithm

logger = get_logger(__name__)


class SM2Algorithm(BaseAlgorithm):
    algo_name = "SM-2"
    desc = "SuperMemo2 (1987) 简单间隔重复调度器"

    class AlgodataDict(TypedDict):
        efactor: float
        real_rept: int
        rept: int
        interval: int
        last_date: int
        next_date: int
        is_activated: int
        last_modify: float

    defaults = {
        "efactor": 2.5,
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
    ):
        """SM-2 算法迭代决策机制实现
        根据 quality(0 ~ 5) 进行参数迭代最佳间隔
        quality 由主程序评估

        Args:
            quality (int): 记忆保留率量化参数
        """
        logger.debug(
            "SM2.revisor, feedback: %d, is_new_activation: %s",
            feedback,
            is_new_activation,
        )

        if feedback == -1:
            logger.debug("feedback = -1, update skipped")
            return

        algodata[cls.algo_name]["efactor"] = algodata[cls.algo_name]["efactor"] + (
            0.1 - (5 - feedback) * (0.08 + (5 - feedback) * 0.02)
        )
        algodata[cls.algo_name]["efactor"] = max(
            1.3, algodata[cls.algo_name]["efactor"]
        )
        logger.debug("Update efactor: %f", algodata[cls.algo_name]["efactor"])

        if feedback < 3:
            algodata[cls.algo_name]["rept"] = 0
            algodata[cls.algo_name]["interval"] = 0
            logger.debug("feedback < 3, 重置 rept 和 interval")
        else:
            algodata[cls.algo_name]["rept"] += 1
            logger.debug("Increase rept: %d", algodata[cls.algo_name]["rept"])

        algodata[cls.algo_name]["real_rept"] += 1
        logger.debug("Increase real_rept: %d", algodata[cls.algo_name]["real_rept"])

        if is_new_activation:
            algodata[cls.algo_name]["rept"] = 0
            algodata[cls.algo_name]["efactor"] = 2.5
            logger.debug("New activation, reset rept and efactor")

        if algodata[cls.algo_name]["rept"] == 0:
            algodata[cls.algo_name]["interval"] = 1
            logger.debug("rept=0, set interval=1")
        elif algodata[cls.algo_name]["rept"] == 1:
            algodata[cls.algo_name]["interval"] = 6
            logger.debug("rept=1, set interval=6")
        else:
            algodata[cls.algo_name]["interval"] = round(
                algodata[cls.algo_name]["interval"] * algodata[cls.algo_name]["efactor"]
            )
            logger.debug(
                "rept>1, providing interval: %d", algodata[cls.algo_name]["interval"]
            )

        algodata[cls.algo_name]["last_date"] = timer.get_daystamp()
        algodata[cls.algo_name]["next_date"] = (
            timer.get_daystamp() + algodata[cls.algo_name]["interval"]
        )
        algodata[cls.algo_name]["last_modify"] = timer.get_timestamp()

        logger.debug(
            "Update date: last_date=%d, next_date=%d, last_modify=%f",
            algodata[cls.algo_name]["last_date"],
            algodata[cls.algo_name]["next_date"],
            algodata[cls.algo_name]["last_modify"],
        )

    @classmethod
    def is_due(cls, algodata):
        result = algodata[cls.algo_name]["next_date"] <= timer.get_daystamp()
        logger.debug(
            "SM2.is_due: next_date=%d, current_daystamp=%d, result=%s",
            algodata[cls.algo_name]["next_date"],
            timer.get_daystamp(),
            result,
        )
        return result

    @classmethod
    def get_rating(cls, algodata):
        efactor = algodata[cls.algo_name]["efactor"]
        logger.debug("SM2.rate: efactor=%f", efactor)
        return str(efactor)

    @classmethod
    def nextdate(cls, algodata) -> int:
        next_date = algodata[cls.algo_name]["next_date"]
        logger.debug("SM2.nextdate: %d", next_date)
        return next_date
