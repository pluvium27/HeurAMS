from typing import TypedDict

import heurams.services.timer as timer
from heurams.services.logger import get_logger

from .base import BaseAlgorithm

logger = get_logger(__name__)


class SM2Algorithm(BaseAlgorithm):
    """SuperMemo-2 算法实现

    经典间隔重复算法, 基于 1987 年 Piotr Wozniak 设计的 SM-2. 
    通过维护 efactor (难度因子) 来调整复习间隔. 

    Attributes:
        algo_name: "SM-2"
        desc: SuperMemo2 (1987) 简单间隔重复调度器
    """

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

        根据 feedback (0-5) 更新 efactor 并计算下次复习间隔. 

        Args:
            algodata: 算法数据字典
            feedback: 记忆保留率量化参数 (0-5), -1 表示跳过
            is_new_activation: 是否为首次激活
        """
        logger.debug(
            "SM2.revisor 开始, feedback: %d, is_new_activation: %s",
            feedback,
            is_new_activation,
        )

        if feedback == -1:
            logger.debug("feedback 为 -1, 跳过更新")
            return

        algodata[cls.algo_name]["efactor"] = algodata[cls.algo_name]["efactor"] + (
            0.1 - (5 - feedback) * (0.08 + (5 - feedback) * 0.02)
        )
        algodata[cls.algo_name]["efactor"] = max(
            1.3, algodata[cls.algo_name]["efactor"]
        )
        logger.debug("更新 efactor: %f", algodata[cls.algo_name]["efactor"])

        if feedback < 3:
            algodata[cls.algo_name]["rept"] = 0
            algodata[cls.algo_name]["interval"] = 0
            logger.debug("feedback < 3, 重置 rept 和 interval")
        else:
            algodata[cls.algo_name]["rept"] += 1
            logger.debug("递增 rept: %d", algodata[cls.algo_name]["rept"])

        algodata[cls.algo_name]["real_rept"] += 1
        logger.debug("递增 real_rept: %d", algodata[cls.algo_name]["real_rept"])

        if is_new_activation:
            algodata[cls.algo_name]["rept"] = 0
            algodata[cls.algo_name]["efactor"] = 2.5
            logger.debug("新激活, 重置 rept 和 efactor")

        if algodata[cls.algo_name]["rept"] == 0:
            algodata[cls.algo_name]["interval"] = 1
            logger.debug("rept=0, 设置 interval=1")
        elif algodata[cls.algo_name]["rept"] == 1:
            algodata[cls.algo_name]["interval"] = 6
            logger.debug("rept=1, 设置 interval=6")
        else:
            algodata[cls.algo_name]["interval"] = round(
                algodata[cls.algo_name]["interval"] * algodata[cls.algo_name]["efactor"]
            )
            logger.debug(
                "rept>1, 计算 interval: %d", algodata[cls.algo_name]["interval"]
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
        """判断是否应该复习

        Args:
            algodata: 算法数据字典

        Returns:
            True 表示到期, False 表示未到期
        """
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
        """获取当前 efactor 作为评分信息

        Args:
            algodata: 算法数据字典

        Returns:
            efactor 值的字符串表示
        """
        efactor = algodata[cls.algo_name]["efactor"]
        logger.debug("SM2.rate: efactor=%f", efactor)
        return str(efactor)

    @classmethod
    def nextdate(cls, algodata) -> int:
        """获取下一次复习日期

        Args:
            algodata: 算法数据字典

        Returns:
            下次复习的天数戳
        """
        next_date = algodata[cls.algo_name]["next_date"]
        logger.debug("SM2.nextdate: %d", next_date)
        return next_date
