"""音频服务"""

from typing import Callable

from heurams.context import config_var
from heurams.providers.audio import providers as prov
from heurams.services.logger import get_logger

logger = get_logger(__name__)

play_by_path: Callable = prov[
    config_var.get()["services"]["audio"]["provider"]
].play_by_path
logger.info(
    "TTS Service inited, using provider %s",
    config_var.get()["services"]["audio"]["provider"],
)
