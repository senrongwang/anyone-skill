# 前任.skill 多 API 使用指南

本项目已改造为支持多种 LLM API 的独立应用，不再依赖 Claude Code。

## 支持的 API

| Provider | 模型示例 | 需要 API Key |
|----------|----------|-------------|
| OpenAI | gpt-4, gpt-4o, gpt-3.5-turbo | ✅ |
| Anthropic | claude-3-opus, claude-3-sonnet, claude-3-haiku | ✅ |
| Google | gemini-pro, gemini-1.5-flash | ✅ |
| DashScope | qwen-max, qwen-plus, qwen-turbo | ✅ |
| Ollama | llama2, mistral, qwen2.5 等本地模型 | ❌ |

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置 API 密钥

**方式一：环境变量**

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

```bash
cp .env.example .env
# 编辑 .env 文件填入密钥
```

### 3. 使用对话工具

```bash
# 列出所有可用的前任 Skill
python chat.py --list-skills

# 列出所有可用的模型
python chat.py --list-models

# 使用 OpenAI GPT-4 对话
python chat.py --ex 小明 --model openai/gpt-4

# 使用 Claude 对话
python chat.py --ex 初恋 --model anthropic/claude-3-opus

# 使用 Gemini 对话
python chat.py --ex 前任 --model gemini/gemini-pro

# 使用通义千问对话
python chat.py --ex 前任 --model qwen/qwen-max
python chat.py --ex 前任 --model qwen/qwen-plus
python chat.py --ex 前任 --model qwen/qwen-turbo

# 使用本地 Ollama 模型
python chat.py --ex 前任 --model ollama/llama2
```

## 命令行参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--ex`, `--slug` | 前任 Skill 代号 | 必填 |
| `--model`, `-m` | 模型标识 | openai/gpt-4o |
| `--list-skills`, `-l` | 列出所有 Skill | - |
| `--list-models` | 列出所有模型 | - |
| `--no-stream` | 禁用流式输出 | - |
| `--temperature`, `-t` | 温度参数 | 0.7 |
| `--max-tokens` | 最大 token 数 | 2000 |

## 对话命令

在对话过程中，可以使用以下命令：

| 命令 | 说明 |
|------|------|
| `/quit`, `/q`, `exit` | 退出对话 |
| `/clear` | 清空对话历史 |
| `/info` | 显示当前 Skill 信息 |

## 使用第三方 API（兼容 OpenAI 格式）

如果你想使用兼容 OpenAI 格式的第三方 API（如 DeepSeek、Moonshot、Azure 等），可以修改配置：

```python
# 在代码中创建自定义配置
from tools.config.settings import ModelConfig
from tools.llm.factory import LLMFactory

config = ModelConfig(
    provider='openai',
    model='deepseek-chat',
    api_key='your-api-key',
    base_url='https://api.deepseek.com/v1',  # 自定义 API 端点
    temperature=0.7,
    max_tokens=2000
)

client = LLMFactory.create_client(config=config)
```

## 本地模型（Ollama）

### 安装 Ollama

访问 https://ollama.ai 下载并安装 Ollama。

### 拉取模型

```bash
ollama pull llama2
ollama pull mistral
ollama pull qwen2.5
```

### 使用

```bash
python chat.py --ex 前任 --model ollama/llama2
```

## 故障排除

### ImportError: 请先安装 openai

```bash
pip install openai anthropic google-generativeai
```

### 找不到前任 Skill

确保你已经使用 `create-ex` 创建了 Skill，并且 Skill 文件位于 `exes/{slug}/` 目录下。

### API Key 无效

检查环境变量或 .env 文件中的 API Key 是否正确设置。

### Ollama 连接失败

确保 Ollama 服务已启动：

```bash
ollama serve
```

## 架构说明

```
tools/
├── config/           # 配置管理
│   ├── __init__.py
│   └── settings.py   # API 密钥、模型配置
├── llm/              # LLM 客户端
│   ├── __init__.py
│   ├── base.py       # 抽象基类
│   ├── openai_client.py
│   ├── anthropic_client.py
│   ├── gemini_client.py
│   ├── ollama_client.py
│   └── factory.py    # 工厂模式
├── chat_engine.py    # 对话引擎
└── ...               # 原有工具
```

## 与 Claude Code 版本的区别

| 功能 | Claude Code 版本 | 多 API 版本 |
|------|-----------------|-------------|
| 运行环境 | Claude Code | 独立 Python 应用 |
| 触发方式 | `/create-ex`, `/{slug}` | `python chat.py --ex {slug}` |
| 支持模型 | Claude  only | OpenAI, Claude, Gemini, Ollama |
| 数据解析 | ✅ 相同 | ✅ 相同 |
| Skill 格式 | AgentSkills 标准 | 独立格式（兼容） |

原有数据解析工具（微信/QQ/照片解析器）完全兼容，可以继续使用。
