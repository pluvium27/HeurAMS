# 哈希服务
import hashlib
from heurams.services.logger import get_logger

logger = get_logger(__name__)


def get_md5(text):
    logger.debug(f"MD5 hash input`{text}`")
    result = hashlib.md5(text.encode("utf-8")).hexdigest()
    logger.debug("Providing MD5 hash: %s...", result[:8])
    return result


def hash(text):
    return get_md5(text)
