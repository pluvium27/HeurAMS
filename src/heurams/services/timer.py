# 时间服务
import datetime
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
    # 搞这个函数的原因是要支持可复现操作
    time_override = config_var.get()["services"]["timer"]["timestamp_override"]
    if time_override != -1:
        logger.debug("使用覆盖的时间戳: %f", time_override)
        return float(time_override)

    result = time.time()
    logger.debug("获取当前时间戳: %f", result)
    return result


def get_timestamp_ms() -> int:
    """获取当前毫秒级 Unix 时间戳"""
    return int(get_timestamp() * 1000)


def daystamp_to_datetime(daystamp: int) -> datetime.datetime:
    """将日戳转换为 UTC datetime (当日午夜)"""
    return datetime.datetime(1970, 1, 1, tzinfo=datetime.timezone.utc) + datetime.timedelta(
        days=daystamp
    )


def datetime_to_daystamp(dt: datetime.datetime) -> int:
    """将 datetime 转换为日戳（从 1970-01-01 起的天数）

    接受带时区或 naive 的 datetime（naive 视为 UTC）。
    """
    epoch = datetime.datetime(1970, 1, 1, tzinfo=datetime.timezone.utc)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=datetime.timezone.utc)
    delta = dt - epoch
    return delta.days


def get_now_datetime() -> datetime.datetime:
    """获取当前时间的 UTC datetime（遵守时间覆盖）"""
    return datetime.datetime.fromtimestamp(get_timestamp(), tz=datetime.timezone.utc)
