from heurams.services.logger import get_logger

from .base import BaseTTS
from .edge_tts import EdgeTTS

logger = get_logger(__name__)

__all__ = [
    "BaseTTS",
    "EdgeTTS",
]

providers = {
    "basetts": BaseTTS,
    "edgetts": EdgeTTS,
}

logger.debug("TTS providers registered: %s", list(providers.keys()))
