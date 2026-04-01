"""阿里云 DashScope (通义千问) API 客户端

DashScope 提供 OpenAI 兼容的 API 格式，这里继承 OpenAIClient 并设置正确的 base_url。
"""

from typing import List, Generator

from .openai_client import OpenAIClient
from .base import LLMResponse, Message


class DashScopeClient(OpenAIClient):
    """阿里云 DashScope API 客户端
    
    通义千问系列模型：
    - qwen-max: 通义千问 Max，最强性能
    - qwen-plus: 通义千问 Plus，均衡性能
    - qwen-turbo: 通义千问 Turbo，快速经济
    
    文档: https://help.aliyun.com/zh/dashscope/
    """
    
    def __init__(self, config):
        # 确保使用 DashScope 的 API 端点
        if not config.base_url:
            config.base_url = 'https://dashscope.aliyuncs.com/compatible-mode/v1'
        
        # 调用父类初始化
        super().__init__(config)
        self.provider = 'dashscope'
    
    def validate_config(self) -> bool:
        """验证配置"""
        if not self.config.api_key:
            # 尝试从 DASHSCOPE_API_KEY 环境变量读取
            import os
            api_key = os.getenv('DASHSCOPE_API_KEY')
            if api_key:
                self.config.api_key = api_key
                # 重新初始化客户端
                from openai import OpenAI
                self.client = OpenAI(
                    api_key=api_key,
                    base_url=self.config.base_url
                )
            else:
                return False
        return True
    
    def chat(self, messages: List[Message], **kwargs) -> LLMResponse:
        """发送对话请求"""
        # 确保配置有效
        if not self.validate_config():
            raise ValueError("DASHSCOPE_API_KEY 未设置。请设置环境变量或在 .env 文件中配置。")
        
        # 调用父类方法
        return super().chat(messages, **kwargs)
    
    def chat_stream(self, messages: List[Message], **kwargs) -> Generator[str, None, None]:
        """流式对话请求"""
        # 确保配置有效
        if not self.validate_config():
            raise ValueError("DASHSCOPE_API_KEY 未设置。请设置环境变量或在 .env 文件中配置。")
        
        # 调用父类方法
        yield from super().chat_stream(messages, **kwargs)
