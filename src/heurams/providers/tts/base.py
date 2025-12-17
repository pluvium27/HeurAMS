import pathlib
from heurams.services.logger import get_logger

logger = get_logger(__name__)


class BaseTTS:
    name = "BaseTTS"

    @classmethod
    def convert(cls, text: str, path: pathlib.Path | str = "") -> pathlib.Path:
        """path 是可选参数, 不填则自动返回生成文件路径"""
        logger.debug("BaseTTS.convert: text length=%d, path=%s", len(text), path)
        logger.warning("BaseTTS.convert 是基类方法, 未实现具体功能")
        return path  # type: ignore
