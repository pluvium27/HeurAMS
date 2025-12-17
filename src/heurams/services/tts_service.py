# 文本转语音服务
from heurams.context import config_var
from heurams.providers.tts import TTSs
from typing import Callable
from heurams.services.logger import get_logger

logger = get_logger(__name__)

convert: Callable = TTSs[config_var.get().get("tts_provider")]
logger.debug(
    "TTS服务初始化完成, 使用 provider: %s", config_var.get().get("tts_provider")
)
