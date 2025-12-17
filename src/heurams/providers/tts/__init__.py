from .base import BaseTTS
from .edge_tts import EdgeTTS
from heurams.services.logger import get_logger

logger = get_logger(__name__)

__all__ = [
    "BaseTTS",
    "EdgeTTS",
]

providers = {
    "basetts": BaseTTS,
    "edgetts": EdgeTTS,
}

logger.debug("TTS providers 已注册: %s", list(providers.keys()))
