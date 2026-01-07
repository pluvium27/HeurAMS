"""OpenAI 兼容 LLM 提供者"""

import asyncio
from typing import Any, AsyncGenerator, Dict, List, Optional

from heurams.services.logger import get_logger

from .base import BaseLLM

logger = get_logger(__name__)


class OpenAILLM(BaseLLM):
    """OpenAI 兼容 LLM 提供者"""

    name = "OpenAI"

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.api_key = config.get("key", "")
        self.base_url = config.get("url", "https://api.openai.com/v1")
        self._client = None
        logger.debug("OpenAILLM 初始化完成: base_url=%s", self.base_url)

    def _get_client(self):
        """获取 OpenAI 客户端（延迟导入）"""
        if self._client is None:
            try:
                from openai import AsyncOpenAI
            except ImportError:
                logger.error("未安装 openai 库，请运行: pip install openai")
                raise ImportError("未安装 openai 库，请运行: pip install openai")

            self._client = AsyncOpenAI(
                api_key=self.api_key if self.api_key else None,
                base_url=self.base_url if self.base_url else None,
            )
        return self._client

    async def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """发送聊天消息并获取响应"""
        logger.debug("OpenAILLM.chat: messages=%d", len(messages))

        client = self._get_client()

        # 默认参数
        default_kwargs = {
            "model": kwargs.get("model", "gpt-3.5-turbo"),
            "temperature": kwargs.get("temperature", 0.7),
            "max_tokens": kwargs.get("max_tokens", 1000),
        }

        # 合并参数，优先使用传入的 kwargs
        request_kwargs = {**default_kwargs, **kwargs}
        request_kwargs["messages"] = messages

        try:
            response = await client.chat.completions.create(**request_kwargs)
            content = response.choices[0].message.content
            logger.debug(
                "OpenAILLM.chat 成功: response length=%d",
                len(content) if content else 0,
            )
            return content or ""
        except Exception as e:
            logger.error("OpenAILLM.chat 失败: %s", e)
            raise

    async def chat_stream(
        self, messages: List[Dict[str, str]], **kwargs
    ) -> AsyncGenerator[str, None]:
        """流式聊天"""
        logger.debug("OpenAILLM.chat_stream: messages=%d", len(messages))

        client = self._get_client()

        # 默认参数
        default_kwargs = {
            "model": kwargs.get("model", "gpt-3.5-turbo"),
            "temperature": kwargs.get("temperature", 0.7),
            "max_tokens": kwargs.get("max_tokens", 1000),
            "stream": True,
        }

        # 合并参数
        request_kwargs = {**default_kwargs, **kwargs}
        request_kwargs["messages"] = messages

        try:
            stream = await client.chat.completions.create(**request_kwargs)
            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        except Exception as e:
            logger.error("OpenAILLM.chat_stream 失败: %s", e)
            raise
