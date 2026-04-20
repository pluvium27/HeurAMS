# 时间服务
import time

from heurams.context import config_var
from heurams.services.logger import get_logger

logger = get_logger(__name__)


def get_daystamp() -> int:
    """获取当前日戳(以天为单位的整数时间戳)"""
    time_override = config_var.get()["services"]["timer"]["daystamp_override"]
    if time_override != -1:
        logger.debug("使用覆盖的日戳: %d", time_override)
        return int(time_override)

    result = int(
        (time.time() + config_var.get()["services"]["timer"]["timezone_offset"])
        // (24 * 3600)
    )
    logger.debug("计算日戳: %d", result)
    return result


def get_timestamp() -> float:
    """获取 UNIX 时间戳"""
    # 搞这个类的原因是要支持可复现操作
    time_override = config_var.get()["services"]["timer"]["timestamp_override"]
    if time_override != -1:
        logger.debug("使用覆盖的时间戳: %f", time_override)
        return float(time_override)

    result = time.time()
    logger.debug("获取当前时间戳: %f", result)
    return result
