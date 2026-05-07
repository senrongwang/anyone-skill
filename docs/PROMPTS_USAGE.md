# 提示词系统使用说明

## 概述

本项目已实现模块化的提示词管理系统，支持5种关系类型的记忆分析和人物性格构建。

## 目录结构

```
prompts/
├── memory_analyzer/           # 记忆分析器（按关系类型）
│   ├── ex_partner.md          # 前任/恋人
│   ├── friend.md              # 朋友
│   ├── family.md              # 家人
│   ├── colleague.md           # 同事
│   └── idol.md                # 偶像/角色
├── persona_builder/           # 人物性格构建器（待创建）
│   └── (各关系类型文件)
├── correction_handler.md      # 通用纠正处理器
├── merger.md                  # 通用合并工具
└── intake.md                  # 信息收集模板
```

## 使用方式

### 1. 在代码中加载提示词

```python
from tools.prompt_loader import load_prompt

# 加载朋友关系的记忆分析器
prompt = load_prompt('friend', 'memory_analyzer')

# 加载前任的人物性格构建器
prompt = load_prompt('ex_partner', 'persona_builder')
```

### 2. 自动AI分析（create_persona.py）

当你在 `create_persona.py` 中导入原始材料（聊天记录等）时，系统会自动：

1. 检测是否有足够的原始内容（>100字符）
2. 加载对应关系类型的记忆分析器提示词
3. 调用 OpenAI GPT-4o 进行智能分析
4. 自动填充记忆字段

如果AI分析失败，会降级使用基础模板。

### 3. 手动测试

运行测试脚本验证提示词系统：

```bash
python test_prompts.py
```

## 各关系类型的记忆维度

### 🤝 朋友 (Friend)
- 相识经历
- 共同爱好 🎯
- 难忘经历 ⭐
- 互相支持 💪
- 常聚地点 📍
- 友情仪式 🎊
- 日常互动模式
- Inside Jokes

### 🏠 家人 (Family)
- 成长记忆 👶
- 关怀方式 ❤️
- 家庭传统 🏠
- 人生教诲 📚
- 拿手菜/味道 🍜
- 变化与衰老 ⏳
- 日常互动
- 家庭角色

### 💼 同事 (Colleague)
- 合作项目 💼
- 工作风格 ⚙️
- 职场互动 💬
- 危机时刻 🔥
- 工作之外 🍻
- 职业影响 📈
- 职场关系动态

### ⭐ 偶像/角色 (Idol)
- 人物弧线 📖
- 经典时刻 ✨
- 人物关系 🤝
- 经典语录 💬
- 粉丝记忆 🌟
- 个人理解 💭
- 外在特征
- 内在特质

### 💔 前任/恋人 (Ex-Partner)
- 关系时间线 💑
- 日常模式 📱
- 共同经历 🎡
- 饮食偏好 🍜
- 兴趣爱好 🎮
- 争吵模式 ⚡
- 甜蜜瞬间 💕
- 分手相关 💔

## 扩展指南

### 添加新的关系类型

1. 在 `tools/relationship_types.py` 中创建新的关系类型类
2. 在 `prompts/memory_analyzer/` 下创建对应的提示词文件
3. 在 `prompts/persona_builder/` 下创建对应的提示词文件（可选）
4. 更新 `PromptLoader` 中的 `type_mapping`

### 修改现有提示词

直接编辑 `prompts/memory_analyzer/` 或 `prompts/persona_builder/` 下的对应文件即可。

### 添加新的任务类型

1. 在 `prompts/` 下创建新的子目录（如 `sentiment_analyzer/`）
2. 为各关系类型创建对应的提示词文件
3. 在 `PromptLoader.list_available_prompts()` 中添加检查逻辑

## 注意事项

1. **API Key 配置**：AI分析功能需要配置 OpenAI API Key
2. **降级机制**：如果AI分析失败，系统会自动使用基础模板
3. **提示词格式**：所有提示词文件必须是 UTF-8 编码的 Markdown 格式
4. **输出格式**：提示词中应明确指定输出的 Markdown 格式，便于后续解析

## 故障排除

### 问题：提示词加载失败

```python
FileNotFoundError: 找不到提示词文件: memory_analyzer/friend.md
```

**解决**：检查文件是否存在于正确路径，确保文件名和关系类型匹配。

### 问题：AI分析超时

```
Request timed out.
```

**解决**：
- 检查网络连接
- 确认 API Key 有效
- 系统会自动降级到基础模板

### 问题：字段未被填充

如果生成的 `memory.md` 中某些字段仍然是"待补充"：

1. 检查原始材料是否包含相关信息
2. 调整提示词中的提取维度描述
3. 增加 `max_tokens` 参数（当前为3000）
4. 尝试更换更强的模型（如 gpt-4o）

## 未来改进方向

1. ✅ 已完成：模块化提示词管理
2. ✅ 已完成：多关系类型支持
3. ✅ 已完成：自动AI分析集成
4. ⏳ 待完成：persona_builder 提示词创建
5. ⏳ 待完成：支持流式输出显示分析进度
6. ⏳ 待完成：添加分析结果预览和编辑功能
7. ⏳ 待完成：支持自定义提示词模板
