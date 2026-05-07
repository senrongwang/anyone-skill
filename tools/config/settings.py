"""配置管理系统

支持从环境变量、.env 文件、配置文件读取 API 密钥和模型配置。
"""

import os
from pathlib import Path
from typing import Optional, Dict, Any
from dataclasses import dataclass, field


@dataclass
class ModelConfig:
    """单个模型配置"""
    provider: str  # openai, anthropic, gemini, ollama, dashscope
    model: str
    api_key: Optional[str] = None
    base_url: Optional[str] = None  # 用于自定义 API 端点或本地模型
    temperature: float = 0.7
    max_tokens: int = 2000
    timeout: int = 60
    
    def __post_init__(self):
        # 自动从环境变量读取 API key（如果未提供）
        if self.api_key is None:
            env_var_map = {
                'openai': 'OPENAI_API_KEY',
                'anthropic': 'ANTHROPIC_API_KEY',
                'gemini': 'GEMINI_API_KEY',
                'google': 'GOOGLE_API_KEY',
                'dashscope': 'DASHSCOPE_API_KEY',
                'deepseek': 'DEEPSEEK_API_KEY',
            }
            env_var = env_var_map.get(self.provider)
            if env_var:
                self.api_key = os.getenv(env_var)


@dataclass
class Settings:
    """应用配置"""
    
    # 基础路径
    base_dir: Path = field(default_factory=lambda: Path(__file__).parent.parent.parent)
    personas_dir: Path = field(default_factory=lambda: Path(__file__).parent.parent.parent / 'personas')
    
    # 默认模型配置
    default_provider: str = 'openai'
    default_model: str = 'gpt-4o'
    
    # 模型配置字典
    models: Dict[str, ModelConfig] = field(default_factory=dict)
    
    def __post_init__(self):
        self._init_default_models()
        self._load_env_file()
    
    def _init_default_models(self):
        """初始化默认模型配置"""
        default_configs = {
            'openai/gpt-4': ModelConfig(
                provider='openai',
                model='gpt-4',
                temperature=0.7,
                max_tokens=2000
            ),
            'openai/gpt-4o': ModelConfig(
                provider='openai',
                model='gpt-4o',
                temperature=0.7,
                max_tokens=2000
            ),
            'openai/gpt-3.5-turbo': ModelConfig(
                provider='openai',
                model='gpt-3.5-turbo',
                temperature=0.7,
                max_tokens=2000
            ),
            'anthropic/claude-3-opus': ModelConfig(
                provider='anthropic',
                model='claude-3-opus-20240229',
                temperature=0.7,
                max_tokens=2000
            ),
            'anthropic/claude-3-sonnet': ModelConfig(
                provider='anthropic',
                model='claude-3-sonnet-20240229',
                temperature=0.7,
                max_tokens=2000
            ),
            'anthropic/claude-3-haiku': ModelConfig(
                provider='anthropic',
                model='claude-3-haiku-20240307',
                temperature=0.7,
                max_tokens=2000
            ),
            'gemini/gemini-pro': ModelConfig(
                provider='gemini',
                model='gemini-pro',
                temperature=0.7,
                max_tokens=2000
            ),
            'gemini/gemini-1.5-flash': ModelConfig(
                provider='gemini',
                model='gemini-1.5-flash',
                temperature=0.7,
                max_tokens=2000
            ),
            # DeepSeek
            'deepseek/deepseek-v4-flash': ModelConfig(
                provider='deepseek',
                model='deepseek-v4-flash',
                base_url='https://api.deepseek.com',
                temperature=0.7,
                max_tokens=4096
            ),
            'deepseek/deepseek-v4-pro': ModelConfig(
                provider='deepseek',
                model='deepseek-v4-pro',
                base_url='https://api.deepseek.com',
                temperature=0.7,
                max_tokens=4096
            ),
            'deepseek/deepseek-chat': ModelConfig(
                provider='deepseek',
                model='deepseek-chat',
                base_url='https://api.deepseek.com',
                temperature=0.7,
                max_tokens=4096
            ),
            'deepseek/deepseek-reasoner': ModelConfig(
                provider='deepseek',
                model='deepseek-reasoner',
                base_url='https://api.deepseek.com',
                temperature=0.7,
                max_tokens=4096
            ),
            # 阿里云 DashScope (通义千问)
            'qwen/qwen-max': ModelConfig(
                provider='dashscope',
                model='qwen-max',
                base_url='https://dashscope.aliyuncs.com/compatible-mode/v1',
                temperature=0.7,
                max_tokens=2000
            ),
            'qwen/qwen-plus': ModelConfig(
                provider='dashscope',
                model='qwen-plus',
                base_url='https://dashscope.aliyuncs.com/compatible-mode/v1',
                temperature=0.7,
                max_tokens=2000
            ),
            'qwen/qwen-turbo': ModelConfig(
                provider='dashscope',
                model='qwen-turbo',
                base_url='https://dashscope.aliyuncs.com/compatible-mode/v1',
                temperature=0.7,
                max_tokens=2000
            ),
        }
        
        # 添加本地模型支持（Ollama）
        ollama_models = os.getenv('OLLAMA_MODELS', 'llama2,mistral,qwen2.5').split(',')
        for model in ollama_models:
            model = model.strip()
            if model:
                key = f'ollama/{model}'
                default_configs[key] = ModelConfig(
                    provider='ollama',
                    model=model,
                    base_url=os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434'),
                    temperature=0.7,
                    max_tokens=2000
                )
        
        self.models.update(default_configs)
    
    def _load_env_file(self):
        """从 .env 文件加载配置"""
        env_file = self.base_dir / '.env'
        if env_file.exists():
            with open(env_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        os.environ.setdefault(key.strip(), value.strip().strip('"\''))
        
        # 重新初始化模型配置以读取环境变量
        self._init_default_models()
    
    def get_model_config(self, model_key: str) -> ModelConfig:
        """获取模型配置
        
        Args:
            model_key: 格式为 "provider/model" 或 "model"
        
        Returns:
            ModelConfig 对象
        """
        if model_key in self.models:
            return self.models[model_key]
        
        # 尝试解析 provider/model 格式
        if '/' in model_key:
            provider, model = model_key.split('/', 1)
            return ModelConfig(
                provider=provider,
                model=model,
                temperature=0.7,
                max_tokens=2000
            )
        
        # 默认使用 default_provider
        return ModelConfig(
            provider=self.default_provider,
            model=model_key,
            temperature=0.7,
            max_tokens=2000
        )
    
    def get_persona_skill_path(self, slug: str) -> Path:
        """获取 Persona Skill 目录路径"""
        return self.personas_dir / slug
    
    def list_persona_skills(self) -> list:
        """列出所有已创建的 Persona Skill"""
        if not self.personas_dir.exists():
            return []
        
        skills = []
        for slug in sorted(self.personas_dir.iterdir()):
            if slug.is_dir():
                skill_file = slug / 'SKILL.md'
                meta_file = slug / 'meta.json'
                if skill_file.exists():
                    skills.append({
                        'slug': slug.name,
                        'path': slug,
                        'has_meta': meta_file.exists()
                    })
        return skills


# 全局配置实例
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """获取全局配置实例"""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
