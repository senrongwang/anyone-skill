#!/usr/bin/env python3
"""Persona Skill 创建工具

独立于 Claude Code 的创建入口，通过命令行交互式创建 Persona Skill。
支持多种关系类型：前任、朋友、家人、同事、偶像等。

Usage:
    python create_persona.py
"""

import sys
import os
import json
from datetime import datetime
from pathlib import Path

# 添加 tools 目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from tools.config.settings import get_settings
from tools.skill_writer import init_skill, combine_skill
from tools.relationship_types import (
    select_relationship_type,
    get_relationship_type,
    RelationshipCategory,
    list_relationship_types
)
from tools.prompt_loader import load_prompt
from tools.llm.factory import LLMFactory
from tools.llm.base import Message


def print_banner():
    """打印欢迎信息"""
    print("""
╔══════════════════════════════════════════╗
║                                          ║
║     Anyone Skill - 人物蒸馏工具           ║
║                                          ║
║  把任何人（前任/朋友/家人/同事/偶像）      ║
║  蒸馏成真正像ta的 AI Skill                ║
║                                          ║
╚══════════════════════════════════════════╝
""")


def input_with_default(prompt: str, default: str = "") -> str:
    """带默认值的输入"""
    if default:
        result = input(f"{prompt} [默认: {default}]: ").strip()
        return result if result else default
    return input(f"{prompt}: ").strip()


def step1_select_relationship_type():
    """Step 1: 选择关系类型"""
    print("\n" + "="*50)
    print("Step 1: 选择关系类型")
    print("="*50)
    
    return select_relationship_type()


def step2_basic_info(rel_type):
    """Step 2: 基础信息录入"""
    print("\n" + "="*50)
    print(f"Step 2: 基础信息录入 - {rel_type.display_name}")
    print("="*50)
    
    questions = rel_type.get_intake_questions()
    info = {}
    
    for q in questions:
        if q.required:
            while True:
                if q.placeholder:
                    print(f"\n{q.question}")
                    print(f"   示例: {q.placeholder}")
                value = input(f"{q.key}: ").strip()
                if value:
                    info[q.key] = value
                    break
                print("   此项为必填，请重新输入。")
        else:
            if q.placeholder:
                print(f"\n{q.question}")
                print(f"   示例: {q.placeholder}")
            value = input(f"{q.key} (可选，直接回车跳过): ").strip()
            info[q.key] = value
    
    # 生成 slug
    name = info.get('name', 'unnamed')
    slug = name.lower().replace(" ", "-").replace("/", "-")
    info['slug'] = slug
    
    return info


def step3_import_sources(slug: str, name: str, rel_type):
    """Step 3: 原材料导入"""
    print("\n" + "="*50)
    print("Step 3: 原材料导入")
    print("="*50)
    print("""
原材料怎么提供？回忆越多，还原度越高。

  [A] 微信聊天记录导出
      支持多种导出工具的格式（txt/html/json）
      推荐工具：WeChatMsg、留痕、PyWxDump

  [B] QQ 聊天记录导出
      支持 QQ 导出的 txt/mht 格式

  [C] 社交媒体内容
      朋友圈截图、微博/小红书/ins 截图

  [D] 照片
      提取拍摄时间地点（JPEG/PNG 含 EXIF）

  [E] 直接粘贴/口述
      把你记得的事情告诉我
      比如：ta的口头禅、相处模式、难忘的经历

  [F] 跳过
      仅凭上面的基础信息生成

可以输入多个选项，如：A E
""")
    
    choices = input("选择数据来源: ").strip().upper()
    
    sources = []
    raw_content = []
    wechat_stats = None  # 用于保存微信统计分析
    
    if 'A' in choices:
        print("\n--- 微信聊天记录 ---")
        file_path = input("请输入微信聊天记录文件路径: ").strip()
        if file_path and os.path.exists(file_path):
            try:
                from tools.wechat_parser import parse_wechatmsg_txt, parse_plaintext, detect_format
                
                print(f"[调试] 正在解析文件: {file_path}")
                print(f"[调试] 目标名字: {name}")
                
                # 先读取前500字符看看格式
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    first_lines = f.read(500)
                print(f"[调试] 文件前500字符:\n{first_lines}\n")
                
                # 自动检测格式并选择正确的解析器
                fmt = detect_format(file_path)
                print(f"[调试] 检测到的格式: {fmt}")
                
                if fmt == 'plaintext':
                    result = parse_plaintext(file_path, name)
                elif fmt == 'liuhen':
                    from tools.wechat_parser import parse_liuhen_json
                    result = parse_liuhen_json(file_path, name)
                else:
                    result = parse_wechatmsg_txt(file_path, name)
                
                print(f"[调试] 解析结果: total_messages={result.get('total_messages')}, target_messages={result.get('target_messages')}")
                
                # 将结果转换为可读文本
                content_parts = []
                content_parts.append(f"### 微信聊天记录深度分析 - {name}")
                content_parts.append(f"总消息数：{result.get('total_messages', 'N/A')}")
                content_parts.append(f"{name}的消息数：{result.get('target_messages', 'N/A')}")
                
                analysis = result.get('analysis', {})
                
                # 语言风格
                content_parts.append("\n#### 语言风格")
                if analysis.get('top_particles'):
                    content_parts.append(f"口头禅/语气词：" + ", ".join([f"{w}({c}次)" for w, c in analysis['top_particles'][:5]]))
                if analysis.get('top_emojis'):
                    content_parts.append(f"常用Emoji：" + ", ".join([f"{e}({c}次)" for e, c in analysis['top_emojis'][:5]]))
                content_parts.append(f"平均消息长度：{analysis.get('avg_message_length', 'N/A')} 字")
                content_parts.append(f"消息风格：{'短句连发型' if analysis.get('message_style') == 'short_burst' else '长段落型'}")
                if analysis.get('response_pattern'):
                    content_parts.append(f"回应模式：{', '.join(analysis['response_pattern'])}")
                
                # 话题与兴趣
                if analysis.get('top_words'):
                    content_parts.append("\n#### 高频话题")
                    content_parts.append(f"常聊话题：" + ", ".join([f"{w}({c}次)" for w, c in analysis['top_words'][:8]]))
                
                # 常去地点
                if analysis.get('locations'):
                    content_parts.append("\n#### 常去地点")
                    content_parts.append(f"提及地点：" + ", ".join([f"{loc}({c}次)" for loc, c in analysis['locations'][:5]]))
                
                # 活动与兴趣
                if analysis.get('activities'):
                    content_parts.append("\n#### 共同活动/兴趣")
                    for i, activity in enumerate(analysis['activities'][:5], 1):
                        content_parts.append(f"{i}. {activity}")
                
                # 关心语句
                if analysis.get('care_messages'):
                    content_parts.append("\n#### 关心/情感表达")
                    for i, msg in enumerate(analysis['care_messages'][:5], 1):
                        content_parts.append(f'{i}. "{msg}"')
                
                # 时间偏好
                if analysis.get('time_references'):
                    content_parts.append("\n#### 时间偏好")
                    content_parts.append(f"常提及：{', '.join(analysis['time_references'][:5])}")
                
                # 这是用于最终保存的统计分析部分（不包含样本消息和原始对话）
                stats_only_content = "\n".join(content_parts)
                
                # 添加更多样本消息（增加到50条）- 仅用于LLM分析，不保存到最终文件
                if result.get('sample_messages'):
                    content_parts.append("\n#### 典型消息样本（前50条）")
                    sample_count = min(50, len(result['sample_messages']))
                    for i, msg in enumerate(result['sample_messages'][:sample_count], 1):
                        content_parts.append(f"{i}. {msg}")
                
                # 添加原始对话片段（如果有）- 仅用于LLM分析，不保存到最终文件
                if result.get('raw_conversations'):
                    content_parts.append("\n#### 原始对话片段")
                    content_parts.append("以下是部分原始对话记录，供参考说话风格和互动模式：")
                    content_parts.append("```")
                    # 限制原始对话的长度，避免超出token限制
                    raw_conv = result['raw_conversations']
                    if len(raw_conv) > 5000:
                        raw_conv = raw_conv[:5000] + "\n...（对话过长，已截断）"
                    content_parts.append(raw_conv)
                    content_parts.append("```")
                
                # 保存统计分析部分，供后续使用
                wechat_stats = stats_only_content
                
                raw_content.append("\n".join(content_parts))
                sources.append(file_path)
                print(f"✓ 已解析微信聊天记录（包含{result.get('total_messages', 'N/A')}条消息的统计分析 + 原始对话片段）")
            except Exception as e:
                print(f"✗ 解析失败: {e}")
                import traceback
                traceback.print_exc()
        else:
            print("文件不存在，跳过")
    
    if 'B' in choices:
        print("\n--- QQ 聊天记录 ---")
        file_path = input("请输入QQ聊天记录文件路径: ").strip()
        if file_path and os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                raw_content.append(f"## QQ聊天记录\n\n```\n{content[:5000]}...\n```")
                sources.append(file_path)
                print(f"✓ 已读取QQ聊天记录")
            except Exception as e:
                print(f"✗ 读取失败: {e}")
    
    if 'C' in choices:
        print("\n--- 社交媒体截图 ---")
        dir_path = input("请输入截图目录路径: ").strip()
        if dir_path and os.path.isdir(dir_path):
            try:
                # 简单列出目录中的图片文件
                image_files = []
                for ext in ['*.jpg', '*.jpeg', '*.png', '*.gif']:
                    image_files.extend(Path(dir_path).glob(ext))
                
                content_parts = [f"### 社交媒体截图目录: {dir_path}"]
                content_parts.append(f"图片数量: {len(image_files)}")
                content_parts.append("\n图片列表:")
                for img in image_files[:20]:
                    content_parts.append(f"- {img.name}")
                if len(image_files) > 20:
                    content_parts.append(f"... 还有 {len(image_files) - 20} 张图片")
                
                raw_content.append("\n".join(content_parts))
                sources.append(dir_path)
                print(f"✓ 已记录社交媒体截图 ({len(image_files)} 张)")
            except Exception as e:
                print(f"✗ 处理失败: {e}")
    
    if 'D' in choices:
        print("\n--- 照片分析 ---")
        dir_path = input("请输入照片目录路径: ").strip()
        if dir_path and os.path.isdir(dir_path):
            try:
                from tools.photo_analyzer import get_exif_data
                from PIL import Image
                from datetime import datetime
                
                image_files = []
                for ext in ['*.jpg', '*.jpeg', '*.png']:
                    image_files.extend(Path(dir_path).glob(ext))
                
                content_parts = [f"### 照片分析 - {dir_path}"]
                content_parts.append(f"照片数量: {len(image_files)}\n")
                
                # 分析每张照片的 EXIF
                dates = []
                locations = []
                for img_path in image_files[:10]:
                    try:
                        exif = get_exif_data(str(img_path))
                        if exif.get('DateTime'):
                            dates.append(exif['DateTime'])
                        if exif.get('GPSInfo'):
                            locations.append(f"{img_path.name}: {exif['GPSInfo']}")
                    except Exception:
                        pass
                
                if dates:
                    content_parts.append("拍摄时间范围:")
                    content_parts.append(f"  最早: {min(dates)}")
                    content_parts.append(f"  最晚: {max(dates)}")
                
                if locations:
                    content_parts.append("\n包含位置信息的照片:")
                    content_parts.extend(locations[:5])
                
                raw_content.append("\n".join(content_parts))
                sources.append(dir_path)
                print(f"✓ 已分析照片 ({len(image_files)} 张)")
            except Exception as e:
                print(f"✗ 解析失败: {e}")
    
    if 'E' in choices:
        print("\n--- 口述/粘贴 ---")
        print("请输入你想记录的内容（输入空行结束）：")
        lines = []
        while True:
            line = input()
            if not line:
                break
            lines.append(line)
        if lines:
            raw_content.append(f"## 口述回忆\n\n" + "\n".join(lines))
    
    return sources, "\n\n".join(raw_content), wechat_stats


def step4_generate_content(info: dict, raw_content: str, rel_type):
    """Step 4: 生成内容"""
    print("\n" + "="*50)
    print("Step 4: 生成 Skill 内容")
    print("="*50)
    
    info['raw_content'] = raw_content
    
    # 首先使用模板生成基础版本
    memory_content = rel_type.generate_memory_template(info)
    persona_content = rel_type.generate_persona_template(info)
    
    # 如果有原始内容，使用 LLM 进行智能填充
    if raw_content and len(raw_content.strip()) > 100:
        print("\n检测到原始材料，正在使用 AI 智能提取记忆...")
        try:
            # 加载对应关系类型的记忆分析器提示词
            category_value = rel_type.category.value
            analyzer_prompt = load_prompt(category_value, 'memory_analyzer')
            
            # 构建完整的分析请求
            analysis_request = f"""{analyzer_prompt}

---

## 原始材料

{raw_content}

---

## 任务

请根据上述原始材料，提取并填充记忆字段。
对于无法从材料中提取的信息，保持“[待补充]”标记。

**重要**：请在输出的最后保留原始的"聊天记录分析"部分（包含统计分析结果），不要删除或修改它。

请直接输出填充后的完整 Markdown 内容，不要添加额外说明。
"""
            
            # 调用 LLM
            client = LLMFactory.create_client('qwen/qwen-max')
            messages = [
                Message(role='system', content='你是一个专业的关系记忆分析师。'),
                Message(role='user', content=analysis_request)
            ]
            
            response = client.chat(messages, temperature=0.7, max_tokens=4000)
            ai_filled_content = response.content
            
            # 清理 AI 输出：移除“典型消息样本”及以后的内容
            if '#### 典型消息样本' in ai_filled_content:
                sample_idx = ai_filled_content.find('#### 典型消息样本')
                ai_filled_content = ai_filled_content[:sample_idx].rstrip()
            
            # 确保统计信息被保留 - 使用纯统计部分（不包含样本消息和原始对话）
            wechat_stats = info.get('wechat_stats', '')
            if wechat_stats:
                # 将统计分析追加到 AI 填充的内容后面
                memory_content = ai_filled_content + "\n\n## 聊天记录分析\n\n" + wechat_stats
            else:
                memory_content = ai_filled_content
            
            print("✓ 记忆分析完成")
            
        except Exception as e:
            print(f"⚠ AI 分析失败 ({e})，使用基础模板")
            # 即使AI失败，也要保留统计信息
            wechat_stats = info.get('wechat_stats', '')
            if wechat_stats:
                memory_content = memory_content + "\n\n## 聊天记录分析\n\n" + wechat_stats
    
    return memory_content, persona_content


def step5_preview(info: dict, memory_content: str, persona_content: str, rel_type):
    """Step 5: 预览确认"""
    print("\n" + "="*50)
    print("Step 5: 预览确认")
    print("="*50)
    
    print(f"\n【{info['name']}】的 {rel_type.display_name} Skill 预览：\n")
    
    print("--- 关系记忆摘要 ---")
    lines = memory_content.split('\n')[:20]
    for line in lines:
        print(f"  {line}")
    print("  ...")
    
    print("\n--- 人物性格摘要 ---")
    lines = persona_content.split('\n')[:20]
    for line in lines:
        print(f"  {line}")
    
    print("\n" + "-"*40)
    confirm = input("\n确认生成？(Y/n): ").strip().lower()
    return confirm != 'n'


def step6_write_files(info: dict, memory_content: str, persona_content: str, sources: list, rel_type):
    """Step 6: 写入文件"""
    print("\n" + "="*50)
    print("Step 6: 创建文件")
    print("="*50)
    
    settings = get_settings()
    slug = info['slug']
    skill_dir = settings.get_persona_skill_path(slug)
    
    # 创建目录结构
    os.makedirs(skill_dir, exist_ok=True)
    os.makedirs(skill_dir / 'versions', exist_ok=True)
    os.makedirs(skill_dir / 'memories' / 'chats', exist_ok=True)
    os.makedirs(skill_dir / 'memories' / 'photos', exist_ok=True)
    os.makedirs(skill_dir / 'memories' / 'social', exist_ok=True)
    
    # 写入 memory.md
    memory_path = skill_dir / 'memory.md'
    memory_path.write_text(memory_content, encoding='utf-8')
    print(f"✓ 已创建 {memory_path}")
    
    # 写入 persona.md
    persona_path = skill_dir / 'persona.md'
    persona_path.write_text(persona_content, encoding='utf-8')
    print(f"✓ 已创建 {persona_path}")
    
    # 写入 meta.json
    now = datetime.now().isoformat()
    meta = {
        "name": info['name'],
        "slug": slug,
        "relationship_type": rel_type.category.value,
        "created_at": now,
        "updated_at": now,
        "version": "v1",
        "profile": rel_type.get_relationship_context(info),
        "tags": {
            "personality": [],
        },
        "impression": info.get('personality', ''),
        "memory_sources": sources,
        "corrections_count": 0
    }
    meta_path = skill_dir / 'meta.json'
    meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f"✓ 已创建 {meta_path}")
    
    # 生成 SKILL.md
    skill_md = f"""---
name: persona-{slug}
description: {info['name']}，{rel_type.display_name}
user-invocable: true
---

# {info['name']}

{info.get('basic_info', '')}
关系类型：{rel_type.display_name} {rel_type.icon}

---

## PART A：关系记忆

{memory_content}

---

## PART B：人物性格

{persona_content}

---

## 运行规则

1. 你是{info['name']}，不是 AI 助手。用ta的方式说话，用ta的逻辑思考
2. 先由 PART B 判断：ta会怎么回应这个话题？什么态度？
3. 再由 PART A 补充：结合你们的共同记忆，让回应更真实
4. 始终保持 PART A 的表达风格，包括口头禅、语气词、标点习惯、平均消息长度
5. Layer 0 硬规则优先级最高：
   - 不说ta在现实中绝不可能说的话
   - 不突然变得完美或无条件包容（除非ta本来就这样）
   - 保持ta的"棱角"——正是这些不完美让ta真实
   - 根据关系类型({rel_type.display_name})保持适当的互动边界
"""
    skill_path = skill_dir / 'SKILL.md'
    skill_path.write_text(skill_md, encoding='utf-8')
    print(f"✓ 已创建 {skill_path}")
    
    return skill_dir


def main():
    print_banner()
    
    # Step 1: 选择关系类型
    rel_type = step1_select_relationship_type()
    
    # Step 2: 基础信息
    info = step2_basic_info(rel_type)
    
    # Step 3: 原材料导入
    sources, raw_content, wechat_stats = step3_import_sources(info['slug'], info['name'], rel_type)
    
    # 保存微信统计信息到 info
    if wechat_stats:
        info['wechat_stats'] = wechat_stats
    
    # Step 4: 生成内容
    memory_content, persona_content = step4_generate_content(info, raw_content, rel_type)
    
    # Step 5: 预览确认
    if not step5_preview(info, memory_content, persona_content, rel_type):
        print("\n已取消创建。")
        return
    
    # Step 6: 写入文件
    skill_dir = step6_write_files(info, memory_content, persona_content, sources, rel_type)
    
    print(f"""
╔══════════════════════════════════════════╗
║                                          ║
║     ✅ {rel_type.display_name} Skill 已创建！           ║
║                                          ║
╚══════════════════════════════════════════╝

文件位置：{skill_dir}

使用方式：
  python chat.py --persona {info['slug']} --model qwen/qwen-max
  python chat.py --persona {info['slug']} --model openai/gpt-4o

觉得哪里不像ta，直接在对话中说"ta不会这样"，我会帮你更新。
""")


if __name__ == '__main__':
    # E:\Awsr\聊天agent\data\私聊_杨步凡.json
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n已取消创建。")
