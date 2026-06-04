from typing import TypedDict

import heurams.services.timer as timer
from heurams.services.logger import get_logger

from .base import BaseAlgorithm

logger = get_logger(__name__)


class NSP0Algorithm(BaseAlgorithm):
    """NSP-0 非间隔重复调度器

    快速筛选用算法, 对低分项目保持每日复习, 高分项目标记为已掌握. 
    适用于需要快速过滤大量材料的场景. 

    Attributes:
        algo_name: "NSP-0"
        desc: 快速筛选用非间隔重复调度器
    """

    algo_name = "NSP-0"
    desc = "快速筛选用非间隔重复调度器"

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

        低分 (feedback<=3) 设置间隔为 1 天, 高分标记为已掌握 (间隔无限). 

        Args:
            algodata: 算法数据字典
            feedback: 记忆保留率量化参数 (0-5), -1 表示跳过
            is_new_activation: 是否为首次激活
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
        """判断是否应该复习

        Args:
            algodata: 算法数据字典

        Returns:
            True 表示到期, False 表示未到期
        """
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
        """获取当前 important 标记作为评分信息

        Args:
            algodata: 算法数据字典

        Returns:
            important 值的字符串表示
        """
        important = algodata[cls.algo_name]["important"]
        logger.debug("NSP0.rate: important=%d", important)
        return str(important)

    @classmethod
    def nextdate(cls, algodata) -> int:
        """获取下一次复习日期

        Args:
            algodata: 算法数据字典

        Returns:
            下次复习的天数戳
        """
        next_date = algodata[cls.algo_name]["next_date"]
        logger.debug("NSP0.nextdate: %d", next_date)
        return next_date
