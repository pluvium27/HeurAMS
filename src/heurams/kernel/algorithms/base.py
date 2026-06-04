from typing import TypedDict

import heurams.services.timer as timer
from heurams.services.logger import get_logger

logger = get_logger(__name__)

_registry: dict[str, type["BaseAlgorithm"]] = {}


class BaseAlgorithm:
    """间隔重复算法基类

    定义所有调度算法必须实现的接口. 子类通过继承此类并设置 algo_name
    自动注册到全局算法注册表. 

    Attributes:
        algo_name: 算法的唯一标识名称, 用于注册和查找
        desc: 算法的简短描述
        defaults: 算法数据字典的默认值模板
    """

    algo_name = "BaseAlgorithm"
    desc = "算法基类"

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        _registry[cls.algo_name] = cls

    @classmethod
    def get_registry(cls) -> dict[str, type["BaseAlgorithm"]]:
        """获取所有已注册算法的字典

        Returns:
            键为 algo_name, 值为算法类的字典
        """
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
        """迭代记忆数据

        根据用户反馈更新算法状态, 计算下一次复习时间. 

        Args:
            algodata: 算法数据字典, 包含该算法的所有状态参数
            feedback: 用户反馈评分 (0-5), -1 表示跳过更新
            is_new_activation: 是否为首次激活, 首次激活时重置部分参数
        """
        logger.debug(
            "BaseAlgorithm.revisor 被调用, algodata keys: %s, feedback: %d, is_new_activation: %s",
            list(algodata.keys()) if algodata else [],
            feedback,
            is_new_activation,
        )

    @classmethod
    def is_due(cls, algodata) -> int:
        """判断是否应该复习

        Args:
            algodata: 算法数据字典

        Returns:
            1 表示应该复习, 0 表示不需要
        """
        logger.debug(
            "BaseAlgorithm.is_due 被调用, algodata keys: %s",
            list(algodata.keys()) if algodata else [],
        )
        return 1

    @classmethod
    def get_rating(cls, algodata) -> str:
        """获取当前记忆状态的评分信息

        Args:
            algodata: 算法数据字典

        Returns:
            评分的字符串表示, 如 efactor 值
        """
        logger.debug(
            "BaseAlgorithm.rate 被调用, algodata keys: %s",
            list(algodata.keys()) if algodata else [],
        )
        return ""

    @classmethod
    def nextdate(cls, algodata) -> int:
        """获取下一次复习的时间戳

        Args:
            algodata: 算法数据字典

        Returns:
            下次复习的日期戳 (天数), -1 表示无计划
        """
        logger.debug(
            "BaseAlgorithm.nextdate 被调用, algodata keys: %s",
            list(algodata.keys()) if algodata else [],
        )
        return -1

    @classmethod
    def check_integrity(cls, algodata):
        """校验算法数据完整性

        Args:
            algodata: 算法数据字典

        Returns:
            1 表示数据完整, 0 表示数据缺失或格式错误
        """
        try:
            cls.AlgodataDict(**algodata[cls.algo_name])
            return 1
        except (KeyError, TypeError, ValueError):
            return 0
