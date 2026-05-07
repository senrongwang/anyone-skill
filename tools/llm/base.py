"""LLM 客户端抽象基类"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, List, Dict, Generator


@dataclass
class LLMResponse:
    """LLM 响应"""
    content: str
    model: str
    provider: str
    usage: Optional[Dict[str, int]] = None
    finish_reason: Optional[str] = None


@dataclass
class Message:
    """对话消息"""
    role: str  # system, user, assistant
    content: str


class BaseLLMClient(ABC):
    """LLM 客户端抽象基类"""
    
    def __init__(self, config):
        self.config = config
        self.provider = config.provider
        self.model = config.model
    
    @abstractmethod
    def chat(self, messages: List[Message], **kwargs) -> LLMResponse:
        """发送对话请求
        
        Args:
            messages: 消息列表
            **kwargs: 额外参数（temperature, max_tokens 等）
        
        Returns:
            LLMResponse 对象
        """
        pass
    
    @abstractmethod
    def chat_stream(self, messages: List[Message], **kwargs) -> Generator[str, None, None]:
        """流式对话请求
        
        Args:
            messages: 消息列表
            **kwargs: 额外参数
        
        Yields:
            生成的文本片段
        """
        pass
    
    def get_model_name(self) -> str:
        """获取模型名称"""
        return f"{self.provider}/{self.model}"
