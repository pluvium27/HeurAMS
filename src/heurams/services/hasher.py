# 哈希服务
import hashlib
from heurams.services.logger import get_logger

logger = get_logger(__name__)


def get_md5(text):
    logger.debug(f"计算哈希, 输入`{text}`")
    result = hashlib.md5(text.encode("utf-8")).hexdigest()
    logger.debug("哈希结果: %s...", result[:8])
    return result


def hash(text):
    logger.debug(f"计算哈希, 输入`{text}`")
    result = hashlib.md5(text.encode("utf-8")).hexdigest()
    logger.debug("哈希结果: %s...", result[:8])
    return result
