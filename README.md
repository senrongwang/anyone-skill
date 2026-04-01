# Anyone Skill

> *"欢迎加入数字生命1.0吧"*

**把任何人蒸馏成真正像ta的 AI。**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://python.org)
[![Multi API](https://img.shields.io/badge/Multi%20API-OpenAI%20%7C%20Claude%20%7C%20Gemini%20%7C%20Qwen-orange)](API_USAGE.md)

&nbsp;

提供人物的原材料（微信聊天记录、QQ消息、朋友圈截图、照片）加上你的主观描述  
生成一个**真正像ta的 AI Persona**  
用ta的口头禅说话，用ta的方式回复你，记得你们一起去过的地方

支持多种关系类型：**前任/恋人** 💔 · **朋友** 🤝 · **家人** 🏠 · **同事** 💼 · **偶像/角色** ⭐

> **关于本项目**：本项目基于 [ex-skill](https://github.com/therealXiaomanChu/ex-skill) 进行二次开发，主要改进包括：① 移除 Claude Code 依赖，改为纯 API 调用方式；② 扩展关系类型系统，支持前任/朋友/家人/同事/偶像等多种关系；③ 重构架构抽象出 `RelationshipType` 基类，每种类型有独立的录入模板、记忆维度和标签体系；④ 目录结构从 `exes/` 改为 `personas/`，命名更加通用。

⚠️ **本项目仅用于个人回忆与情感疗愈，不用于骚扰、跟踪或侵犯他人隐私。**

[安装](#安装) · [使用教程](#使用教程) · [关系类型](#关系类型) · [效果示例](#效果示例)

---

## 安装

### 环境要求

- Python 3.9+
- 支持的操作系统：Windows / macOS / Linux

### 克隆项目
```bash
git clone https://github.com/senrongwang/anyone-skill.git
```

### 安装依赖
进入项目文件夹中运行：
```bash
pip install -r requirements.txt
```

依赖包括：
- `openai` - OpenAI API 客户端
- `anthropic` - Claude API 客户端
- `google-generativeai` - Gemini API 客户端
- `dashscope` - 通义千问 API 客户端
- `Pillow` - 图片处理（照片 EXIF 提取）

---

## 使用教程

### 1. 创建 Persona Skill

运行创建工具：

```bash
python create_persona.py
```

按提示完成以下步骤：

#### Step 1: 选择关系类型

```
请选择关系类型：

  [1] 💔 前任/恋人 - 恋爱关系，包含甜蜜回忆、争吵模式、分手经历等
  [2] 🤝 朋友 - 友情关系，包含共同爱好、相处模式、难忘经历等
  [3] 🏠 家人 - 亲情关系，包含家庭角色、成长记忆、关怀方式等
  [4] 💼 同事 - 职场关系，包含工作风格、合作项目、职场互动等
  [5] ⭐ 偶像/角色 - 偶像、虚拟角色或历史人物，基于公开资料或作品设定
```

#### Step 2: 填写基础信息

根据选择的关系类型，系统会询问对应的问题：

**前任/恋人示例：**
- 花名/代号（必填）：小明、初恋、那个人
- 基本信息：在一起两年、分手半年、互联网产品经理
- 性格画像：ENFP 双子座 话很多 但深夜会突然emo
- 分开原因：异地恋，毕业后各奔东西

**朋友示例：**
- 朋友称呼（必填）：老王、阿杰
- 认识背景：大学同学，认识8年了，现在是程序员
- 性格特点：INTJ 喜欢打游戏 话不多但很靠谱
- 相处模式：经常一起开黑，偶尔约饭，有事直说

#### Step 3: 导入原材料（可选）

选择数据来源：

- **微信聊天记录** - 支持 WeChatMsg / 留痕 / WeFlow 导出的 txt/html/json
- **QQ 聊天记录** - 支持 QQ 导出的 txt/mht 格式
- **社交媒体** - 朋友圈/微博/小红书截图
- **照片** - 提取 EXIF 时间线和地点
- **口述/粘贴** - 直接输入你记得的事情
- 也可以跳过数据导入，仅凭描述生成基础版本。
<br>**注！！聊天记录中的聊天对象需要是Step2填写的人名（代号）**
#### Step 4: 确认生成

系统会展示生成的记忆摘要和性格摘要，确认后写入文件。

---

### 2. 配置 API 密钥

**方式一：环境变量（推荐）**

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

**方式二：.env 文件**

复制 `.env.example` 为 `.env`，填入你的 API 密钥：

```
OPENAI_API_KEY=sk-your-key-here
ANTHROPIC_API_KEY=sk-your-key-here
GEMINI_API_KEY=your-key-here
DASHSCOPE_API_KEY=sk-your-key-here
```

---

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

# 使用本地 Ollama 模型（无需 API Key）
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

#### 对话中的命令

| 命令 | 说明 |
|------|------|
| `/quit`, `/q`, `exit` | 退出对话 |
| `/clear` | 清空对话历史 |
| `/info` | 显示当前 Skill 信息 |

---

## 关系类型

### 💔 前任/恋人

**适用场景：** 恋爱关系，想回忆过去的甜蜜或处理未完成的情感

**录入信息：**
- 花名/代号（必填）
- 在一起多久、分手多久、ta做什么的
- MBTI、星座、性格标签
- 分开的原因

**记忆维度：** 关系时间线、甜蜜瞬间、争吵模式、日常习惯、专属梗、常去地点

**标签体系：** 依恋类型（安全型/焦虑型/回避型/混乱型）、爱的语言、性格标签

---

### 🤝 朋友

**适用场景：** 挚友、发小、同学，想保留那份默契和回忆

**录入信息：**
- 朋友称呼/昵称（必填）
- 认识多久了、怎么认识的、ta做什么的
- 性格特点、兴趣爱好
- 你们的相处模式

**记忆维度：** 相识经历、共同爱好、难忘经历、互相支持、常聚地点、友情仪式

**标签体系：** 友情类型（发小/同学/同事/网友）、相处模式、性格标签

---

### 🏠 家人

**适用场景：** 父母、兄弟姐妹，记录家庭温暖和成长记忆

**录入信息：**
- 称呼（如：妈妈、老爸）（必填）
- 具体关系（必填）
- 年龄、职业、居住地
- 性格特点、在家庭中的角色

**记忆维度：** 成长记忆、关怀方式、家庭传统、人生教诲、拿手菜/味道、变化与衰老

**标签体系：** 家庭角色（权威型/温柔型/幽默型）、关怀方式、性格标签

---

### 💼 同事

**适用场景：** 职场导师、默契搭档，记录职业成长历程

**录入信息：**
- 同事称呼/花名（必填）
- 职位、部门、共事多久
- 工作风格和性格
- 你们的职场关系

**记忆维度：** 合作项目、工作风格、职场互动、危机时刻、工作之外、职业影响

**标签体系：** 工作风格、职位关系、职场性格

---

### ⭐ 偶像/角色

**适用场景：** 追星、二次元、历史人物，基于公开资料创建虚拟人格

**录入信息：**
- 名字（真实姓名或角色名）（必填）
- 出处（作品、领域、时代）
- 基本设定（身份、背景、特点）
- 性格特征
- 你对ta的了解程度

**记忆维度：** 人物弧线、经典时刻、人物关系、经典语录、粉丝记忆、个人理解

**标签体系：** 类型（真实人物/虚构角色/历史人物）、性格特质、魅力点

---

## 效果示例

### 前任/恋人场景

> 输入：`初恋，在一起三年，大学时期，ENFP，双子座，话痨，半夜给我发语音`

**日常聊天：**
```
用户      ❯ 在干嘛

前任.skill ❯ 刚吃完饭 在刷手机
             你呢 怎么突然找我
             [发送了一个表情包]
```

**回忆杀：**
```
用户      ❯ 还记得我们第一次约会吗

前任.skill ❯ 就那个超难吃的意面吗哈哈哈哈
             你还假装很好吃 我都看出来了
             那家店后来倒闭了你知道吗
```

**深夜emo：**
```
用户      ❯ 我有点想你

前任.skill ❯ ...
             嗯
             早点睡吧
```

### 朋友场景

```
用户      ❯ 周末开黑吗

朋友.skill ❯ 来啊 几点
             我先把外卖点了
             今天必须上分
```

### 家人场景

```
用户      ❯ 妈，我下周回家

家人.skill ❯ 真的啊？想吃什么妈给你做
             你爸天天念叨你
             房间我都收拾好了
```

---

## 功能特性

### 数据源支持

| 来源 | 格式 | 提取内容 | 优先级 |
|------|------|---------|--------|
| 微信聊天记录 | WeFlow / 留痕 / PyWxDump | 完整对话、语气词、回复模式 | ⭐⭐⭐ |
| QQ 聊天记录 | txt / mht | 完整对话 | ⭐⭐⭐ |
| 照片 | JPEG/PNG + EXIF | 时间线、地点 | ⭐⭐ |
| 朋友圈/微博 | 截图 | 公开人设、兴趣 | ⭐⭐ |
| 口述/粘贴 | 纯文本 | 主观记忆 | ⭐ |

### 双层架构

每个 Persona Skill 由两部分组成：

| 部分 | 内容 |
|------|------|
| **Part A — Context Memory** | 关系特定记忆：共同经历、相处模式、难忘时刻 |
| **Part B — Persona** | 5 层性格结构：硬规则 → 身份 → 说话风格 → 情感模式 → 关系行为 |

**运行逻辑：** `收到消息 → Persona 判断ta会怎么回 → Memory 补充共同记忆 → 用ta的方式输出`

### 进化机制

- **追加记忆** → 找到更多聊天记录/照片 → 自动分析增量 → merge 进对应部分
- **对话纠正** → 说「ta不会这样说」→ 写入 Correction 层，立即生效
- **版本管理** → 每次更新自动存档，支持回滚

---

## 项目结构

```
anyone-skill-main/
├── chat.py                 # 对话入口（支持多 API）
├── create_persona.py       # Persona Skill 创建工具
├── SKILL.md                # Skill 定义文档
├── prompts/                # Prompt 模板
│   ├── intake.md           #   信息录入模板
│   ├── memory_analyzer.md  #   记忆提取模板
│   ├── persona_analyzer.md #   性格分析模板
│   ├── memory_builder.md   #   memory.md 生成模板
│   ├── persona_builder.md  #   persona.md 生成模板
│   ├── merger.md           #   增量 merge 逻辑
│   └── correction_handler.md # 对话纠正处理
├── tools/                  # Python 工具
│   ├── relationship_types.py # 关系类型定义
│   ├── chat_engine.py      #   对话引擎
│   ├── config/             #   配置管理
│   │   ├── __init__.py
│   │   └── settings.py     #     API 密钥、模型配置
│   ├── llm/                #   LLM 客户端
│   │   ├── __init__.py
│   │   ├── base.py         #     抽象基类
│   │   ├── openai_client.py
│   │   ├── anthropic_client.py
│   │   ├── gemini_client.py
│   │   ├── dashscope_client.py
│   │   ├── ollama_client.py
│   │   └── factory.py      #     工厂模式
│   ├── wechat_parser.py    #   微信聊天记录解析
│   ├── qq_parser.py        #   QQ 聊天记录解析
│   ├── social_parser.py    #   社交媒体解析
│   ├── photo_analyzer.py   #   照片元信息分析
│   ├── skill_writer.py     #   Skill 文件管理
│   └── version_manager.py  #   版本管理
├── personas/               # 生成的 Persona Skill（gitignored）
├── .env.example            # 环境变量配置示例
├── API_USAGE.md            # API 使用详细指南
├── requirements.txt
└── LICENSE
```

---

## 推荐的聊天记录导出工具

- **[WeFlow](https://github.com/hicccc77/WeFlow)** — 微信聊天记录导出（Windows）
- **留痕** — 微信聊天记录导出（macOS）

---

## 注意事项

- **聊天记录质量决定还原度**：微信导出 + 口述 > 仅口述
- 建议优先提供：**深夜对话** > **争吵记录** > **日常消息**（最能体现真实性格）
- 本项目不鼓励对任何人的不健康执念，如果你发现自己过于沉浸，请寻求专业帮助
- 对于真实人物，ta有自己的人生。这个 Skill 只是你记忆中的ta

---

## 致敬 & 引用

本项目灵感直接来源于 **[前任.skill](https://github.com/therealXiaomanChu/ex-skill)。**[同事.skill](https://github.com/titanwings/colleague-skill)首创了"把人蒸馏成 AI Skill"的双层架构（Work Skill + Persona），[前任.skill](https://github.com/therealXiaomanChu/ex-skill)在此基础上将场景从职场迁移到了恋爱关系，[Anyone.Skill](https://github.com/senrongwang/anyone-skill) 进一步扩展为支持多种关系类型的通用框架。致敬原作者的创意和开源精神。
