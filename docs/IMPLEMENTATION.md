# Anyone Skill 实现文档

本文档详细介绍 Anyone Skill 项目的各个流程是如何实现的，包括架构设计、核心模块、数据流转等。

---

## 目录

1. [架构概览](#架构概览)
2. [关系类型系统](#关系类型系统)
3. [创建流程实现](#创建流程实现)
4. [对话流程实现](#对话流程实现)
5. [数据解析模块](#数据解析模块)
6. [LLM 客户端](#llm-客户端)
7. [文件存储结构](#文件存储结构)

---

## 架构概览

### 整体架构图

```
┌─────────────────────────────────────────────────────────────┐
│                        用户交互层                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │ create_persona│  │   chat.py    │  │  skill_writer.py │  │
│  │    .py       │  │              │  │                  │  │
│  └──────┬───────┘  └──────┬───────┘  └────────┬─────────┘  │
└─────────┼─────────────────┼───────────────────┼────────────┘
          │                 │                   │
          ▼                 ▼                   ▼
┌─────────────────────────────────────────────────────────────┐
│                        核心逻辑层                            │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐  │
│  │ relationship_   │  │   chat_engine   │  │   config/   │  │
│  │   types.py      │  │     .py         │  │  settings   │  │
│  │  (关系类型定义)  │  │   (对话引擎)     │  │  (配置管理)  │  │
│  └─────────────────┘  └─────────────────┘  └─────────────┘  │
└─────────────────────────────────────────────────────────────┘
          │                 │                   │
          ▼                 ▼                   ▼
┌─────────────────────────────────────────────────────────────┐
│                        基础设施层                            │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │    llm/     │  │  *_parser.py│  │   version_manager   │  │
│  │  (多API支持) │  │  (数据解析)  │  │    (版本管理)        │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
          │                 │                   │
          ▼                 ▼                   ▼
┌─────────────────────────────────────────────────────────────┐
│                        数据存储层                            │
│                    personas/{slug}/                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────┐ │
│  │SKILL.md  │  │memory.md │  │persona.md│  │  meta.json   │ │
│  │(完整Skill)│  │(关系记忆) │  │(人物性格) │  │  (元信息)     │ │
│  └──────────┘  └──────────┘  └──────────┘  └──────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### 核心设计原则

1. **开闭原则**：通过 `RelationshipType` 抽象基类，易于扩展新的关系类型
2. **单一职责**：每个模块只负责一项功能（创建、对话、解析、配置）
3. **依赖注入**：LLM 客户端通过工厂模式创建，支持运行时切换

---

## 关系类型系统

### 核心抽象

```
python
# tools/relationship_types.py

class RelationshipType(ABC):
    """关系类型抽象基类"""
    
    @abstractmethod
    def get_intake_questions(self) -> List[QuestionTemplate]:
        """获取信息录入问题列表"""
        pass
    
    @abstractmethod
    def get_memory_dimensions(self) -> List[MemoryDimension]:
        """获取记忆提取维度"""
        pass
    
    @abstractmethod
    def generate_memory_template(self, info: Dict[str, Any]) -> str:
        """生成记忆文档模板"""
        pass
    
    @abstractmethod
    def generate_persona_template(self, info: Dict[str, Any]) -> str:
        """生成性格文档模板"""
        pass
```

### 实现机制

每种关系类型是一个独立的类，继承自 `RelationshipType`：

```
RelationshipType (抽象基类)
    ├── ExPartnerType    # 前任/恋人
    ├── FriendType       # 朋友
    ├── FamilyType       # 家人
    ├── ColleagueType    # 同事
    └── IdolType         # 偶像/角色
```

### 动态加载

```
python
# 关系类型注册表
RELATIONSHIP_TYPES = {
    RelationshipCategory.EX_PARTNER: ExPartnerType(),
    RelationshipCategory.FRIEND: FriendType(),
    RelationshipCategory.FAMILY: FamilyType(),
    RelationshipCategory.COLLEAGUE: ColleagueType(),
    RelationshipCategory.IDOL: IdolType(),
}

# 运行时根据用户选择获取对应类型
def get_relationship_type(category: RelationshipCategory) -> RelationshipType:
    return RELATIONSHIP_TYPES.get(category, ExPartnerType())
```

### 差异化配置示例

**前任类型的问题模板：**
```
python
def get_intake_questions(self) -> List[QuestionTemplate]:
    return [
        QuestionTemplate(key="name", question="花名/代号", required=True),
        QuestionTemplate(key="basic_info", question="在一起多久、分手多久、ta做什么的"),
        QuestionTemplate(key="personality", question="MBTI、星座、性格标签"),
        QuestionTemplate(key="breakup_reason", question="分开的原因"),
    ]
```

**朋友类型的问题模板：**
```
python
def get_intake_questions(self) -> List[QuestionTemplate]:
    return [
        QuestionTemplate(key="name", question="朋友称呼/昵称", required=True),
        QuestionTemplate(key="basic_info", question="认识多久了、怎么认识的、ta做什么的"),
        QuestionTemplate(key="personality", question="性格特点、兴趣爱好"),
        QuestionTemplate(key="friendship_dynamic", question="你们的相处模式"),
    ]
```

---

## 创建流程实现

### 流程图

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   启动程序   │ -> │ 选择关系类型 │ -> │ 填写基础信息 │ -> │ 导入原材料  │ -> │  生成内容   │ -> │  写入文件   │
│             │    │             │    │             │    │  (可选)     │    │             │    │             │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
                                                                                                      │
                                                                                                      ▼
                                                                                              ┌─────────────┐
                                                                                              │  创建完成   │
                                                                                              └─────────────┘
```

### Step 1: 选择关系类型

**实现文件：** `create_persona.py` -> `step1_select_relationship_type()`

```
python
def select_relationship_type() -> RelationshipType:
    # 展示所有可用类型
    types = list_relationship_types()
    for i, rt in enumerate(types, 1):
        print(f"  [{i}] {rt['icon']} {rt['name']} - {rt['description']}")
    
    # 用户输入数字选择
    choice = input("\n选择 (1-5): ").strip()
    idx = int(choice) - 1
    selected = types[idx]
    
    # 返回对应的关系类型实例
    return get_relationship_type(RelationshipCategory(selected['key']))
```

### Step 2: 填写基础信息

**实现文件：** `create_persona.py` -> `step2_basic_info(rel_type)`

```
python
def step2_basic_info(rel_type):
    questions = rel_type.get_intake_questions()
    info = {}
    
    for q in questions:
        if q.required:
            # 必填项循环直到有输入
            while True:
                value = input(f"{q.key}: ").strip()
                if value:
                    info[q.key] = value
                    break
        else:
            # 选填项可直接跳过
            value = input(f"{q.key} (可选): ").strip()
            info[q.key] = value
    
    # 自动生成 slug（URL 友好的标识符）
    info['slug'] = info['name'].lower().replace(" ", "-")
    return info
```

### Step 3: 导入原材料

**实现文件：** `create_persona.py` -> `step3_import_sources()`

支持的数据源及其实现：

| 数据源 | 实现文件 | 核心函数 | 输出格式 |
|--------|----------|----------|----------|
| 微信聊天记录 | `wechat_parser.py` | `parse_wechatmsg_txt()` | 结构化字典 |
| QQ 聊天记录 | `qq_parser.py` | `parse_qq_txt()` | 原始文本 |
| 照片 | `photo_analyzer.py` | `get_exif_data()` | EXIF 信息 |
| 社交媒体 | `social_parser.py` | `parse_screenshots()` | 文件列表 |

**微信解析示例：**
```
python
# 自动检测格式
fmt = detect_format(file_path)

if fmt == 'plaintext':
    result = parse_plaintext(file_path, name)
elif fmt == 'liuhen':
    result = parse_liuhen_json(file_path, name)
else:
    result = parse_wechatmsg_txt(file_path, name)

# 提取分析维度
analysis = {
    'top_particles': 统计语气词,      # 么、吧、啊
    'top_emojis': 统计表情符号,        # 👌、😂
    'avg_message_length': 平均消息长度,
    'message_style': 消息风格,         # 短句连发 / 长段落
    'response_pattern': 回应模式,      # 秒回 / 已读不回
    'top_words': 高频话题,
    'locations': 提及地点,
    'activities': 共同活动,
}
```

### Step 4: 生成内容

**实现文件：** `create_persona.py` -> `step4_generate_content()`

```
python
def step4_generate_content(info, raw_content, rel_type):
    info['raw_content'] = raw_content
    
    # 调用关系类型的模板生成方法
    memory_content = rel_type.generate_memory_template(info)
    persona_content = rel_type.generate_persona_template(info)
    
    return memory_content, persona_content
```

**模板生成逻辑（以 ExPartnerType 为例）：**
```
python
def generate_memory_template(self, info):
    return f"""# 关系记忆

## 基本信息
- 花名：{info.get('name')}
- 关系描述：{info.get('basic_info')}
- 分开原因：{info.get('breakup_reason')}

## 关系时间线
- 认识时间：待补充
- 在一起时间：待补充
- 分手时间：待补充

## 甜蜜瞬间
待补充

## 争吵模式
待补充

## 聊天记录分析
{info.get('raw_content')}
"""
```

### Step 5: 预览确认

展示生成的 memory.md 和 persona.md 摘要（各 15 行），用户确认后继续。

### Step 6: 写入文件

**目录结构创建：**
```
python
skill_dir = settings.get_persona_skill_path(slug)
os.makedirs(skill_dir, exist_ok=True)
os.makedirs(skill_dir / 'versions', exist_ok=True)
os.makedirs(skill_dir / 'memories' / 'chats', exist_ok=True)
os.makedirs(skill_dir / 'memories' / 'photos', exist_ok=True)
os.makedirs(skill_dir / 'memories' / 'social', exist_ok=True)
```

**文件写入：**
| 文件 | 内容 | 用途 |
|------|------|------|
| `memory.md` | 关系记忆 | Part A：事实性记忆 |
| `persona.md` | 人物性格 | Part B：行为驱动 |
| `meta.json` | 元信息 | 关系类型、版本、标签 |
| `SKILL.md` | 完整组合 | 可直接运行的 Skill |

---

## 对话流程实现

### 流程图

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  启动对话    │ --> │  加载 Skill  │ --> │  初始化 LLM  │ --> │  交互循环   │
│             │     │   数据      │     │   客户端     │     │             │
└─────────────┘     └─────────────┘     └─────────────┘     └──────┬──────┘
                                                                   │
                    ┌──────────────────────────────────────────────┘
                    │
                    ▼
            ┌───────────────┐
            │  用户输入消息  │
            └───────┬───────┘
                    │
        ┌───────────┼───────────┐
        ▼           ▼           ▼
   ┌─────────┐ ┌─────────┐ ┌─────────┐
   │ /quit   │ │ /clear  │ │ 普通消息 │
   │  退出   │ │ 清空历史│ │         │
   └─────────┘ └─────────┘ └────┬────┘
                                 │
                                 ▼
                    ┌─────────────────────┐
                    │  构造 System Prompt  │
                    │  (memory + persona)  │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │   调用 LLM API      │
                    │  (流式/非流式)      │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │    输出回复         │
                    │   (像ta一样说话)     │
                    └─────────────────────┘
```

### Skill 数据加载

**实现文件：** `tools/chat_engine.py` -> `ChatEngine._load_skill()`

```
python
def _load_skill(self) -> PersonaSkillData:
    settings = get_settings()
    skill_path = settings.get_persona_skill_path(self.slug)
    
    # 读取 meta.json 获取基本信息
    meta = json.loads((skill_path / 'meta.json').read_text())
    
    # 读取 memory.md 和 persona.md
    memory_content = (skill_path / 'memory.md').read_text()
    persona_content = (skill_path / 'persona.md').read_text()
    
    return PersonaSkillData(
        slug=self.slug,
        name=meta.get('name', self.slug),
        memory_content=memory_content,
        persona_content=persona_content,
        meta=meta
    )
```

### System Prompt 构造

```
python
@property
def system_prompt(self) -> str:
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
   - 不突然变得完美或无条件包容
   - 保持ta的"棱角"
"""
```

### LLM 调用流程

**工厂模式创建客户端：**
```
python
# tools/llm/factory.py

class LLMFactory:
    @staticmethod
    def create_client(model_key: str):
        provider, model = model_key.split('/')
        
        if provider == 'openai':
            return OpenAIClient(model)
        elif provider == 'anthropic':
            return AnthropicClient(model)
        elif provider == 'gemini':
            return GeminiClient(model)
        elif provider == 'dashscope':
            return DashScopeClient(model)
        elif provider == 'ollama':
            return OllamaClient(model)
```

**对话执行：**
```python
def chat_stream(self, user_message: str) -> Generator[str, None, None]:
    # 添加用户消息到历史
    self.history.append(Message(role='user', content=user_message))
    
    # 流式调用 LLM
    full_response = []
    for chunk in self.client.chat_stream(self.history):
        full_response.append(chunk)
        yield chunk  # 实时输出给用户
    
    # 保存完整回复到历史
    complete_response = ''.join(full_response)
    self.history.append(Message(role='assistant', content=complete_response))
```

---

## 数据解析模块

### 微信聊天记录解析

**实现文件：** `tools/wechat_parser.py`

**支持格式：**
- WeChatMsg 导出的 txt/html/csv
- 留痕导出的 JSON
- PyWxDump 导出的 SQLite
- 手动复制的纯文本

**解析流程：**
```python
def parse_wechatmsg_txt(file_path: str, target_name: str) -> Dict:
    messages = []
    
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            # 解析格式："2024-01-15 14:30 小明: 消息内容"
            match = re.match(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2})\s+([^:]+):\s*(.+)', line)
            if match:
                time_str, sender, content = match.groups()
                messages.append({
                    'time': time_str,
                    'sender': sender.strip(),
                    'content': content.strip()
                })
    
    # 筛选目标人物的消息
    target_messages = [m for m in messages if target_name in m['sender']]
    
    # 统计分析
    analysis = analyze_messages(target_messages)
    
    return {
        'total_messages': len(messages),
        'target_messages': len(target_messages),
        'analysis': analysis,
        'sample_messages': target_messages[:20]
    }
```

**统计分析维度：**
```python
def analyze_messages(messages: List[Dict]) -> Dict:
    # 1. 语气词统计
    particles = Counter(re.findall(r'[么呢吧啊嗯哦哈]+', content))
    
    # 2. Emoji 统计
    emojis = Counter(re.findall(r'[\U0001F600-\U0001F64F]', content))
    
    # 3. 平均消息长度
    avg_length = sum(len(m['content']) for m in messages) / len(messages)
    
    # 4. 消息风格判断
    if avg_length < 15:
        style = 'short_burst'  # 短句连发
    else:
        style = 'long_paragraph'  # 长段落
    
    # 5. 回应模式
    time_diffs = calculate_time_diffs(messages)
    if avg(time_diffs) < 60:  # 平均1分钟内回复
        response_pattern = ['秒回型']
    else:
        response_pattern = ['延迟型']
    
    return {
        'top_particles': particles.most_common(10),
        'top_emojis': emojis.most_common(10),
        'avg_message_length': round(avg_length, 1),
        'message_style': style,
        'response_pattern': response_pattern,
    }
```

### 照片 EXIF 提取

**实现文件：** `tools/photo_analyzer.py`

```python
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS

def get_exif_data(image_path: str) -> Dict:
    image = Image.open(image_path)
    exif = image._getexif()
    
    data = {}
    if exif:
        for tag_id, value in exif.items():
            tag = TAGS.get(tag_id, tag_id)
            data[tag] = value
            
            # 提取 GPS 信息
            if tag == 'GPSInfo':
                data['GPSInfo'] = parse_gps_info(value)
    
    return data

def parse_gps_info(gps_info) -> Dict:
    """解析 GPS 坐标为可读格式"""
    lat = convert_to_degrees(gps_info[2])  # 纬度
    lon = convert_to_degrees(gps_info[4])  # 经度
    return {'latitude': lat, 'longitude': lon}
```

---

## LLM 客户端

### 抽象基类

**实现文件：** `tools/llm/base.py`

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Generator

@dataclass
class Message:
    role: str  # 'system', 'user', 'assistant'
    content: str

class BaseLLMClient(ABC):
    def __init__(self, model: str, api_key: str = None):
        self.model = model
        self.api_key = api_key
        self.provider = self.__class__.__name__.lower().replace('client', '')
    
    @abstractmethod
    def chat(self, messages: List[Message], **kwargs) -> Message:
        """非流式对话"""
        pass
    
    @abstractmethod
    def chat_stream(self, messages: List[Message], **kwargs) -> Generator[str, None, None]:
        """流式对话"""
        pass
```

### OpenAI 客户端实现

**实现文件：** `tools/llm/openai_client.py`

```python
import openai
from .base import BaseLLMClient, Message

class OpenAIClient(BaseLLMClient):
    def __init__(self, model: str = 'gpt-4o'):
        super().__init__(model)
        self.client = openai.OpenAI()
    
    def chat(self, messages: List[Message], **kwargs) -> Message:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{'role': m.role, 'content': m.content} for m in messages],
            temperature=kwargs.get('temperature', 0.7),
            max_tokens=kwargs.get('max_tokens', 2000),
        )
        return Message(
            role='assistant',
            content=response.choices[0].message.content
        )
    
    def chat_stream(self, messages: List[Message], **kwargs) -> Generator[str, None, None]:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{'role': m.role, 'content': m.content} for m in messages],
            stream=True,  # 启用流式输出
            **kwargs
        )
        for chunk in response:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
```

### 其他客户端

| Provider | 文件 | 特点 |
|----------|------|------|
| Anthropic | `anthropic_client.py` | 支持 Claude 3 系列 |
| Gemini | `gemini_client.py` | Google API，需特殊处理 |
| DashScope | `dashscope_client.py` | 阿里云，兼容 OpenAI 格式 |
| Ollama | `ollama_client.py` | 本地模型，无需 API Key |

---

## 文件存储结构

### 目录结构

```
personas/
└── {slug}/                          # 人物标识符
    ├── SKILL.md                     # 完整 Skill（可直接运行）
    ├── memory.md                    # Part A: 关系记忆
    ├── persona.md                   # Part B: 人物性格
    ├── meta.json                    # 元信息
    ├── versions/                    # 版本历史
    │   ├── v1_20240115_143022/     # 备份版本
    │   │   ├── memory.md
    │   │   └── persona.md
    │   └── v2_20240120_090015/
    └── memories/                    # 原始材料
        ├── chats/                   # 聊天记录
        │   └── wechat_export.txt
        ├── photos/                  # 照片
        │   └── photo_001.jpg
        └── social/                  # 社交媒体截图
            └── moments_001.png
```

### meta.json 结构

```json
{
  "name": "小明",
  "slug": "xiaoming",
  "relationship_type": "ex_partner",
  "created_at": "2024-01-15T14:30:22",
  "updated_at": "2024-01-20T09:00:15",
  "version": "v2",
  "profile": {
    "together_duration": "2年",
    "apart_since": "2023-06",
    "breakup_reason": "异地恋"
  },
  "tags": {
    "personality": ["话痨", "ENFP"],
    "attachment_style": "焦虑型",
    "love_language": "肯定的言辞"
  },
  "memory_sources": [
    "wechat_export.txt",
    "photos/"
  ],
  "corrections_count": 3
}
```

---

## 扩展指南

### 添加新的关系类型

1. **创建新类继承 RelationshipType：**
```python
class MentorType(RelationshipType):
    def __init__(self):
        super().__init__()
        self.category = RelationshipCategory.MENTOR
        self.display_name = "导师"
        self.icon = "📚"
    
    def get_intake_questions(self):
        return [
            QuestionTemplate(key="name", question="导师称呼", required=True),
            QuestionTemplate(key="field", question="专业领域"),
            # ...
        ]
    
    def get_memory_dimensions(self):
        return [
            MemoryDimension(key="teaching", name="教学方式", ...),
            # ...
        ]
```

2. **注册到关系类型表：**
```python
RELATIONSHIP_TYPES = {
    # ... 原有类型
    RelationshipCategory.MENTOR: MentorType(),
}
```

3. **更新枚举：**
```python
class RelationshipCategory(str, Enum):
    # ... 原有类型
    MENTOR = "mentor"
```

---

## 总结

Anyone Skill 的核心设计亮点：

1. **抽象基类 + 多态**：通过 `RelationshipType` 实现不同关系类型的差异化配置
2. **工厂模式**：`LLMFactory` 支持多种 API 的动态切换
3. **分层架构**：清晰的职责分离（交互层、逻辑层、基础设施层、存储层）
4. **模块化设计**：每个功能独立成模块，易于测试和维护
5. **可扩展性**：新增关系类型只需实现抽象基类，无需修改核心逻辑
