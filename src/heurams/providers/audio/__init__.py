# 音频播放器, 必须基于文件操作
from . import termux_audio
from . import playsound_audio
from heurams.services.logger import get_logger

logger = get_logger(__name__)

__all__ = [
    "termux_audio",
    "playsound_audio",
]

providers = {"termux": termux_audio, "playsound": playsound_audio}
logger.debug("音频 providers 已注册: %s", list(providers.keys()))
