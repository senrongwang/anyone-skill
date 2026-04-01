"""LLM 客户端工厂"""

from typing import Optional

from ..config.settings import ModelConfig, get_settings
from .base import BaseLLMClient
from .openai_client import OpenAIClient
from .anthropic_client import AnthropicClient
from .gemini_client import GeminiClient
from .ollama_client import OllamaClient
from .dashscope_client import DashScopeClient


class LLMFactory:
    """LLM 客户端工厂
    
    根据配置创建对应的 LLM 客户端实例
    """
    
    _clients = {}
    
    @classmethod
    def create_client(cls, model_key: Optional[str] = None, config: Optional[ModelConfig] = None) -> BaseLLMClient:
        """创建 LLM 客户端
        
        Args:
            model_key: 模型标识，如 "openai/gpt-4", "anthropic/claude-3-opus"
            config: 直接传入 ModelConfig 对象（可选）
        
        Returns:
            BaseLLMClient 实例
        """
        if config is None:
            if model_key is None:
                settings = get_settings()
                model_key = f"{settings.default_provider}/{settings.default_model}"
            
            settings = get_settings()
            config = settings.get_model_config(model_key)
        
        # 根据 provider 创建对应客户端
        provider_map = {
            'openai': OpenAIClient,
            'anthropic': AnthropicClient,
            'gemini': GeminiClient,
            'google': GeminiClient,
            'ollama': OllamaClient,
            'dashscope': DashScopeClient,
            'qwen': DashScopeClient,
        }
        
        client_class = provider_map.get(config.provider)
        if client_class is None:
            raise ValueError(f"不支持的 provider: {config.provider}. 支持的 provider: {list(provider_map.keys())}")
        
        return client_class(config)
    
    @classmethod
    def get_or_create_client(cls, model_key: str) -> BaseLLMClient:
        """获取或创建客户端（单例模式）"""
        if model_key not in cls._clients:
            cls._clients[model_key] = cls.create_client(model_key)
        return cls._clients[model_key]
    
    @classmethod
    def list_supported_providers(cls) -> list:
        """列出支持的 provider"""
        return ['openai', 'anthropic', 'gemini', 'ollama', 'dashscope', 'qwen']
    
    @classmethod
    def list_available_models(cls) -> dict:
        """列出所有可用的模型配置"""
        settings = get_settings()
        result = {}
        for key, config in settings.models.items():
            result[key] = {
                'provider': config.provider,
                'model': config.model,
                'has_api_key': bool(config.api_key)
            }
        return result
