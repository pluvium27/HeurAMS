import pathlib

import edge_tts

from heurams.services.logger import get_logger

from .base import BaseTTS

logger = get_logger(__name__)


class EdgeTTS(BaseTTS):
    name = "EdgeTTS"

    @classmethod
    def convert(cls, text, path: pathlib.Path | str = "") -> pathlib.Path:
        logger.debug("EdgeTTS.convert: text length=%d, path=%s", len(text), path)
        try:
            communicate = edge_tts.Communicate(
                text,
                "zh-CN-YunjianNeural",
            )
            logger.debug("EdgeTTS 通信对象创建成功, 正在保存音频")
            communicate.save_sync(str(path))
            logger.debug("EdgeTTS 音频已保存到: %s", path)
            return path  # type: ignore
        except Exception as e:
            logger.error("EdgeTTS.convert 失败: %s", e)
            raise
