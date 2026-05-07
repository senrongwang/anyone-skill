"""关系类型定义——数据驱动

每种关系类型是 RelationshipType 的一个实例，配置不同的问题模板和内容模板。
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Any


@dataclass
class QuestionTemplate:
    """问题模板"""
    key: str
    question: str
    placeholder: str = ""
    required: bool = False


@dataclass
class RelationshipType:
    """关系类型——纯数据驱动，无需继承"""
    key: str
    display_name: str
    description: str
    icon: str
    intake_questions: List[QuestionTemplate]
    memory_template: str = ""
    persona_template: str = ""

    def generate_memory_template(self, info: Dict[str, Any]) -> str:
        """生成 memory.md 占位内容"""
        return _fill_template(self.memory_template, info)

    def generate_persona_template(self, info: Dict[str, Any]) -> str:
        """生成 persona.md 占位内容"""
        return _fill_template(self.persona_template, info)

    def get_relationship_context(self, info: Dict[str, Any]) -> Dict[str, Any]:
        """获取关系上下文（写入 meta.json）"""
        return {"relationship_type": self.key}


def _fill_template(template: str, info: Dict[str, Any]) -> str:
    """用 info 填充模板中的 {key} 占位符，缺失项保留原占位符"""
    result = template
    for key, value in info.items():
        result = result.replace(f'{{{key}}}', value if value else '')
    return result


# ============================================================
# 5 种关系类型的配置
# ============================================================

RELATIONSHIP_TYPES: Dict[str, RelationshipType] = {
    "ex_partner": RelationshipType(
        key="ex_partner",
        display_name="前任/恋人",
        description="恋爱关系，包含甜蜜回忆、争吵模式、分手经历等",
        icon="💔",
        intake_questions=[
            QuestionTemplate(key="name", question="花名/代号（如：小明、初恋、那个人）",
                             placeholder="小明", required=True),
            QuestionTemplate(key="basic_info",
                             question="基本信息（在一起多久、分手多久、ta做什么的）",
                             placeholder="在一起两年 分手半年了 互联网产品经理"),
            QuestionTemplate(key="personality",
                             question="性格画像（MBTI、星座、性格标签、你对ta的印象）",
                             placeholder="ENFP 双子座 话很多 永远在社交 但深夜会突然emo"),
            QuestionTemplate(key="breakup_reason",
                             question="分开的原因（简要描述）",
                             placeholder="异地恋，毕业后各奔东西"),
        ],
        memory_template="""# 关系记忆

## 基本信息
- 花名：{name}
- 关系描述：{basic_info}
- 分开原因：{breakup_reason}

## 关系时间线
- 认识时间：待补充
- 在一起时间：待补充
- 分手时间：待补充

## 甜蜜瞬间
待补充

## 争吵模式
待补充

## 日常习惯
待补充

## 专属梗
待补充

## 常去地点
待补充

## 聊天记录分析
{raw_content}""",
        persona_template="""# 人物性格

## Layer 0: 硬规则
- 不说现实中绝不会说的话
- 不突然变得完美或无条件包容
- 保持真实的"棱角"

## Layer 1: 身份
- 名字：{name}
- {basic_info}

## Layer 2: 说话风格
- 性格描述：{personality}
- 口头禅：待补充
- 语气习惯：待补充
- 表情符号偏好：待补充

## Layer 3: 情感模式
- 依恋类型：待补充
- 爱的语言：待补充
- 表达方式：待补充

## Layer 4: 关系行为
- 吵架模式：待补充
- 和好方式：待补充
- 日常互动：待补充
- 分手后的态度：待补充""",
    ),

    "friend": RelationshipType(
        key="friend",
        display_name="朋友",
        description="友情关系，包含共同爱好、相处模式、难忘经历等",
        icon="🤝",
        intake_questions=[
            QuestionTemplate(key="name", question="朋友称呼/昵称",
                             placeholder="老王、阿杰", required=True),
            QuestionTemplate(key="basic_info",
                             question="认识多久了、怎么认识的、ta做什么的",
                             placeholder="大学同学，认识8年了，现在是程序员"),
            QuestionTemplate(key="personality",
                             question="性格特点（MBTI、兴趣爱好、你对ta的印象）",
                             placeholder="INTJ 喜欢打游戏 话不多但很靠谱"),
            QuestionTemplate(key="friendship_dynamic",
                             question="你们的相处模式",
                             placeholder="经常一起开黑，偶尔约饭，有事直说"),
        ],
        memory_template="""# 友情记忆

## 基本信息
- 称呼：{name}
- 认识背景：{basic_info}
- 相处模式：{friendship_dynamic}

## 相识经历
- 认识时间：待补充
- 认识场景：待补充
- 第一印象：待补充

## 共同爱好
待补充

## 难忘经历
待补充

## 互相支持
待补充

## 常聚地点
待补充

## 友情仪式
待补充

## 聊天记录分析
{raw_content}""",
        persona_template="""# 人物性格

## Layer 0: 硬规则
- 不说现实中绝不会说的话
- 保持朋友的真实性格
- 不刻意迎合或过度热情

## Layer 1: 身份
- 名字：{name}
- {basic_info}

## Layer 2: 说话风格
- 性格描述：{personality}
- 口头禅：待补充
- 聊天习惯：待补充
- 回复速度：待补充

## Layer 3: 情感表达
- 关心方式：待补充
- 安慰模式：待补充
- 开玩笑风格：待补充

## Layer 4: 相处行为
- 主动程度：待补充
- 约人习惯：待补充
- 朋友圈互动：待补充
- 有事时的反应：待补充""",
    ),

    "family": RelationshipType(
        key="family",
        display_name="家人",
        description="亲情关系，包含家庭角色、成长记忆、关怀方式等",
        icon="🏠",
        intake_questions=[
            QuestionTemplate(key="name", question="称呼（如：妈妈、老爸、姐姐）",
                             placeholder="老妈", required=True),
            QuestionTemplate(key="relation", question="具体关系",
                             placeholder="母亲", required=True),
            QuestionTemplate(key="basic_info",
                             question="基本信息（年龄、职业、居住地）",
                             placeholder="55岁，退休教师，住在老家"),
            QuestionTemplate(key="personality",
                             question="性格特点（你对ta的印象）",
                             placeholder="严厉但关心人，爱唠叨，手艺很好"),
            QuestionTemplate(key="family_role",
                             question="在家庭中的角色",
                             placeholder="家里的主心骨，大事都听她的"),
        ],
        memory_template="""# 亲情记忆

## 基本信息
- 称呼：{name}
- 关系：{relation}
- 基本情况：{basic_info}
- 家庭角色：{family_role}

## 成长记忆
待补充

## 关怀方式
待补充

## 家庭传统
待补充

## 人生教诲
待补充

## 拿手菜/味道
待补充

## 变化与衰老
待补充

## 聊天记录分析
{raw_content}""",
        persona_template="""# 人物性格

## Layer 0: 硬规则
- 保持家人的真实性格
- 体现长辈的关怀或同辈的亲密
- 符合家庭角色的说话方式

## Layer 1: 身份
- 称呼：{name}
- 关系：{relation}
- {basic_info}

## Layer 2: 说话风格
- 性格描述：{personality}
- 说话特点：待补充
- 常用语：待补充
- 称呼你的方式：待补充

## Layer 3: 情感表达
- 关心方式：待补充
- 表达爱的方式：待补充
- 生气时的表现：待补充

## Layer 4: 相处行为
- 联系频率：待补充
- 见面时的表现：待补充
- 对你的期望：待补充
- 家庭事务中的角色：待补充""",
    ),

    "colleague": RelationshipType(
        key="colleague",
        display_name="同事",
        description="职场关系，包含工作风格、合作项目、职场互动等",
        icon="💼",
        intake_questions=[
            QuestionTemplate(key="name", question="同事称呼/花名",
                             placeholder="张哥、Lisa", required=True),
            QuestionTemplate(key="basic_info",
                             question="职位、部门、共事多久",
                             placeholder="技术总监，研发部，共事3年"),
            QuestionTemplate(key="personality",
                             question="工作风格和性格",
                             placeholder="雷厉风行，细节控，对下属很好"),
            QuestionTemplate(key="work_relationship",
                             question="你们的职场关系",
                             placeholder="我带过ta的项目，现在是平级合作"),
        ],
        memory_template="""# 职场记忆

## 基本信息
- 称呼：{name}
- 职位信息：{basic_info}
- 职场关系：{work_relationship}

## 合作项目
待补充

## 工作风格
待补充

## 职场互动
待补充

## 危机时刻
待补充

## 工作之外
待补充

## 职业影响
待补充

## 聊天记录分析
{raw_content}""",
        persona_template="""# 人物性格

## Layer 0: 硬规则
- 保持职场专业性
- 符合职位身份的说话方式
- 体现真实的职场性格

## Layer 1: 身份
- 称呼：{name}
- {basic_info}

## Layer 2: 说话风格
- 工作风格：{personality}
- 沟通方式：待补充
- 会议风格：待补充
- 写邮件/消息的习惯：待补充

## Layer 3: 职场情感
- 对工作的态度：待补充
- 对团队的关心：待补充
- 压力下的表现：待补充

## Layer 4: 相处行为
- 协作模式：待补充
- 反馈方式：待补充
- 社交边界：待补充
- 工作之外的关系：待补充""",
    ),

    "idol": RelationshipType(
        key="idol",
        display_name="偶像/角色",
        description="偶像、虚拟角色或历史人物，基于公开资料或作品设定",
        icon="⭐",
        intake_questions=[
            QuestionTemplate(key="name", question="名字（真实姓名或角色名）",
                             placeholder="周杰伦、孙悟空、Sherlock Holmes", required=True),
            QuestionTemplate(key="source",
                             question="出处（作品、领域、时代）",
                             placeholder="华语乐坛、《西游记》、英剧《神探夏洛克》"),
            QuestionTemplate(key="basic_info",
                             question="基本设定（身份、背景、特点）",
                             placeholder="天才侦探，观察力敏锐，有点反社会"),
            QuestionTemplate(key="personality",
                             question="性格特征",
                             placeholder="高冷、毒舌、对朋友很好"),
            QuestionTemplate(key="fandom_level",
                             question="你对ta的了解程度",
                             placeholder="看过所有作品/专辑，追了10年"),
        ],
        memory_template="""# 角色记忆

## 基本信息
- 名字：{name}
- 出处：{source}
- 基本设定：{basic_info}
- 粉丝程度：{fandom_level}

## 人物弧线
待补充

## 经典时刻
待补充

## 人物关系
待补充

## 经典语录
待补充

## 粉丝记忆
待补充

## 个人理解
待补充

## 参考资料
{raw_content}""",
        persona_template="""# 角色性格

## Layer 0: 硬规则
- 严格遵循原作/真实人物的设定
- 不说与角色性格不符的话
- 保持角色的一致性和真实感

## Layer 1: 身份
- 名字：{name}
- 出处：{source}
- {basic_info}

## Layer 2: 说话风格
- 性格特征：{personality}
- 语言特点：待补充
- 经典台词：待补充
- 表达方式：待补充

## Layer 3: 情感模式
- 情感表达方式：待补充
- 对重要事物的态度：待补充
- 弱点和软肋：待补充

## Layer 4: 互动模式
- 与他人的互动方式：待补充
- 面对不同人的态度差异：待补充
- 特殊情境下的反应：待补充""",
    ),
}


# ============================================================
# 便捷函数（对外 API）
# ============================================================

def get_relationship_type(key: str) -> RelationshipType:
    """根据 key 获取关系类型实例"""
    if key not in RELATIONSHIP_TYPES:
        raise KeyError(f"未知的关系类型: {key}，可用类型: {list(RELATIONSHIP_TYPES.keys())}")
    return RELATIONSHIP_TYPES[key]


def list_relationship_types() -> List[Dict[str, str]]:
    """列出所有可用的关系类型"""
    return [
        {"key": rt.key, "name": rt.display_name,
         "description": rt.description, "icon": rt.icon}
        for rt in RELATIONSHIP_TYPES.values()
    ]


def select_relationship_type() -> RelationshipType:
    """交互式选择关系类型"""
    print("\n请选择关系类型：\n")
    types = list_relationship_types()
    for i, rt in enumerate(types, 1):
        print(f"  [{i}] {rt['icon']} {rt['name']} - {rt['description']}")

    while True:
        try:
            choice = input("\n选择 (1-5): ").strip()
            idx = int(choice) - 1
            if 0 <= idx < len(types):
                return RELATIONSHIP_TYPES[types[idx]['key']]
            print("无效选择，请重试。")
        except (ValueError, IndexError):
            print("请输入数字 1-5。")
