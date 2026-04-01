#!/usr/bin/env python3
"""微信聊天记录解析器

支持主流导出工具的格式：
- WeChatMsg 导出（txt/html/csv）
- 留痕导出（json）
- PyWxDump 导出（sqlite）
- 手动复制粘贴（纯文本）

Usage:
    python3 wechat_parser.py --file <path> --target <name> --output <output_path> [--format auto]
"""

import argparse
import json
import re
import os
import sys
from datetime import datetime
from typing import Optional
from pathlib import Path


def detect_format(file_path: str) -> str:
    """自动检测文件格式"""
    ext = Path(file_path).suffix.lower()
    
    if ext == '.json':
        return 'liuhen'  # 留痕导出
    elif ext == '.csv':
        return 'wechatmsg_csv'
    elif ext == '.html' or ext == '.htm':
        return 'wechatmsg_html'
    elif ext == '.db' or ext == '.sqlite':
        return 'pywxdump'
    elif ext == '.txt':
        # 尝试区分 WeChatMsg txt 和纯文本
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            first_lines = f.read(2000)
        # WeChatMsg 格式通常有时间戳模式
        if re.search(r'\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}', first_lines):
            return 'wechatmsg_txt'
        return 'plaintext'
    else:
        return 'plaintext'


def parse_wechatmsg_txt(file_path: str, target_name: str) -> dict:
    """解析 WeChatMsg 导出的 txt 格式
    
    典型格式：
    2024-01-15 20:30:45 张三
    今天好累啊
    
    2024-01-15 20:31:02 我
    怎么了？
    """
    messages = []
    current_msg = None
    
    # WeChatMsg 时间戳 + 发送者模式
    msg_pattern = re.compile(r'^(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})\s+(.+)$')
    
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            line = line.rstrip('\n')
            match = msg_pattern.match(line)
            if match:
                if current_msg:
                    messages.append(current_msg)
                timestamp, sender = match.groups()
                current_msg = {
                    'timestamp': timestamp,
                    'sender': sender.strip(),
                    'content': ''
                }
            elif current_msg and line.strip():
                if current_msg['content']:
                    current_msg['content'] += '\n'
                current_msg['content'] += line
    
    if current_msg:
        messages.append(current_msg)
    
    return analyze_messages(messages, target_name)


def parse_liuhen_json(file_path: str, target_name: str) -> dict:
    """解析留痕/WeFlow 导出的 JSON 格式
    
    支持格式：
    - 留痕导出: [{"time": ..., "sender": ..., "content": ...}]
    - WeFlow导出: {"session": {...}, "messages": [{"createTime": ..., "senderDisplayName": ..., "content": ...}]}
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    messages = []
    
    # WeFlow 格式: data.messages 数组
    if 'messages' in data and isinstance(data['messages'], list):
        msg_list = data['messages']
        for msg in msg_list:
            # WeFlow 格式字段
            sender = msg.get('senderDisplayName', msg.get('senderNickname', msg.get('senderUsername', '')))
            content = msg.get('content', '')
            timestamp = msg.get('formattedTime', str(msg.get('createTime', '')))
            
            # 过滤系统消息
            if msg.get('type') in ['系统消息', '撤回消息'] or not content:
                continue
                
            messages.append({
                'timestamp': timestamp,
                'sender': sender,
                'content': content
            })
    
    # 留痕格式: 直接是数组或 data.data
    elif isinstance(data, list):
        for msg in data:
            messages.append({
                'timestamp': msg.get('time', msg.get('timestamp', '')),
                'sender': msg.get('sender', msg.get('nickname', msg.get('from', ''))),
                'content': msg.get('content', msg.get('message', msg.get('text', '')))
            })
    
    # 其他格式尝试通用提取
    else:
        msg_list = data.get('data', [])
        for msg in msg_list:
            messages.append({
                'timestamp': msg.get('time', msg.get('timestamp', '')),
                'sender': msg.get('sender', msg.get('nickname', msg.get('from', ''))),
                'content': msg.get('content', msg.get('message', msg.get('text', '')))
            })
    
    return analyze_messages(messages, target_name)


def parse_plaintext(file_path: str, target_name: str) -> dict:
    """解析纯文本粘贴的聊天记录
    
    支持格式：
    名字1：消息内容
    名字2：消息内容
    
    或：
    2024-01-15 20:30:45 名字1
    消息内容
    """
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    messages = []
    lines = content.split('\n')
    
    # 尝试检测格式
    # 格式1: "名字：消息" (你的格式)
    # 格式2: 时间戳 + 换行 + 消息 (WeChatMsg格式)
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if not line:
            i += 1
            continue
        
        # 尝试匹配 "名字：消息" 格式
        if '：' in line or ':' in line:
            # 尝试中文冒号
            if '：' in line:
                sender, msg_content = line.split('：', 1)
            else:
                sender, msg_content = line.split(':', 1)
            
            sender = sender.strip()
            msg_content = msg_content.strip()
            
            if sender and msg_content:
                messages.append({
                    'timestamp': '',
                    'sender': sender,
                    'content': msg_content
                })
        
        i += 1
    
    # 如果解析到消息，使用 analyze_messages 分析
    if messages:
        return analyze_messages(messages, target_name)
    
    # 否则返回原始内容
    return {
        'raw_text': content,
        'target_name': target_name,
        'format': 'plaintext',
        'message_count': 0,
        'analysis': {
            'note': '纯文本格式，需要人工辅助分析'
        }
    }


def analyze_messages(messages: list, target_name: str) -> dict:
    """分析消息列表，提取关键特征
    
    提取维度：
    1. 基础统计：消息数、长度、频率
    2. 语言风格：语气词、emoji、标点习惯
    3. 话题分析：高频词汇、兴趣点
    4. 行为模式：回复速度、主动/被动比例
    5. 情感表达：情绪词、关心语句
    6. 关系线索：共同活动、提及的地点/时间
    """
    target_msgs = [m for m in messages if target_name in m.get('sender', '')]
    user_msgs = [m for m in messages if target_name not in m.get('sender', '')]
    
    # 提取口头禅（高频词分析）
    all_target_text = ' '.join([m['content'] for m in target_msgs if m.get('content')])
    
    # 提取语气词
    particles = re.findall(r'[哈嗯哦噢嘿唉呜啊呀吧嘛呢吗么]+', all_target_text)
    particle_freq = {}
    for p in particles:
        particle_freq[p] = particle_freq.get(p, 0) + 1
    top_particles = sorted(particle_freq.items(), key=lambda x: -x[1])[:10]
    
    # 提取 emoji
    emoji_pattern = re.compile(
        r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF'
        r'\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF'
        r'\U00002702-\U000027B0\U0000FE00-\U0000FE0F'
        r'\U0001F900-\U0001F9FF]+', re.UNICODE
    )
    emojis = emoji_pattern.findall(all_target_text)
    emoji_freq = {}
    for e in emojis:
        emoji_freq[e] = emoji_freq.get(e, 0) + 1
    top_emojis = sorted(emoji_freq.items(), key=lambda x: -x[1])[:10]
    
    # 消息长度统计
    msg_lengths = [len(m['content']) for m in target_msgs if m.get('content')]
    avg_length = sum(msg_lengths) / len(msg_lengths) if msg_lengths else 0
    
    # 标点习惯
    punctuation_counts = {
        '句号': all_target_text.count('。'),
        '感叹号': all_target_text.count('！') + all_target_text.count('!'),
        '问号': all_target_text.count('？') + all_target_text.count('?'),
        '省略号': all_target_text.count('...') + all_target_text.count('…'),
        '波浪号': all_target_text.count('～') + all_target_text.count('~'),
    }
    
    # 提取高频实词（话题分析）
    # 过滤常见停用词后统计
    stop_words = {'的', '了', '是', '我', '你', '在', '有', '就', '不', '人', '都', '一', '一个', '上', '也', '很', '到', '说', '要', '去', '可以', '会', '着', '没有', '看', '好', '自己', '这'}
    words = re.findall(r'[\u4e00-\u9fa5]{2,4}', all_target_text)  # 2-4字中文词
    word_freq = {}
    for w in words:
        if w not in stop_words and len(w) >= 2:
            word_freq[w] = word_freq.get(w, 0) + 1
    top_words = sorted(word_freq.items(), key=lambda x: -x[1])[:15]
    
    # 提取可能的地点（包含"路、街、店、商场、公园"等）
    location_pattern = re.compile(r'([\u4e00-\u9fa5]{2,6}(?:路|街|大道|店|商场|广场|公园|餐厅|饭店|酒店|小区|楼|大厦))')
    locations = location_pattern.findall(all_target_text)
    location_freq = {}
    for loc in locations:
        location_freq[loc] = location_freq.get(loc, 0) + 1
    top_locations = sorted(location_freq.items(), key=lambda x: -x[1])[:10]
    
    # 提取时间相关词汇
    time_pattern = re.compile(r'(\d{1,2}[:：]\d{2}|\d{1,2}点|早上|中午|晚上|周末|星期[一二三四五六日]|下周|明天|昨天)')
    time_refs = time_pattern.findall(all_target_text)
    
    # 提取活动/兴趣点
    activity_keywords = ['吃', '喝', '玩', '看', '去', '买', '逛', '电影', '游戏', '音乐', '旅游', '运动', '健身', '跑步', '火锅', '烧烤', '奶茶']
    activities = []
    for keyword in activity_keywords:
        if keyword in all_target_text:
            # 找到包含关键词的上下文
            for msg in target_msgs[:30]:
                if keyword in msg.get('content', ''):
                    activities.append(msg['content'])
                    break
    
    # 提取关心/情感表达语句
    care_patterns = ['注意', '小心', '早点睡', '别太累', '照顾好', '记得', '担心', '想你了', '爱你', '抱抱']
    care_messages = []
    for msg in target_msgs:
        content = msg.get('content', '')
        for pattern in care_patterns:
            if pattern in content and len(content) < 50:
                care_messages.append(content)
                break
    
    # 识别回应模式（秒回 vs 延迟）
    response_patterns = {
        '秒回型': len([m for m in target_msgs if len(m.get('content', '')) < 10]) > len(target_msgs) * 0.6,
        '话痨型': avg_length > 30,
        '简洁型': avg_length < 15,
    }
    
    return {
        'target_name': target_name,
        'total_messages': len(messages),
        'target_messages': len(target_msgs),
        'user_messages': len(user_msgs),
        'analysis': {
            'top_particles': top_particles,
            'top_emojis': top_emojis,
            'top_words': top_words,  # 高频话题词
            'avg_message_length': round(avg_length, 1),
            'punctuation_habits': punctuation_counts,
            'message_style': 'short_burst' if avg_length < 20 else 'long_form',
            'response_pattern': [k for k, v in response_patterns.items() if v],
            'locations': top_locations,  # 常提地点
            'time_references': list(set(time_refs))[:10],  # 时间偏好
            'activities': activities[:10],  # 活动/兴趣
            'care_messages': care_messages[:10],  # 关心语句
        },
        'sample_messages': [m['content'] for m in target_msgs[:50] if m.get('content')],
    }


def main():
    parser = argparse.ArgumentParser(description='微信聊天记录解析器')
    parser.add_argument('--file', required=True, help='输入文件路径')
    parser.add_argument('--target', required=True, help='前任的名字/昵称')
    parser.add_argument('--output', required=True, help='输出文件路径')
    parser.add_argument('--format', default='auto', help='文件格式 (auto/wechatmsg_txt/liuhen/pywxdump/plaintext)')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.file):
        print(f"错误：文件不存在 {args.file}", file=sys.stderr)
        sys.exit(1)
    
    fmt = args.format
    if fmt == 'auto':
        fmt = detect_format(args.file)
        print(f"自动检测格式：{fmt}")
    
    parsers = {
        'wechatmsg_txt': parse_wechatmsg_txt,
        'liuhen': parse_liuhen_json,
        'plaintext': parse_plaintext,
    }
    
    parse_func = parsers.get(fmt, parse_plaintext)
    result = parse_func(args.file, args.target)
    
    # 输出分析结果
    os.makedirs(os.path.dirname(args.output) or '.', exist_ok=True)
    
    with open(args.output, 'w', encoding='utf-8') as f:
        f.write(f"# 微信聊天记录分析 — {args.target}\n\n")
        f.write(f"来源文件：{args.file}\n")
        f.write(f"检测格式：{fmt}\n")
        f.write(f"总消息数：{result.get('total_messages', 'N/A')}\n")
        f.write(f"ta的消息数：{result.get('target_messages', 'N/A')}\n\n")
        
        analysis = result.get('analysis', {})
        
        if analysis.get('top_particles'):
            f.write("## 高频语气词\n")
            for word, count in analysis['top_particles']:
                f.write(f"- {word}: {count}次\n")
            f.write("\n")
        
        if analysis.get('top_emojis'):
            f.write("## 高频 Emoji\n")
            for emoji, count in analysis['top_emojis']:
                f.write(f"- {emoji}: {count}次\n")
            f.write("\n")
        
        if analysis.get('punctuation_habits'):
            f.write("## 标点习惯\n")
            for punct, count in analysis['punctuation_habits'].items():
                f.write(f"- {punct}: {count}次\n")
            f.write("\n")
        
        f.write(f"## 消息风格\n")
        f.write(f"- 平均消息长度：{analysis.get('avg_message_length', 'N/A')} 字\n")
        f.write(f"- 风格：{'短句连发型' if analysis.get('message_style') == 'short_burst' else '长段落型'}\n\n")
        
        if result.get('sample_messages'):
            f.write("## 消息样本（前50条）\n")
            for i, msg in enumerate(result['sample_messages'], 1):
                f.write(f"{i}. {msg}\n")
    
    print(f"分析完成，结果已写入 {args.output}")


if __name__ == '__main__':
    main()
