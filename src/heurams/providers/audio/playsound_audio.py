"""通用音频适配器
基于 playsound3 的音频播放器, 在绝大多数 python 环境上提供音频服务
注意: 在 termux 不可用
"""

import pathlib

from heurams.services.logger import get_logger

logger = get_logger(__name__)


def play_by_path(path: pathlib.Path):
    logger.debug("playsound_audio.play_by_path: playing %s", path)
    try:
        import playsound3
        playsound3.playsound(str(path))
        logger.debug("Audio playing finished: %s", path)
    except Exception as e:
        logger.error("Failed to play: %s, error: %s", path, e)
