# Anyone Skill 项目结构文档

本文档描述 Anyone Skill 项目在清理未使用代码后的完整结构。

---

## 项目定位

Anyone Skill 是一个**人物蒸馏工具**——通过导入聊天记录、照片、社交媒体内容等原材料，结合用户的主观描述，生成一个高度还原真实人物的 AI Persona。支持多种关系类型：前任/恋人、朋友、家人、同事、偶像/角色。

---

## 目录树

```
anyone-skill-main/
│
├── chat.py                      # 对话入口（支持多 API 流式/非流式对话）
├── create_persona.py            # Persona 创建工具（交互式 CLI）
│
├── requirements.txt             # Python 依赖
├── .env.example                 # 环境变量配置示例
│
├── tools/                       # 核心 Python 模块
│   ├── config/
│   │   ├── __init__.py          #   配置模块入口
│   │   └── settings.py          #   全局设置（API Key、模型配置、路径）
│   │
│   ├── llm/                     # LLM 客户端（工厂模式）
│   │   ├── __init__.py          #   模块入口
│   │   ├── base.py              #   抽象基类 + Message/LLMResponse 数据结构
│   │   ├── factory.py           #   工厂类（根据 model_key 创建客户端）
│   │   ├── openai_client.py     #   OpenAI API 客户端
│   │   ├── anthropic_client.py  #   Anthropic Claude API 客户端
│   │   ├── gemini_client.py     #   Google Gemini API 客户端
│   │   ├── dashscope_client.py  #   阿里云 DashScope（通义千问）客户端
│   │   └── ollama_client.py     #   Ollama 本地模型客户端
│   │
│   ├── relationship_types.py    # 关系类型系统（抽象基类 + 5 种实现）
│   ├── chat_engine.py           # 对话引擎（加载 Skill、构造 System Prompt）
│   ├── wechat_parser.py         # 微信聊天记录解析器
│   ├── photo_analyzer.py        # 照片 EXIF 信息提取
│   ├── skill_writer.py          # Skill 文件管理（目录初始化、组合 SKILL.md）
│   └── prompt_loader.py         # 提示词模板加载器
│
├── prompts/                     # 提示词模板
│   ├── memory_analyzer/         # 记忆分析器（每关系类型独立文件）
│   │   ├── ex_partner.md
│   │   ├── friend.md
│   │   ├── family.md
│   │   ├── colleague.md
│   │   └── idol.md
│   ├── persona_builder/         # 性格构建器（每关系类型独立文件）
│   │   ├── ex_partner.md
│   │   ├── friend.md
│   │   ├── family.md
│   │   ├── colleague.md
│   │   └── idol.md
│   ├── correction_handler.md    # 对话纠正处理器
│   └── merger.md                # 增量合并处理器
│
├── personas/                    # 生成的 Persona Skill（gitignored）
│   └── {slug}/                  # 人物标识符目录
│       ├── SKILL.md             #     完整 Skill（可直接运行）
│       ├── memory.md            #     Part A: 关系记忆
│       ├── persona.md           #     Part B: 人物性格
│       ├── meta.json            #     元信息
│       ├── versions/            #     版本历史
│       │   └── v1_20240115_143022/
│       └── memories/            #     原始材料存档
│           ├── chats/
│           ├── photos/
│           └── social/
│
├── docs/                        # 文档
│   ├── IMPLEMENTATION.md        #   技术实现文档
│   ├── FLOW_GUIDE.md            #   完整流程说明文档
│   └── PROMPTS_USAGE.md         #   提示词使用说明
│
├── API_USAGE.md                 # API 使用指南
├── LICENSE                      # MIT 许可证
└── README.md                    # 项目自述文件
```

---

## 核心架构

### 分层设计

```
┌──────────────────────────────────────────────────┐
│                 用户交互层                         │
│   create_persona.py     chat.py                   │
└──────────────────────┬───────────────────────────┘
                       │
┌──────────────────────▼───────────────────────────┐
│                 核心逻辑层                         │
│   relationship_types.py    chat_engine.py         │
│   prompt_loader.py          skill_writer.py       │
└──────────────────────┬───────────────────────────┘
                       │
┌──────────────────────▼───────────────────────────┐
│                 基础设施层                         │
│   config/settings.py    llm/ (6 clients)          │
│   wechat_parser.py       photo_analyzer.py        │
└──────────────────────┬───────────────────────────┘
                       │
┌──────────────────────▼───────────────────────────┐
│                 数据存储层                         │
│   personas/{slug}/{SKILL.md,memory.md,persona.md} │
└──────────────────────────────────────────────────┘
```

### 关系类型系统

`RelationshipType` 抽象基类定义了 5 种关系类型的通用接口。每种类型独立实现：

```
RelationshipType (ABC)
├── ExPartnerType    # 前任/恋人  💔
├── FriendType       # 朋友       🤝
├── FamilyType       # 家人       🏠
├── ColleagueType    # 同事       💼
└── IdolType         # 偶像/角色  ⭐
```

### LLM 客户端工厂

支持 5 种 Provider，通过工厂模式创建：

```
LLMFactory.create_client(model_key)
    ├── "openai/..."   → OpenAIClient
    ├── "anthropic/..." → AnthropicClient
    ├── "gemini/..."   → GeminiClient
    ├── "qwen/..."     → DashScopeClient
    └── "ollama/..."   → OllamaClient
```

---

## 数据流

### 创建流程

```
选择关系类型 → 填写信息 → 导入原材料 → AI 分析 → 写入文件
                                    ↓
                              (可选，需聊天记录)
```

### 对话流程

```
用户输入 → 构造 System Prompt (memory + persona) → 调用 LLM API → 输出回复
```

---

## 模块依赖关系

```
chat.py
  └── chat_engine.py
        ├── config/settings.py
        └── llm/factory.py
              ├── llm/base.py
              ├── llm/openai_client.py
              ├── llm/anthropic_client.py
              ├── llm/gemini_client.py
              ├── llm/dashscope_client.py
              └── llm/ollama_client.py

create_persona.py
  ├── relationship_types.py
  ├── skill_writer.py
  ├── prompt_loader.py
  ├── wechat_parser.py
  ├── photo_analyzer.py
  ├── config/settings.py
  └── llm/factory.py
```

---

## 已移除/归档文件

| 文件 | 位置 | 原因 |
|------|------|------|
| `qq_parser.py` | → `archive/tools/` | 未被导入，功能已内联 |
| `social_parser.py` | → `archive/tools/` | 未被导入，功能已内联 |
| `version_manager.py` | → `archive/tools/` | 未被导入，未集成 |
| `INSTALL.md` | → `archive/docs/` | 过时的 Claude Code 安装说明 |
| `.qoder/` | → `archive/qoder/` | 自动生成的 Wiki 文档 |

详见 [`archive/README.md`](../archive/README.md)。
