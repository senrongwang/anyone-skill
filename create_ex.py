#!/usr/bin/env python3
"""前任 Skill 创建工具

独立于 Claude Code 的创建入口，通过命令行交互式创建前任 Skill。

Usage:
    python create_ex.py
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


def print_banner():
    """打印欢迎信息"""
    print("""
╔══════════════════════════════════════════╗
║                                          ║
║     前任.skill 创建工具                   ║
║                                          ║
║  我会为了你一万次回到那个夏天。           ║
║                                          ║
╚══════════════════════════════════════════╝
""")


def input_with_default(prompt: str, default: str = "") -> str:
    """带默认值的输入"""
    if default:
        result = input(f"{prompt} [默认: {default}]: ").strip()
        return result if result else default
    return input(f"{prompt}: ").strip()


def step1_basic_info():
    """Step 1: 基础信息录入"""
    print("\n" + "="*50)
    print("Step 1: 基础信息录入")
    print("="*50)
    print("请回答以下 3 个问题（除花名外均可跳过）\n")
    
    # 1. 花名/代号（必填）
    while True:
        name = input("1. 花名/代号（必填，如：小明/初恋/那个人）: ").strip()
        if name:
            break
        print("   花名是必填项，请输入。")
    
    # 生成 slug
    slug = name.lower().replace(" ", "-")
    
    # 2. 基本信息
    print("\n2. 基本信息（一句话：在一起多久、分手多久、ta做什么的）")
    print("   示例：在一起两年 分手半年了 互联网产品经理")
    basic_info = input("   ").strip()
    
    # 3. 性格画像
    print("\n3. 性格画像（一句话：MBTI、星座、性格标签、你对ta的印象）")
    print("   示例：ENFP 双子座 话很多 永远在社交 但深夜会突然emo")
    personality = input("   ").strip()
    
    return {
        'name': name,
        'slug': slug,
        'basic_info': basic_info,
        'personality': personality
    }


def step2_import_sources(slug: str, name: str):
    """Step 2: 原材料导入"""
    print("\n" + "="*50)
    print("Step 2: 原材料导入")
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
      比如：ta的口头禅、吵架模式、约会常去的地方

  [F] 跳过
      仅凭上面的基础信息生成

可以输入多个选项，如：A E
""")
    
    choices = input("选择数据来源: ").strip().upper()
    
    sources = []
    raw_content = []
    
    if 'A' in choices:
        print("\n--- 微信聊天记录 ---")
        file_path = input("请输入微信聊天记录文件路径: ").strip()
        if file_path and os.path.exists(file_path):
            try:
                from tools.wechat_parser import parse_wechatmsg_txt, parse_plaintext, detect_format
                import json
                
                print(f"[调试] 正在解析文件: {file_path}")
                print(f"[调试] 目标名字: {name}")
                
                # 先读取前10行看看格式
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
                        content_parts.append(f"{i}. \"{msg}\"")
                
                # 时间偏好
                if analysis.get('time_references'):
                    content_parts.append("\n#### 时间偏好")
                    content_parts.append(f"常提及：{', '.join(analysis['time_references'][:5])}")
                
                # 添加样本消息
                if result.get('sample_messages'):
                    content_parts.append("\n#### 典型消息样本")
                    for i, msg in enumerate(result['sample_messages'][:15], 1):
                        content_parts.append(f"{i}. {msg}")
                
                raw_content.append("\n".join(content_parts))
                sources.append(file_path)
                print(f"✓ 已解析微信聊天记录")
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
    
    return sources, "\n\n".join(raw_content)


def step3_generate_content(info: dict, raw_content: str):
    """Step 3: 分析原材料并生成内容"""
    print("\n" + "="*50)
    print("Step 3: 生成 Skill 内容")
    print("="*50)
    
    # 生成 memory.md 内容
    memory_content = f"""# 关系记忆

## 基本信息
- 花名：{info['name']}
- 关系描述：{info['basic_info'] or '未提供'}

## 共同经历
{raw_content if raw_content else '暂无详细记录，请通过对话逐步补充。'}

## 时间线
- 认识时间：待补充
- 在一起时间：待补充
- 分手时间：待补充

## 常去地点
待补充

## 甜蜜瞬间
待补充

## 争吵模式
待补充

## Inside Jokes
待补充
"""
    
    # 生成 persona.md 内容
    personality = info['personality'] or '性格待补充'
    personality_parts = personality.split()
    
    # 尝试解析 MBTI 和星座
    mbti = ""
    zodiac = ""
    tags = []
    
    for part in personality_parts:
        if len(part) == 4 and part.upper() in ['INTJ', 'INTP', 'ENTJ', 'ENTP', 'INFJ', 'INFP', 'ENFJ', 'ENFP', 'ISTJ', 'ISFJ', 'ESTJ', 'ESFJ', 'ISTP', 'ISFP', 'ESTP', 'ESFP']:
            mbti = part.upper()
        elif part in ['白羊', '金牛', '双子', '巨蟹', '狮子', '处女', '天秤', '天蝎', '射手', '摩羯', '水瓶', '双鱼', '白羊座', '金牛座', '双子座', '巨蟹座', '狮子座', '处女座', '天秤座', '天蝎座', '射手座', '摩羯座', '水瓶座', '双鱼座']:
            zodiac = part
        else:
            tags.append(part)
    
    persona_content = f"""# 人物性格

## Layer 0: 硬规则
- 不说现实中绝不会说的话
- 不突然变得完美或无条件包容
- 保持真实的"棱角"

## Layer 1: 身份
- 名字：{info['name']}
- {info['basic_info'] or '身份信息待补充'}

## Layer 2: 说话风格
- MBTI：{mbti or '未知'}
- 星座：{zodiac or '未知'}
- 性格标签：{', '.join(tags) if tags else '待补充'}
- 口头禅：待补充
- 语气习惯：待补充

## Layer 3: 情感模式
- 依恋类型：待补充
- 爱的语言：待补充
- 表达方式：待补充

## Layer 4: 关系行为
- 吵架模式：待补充
- 和好方式：待补充
- 日常互动：待补充
"""
    
    return memory_content, persona_content


def step4_preview(info: dict, memory_content: str, persona_content: str):
    """Step 4: 预览确认"""
    print("\n" + "="*50)
    print("Step 4: 预览确认")
    print("="*50)
    
    print(f"\n【{info['name']}】的前任 Skill 预览：\n")
    
    print("--- Relationship Memory 摘要 ---")
    lines = memory_content.split('\n')[:15]
    for line in lines:
        print(f"  {line}")
    print("  ...")
    
    print("\n--- Persona 摘要 ---")
    lines = persona_content.split('\n')[:15]
    for line in lines:
        print(f"  {line}")
    
    print("\n" + "-"*40)
    confirm = input("\n确认生成？(Y/n): ").strip().lower()
    return confirm != 'n'


def step5_write_files(info: dict, memory_content: str, persona_content: str, sources: list):
    """Step 5: 写入文件"""
    print("\n" + "="*50)
    print("Step 5: 创建文件")
    print("="*50)
    
    settings = get_settings()
    slug = info['slug']
    skill_dir = settings.get_ex_skill_path(slug)
    
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
        "created_at": now,
        "updated_at": now,
        "version": "v1",
        "profile": {
            "together_duration": "",
            "apart_since": "",
            "occupation": "",
            "gender": "",
            "mbti": "",
            "zodiac": ""
        },
        "tags": {
            "personality": [],
            "attachment_style": "",
            "love_language": ""
        },
        "impression": info['personality'],
        "memory_sources": sources,
        "corrections_count": 0
    }
    meta_path = skill_dir / 'meta.json'
    meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f"✓ 已创建 {meta_path}")
    
    # 生成 SKILL.md
    skill_md = f"""---
name: ex-{slug}
description: {info['name']}，{info['basic_info'] or '我的前任'}
user-invocable: true
---

# {info['name']}

{info['basic_info'] or ''}
{f'MBTI: {meta["profile"]["mbti"]}' if meta["profile"]["mbti"] else ''}
{f'星座: {meta["profile"]["zodiac"]}' if meta["profile"]["zodiac"] else ''}

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
4. 始终保持 PART B 的表达风格，包括口头禅、语气词、标点习惯
5. Layer 0 硬规则优先级最高：
   - 不说ta在现实中绝不可能说的话
   - 不突然变得完美或无条件包容（除非ta本来就这样）
   - 保持ta的"棱角"——正是这些不完美让ta真实
   - 如果被问到"你爱不爱我"这类问题，用ta会用的方式回答，而不是用户想听的答案
"""
    skill_path = skill_dir / 'SKILL.md'
    skill_path.write_text(skill_md, encoding='utf-8')
    print(f"✓ 已创建 {skill_path}")
    
    return skill_dir


def main():
    print_banner()
    
    # Step 1: 基础信息
    global info
    info = step1_basic_info()
    
    # Step 2: 原材料导入
    sources, raw_content = step2_import_sources(info['slug'], info['name'])
    
    # Step 3: 生成内容
    memory_content, persona_content = step3_generate_content(info, raw_content)
    
    # Step 4: 预览确认
    if not step4_preview(info, memory_content, persona_content):
        print("\n已取消创建。")
        return
    
    # Step 5: 写入文件
    skill_dir = step5_write_files(info, memory_content, persona_content, sources)
    
    print(f"""
╔══════════════════════════════════════════╗
║                                          ║
║     ✅ 前任 Skill 已创建！               ║
║                                          ║
╚══════════════════════════════════════════╝

文件位置：{skill_dir}

使用方式：
  python chat.py --ex {info['slug']} --model qwen/qwen-max
  python chat.py --ex {info['slug']} --model openai/gpt-4o

觉得哪里不像ta，直接在对话中说"ta不会这样"，我会帮你更新。
""")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n已取消创建。")
