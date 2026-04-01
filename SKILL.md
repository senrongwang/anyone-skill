---
name: create-persona
description: Distill anyone into an AI Skill. Import chat history, photos, social media, generate Context Memory + Persona, with continuous evolution. | 把任何人（前任/朋友/家人/同事/偶像）蒸馏成 AI Skill，导入聊天记录、照片、社交媒体，生成记忆 + 性格，支持持续进化。
argument-hint: [persona-name-or-slug]
version: 2.0.0
user-invocable: true
---

> **Language / 语言**: This skill supports both English and Chinese. Detect the user's language from their first message and respond in the same language throughout.
>
> 本 Skill 支持中英文。根据用户第一条消息的语言，全程使用同一语言回复。

# Anyone Skill 使用指南

## 独立运行方式（推荐）

无需 Claude Code，直接通过命令行运行，支持 OpenAI、Claude、Gemini、通义千问等多种 LLM API。

### 1. 创建 Persona Skill

```bash
python create_persona.py
```

按提示操作：
1. **选择关系类型** - 前任/朋友/家人/同事/偶像
2. **填写基础信息** - 根据关系类型回答对应问题
3. **导入原材料**（可选）- 微信/QQ聊天记录、照片、社交媒体截图
4. **确认生成** - 预览并确认生成 Skill

### 2. 配置 API 密钥

**环境变量方式：**

```bash
# Windows PowerShell
$env:OPENAI_API_KEY="sk-your-key-here"
$env:ANTHROPIC_API_KEY="sk-your-key-here"
$env:GEMINI_API_KEY="your-key-here"
$env:DASHSCOPE_API_KEY="sk-your-key-here"

# Linux/macOS
export OPENAI_API_KEY="sk-your-key-here"
export ANTHROPIC_API_KEY="sk-your-key-here"
export GEMINI_API_KEY="your-key-here"
export DASHSCOPE_API_KEY="sk-your-key-here"
```

**或 .env 文件方式：**

复制 `.env.example` 为 `.env`，填入你的 API 密钥。

### 3. 运行对话

```bash
# 列出所有可用的 Persona Skill
python chat.py --list-skills

# 使用 OpenAI GPT-4 对话
python chat.py --persona 小明 --model openai/gpt-4o

# 使用 Claude 对话
python chat.py --persona 初恋 --model anthropic/claude-3-opus

# 使用 Gemini 对话
python chat.py --persona 老王 --model gemini/gemini-pro

# 使用通义千问对话
python chat.py --persona 老妈 --model qwen/qwen-max

# 使用本地 Ollama 模型
python chat.py --persona 偶像 --model ollama/llama2
```

#### 支持的模型

| Provider | 模型示例 | 需要 API Key |
|----------|----------|-------------|
| OpenAI | gpt-4, gpt-4o, gpt-3.5-turbo | ✅ |
| Anthropic | claude-3-opus, claude-3-sonnet, claude-3-haiku | ✅ |
| Google | gemini-pro, gemini-1.5-flash | ✅ |
| DashScope | qwen-max, qwen-plus, qwen-turbo | ✅ |
| Ollama | llama2, mistral, qwen2.5 等 | ❌ |

#### 对话命令

在对话过程中，可以使用以下命令：

| 命令 | 说明 |
|------|------|
| `/quit`, `/q`, `exit` | 退出对话 |
| `/clear` | 清空对话历史 |
| `/info` | 显示当前 Skill 信息 |

---

## 关系类型

### 💔 前任/恋人
恋爱关系，包含甜蜜回忆、争吵模式、分手经历等。

**录入信息：**
- 花名/代号（必填）
- 基本信息（在一起多久、分手多久、ta做什么的）
- 性格画像（MBTI、星座、性格标签）
- 分开的原因

**记忆维度：**
- 关系时间线
- 甜蜜瞬间
- 争吵模式
- 日常习惯
- 专属梗
- 常去地点

### 🤝 朋友
友情关系，包含共同爱好、相处模式、难忘经历等。

**录入信息：**
- 朋友称呼/昵称（必填）
- 认识多久了、怎么认识的、ta做什么的
- 性格特点（MBTI、兴趣爱好）
- 你们的相处模式

**记忆维度：**
- 相识经历
- 共同爱好
- 难忘经历
- 互相支持
- 常聚地点
- 友情仪式

### 🏠 家人
亲情关系，包含家庭角色、成长记忆、关怀方式等。

**录入信息：**
- 称呼（如：妈妈、老爸）（必填）
- 具体关系（必填）
- 基本信息（年龄、职业、居住地）
- 性格特点
- 在家庭中的角色

**记忆维度：**
- 成长记忆
- 关怀方式
- 家庭传统
- 人生教诲
- 拿手菜/味道
- 变化与衰老

### 💼 同事
职场关系，包含工作风格、合作项目、职场互动等。

**录入信息：**
- 同事称呼/花名（必填）
- 职位、部门、共事多久
- 工作风格和性格
- 你们的职场关系

**记忆维度：**
- 合作项目
- 工作风格
- 职场互动
- 危机时刻
- 工作之外
- 职业影响

### ⭐ 偶像/角色
偶像、虚拟角色或历史人物，基于公开资料或作品设定。

**录入信息：**
- 名字（真实姓名或角色名）（必填）
- 出处（作品、领域、时代）
- 基本设定（身份、背景、特点）
- 性格特征
- 你对ta的了解程度

**记忆维度：**
- 人物弧线
- 经典时刻
- 人物关系
- 经典语录
- 粉丝记忆
- 个人理解

---

## 数据源支持

| 来源 | 格式 | 提取内容 |
|------|------|---------|
| 微信聊天记录 | WeChatMsg / 留痕 / PyWxDump 导出 | 完整对话、语气词、回复模式 |
| QQ 聊天记录 | txt / mht 导出 | 完整对话 |
| 朋友圈/微博 | 截图 | 公开人设、兴趣 |
| 照片 | JPEG/PNG + EXIF | 时间线、地点 |
| 口述/粘贴 | 纯文本 | 主观记忆 |

### 推荐的聊天记录导出工具

- **[WeChatMsg](https://github.com/LC044/WeChatMsg)** — 微信聊天记录导出（Windows）
- **[PyWxDump](https://github.com/xaoyaoo/PyWxDump)** — 微信数据库解密导出（Windows）
- **留痕** — 微信聊天记录导出（macOS）

---

## 安全边界（⚠️ 重要）

1. **仅用于个人回忆与情感疗愈**，不用于骚扰、跟踪或任何侵犯他人隐私的目的
2. **不主动联系真人**：生成的 Skill 是对话模拟，不会也不应替代真实沟通
3. **不鼓励不健康执念**：如果用户表现出不健康的执念，温和提醒并建议寻求专业帮助
4. **隐私保护**：所有数据仅本地存储，不上传任何服务器
5. **Layer 0 硬规则**：生成的 Skill 不会说出现实中的人绝不可能说的话，除非有原材料证据支持

---

## 生成的 Skill 结构

每个 Persona Skill 由两部分组成：

| 部分 | 内容 |
|------|------|
| **Part A — Context Memory** | 关系特定记忆：共同经历、相处模式、难忘时刻 |
| **Part B — Persona** | 5 层性格结构：硬规则 → 身份 → 说话风格 → 情感模式 → 关系行为 |

运行逻辑：`收到消息 → Persona 判断ta会怎么回 → Memory 补充共同记忆 → 用ta的方式输出`

---

## 文件结构

```
personas/
  └── {slug}/
      ├── SKILL.md          # 完整组合版，可直接运行
      ├── memory.md         # Part A：关系记忆
      ├── persona.md        # Part B：人物性格
      ├── meta.json         # 元信息（包含 relationship_type）
      ├── versions/         # 历史版本存档
      └── memories/         # 原始材料存放
          ├── chats/
          ├── photos/
          └── social/
```

---

## 管理命令

```bash
# 列出所有 Persona Skill
python chat.py --list-skills

# 使用 skill_writer 工具
python tools/skill_writer.py --action list --base-dir ./personas

# 版本回滚
python tools/version_manager.py --action rollback --slug {slug} --version {version} --base-dir ./personas
```

---

# English Version

## Standalone Usage (Recommended)

No Claude Code required. Run directly via command line with support for OpenAI, Claude, Gemini, Qwen, and other LLM APIs.

### 1. Create Persona Skill

```bash
python create_persona.py
```

Follow the prompts:
1. **Select relationship type** - Ex-Partner/Friend/Family/Colleague/Idol
2. **Fill in basic info** - Answer questions based on relationship type
3. **Import source materials** (optional) - WeChat/QQ chat logs, photos, social media screenshots
4. **Confirm generation** - Preview and confirm to generate Skill

### 2. Configure API Keys

**Environment Variables:**

```bash
# Windows PowerShell
$env:OPENAI_API_KEY="sk-your-key-here"
$env:ANTHROPIC_API_KEY="sk-your-key-here"

# Linux/macOS
export OPENAI_API_KEY="sk-your-key-here"
export ANTHROPIC_API_KEY="sk-your-key-here"
```

**Or use .env file:**

Copy `.env.example` to `.env` and fill in your API keys.

### 3. Start Chat

```bash
# List all Persona Skills
python chat.py --list-skills

# Chat with OpenAI
python chat.py --persona xiaoming --model openai/gpt-4o

# Chat with Claude
python chat.py --persona friend --model anthropic/claude-3-opus

# Chat with local Ollama model
python chat.py --persona idol --model ollama/llama2
```

### Supported Models

| Provider | Examples | API Key Required |
|----------|----------|-----------------|
| OpenAI | gpt-4, gpt-4o | ✅ |
| Anthropic | claude-3-opus, claude-3-sonnet | ✅ |
| Google | gemini-pro | ✅ |
| DashScope | qwen-max, qwen-plus | ✅ |
| Ollama | llama2, mistral | ❌ |

---

## Relationship Types

1. **Ex-Partner** 💔 - Romantic relationship with memories, conflict patterns, breakup
2. **Friend** 🤝 - Friendship with shared hobbies, adventures, support moments
3. **Family** 🏠 - Family relationship with childhood memories, care expressions
4. **Colleague** 💼 - Professional relationship with projects, work style
5. **Idol/Character** ⭐ - Public figure or fictional character based on source material

---

## Safety Boundaries

1. **For personal reflection and emotional healing only** — not for harassment or privacy invasion
2. **No real contact**: Generated Skills simulate conversation, they do not replace real communication
3. **No unhealthy attachment**: If showing signs of obsessive behavior, suggest professional help
4. **Privacy protection**: All data stored locally only
5. **Layer 0 hard rules**: Will not say things the real person would never say
