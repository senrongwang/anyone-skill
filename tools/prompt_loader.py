#!/usr/bin/env python3
"""提示词模板加载器

根据关系类型和任务类型加载对应的提示词模板。

Usage:
    from tools.prompt_loader import load_prompt
    
    # 加载朋友关系的记忆分析器
    prompt = load_prompt('friend', 'memory_analyzer')
    
    # 加载前任的人物性格构建器
    prompt = load_prompt('ex_partner', 'persona_builder')
"""

import os
from pathlib import Path
from typing import Optional


class PromptLoader:
    """提示词加载器"""
    
    def __init__(self, base_dir: Optional[str] = None):
        """
        Args:
            base_dir: prompts 目录路径,默认为项目根目录下的 prompts
        """
        if base_dir is None:
            # 默认找到项目根目录
            current_file = Path(__file__).resolve()
            self.base_dir = current_file.parent.parent / 'prompts'
        else:
            self.base_dir = Path(base_dir)
    
    def load(self, relationship_type: str, task_type: str) -> str:
        """加载提示词模板
        
        Args:
            relationship_type: 关系类型 (ex_partner, friend, family, colleague, idol)
            task_type: 任务类型 (memory_analyzer, persona_builder)
        
        Returns:
            提示词内容
        
        Raises:
            FileNotFoundError: 提示词文件不存在
        """
        # 映射关系到文件名
        type_mapping = {
            'ex_partner': 'ex_partner',
            'friend': 'friend',
            'family': 'family',
            'colleague': 'colleague',
            'idol': 'idol',
        }
        
        # 检查是否是特定关系类型的提示词
        if relationship_type in type_mapping:
            # 尝试加载特定关系类型的提示词
            prompt_file = self.base_dir / task_type / f"{type_mapping[relationship_type]}.md"
            
            if prompt_file.exists():
                return prompt_file.read_text(encoding='utf-8')
        
        # 如果找不到特定关系类型的,尝试加载通用的
        generic_file = self.base_dir / f"{task_type}.md"
        if generic_file.exists():
            return generic_file.read_text(encoding='utf-8')
        
        raise FileNotFoundError(
            f"找不到提示词文件: {task_type}/{relationship_type}.md 或 {task_type}.md"
        )
    
    def list_available_prompts(self) -> dict:
        """列出所有可用的提示词
        
        Returns:
            字典,key为关系类型,value为该类型下可用的任务类型列表
        """
        available = {}
        
        # 检查各个关系类型目录
        for rel_type in ['ex_partner', 'friend', 'family', 'colleague', 'idol']:
            tasks = []
            
            # 检查 memory_analyzer
            if (self.base_dir / 'memory_analyzer' / f'{rel_type}.md').exists():
                tasks.append('memory_analyzer')
            
            # 检查 persona_builder
            if (self.base_dir / 'persona_builder' / f'{rel_type}.md').exists():
                tasks.append('persona_builder')
            
            if tasks:
                available[rel_type] = tasks
        
        # 检查通用提示词
        generic_tasks = []
        for task in ['correction_handler', 'merger', 'intake']:
            if (self.base_dir / f'{task}.md').exists():
                generic_tasks.append(task)
        
        if generic_tasks:
            available['generic'] = generic_tasks
        
        return available


# 全局实例
_loader = None


def get_loader() -> PromptLoader:
    """获取全局 PromptLoader 实例"""
    global _loader
    if _loader is None:
        _loader = PromptLoader()
    return _loader


def load_prompt(relationship_type: str, task_type: str) -> str:
    """便捷函数:加载提示词模板
    
    Args:
        relationship_type: 关系类型
        task_type: 任务类型
    
    Returns:
        提示词内容
    """
    return get_loader().load(relationship_type, task_type)


if __name__ == '__main__':
    # 测试
    loader = PromptLoader()
    print("可用的提示词:")
    for rel_type, tasks in loader.list_available_prompts().items():
        print(f"  {rel_type}: {', '.join(tasks)}")
    
    print("\n" + "="*50)
    print("测试加载朋友关系的记忆分析器:")
    print("="*50)
    try:
        prompt = loader.load('friend', 'memory_analyzer')
        print(prompt[:500])
    except FileNotFoundError as e:
        print(f"错误: {e}")
