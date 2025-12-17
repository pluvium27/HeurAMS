from typing import Protocol
import pathlib
from heurams.services.logger import get_logger

logger = get_logger(__name__)


class PlayFunctionProtocol(Protocol):
    def __call__(self, path: pathlib.Path) -> None: ...


logger.debug("音频协议模块已加载")
