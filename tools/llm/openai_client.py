"""OpenAI API 客户端"""

from typing import List, Generator
import os

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

from .base import BaseLLMClient, LLMResponse, Message


class OpenAIClient(BaseLLMClient):
    """OpenAI API 客户端
    
    支持 OpenAI 官方 API 以及兼容 OpenAI 格式的第三方 API（如 DeepSeek、Moonshot 等）
    """
    
    def __init__(self, config):
        super().__init__(config)
        if OpenAI is None:
            raise ImportError("请先安装 openai: pip install openai")
        
        client_kwargs = {
            'api_key': config.api_key,
        }
        
        # 如果提供了 base_url，使用自定义端点
        if config.base_url:
            client_kwargs['base_url'] = config.base_url
        
        self.client = OpenAI(**client_kwargs)
    
    def validate_config(self) -> bool:
        """验证配置"""
        if not self.config.api_key:
            return False
        return True
    
    def chat(self, messages: List[Message], **kwargs) -> LLMResponse:
        """发送对话请求"""
        # 转换消息格式
        openai_messages = [
            {"role": msg.role, "content": msg.content}
            for msg in messages
        ]
        
        # 合并参数
        params = {
            'model': self.model,
            'messages': openai_messages,
            'temperature': kwargs.get('temperature', self.config.temperature),
            'max_tokens': kwargs.get('max_tokens', self.config.max_tokens),
        }
        
        # 发送请求
        response = self.client.chat.completions.create(**params)
        
        return LLMResponse(
            content=response.choices[0].message.content,
            model=self.model,
            provider=self.provider,
            usage={
                'prompt_tokens': response.usage.prompt_tokens,
                'completion_tokens': response.usage.completion_tokens,
                'total_tokens': response.usage.total_tokens
            } if response.usage else None,
            finish_reason=response.choices[0].finish_reason,
            raw_response=response
        )
    
    def chat_stream(self, messages: List[Message], **kwargs) -> Generator[str, None, None]:
        """流式对话请求"""
        openai_messages = [
            {"role": msg.role, "content": msg.content}
            for msg in messages
        ]
        
        params = {
            'model': self.model,
            'messages': openai_messages,
            'temperature': kwargs.get('temperature', self.config.temperature),
            'max_tokens': kwargs.get('max_tokens', self.config.max_tokens),
            'stream': True
        }
        
        response = self.client.chat.completions.create(**params)
        
        for chunk in response:
            if chunk.choices and chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
