# 哈希服务
import hashlib
from heurams.services.logger import get_logger

logger = get_logger(__name__)


def get_md5(text):
    logger.debug(f"计算MD5哈希, 输入`{text}`")
    result = hashlib.md5(text.encode("utf-8")).hexdigest()
    logger.debug("哈希结果: %s...", result[:8])
    return result


def hash(text):
    #logger.debug(f"计算MD5-时间复合哈希, 输入`{text}`")
    #result = hashlib.md5(f"{text}{random.randint(0,1000)}".encode("utf-8")).hexdigest()
    #logger.debug("哈希结果: %s...", result[:8])
    #return result
    return get_md5(text)