"""Anthropic Claude API 客户端"""

from typing import List, Generator

try:
    import anthropic
except ImportError:
    anthropic = None

from .base import BaseLLMClient, LLMResponse, Message


class AnthropicClient(BaseLLMClient):
    """Anthropic Claude API 客户端"""
    
    def __init__(self, config):
        super().__init__(config)
        if anthropic is None:
            raise ImportError("请先安装 anthropic: pip install anthropic")
        
        self.client = anthropic.Anthropic(api_key=config.api_key)
    
    def _convert_messages(self, messages: List[Message]) -> tuple:
        """转换消息格式为 Claude 格式
        
        Claude 使用 system 参数和 messages 列表
        """
        system_msg = None
        claude_messages = []
        
        for msg in messages:
            if msg.role == 'system':
                system_msg = msg.content
            elif msg.role == 'user':
                claude_messages.append({
                    "role": "user",
                    "content": msg.content
                })
            elif msg.role == 'assistant':
                claude_messages.append({
                    "role": "assistant",
                    "content": msg.content
                })
        
        return system_msg, claude_messages
    
    def chat(self, messages: List[Message], **kwargs) -> LLMResponse:
        """发送对话请求"""
        system_msg, claude_messages = self._convert_messages(messages)
        
        params = {
            'model': self.model,
            'messages': claude_messages,
            'max_tokens': kwargs.get('max_tokens', self.config.max_tokens),
            'temperature': kwargs.get('temperature', self.config.temperature),
        }
        
        if system_msg:
            params['system'] = system_msg
        
        response = self.client.messages.create(**params)
        
        return LLMResponse(
            content=response.content[0].text if response.content else "",
            model=self.model,
            provider=self.provider,
            usage={
                'input_tokens': response.usage.input_tokens,
                'output_tokens': response.usage.output_tokens
            } if response.usage else None,
            finish_reason=response.stop_reason,
        )
    
    def chat_stream(self, messages: List[Message], **kwargs) -> Generator[str, None, None]:
        """流式对话请求"""
        system_msg, claude_messages = self._convert_messages(messages)
        
        params = {
            'model': self.model,
            'messages': claude_messages,
            'max_tokens': kwargs.get('max_tokens', self.config.max_tokens),
            'temperature': kwargs.get('temperature', self.config.temperature),
            'stream': True
        }
        
        if system_msg:
            params['system'] = system_msg
        
        with self.client.messages.stream(**params) as stream:
            for text in stream.text_stream:
                yield text
