"""LLM 提供者基类"""

import asyncio
from typing import Any, Dict, List, Optional

from heurams.services.logger import get_logger

logger = get_logger(__name__)


class BaseLLM:
    """LLM 提供者基类"""

    name = "BaseLLM"

    def __init__(self, config: Dict[str, Any]):
        """初始化 LLM 提供者

        Args:
            config: 提供者配置字典
        """
        self.config = config
        logger.debug("BaseLLM 初始化完成")

    async def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """发送聊天消息并获取响应

        Args:
            messages: 消息列表，每个消息为 {"role": "user"|"assistant"|"system", "content": "消息内容"}
            **kwargs: 其他参数，如 temperature, max_tokens 等

        Returns:
            模型返回的文本响应
        """
        logger.debug("BaseLLM.chat: messages=%d, kwargs=%s", len(messages), kwargs)
        logger.warning("BaseLLM.chat 是基类方法，未实现具体功能")
        await asyncio.sleep(0)  # 避免未使用异步的警告
        return "BaseLLM 未实现具体功能"

    async def chat_stream(self, messages: List[Dict[str, str]], **kwargs):
        """流式聊天（可选实现）

        Args:
            messages: 消息列表
            **kwargs: 其他参数

        Yields:
            流式响应的文本块
        """
        logger.debug(
            "BaseLLM.chat_stream: messages=%d, kwargs=%s", len(messages), kwargs
        )
        logger.warning("BaseLLM.chat_stream 是基类方法，未实现具体功能")
        await asyncio.sleep(0)
        yield "BaseLLM 未实现流式功能"
