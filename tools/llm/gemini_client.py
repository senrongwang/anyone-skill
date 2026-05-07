"""Google Gemini API 客户端"""

from typing import List, Generator

try:
    import google.generativeai as genai
except ImportError:
    genai = None

from .base import BaseLLMClient, LLMResponse, Message


class GeminiClient(BaseLLMClient):
    """Google Gemini API 客户端"""
    
    def __init__(self, config):
        super().__init__(config)
        if genai is None:
            raise ImportError("请先安装 google-generativeai: pip install google-generativeai")
        
        genai.configure(api_key=config.api_key)
        self.client = genai.GenerativeModel(model_name=config.model)
    
    def _convert_messages(self, messages: List[Message]) -> tuple:
        """转换消息格式为 Gemini 格式
        
        Gemini 使用 system_instruction 和 contents
        """
        system_msg = None
        contents = []
        
        for msg in messages:
            if msg.role == 'system':
                system_msg = msg.content
            elif msg.role == 'user':
                contents.append({
                    "role": "user",
                    "parts": [msg.content]
                })
            elif msg.role == 'assistant':
                contents.append({
                    "role": "model",
                    "parts": [msg.content]
                })
        
        return system_msg, contents
    
    def chat(self, messages: List[Message], **kwargs) -> LLMResponse:
        """发送对话请求"""
        system_msg, contents = self._convert_messages(messages)
        
        # 创建配置
        generation_config = {
            'temperature': kwargs.get('temperature', self.config.temperature),
            'max_output_tokens': kwargs.get('max_tokens', self.config.max_tokens),
        }
        
        # 如果有系统消息，创建新的 model 实例
        model = self.client
        if system_msg:
            model = genai.GenerativeModel(
                model_name=self.model,
                system_instruction=system_msg
            )
        
        # 开始对话
        chat = model.start_chat(history=contents[:-1] if len(contents) > 1 else [])
        
        # 发送最后一条用户消息
        last_msg = contents[-1] if contents else {"parts": [""]}
        response = chat.send_message(
            last_msg["parts"][0],
            generation_config=generation_config
        )
        
        return LLMResponse(
            content=response.text,
            model=self.model,
            provider=self.provider,
            usage=None,  # Gemini 不返回 token 使用信息
            finish_reason=None,
        )
    
    def chat_stream(self, messages: List[Message], **kwargs) -> Generator[str, None, None]:
        """流式对话请求"""
        system_msg, contents = self._convert_messages(messages)
        
        generation_config = {
            'temperature': kwargs.get('temperature', self.config.temperature),
            'max_output_tokens': kwargs.get('max_tokens', self.config.max_tokens),
        }
        
        model = self.client
        if system_msg:
            model = genai.GenerativeModel(
                model_name=self.model,
                system_instruction=system_msg
            )
        
        chat = model.start_chat(history=contents[:-1] if len(contents) > 1 else [])
        last_msg = contents[-1] if contents else {"parts": [""]}
        
        response = chat.send_message(
            last_msg["parts"][0],
            generation_config=generation_config,
            stream=True
        )
        
        for chunk in response:
            if chunk.text:
                yield chunk.text
