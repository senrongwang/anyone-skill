"""对话引擎

替代 SKILL.md 的运行逻辑，直接调用 LLM API 进行对话。
"""

import json
import re
from pathlib import Path
from typing import Optional, List, Dict, Any, Generator
from dataclasses import dataclass, field

from .config.settings import get_settings
from .llm.factory import LLMFactory
from .llm.base import Message


@dataclass
class PersonaSkillData:
    """Persona Skill 数据"""
    slug: str
    name: str
    description: str
    memory_content: str  # Part A: 关系记忆
    persona_content: str  # Part B: 人物性格
    meta: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def system_prompt(self) -> str:
        """生成系统 Prompt"""
        return f"""你是 {self.name}，不是 AI 助手。用ta的方式说话，用ta的逻辑思考。

---

## PART A：关系记忆

{self.memory_content}

---

## PART B：人物性格

{self.persona_content}

---

## 运行规则

1. 你是{self.name}，不是 AI 助手。用ta的方式说话，用ta的逻辑思考
2. 先由 PART B 判断：ta会怎么回应这个话题？什么态度？
3. 再由 PART A 补充：结合你们的共同记忆，让回应更真实
4. 始终保持 PART B 的表达风格，包括口头禅、语气词、标点习惯
5. Layer 0 硬规则优先级最高：
   - 不说ta在现实中绝不可能说的话
   - 不突然变得完美或无条件包容（除非ta本来就这样）
   - 保持ta的"棱角"——正是这些不完美让ta真实
   - 如果被问到"你爱不爱我"这类问题，用ta会用的方式回答，而不是用户想听的答案
"""


class ChatEngine:
    """对话引擎"""
    
    def __init__(self, slug: str, model_key: Optional[str] = None):
        """
        Args:
            slug: Persona Skill 的代号
            model_key: 模型标识，如 "openai/gpt-4"
        """
        self.slug = slug
        self.model_key = model_key or self._get_default_model()
        
        # 加载 Skill 数据
        self.skill_data = self._load_skill()
        
        # 创建 LLM 客户端
        self.client = LLMFactory.create_client(self.model_key)
        
        # 对话历史
        self.history: List[Message] = []
        
        # 初始化系统消息
        self._init_system()
    
    def _get_default_model(self) -> str:
        """获取默认模型"""
        settings = get_settings()
        return f"{settings.default_provider}/{settings.default_model}"
    
    def _load_skill(self) -> PersonaSkillData:
        """加载 Persona Skill 数据"""
        settings = get_settings()
        skill_path = settings.get_persona_skill_path(self.slug)
        
        if not skill_path.exists():
            raise FileNotFoundError(f"找不到 Persona Skill: {self.slug} (路径: {skill_path})")
        
        # 读取 SKILL.md
        skill_file = skill_path / 'SKILL.md'
        memory_file = skill_path / 'memory.md'
        persona_file = skill_path / 'persona.md'
        meta_file = skill_path / 'meta.json'
        
        # 优先读取完整的 SKILL.md
        if skill_file.exists():
            content = skill_file.read_text(encoding='utf-8')
            return self._parse_skill_md(content, skill_path)
        
        # 否则读取分开的 memory.md 和 persona.md
        memory_content = ''
        persona_content = ''
        meta = {}
        
        if memory_file.exists():
            memory_content = memory_file.read_text(encoding='utf-8')
        
        if persona_file.exists():
            persona_content = persona_file.read_text(encoding='utf-8')
        
        if meta_file.exists():
            meta = json.loads(meta_file.read_text(encoding='utf-8'))
        
        name = meta.get('name', self.slug)
        
        return PersonaSkillData(
            slug=self.slug,
            name=name,
            description=meta.get('impression', ''),
            memory_content=memory_content,
            persona_content=persona_content,
            meta=meta
        )
    
    def _parse_skill_md(self, content: str, skill_path: Path) -> PersonaSkillData:
        """解析 SKILL.md 文件"""
        # 提取 frontmatter
        frontmatter = {}
        meta_file = skill_path / 'meta.json'
        if meta_file.exists():
            frontmatter = json.loads(meta_file.read_text(encoding='utf-8'))
        
        name = frontmatter.get('name', self.slug)
        
        # 提取 Part A 和 Part B
        memory_content = ''
        persona_content = ''
        
        # 尝试按标记分割
        part_a_match = re.search(r'##\s*PART\s*A.*?(?=##\s*PART\s*B|$)', content, re.DOTALL | re.IGNORECASE)
        part_b_match = re.search(r'##\s*PART\s*B.*?(?=##\s*运行规则|$)', content, re.DOTALL | re.IGNORECASE)
        
        if part_a_match:
            memory_content = part_a_match.group(0)
        if part_b_match:
            persona_content = part_b_match.group(0)
        
        # 如果没找到标记，尝试其他方式
        if not memory_content and not persona_content:
            # 简单分割：前半部分是记忆，后半部分是性格
            lines = content.split('\n')
            mid = len(lines) // 2
            memory_content = '\n'.join(lines[:mid])
            persona_content = '\n'.join(lines[mid:])
        
        return PersonaSkillData(
            slug=self.slug,
            name=name,
            description=frontmatter.get('impression', ''),
            memory_content=memory_content,
            persona_content=persona_content,
            meta=frontmatter
        )
    
    def _init_system(self):
        """初始化系统消息"""
        system_msg = Message(
            role='system',
            content=self.skill_data.system_prompt
        )
        self.history.append(system_msg)
    
    def chat(self, user_message: str, stream: bool = False, **kwargs) -> Optional[str]:
        """发送消息并获取回复
        
        Args:
            user_message: 用户输入
            stream: 是否使用流式输出
            **kwargs: 额外参数
        
        Returns:
            助手回复内容(非流式)或 None(流式)
        """
        # 添加用户消息到历史
        self.history.append(Message(role='user', content=user_message))
        
        if stream:
            return None  # 流式输出通过 chat_stream 方法处理
        
        # 调用 LLM
        response = self.client.chat(self.history, **kwargs)
        
        # 添加助手回复到历史
        self.history.append(Message(role='assistant', content=response.content))
        
        return response.content
    
    def chat_stream(self, user_message: str, **kwargs) -> Generator[str, None, None]:
        """流式对话
        
        Args:
            user_message: 用户输入
            **kwargs: 额外参数
        
        Yields:
            生成的文本片段
        """
        # 添加用户消息到历史
        self.history.append(Message(role='user', content=user_message))
        
        # 调用流式 API
        full_response = []
        for chunk in self.client.chat_stream(self.history, **kwargs):
            full_response.append(chunk)
            yield chunk
        
        # 添加完整回复到历史
        complete_response = ''.join(full_response)
        self.history.append(Message(role='assistant', content=complete_response))
    
    def get_history(self) -> List[Dict[str, str]]:
        """获取对话历史"""
        return [
            {'role': msg.role, 'content': msg.content}
            for msg in self.history
        ]
    
    def clear_history(self, keep_system: bool = True):
        """清空对话历史
        
        Args:
            keep_system: 是否保留系统消息
        """
        if keep_system and self.history and self.history[0].role == 'system':
            self.history = [self.history[0]]
        else:
            self.history = []
            if keep_system:
                self._init_system()
    
    def get_model_info(self) -> Dict[str, str]:
        """获取当前模型信息"""
        return {
            'model_key': self.model_key,
            'provider': self.client.provider,
            'model': self.client.model
        }
    
    def get_skill_info(self) -> Dict[str, Any]:
        """获取 Skill 信息"""
        return {
            'slug': self.skill_data.slug,
            'name': self.skill_data.name,
            'description': self.skill_data.description,
            'meta': self.skill_data.meta
        }


def list_available_skills() -> List[Dict[str, Any]]:
    """列出所有可用的 Persona Skill"""
    settings = get_settings()
    return settings.list_persona_skills()


def create_chat(slug: str, model_key: Optional[str] = None) -> ChatEngine:
    """创建对话引擎实例
    
    Args:
        slug: Persona Skill 代号
        model_key: 模型标识
    
    Returns:
        ChatEngine 实例
    """
    return ChatEngine(slug, model_key)
