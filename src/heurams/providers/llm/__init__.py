# 大语言模型
from heurams.services.logger import get_logger

from .base import BaseLLM
from .openai import OpenAILLM

logger = get_logger(__name__)

__all__ = [
    "BaseLLM",
    "OpenAILLM",
]

providers = {
    "base": BaseLLM,
    "openai": OpenAILLM,
}

logger.debug("LLM providers registered: %s", list(providers.keys()))
