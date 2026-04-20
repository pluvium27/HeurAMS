# 文本转语音服务
from typing import Callable

from heurams.context import config_var
from heurams.providers.tts import providers as prov
from heurams.services.logger import get_logger

logger = get_logger(__name__)

convertor: Callable = prov[config_var.get()["services"]["tts"]["provider"]].convert
logger.debug(
    "TTS 服务初始化完成, 使用 provider: %s",
    config_var.get()["services"]["tts"]["provider"],
)
