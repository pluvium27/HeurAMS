# 音频播放器, 必须基于文件操作
from heurams.services.logger import get_logger

from . import playsound_audio, termux_audio

logger = get_logger(__name__)

__all__ = [
    "termux_audio",
    "playsound_audio",
]

providers = {"termux": termux_audio, "playsound": playsound_audio}
logger.debug("Audio providers registered: %s", list(providers.keys()))
