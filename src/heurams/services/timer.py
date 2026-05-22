"""时间服务
"""
import datetime
import time

from heurams.context import config_var
from heurams.services.logger import get_logger

logger = get_logger(__name__)

daystamp_override = config_var.get()["services"]["timer"]["daystamp_override"]
timestamp_override = config_var.get()["services"]["timer"]["timestamp_override"]
last_daystamp = 0
last_timestamp = 0

def get_daystamp() -> int:
    """获取当前日戳(以天为单位的整数时间戳)"""
    if daystamp_override != -1:
        logger.debug("Daystamp overrode: %d", daystamp_override)
        return int(daystamp_override)

    result = int(
        (time.time() + config_var.get()["services"]["timer"]["timezone_offset"])
        // (24 * 3600)
    )
    global last_daystamp
    if last_daystamp != result: # 用于避免日志泛洪
        logger.debug("Providing new daystamp: %d", result)
        last_daystamp = result
    return result


def get_timestamp() -> float:
    """获取 UNIX 时间戳"""
    # 搞这个函数的原因是要支持可复现操作
    if timestamp_override != -1:
        logger.debug("Timestamp overrode: %f", timestamp_override)
        return float(timestamp_override)

    result = time.time()
    global last_timestamp
    if last_timestamp != result:
        logger.debug("Providing new timestamp: %d", result)
        last_timestamp = result
    return result


def get_timestamp_ms() -> int:
    """获取当前毫秒级 Unix 时间戳"""
    return int(get_timestamp() * 1000)


def daystamp_to_datetime(daystamp: int) -> datetime.datetime:
    """将日戳转换为 UTC datetime (当日午夜)"""
    return datetime.datetime(
        1970, 1, 1, tzinfo=datetime.timezone.utc
    ) + datetime.timedelta(days=daystamp)


def datetime_to_daystamp(dt: datetime.datetime) -> int:
    """将 datetime 转换为日戳 (从 1970-01-01 起的天数)

    接受带时区或 naive 的 datetime (naive 视为 UTC)
    """
    epoch = datetime.datetime(1970, 1, 1, tzinfo=datetime.timezone.utc)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=datetime.timezone.utc)
    delta = dt - epoch
    return delta.days


def get_now_datetime() -> datetime.datetime:
    """获取当前时间的 UTC datetime (遵守时间覆盖)"""
    return datetime.datetime.fromtimestamp(get_timestamp(), tz=datetime.timezone.utc)
