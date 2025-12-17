# base.py
from heurams.services.logger import get_logger

logger = get_logger(__name__)


class BasePuzzle:
    """谜题基类"""

    def refresh(self):
        logger.debug("BasePuzzle.refresh 被调用（未实现）")
        raise NotImplementedError("谜题对象未实现 refresh 方法")

    def __str__(self):
        logger.debug("BasePuzzle.__str__ 被调用")
        return f"谜题: {type(self).__name__}"
