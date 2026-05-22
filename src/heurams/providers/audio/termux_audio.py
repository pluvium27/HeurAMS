"""Termux 音频适配
适配 Termux 的 play-audio 命令, 以在 android 上提供可用的播放体验
无需配置 pulseaudio
"""

import os
import pathlib

from heurams.services.logger import get_logger

logger = get_logger(__name__)

# from .protocol import PlayFunctionProtocol

def play_by_path(path: pathlib.Path):
    logger.debug("termux_audio.play_by_path: playing %s", path)
    try:
        os.system(f"play-audio {path.resolve()}")
        logger.debug("Play audio: %s", path)
    except Exception as e:
        logger.error("Failed to play audio: %s, error: %s", path, e)
