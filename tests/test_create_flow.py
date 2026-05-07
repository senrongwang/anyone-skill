"""Anyone Skill 创建流程测试

测试重构后的 relationship_types.py 能否正常驱动 Persona Skill 的创建。
"""

import sys
import os
import json
import tempfile
from pathlib import Path
from unittest.mock import patch

# 添加项目根目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from tools.relationship_types import (
    RelationshipType,
    get_relationship_type,
    list_relationship_types,
    select_relationship_type,
    RELATIONSHIP_TYPES,
)
from tools.config.settings import get_settings
from tools.llm.base import Message


# ============================================================
# 1. 关系类型注册与查询
# ============================================================

def test_all_types_available():
    """应有 5 种关系类型"""
    types = list_relationship_types()
    assert len(types) == 5


def test_list_returns_correct_keys():
    """list_relationship_types 返回所有类型"""
    keys = {t['key'] for t in list_relationship_types()}
    assert keys == {'ex_partner', 'friend', 'family', 'colleague', 'idol'}


def test_get_relationship_type_returns_correct_type():
    """get_relationship_type 返回正确类型"""
    for key in ['ex_partner', 'friend', 'family', 'colleague', 'idol']:
        rt = get_relationship_type(key)
        assert isinstance(rt, RelationshipType)
        assert rt.key == key


def test_get_relationship_type_invalid_key():
    """无效 key 应抛出 KeyError"""
    try:
        get_relationship_type('nonexistent')
        assert False, "应抛出异常"
    except KeyError:
        pass


def test_select_relationship_type_valid_choice():
    """select_relationship_type 接受 1-5 的有效输入"""
    for choice, expected_key in [('1', 'ex_partner'), ('2', 'friend'),
                                  ('3', 'family'), ('4', 'colleague'), ('5', 'idol')]:
        with patch('builtins.input', return_value=choice):
            rt = select_relationship_type()
            assert rt.key == expected_key, f"输入 {choice} 应返回 {expected_key}，实际得到 {rt.key}"


def test_select_relationship_type_invalid_then_valid():
    """无效输入应重试，直到有效"""
    inputs = ['0', '6', 'abc', '3']
    with patch('builtins.input', side_effect=inputs):
        rt = select_relationship_type()
        assert rt.key == 'family'


# ============================================================
# 2. 模板生成
# ============================================================

FULL_INFO = {
    'name': '测试用户',
    'basic_info': '测试用的基本信息',
    'personality': 'ENFP 双子座 话很多',
    'breakup_reason': '异地恋',
    'relation': '母亲',
    'family_role': '主心骨',
    'friendship_dynamic': '经常一起开黑',
    'work_relationship': '平级合作',
    'source': '华语乐坛',
    'fandom_level': '追了10年',
    'raw_content': '这是聊天记录分析内容',
}


def test_memory_template_generation_for_all_types():
    """所有类型的 memory_template 应正确替换占位符"""
    for key in RELATIONSHIP_TYPES:
        rt = get_relationship_type(key)
        result = rt.generate_memory_template(FULL_INFO)
        # 应包含用户输入的内容
        assert '测试用户' in result
        # 不应有未替换的占位符（raw_content 可能会被替换为空）
        for placeholder in ['{name}', '{basic_info}', '{personality}']:
            assert placeholder not in result, f"{key}: 占位符 {placeholder} 未被替换"


def test_persona_template_generation_for_all_types():
    """所有类型的 persona_template 应正确替换占位符"""
    for key in RELATIONSHIP_TYPES:
        rt = get_relationship_type(key)
        result = rt.generate_persona_template(FULL_INFO)
        assert '测试用户' in result
        for placeholder in ['{name}', '{basic_info}']:
            assert placeholder not in result, f"{key}: 占位符 {placeholder} 未被替换"


def test_memory_template_with_partial_info():
    """部分信息不应导致崩溃，缺失字段保留 待补充"""
    partial_info = {'name': '小明'}
    rt = get_relationship_type('ex_partner')
    result = rt.generate_memory_template(partial_info)
    assert '小明' in result
    # 缺失的字段应被清空（保留模板结构）
    assert '{name}' not in result


def test_memory_template_empty_info():
    """即使 info 为空也不崩溃，占位符保留原样"""
    rt = get_relationship_type('friend')
    result = rt.generate_memory_template({})
    assert '# ' in result  # 至少输出模板结构


def test_persona_template_empty_info():
    """persona 模板空 info 不崩溃"""
    rt = get_relationship_type('family')
    result = rt.generate_persona_template({})
    assert 'Layer' in result


# ============================================================
# 3. 关系上下文
# ============================================================

def test_get_relationship_context():
    """get_relationship_context 返回正确的类型标识"""
    for key in RELATIONSHIP_TYPES:
        rt = get_relationship_type(key)
        ctx = rt.get_relationship_context({})
        assert ctx['relationship_type'] == key


# ============================================================
# 4. 端到端创建流程 (模拟)
# ============================================================

def test_end_to_end_create_flow_with_tempdir():
    """模拟完整的创建流程：step2 → step4 → step6"""
    # 准备临时目录
    with tempfile.TemporaryDirectory() as tmpdir:
        # 模拟 settings 指向临时目录
        settings = get_settings()
        original_personas_dir = settings.personas_dir
        settings.personas_dir = Path(tmpdir)

        try:
            # Step 1: 选择关系类型
            rt = get_relationship_type('ex_partner')

            # Step 2: 模拟基础信息录入
            info = {
                'name': '测试用户',
                'basic_info': '在一起两年 测试用',
                'personality': 'ENFP 双子座',
                'breakup_reason': '异地恋',
                'slug': 'test-user',
                'raw_content': '',
            }

            # Step 4: 生成内容
            memory_content = rt.generate_memory_template(info)
            persona_content = rt.generate_persona_template(info)

            assert '# 关系记忆' in memory_content
            assert '测试用户' in memory_content
            assert '# 人物性格' in persona_content
            assert 'ENFP 双子座' in persona_content

            # Step 6: 写入文件（模拟）
            skill_dir = settings.get_persona_skill_path(info['slug'])
            os.makedirs(skill_dir, exist_ok=True)

            memory_path = skill_dir / 'memory.md'
            memory_path.write_text(memory_content, encoding='utf-8')
            assert memory_path.exists()

            persona_path = skill_dir / 'persona.md'
            persona_path.write_text(persona_content, encoding='utf-8')
            assert persona_path.exists()

            meta = {
                "name": info['name'],
                "slug": info['slug'],
                "relationship_type": rt.key,
                "version": "v1",
            }
            meta_path = skill_dir / 'meta.json'
            meta_path.write_text(json.dumps(meta, ensure_ascii=False), encoding='utf-8')
            assert meta_path.exists()

            # 验证写入的内容可正确读取
            read_meta = json.loads(meta_path.read_text(encoding='utf-8'))
            assert read_meta['name'] == '测试用户'
            assert read_meta['relationship_type'] == 'ex_partner'

            read_memory = memory_path.read_text(encoding='utf-8')
            assert '测试用户' in read_memory

        finally:
            # 恢复原始配置
            settings.personas_dir = original_personas_dir


# ============================================================
# 5. 所有关系类型的完整模板输出检查
# ============================================================

def test_all_types_produce_valid_markdown_structure():
    """所有类型的模板应生成有效的 Markdown 结构"""
    for key, rt in RELATIONSHIP_TYPES.items():
        # memory 模板应有章节标题
        mem = rt.generate_memory_template(FULL_INFO)
        assert '#' in mem, f"{key}: memory 模板缺少 Markdown 标题"

        # persona 模板应有 Layer 结构
        per = rt.generate_persona_template(FULL_INFO)
        assert 'Layer' in per, f"{key}: persona 模板缺少 Layer 结构"


def test_all_types_have_correct_question_count():
    """检查每种类型的问题数量"""
    expected_counts = {
        'ex_partner': 4,
        'friend': 4,
        'family': 5,
        'colleague': 4,
        'idol': 5,
    }
    for key, expected in expected_counts.items():
        rt = get_relationship_type(key)
        assert len(rt.intake_questions) == expected, \
            f"{key}: 期望 {expected} 个问题，实际 {len(rt.intake_questions)}"


def test_required_questions():
    """每种类型至少有一个必填项 (name)"""
    for key in RELATIONSHIP_TYPES:
        rt = get_relationship_type(key)
        required = [q for q in rt.intake_questions if q.required]
        assert len(required) >= 1, f"{key}: 没有必填问题"
        assert required[0].key == 'name', f"{key}: 第一个必填项应为 name"


# ============================================================
# 6. 模板在 chat_engine 中的可用性
# ============================================================

def test_system_prompt_can_be_constructed():
    """生成的模板内容应能被 chat_engine 用于构建 system prompt"""
    rt = get_relationship_type('friend')
    info = {
        'name': '老王',
        'basic_info': '大学同学，认识8年',
        'personality': 'INTJ',
        'friendship_dynamic': '经常一起开黑',
        'raw_content': '',
    }

    memory = rt.generate_memory_template(info)
    persona = rt.generate_persona_template(info)

    # 模拟 PersonaSkillData.system_prompt
    system_prompt = f"""你是 {info['name']}，不是 AI 助手。用ta的方式说话，用ta的逻辑思考。

---

## PART A：关系记忆

{memory}

---

## PART B：人物性格

{persona}

---

## 运行规则

1. 你是{info['name']}，不是 AI 助手。
"""

    assert '老王' in system_prompt
    assert 'PART A' in system_prompt
    assert 'PART B' in system_prompt
    assert '大学同学' in system_prompt
    assert 'INTJ' in system_prompt


# ============================================================
# 7. 验证 prompt_loader 与 relationship_types 的协作
# ============================================================

def test_relationship_key_matches_prompt_files():
    """关系类型的 key 应对应提示词目录中的文件名"""
    from tools.prompt_loader import get_loader
    loader = get_loader()

    for key in RELATIONSHIP_TYPES:
        try:
            loader.load(key, 'memory_analyzer')
        except FileNotFoundError:
            assert False, f"缺少 memory_analyzer/{key}.md"
        try:
            loader.load(key, 'persona_builder')
        except FileNotFoundError:
            assert False, f"缺少 persona_builder/{key}.md"
