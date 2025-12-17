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
    logger.debug("termux_audio.play_by_path: 开始播放 %s", path)
    try:
        os.system(f"play-audio {path}")
        logger.debug("播放命令已执行: %s", path)
    except Exception as e:
        logger.error("播放失败: %s, 错误: %s", path, e)
        raise
