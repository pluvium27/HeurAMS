"""通用音频适配器
基于 playsound 库的音频播放器, 在绝大多数 python 环境上提供音频服务
注意: 在未配置 pulseaudio 的 termux 不可用
"""

import os
import pathlib

import playsound

from heurams.services.logger import get_logger

logger = get_logger(__name__)


def play_by_path(path: pathlib.Path):
    logger.debug("playsound_audio.play_by_path: 开始播放 %s", path)
    try:
        playsound.playsound(str(path))
        logger.debug("播放完成: %s", path)
    except Exception as e:
        logger.error("播放失败: %s, 错误: %s", path, e)
        raise
