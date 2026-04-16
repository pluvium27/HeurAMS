"""音频服务"""
from typing import Callable

from heurams.context import config_var
from heurams.providers.audio import providers as prov
from heurams.services.logger import get_logger

logger = get_logger(__name__)

play_by_path: Callable = prov[config_var.get()["services"]["audio"]].play_by_path
logger.debug(
    "音频服务初始化完成, 使用 Provider: %s", config_var.get()["services"]["audio"]
)
