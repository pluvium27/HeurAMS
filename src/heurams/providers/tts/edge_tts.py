import pathlib

import edge_tts

from heurams.context import config_var
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
                config_var.get()["providers"]["tts"]["edgetts"]["voice"],
            )
            logger.debug("EdgeTTS object created, saving audio")
            communicate.save_sync(str(path))
            logger.debug("EdgeTTS audio saved as %s", path)
            return path  # type: ignore
        except Exception as e:
            logger.error("EdgeTTS.convert failed: %s", e)
            raise
