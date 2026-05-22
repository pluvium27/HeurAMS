"""文本转语音服务
"""
from typing import Callable

from heurams.context import config_var
from heurams.providers.tts import providers as prov
from heurams.services.logger import get_logger

logger = get_logger(__name__)

convertor: Callable = prov[config_var.get()["services"]["tts"]["provider"]].convert
logger.info(
    "TTS Service inited, using provider: %s",
    config_var.get()["services"]["tts"]["provider"],
)
