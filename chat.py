#!/usr/bin/env python3
"""Anyone Skill 对话 CLI

独立于 Claude Code 的对话入口，支持多种 LLM API。

Usage:
    python chat.py --persona {slug} --model openai/gpt-4
    python chat.py --persona {slug} --model anthropic/claude-3-opus
    python chat.py --persona {slug} --model gemini/gemini-pro
    python chat.py --persona {slug} --model ollama/llama2
"""

import argparse
import sys
import os

# 添加 tools 目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from tools.chat_engine import create_chat, list_available_skills
from tools.llm.factory import LLMFactory


def print_banner():
    """打印欢迎信息"""
    print("""
╔══════════════════════════════════════════╗
║                                          ║
║     Anyone Skill - 多 API 对话工具        ║
║                                          ║
╚══════════════════════════════════════════╝
""")


def list_skills():
    """列出所有可用的 Persona Skill"""
    skills = list_available_skills()
    
    if not skills:
        print("还没有创建任何 Persona Skill。")
        print("请先使用 create_persona.py 创建 Skill。")
        return
    
    print(f"共 {len(skills)} 个 Persona Skill：\n")
    for skill in skills:
        slug = skill['slug']
        print(f"  • {slug}")
    print()


def list_models():
    """列出所有可用的模型"""
    models = LLMFactory.list_available_models()
    
    print("可用的模型：\n")
    
    providers = {}
    for key, config in models.items():
        provider = config['provider']
        if provider not in providers:
            providers[provider] = []
        providers[provider].append((key, config))
    
    for provider, model_list in sorted(providers.items()):
        print(f"\n【{provider.upper()}】")
        for key, config in sorted(model_list):
            status = "✓" if config['has_api_key'] else "✗ (未配置 API Key)"
            print(f"  {key} {status}")
    print()


def interactive_chat(engine, stream: bool = True):
    """交互式对话
    
    Args:
        engine: ChatEngine 实例
        stream: 是否使用流式输出
    """
    skill_info = engine.get_skill_info()
    model_info = engine.get_model_info()
    
    print(f"\n正在与 【{skill_info['name']}】 对话")
    print(f"使用模型: {model_info['model_key']}")
    print("\n输入消息开始对话，输入 /quit 或 /q 退出，输入 /clear 清空历史\n")
    
    while True:
        try:
            # 获取用户输入
            user_input = input("你 > ").strip()
            
            if not user_input:
                continue
            
            # 处理命令
            if user_input.lower() in ['/quit', '/q', 'exit', 'quit']:
                print("\n再见。")
                break
            
            if user_input.lower() == '/clear':
                engine.clear_history()
                print("\n[对话历史已清空]\n")
                continue
            
            if user_input.lower() == '/info':
                info = engine.get_skill_info()
                print(f"\n[Skill: {info['name']}]")
                print(f"[描述: {info['description'] or '无'}]")
                print()
                continue
            
            # 发送消息
            if stream:
                print(f"{skill_info['name']} > ", end='', flush=True)
                for chunk in engine.chat_stream(user_input):
                    print(chunk, end='', flush=True)
                print('\n')
            else:
                response = engine.chat(user_input)
                print(f"{skill_info['name']} > {response}\n")
        
        except KeyboardInterrupt:
            print("\n\n再见。")
            break
        except Exception as e:
            print(f"\n[错误] {e}\n")


def main():
    parser = argparse.ArgumentParser(
        description='Anyone Skill 多 API 对话工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python chat.py --list-skills              # 列出所有 Skill
  python chat.py --list-models              # 列出所有模型
  python chat.py --persona 小明 --model openai/gpt-4o
  python chat.py --persona 老王 --model anthropic/claude-3-sonnet
  python chat.py --persona 老妈 --model ollama/llama2 --no-stream
        """
    )
    
    parser.add_argument('--persona', '-p', dest='slug',
                        help='Persona Skill 的代号')
    parser.add_argument('--model', '-m', default='openai/gpt-4o',
                        help='模型标识，如 openai/gpt-4, anthropic/claude-3-opus (默认: openai/gpt-4o)')
    parser.add_argument('--list-skills', '-l', action='store_true',
                        help='列出所有可用的 Persona Skill')
    parser.add_argument('--list-models', action='store_true',
                        help='列出所有可用的模型')
    parser.add_argument('--no-stream', action='store_true',
                        help='禁用流式输出')
    parser.add_argument('--temperature', '-t', type=float, default=0.7,
                        help='温度参数 (默认: 0.7)')
    parser.add_argument('--max-tokens', type=int, default=2000,
                        help='最大生成 token 数 (默认: 2000)')
    
    args = parser.parse_args()
    
    # 处理列表命令
    if args.list_skills:
        list_skills()
        return
    
    if args.list_models:
        list_models()
        return
    
    # 检查必要参数
    if not args.slug:
        print("错误: 请指定 --persona 参数指定要对话的 Persona Skill")
        print("\n使用 --list-skills 查看可用的 Skill")
        print("使用 --help 查看详细用法")
        sys.exit(1)
    
    # 打印欢迎信息
    print_banner()
    
    try:
        # 创建对话引擎
        engine = create_chat(args.slug, args.model)
        
        # 开始交互式对话
        interactive_chat(engine, stream=not args.no_stream)
    
    except FileNotFoundError as e:
        print(f"错误: {e}")
        print("\n使用 --list-skills 查看可用的 Skill")
        sys.exit(1)
    except ImportError as e:
        print(f"错误: {e}")
        print("\n请安装必要的依赖:")
        print("  pip install openai anthropic google-generativeai")
        sys.exit(1)
    except Exception as e:
        print(f"错误: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
