"""LLM 聊天服务"""

import asyncio
import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from heurams.context import config_var
from heurams.providers.llm import providers as prov
from heurams.services.logger import get_logger

logger = get_logger(__name__)


class ChatSession:
    """聊天会话，管理单个对话的历史和参数"""

    def __init__(
        self, session_id: str, llm_provider, system_prompt: str = "", **default_params
    ):
        """初始化聊天会话

        Args:
            session_id: 会话唯一标识符
            llm_provider: LLM 提供者实例
            system_prompt: 系统提示词
            **default_params: 默认参数（temperature, max_tokens, model 等）
        """
        self.session_id = session_id
        self.llm_provider = llm_provider
        self.system_prompt = system_prompt
        self.default_params = default_params

        # 消息历史
        self.messages: List[Dict[str, str]] = []
        if system_prompt:
            self.messages.append({"role": "system", "content": system_prompt})

        logger.debug("创建聊天会话: id=%s", session_id)

    def add_message(self, role: str, content: str):
        """添加消息到历史"""
        self.messages.append({"role": role, "content": content})
        logger.debug(
            "会话 %s 添加消息: role=%s, length=%d", self.session_id, role, len(content)
        )

    def clear_history(self):
        """清空消息历史（保留系统提示）"""
        self.messages = []
        if self.system_prompt:
            self.messages.append({"role": "system", "content": self.system_prompt})
        logger.debug("会话 %s 清空历史", self.session_id)

    def set_system_prompt(self, prompt: str):
        """设置系统提示词"""
        self.system_prompt = prompt
        # 更新消息历史中的系统消息
        if self.messages and self.messages[0]["role"] == "system":
            self.messages[0]["content"] = prompt
        elif prompt:
            self.messages.insert(0, {"role": "system", "content": prompt})
        logger.debug("会话 %s 设置系统提示: length=%d", self.session_id, len(prompt))

    async def send_message(self, message: str, **override_params) -> str:
        """发送消息并获取响应

        Args:
            message: 用户消息内容
            **override_params: 覆盖默认参数

        Returns:
            模型响应内容
        """
        # 添加用户消息
        self.add_message("user", message)

        # 合并参数
        params = {**self.default_params, **override_params}

        # 发送请求
        logger.debug("会话 %s 发送消息: length=%d", self.session_id, len(message))
        response = await self.llm_provider.chat(self.messages, **params)

        # 添加助手响应
        self.add_message("assistant", response)

        return response

    async def send_message_stream(self, message: str, **override_params):
        """流式发送消息

        Args:
            message: 用户消息内容
            **override_params: 覆盖默认参数

        Yields:
            流式响应的文本块
        """
        # 添加用户消息
        self.add_message("user", message)

        # 合并参数
        params = {**self.default_params, **override_params}

        # 发送流式请求
        logger.debug("会话 %s 发送流式消息: length=%d", self.session_id, len(message))

        full_response = ""
        async for chunk in self.llm_provider.chat_stream(self.messages, **params):
            yield chunk
            full_response += chunk

        # 添加完整的助手响应到历史
        self.add_message("assistant", full_response)

    def get_history(self) -> List[Dict[str, str]]:
        """获取消息历史（不包括系统消息）"""
        # 返回用户和助手的消息，可选排除系统消息
        return [msg for msg in self.messages if msg["role"] != "system"]

    def save_to_file(self, file_path: Path):
        """保存会话到文件"""
        data = {
            "session_id": self.session_id,
            "system_prompt": self.system_prompt,
            "default_params": self.default_params,
            "messages": self.messages,
        }
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        logger.debug("会话 %s 保存到: %s", self.session_id, file_path)

    @classmethod
    def load_from_file(cls, file_path: Path, llm_provider):
        """从文件加载会话"""
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        session = cls(
            session_id=data["session_id"],
            llm_provider=llm_provider,
            system_prompt=data.get("system_prompt", ""),
            **data.get("default_params", {})
        )
        session.messages = data["messages"]
        logger.debug("从文件加载会话: %s", file_path)
        return session


class ChatManager:
    """聊天管理器，管理多个会话"""

    def __init__(self):
        self.sessions: Dict[str, ChatSession] = {}
        self.default_session_id = "default"
        logger.debug("聊天管理器初始化完成")

    def get_session(
        self,
        session_id: Optional[str] = None,
        create_if_missing: bool = True,
        **session_params
    ) -> Optional[ChatSession]:
        """获取或创建聊天会话

        Args:
            session_id: 会话标识符，None 则使用默认会话
            create_if_missing: 如果会话不存在则创建
            **session_params: 传递给 ChatSession 的参数

        Returns:
            聊天会话实例，如果不存在且不创建则返回 None
        """
        if session_id is None:
            session_id = self.default_session_id

        if session_id in self.sessions:
            return self.sessions[session_id]

        if create_if_missing:
            # 获取 LLM 提供者
            provider_name = config_var.get()["services"]["llm"]
            provider_config = config_var.get()["providers"]["llm"][provider_name]
            llm_provider = prov[provider_name](provider_config)

            session = ChatSession(
                session_id=session_id, llm_provider=llm_provider, **session_params
            )
            self.sessions[session_id] = session
            logger.debug("创建新会话: id=%s", session_id)
            return session

        return None

    def delete_session(self, session_id: str):
        """删除会话"""
        if session_id in self.sessions:
            del self.sessions[session_id]
            logger.debug("删除会话: id=%s", session_id)

    def list_sessions(self) -> List[str]:
        """列出所有会话ID"""
        return list(self.sessions.keys())


# 全局聊天管理器实例
_chat_manager: Optional[ChatManager] = None


def get_chat_manager() -> ChatManager:
    """获取全局聊天管理器实例"""
    global _chat_manager
    if _chat_manager is None:
        _chat_manager = ChatManager()
        logger.debug("创建全局聊天管理器")
    return _chat_manager


def create_chat_session(
    session_id: Optional[str] = None, **session_params
) -> ChatSession:
    """创建或获取聊天会话（便捷函数）"""
    manager = get_chat_manager()
    return manager.get_session(session_id, True, **session_params)


logger.debug("LLM 服务初始化完成")
