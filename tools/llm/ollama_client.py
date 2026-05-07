"""Ollama 本地模型客户端"""

from typing import List, Generator
import json
import urllib.request
import urllib.error

from .base import BaseLLMClient, LLMResponse, Message


class OllamaClient(BaseLLMClient):
    """Ollama 本地模型客户端
    
    支持本地运行的开源模型，如 llama2, mistral, qwen 等
    """
    
    def __init__(self, config):
        super().__init__(config)
        self.base_url = config.base_url or 'http://localhost:11434'
    
    def _convert_messages(self, messages: List[Message]) -> tuple:
        """转换消息格式"""
        system_msg = None
        chat_messages = []
        
        for msg in messages:
            if msg.role == 'system':
                system_msg = msg.content
            else:
                chat_messages.append({
                    "role": msg.role,
                    "content": msg.content
                })
        
        return system_msg, chat_messages
    
    def chat(self, messages: List[Message], **kwargs) -> LLMResponse:
        """发送对话请求"""
        system_msg, chat_messages = self._convert_messages(messages)
        
        # 构建请求体
        data = {
            'model': self.model,
            'messages': chat_messages,
            'stream': False,
            'options': {
                'temperature': kwargs.get('temperature', self.config.temperature),
            }
        }
        
        if system_msg:
            data['system'] = system_msg
        
        # 发送请求
        req = urllib.request.Request(
            f"{self.base_url}/api/chat",
            data=json.dumps(data).encode('utf-8'),
            headers={'Content-Type': 'application/json'},
            method='POST'
        )
        
        try:
            with urllib.request.urlopen(req, timeout=self.config.timeout) as response:
                result = json.loads(response.read().decode('utf-8'))
                
                return LLMResponse(
                    content=result.get('message', {}).get('content', ''),
                    model=self.model,
                    provider=self.provider,
                    usage=None,
                    finish_reason='stop' if result.get('done') else None,
                )
        except urllib.error.URLError as e:
            raise ConnectionError(f"无法连接到 Ollama 服务: {e}. 请确保 Ollama 已启动并运行在 {self.base_url}")
    
    def chat_stream(self, messages: List[Message], **kwargs) -> Generator[str, None, None]:
        """流式对话请求"""
        system_msg, chat_messages = self._convert_messages(messages)
        
        data = {
            'model': self.model,
            'messages': chat_messages,
            'stream': True,
            'options': {
                'temperature': kwargs.get('temperature', self.config.temperature),
            }
        }
        
        if system_msg:
            data['system'] = system_msg
        
        req = urllib.request.Request(
            f"{self.base_url}/api/chat",
            data=json.dumps(data).encode('utf-8'),
            headers={'Content-Type': 'application/json'},
            method='POST'
        )
        
        try:
            with urllib.request.urlopen(req, timeout=self.config.timeout) as response:
                for line in response:
                    line = line.decode('utf-8').strip()
                    if line:
                        try:
                            chunk = json.loads(line)
                            content = chunk.get('message', {}).get('content', '')
                            if content:
                                yield content
                        except json.JSONDecodeError:
                            continue
        except urllib.error.URLError as e:
            raise ConnectionError(f"无法连接到 Ollama 服务: {e}. 请确保 Ollama 已启动并运行在 {self.base_url}")
