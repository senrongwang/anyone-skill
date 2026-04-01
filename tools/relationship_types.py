#!/usr/bin/env python3
"""关系类型定义模块

定义通用的人物关系类型基类和具体实现。
每种关系类型有独立的信息录入模板、记忆维度和标签体系。
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum


class RelationshipCategory(str, Enum):
    """关系类型枚举"""
    EX_PARTNER = "ex_partner"      # 前任/恋人
    FRIEND = "friend"              # 朋友
    FAMILY = "family"              # 家人
    COLLEAGUE = "colleague"        # 同事
    IDOL = "idol"                  # 偶像/角色
    CUSTOM = "custom"              # 自定义


@dataclass
class QuestionTemplate:
    """问题模板"""
    key: str                       # 字段key
    question: str                  # 问题文本
    placeholder: str = ""          # 输入示例
    required: bool = False         # 是否必填
    multiline: bool = False        # 是否多行输入


@dataclass
class MemoryDimension:
    """记忆维度定义"""
    key: str                       # 维度key
    name: str                      # 显示名称
    description: str               # 描述
    prompt_template: str           # 提取提示模板


@dataclass
class TagCategory:
    """标签类别"""
    key: str
    name: str
    options: List[str]
    multi_select: bool = True


class RelationshipType(ABC):
    """关系类型抽象基类
    
    每种关系类型需要实现：
    - 信息录入问题序列
    - 记忆提取维度
    - 标签体系
    - 记忆模板生成
    """
    
    def __init__(self):
        self.category: RelationshipCategory = RelationshipCategory.CUSTOM
        self.display_name: str = "自定义"
        self.description: str = ""
        self.icon: str = "👤"
    
    @abstractmethod
    def get_intake_questions(self) -> List[QuestionTemplate]:
        """获取信息录入问题列表"""
        pass
    
    @abstractmethod
    def get_memory_dimensions(self) -> List[MemoryDimension]:
        """获取记忆提取维度"""
        pass
    
    @abstractmethod
    def get_tag_categories(self) -> List[TagCategory]:
        """获取标签类别"""
        pass
    
    @abstractmethod
    def generate_memory_template(self, info: Dict[str, Any]) -> str:
        """生成记忆文档模板"""
        pass
    
    @abstractmethod
    def generate_persona_template(self, info: Dict[str, Any]) -> str:
        """生成性格文档模板"""
        pass
    
    def get_relationship_context(self, info: Dict[str, Any]) -> Dict[str, Any]:
        """获取关系特定上下文，用于meta.json"""
        return {}


class ExPartnerType(RelationshipType):
    """前任/恋人关系类型"""
    
    def __init__(self):
        super().__init__()
        self.category = RelationshipCategory.EX_PARTNER
        self.display_name = "前任/恋人"
        self.description = "恋爱关系，包含甜蜜回忆、争吵模式、分手经历等"
        self.icon = "💔"
    
    def get_intake_questions(self) -> List[QuestionTemplate]:
        return [
            QuestionTemplate(
                key="name",
                question="花名/代号（如：小明、初恋、那个人）",
                placeholder="小明",
                required=True
            ),
            QuestionTemplate(
                key="basic_info",
                question="基本信息（在一起多久、分手多久、ta做什么的）",
                placeholder="在一起两年 分手半年了 互联网产品经理",
                required=False
            ),
            QuestionTemplate(
                key="personality",
                question="性格画像（MBTI、星座、性格标签、你对ta的印象）",
                placeholder="ENFP 双子座 话很多 永远在社交 但深夜会突然emo",
                required=False
            ),
            QuestionTemplate(
                key="breakup_reason",
                question="分开的原因（简要描述）",
                placeholder="异地恋，毕业后各奔东西",
                required=False
            )
        ]
    
    def get_memory_dimensions(self) -> List[MemoryDimension]:
        return [
            MemoryDimension(
                key="timeline",
                name="关系时间线",
                description="认识 → 在一起 → 关键事件 → 分手",
                prompt_template="提取关系发展的关键时间节点和事件"
            ),
            MemoryDimension(
                key="sweet_moments",
                name="甜蜜瞬间",
                description="最难忘的浪漫时刻",
                prompt_template="提取恋爱中最甜蜜、最难忘的瞬间"
            ),
            MemoryDimension(
                key="conflict_pattern",
                name="争吵模式",
                description="吵架时的典型行为和解决方式",
                prompt_template="分析争吵触发点、过程和和解方式"
            ),
            MemoryDimension(
                key="daily_routine",
                name="日常习惯",
                description="共同生活的日常模式",
                prompt_template="提取日常生活、饮食习惯、作息规律"
            ),
            MemoryDimension(
                key="inside_jokes",
                name="专属梗",
                description="只有你们懂的笑话和暗语",
                prompt_template="提取内部笑话、专属称呼、共同暗语"
            ),
            MemoryDimension(
                key="favorite_places",
                name="常去地点",
                description="约会和常去的地方",
                prompt_template="提取约会地点、常去餐厅、旅行目的地"
            )
        ]
    
    def get_tag_categories(self) -> List[TagCategory]:
        return [
            TagCategory(
                key="attachment_style",
                name="依恋类型",
                options=["安全型", "焦虑型", "回避型", "混乱型"],
                multi_select=False
            ),
            TagCategory(
                key="love_language",
                name="爱的语言",
                options=["肯定的言辞", "精心的时刻", "接受礼物", "服务的行动", "身体的接触"],
                multi_select=True
            ),
            TagCategory(
                key="personality",
                name="性格标签",
                options=["话痨", "闷骚", "嘴硬心软", "冷暴力", "粘人", "独立", 
                        "浪漫主义", "实用主义", "完美主义", "拖延症", "工作狂",
                        "已读不回", "秒回选手", "半夜发语音"],
                multi_select=True
            )
        ]
    
    def generate_memory_template(self, info: Dict[str, Any]) -> str:
        return f"""# 关系记忆

## 基本信息
- 花名：{info.get('name', '未命名')}
- 关系描述：{info.get('basic_info', '未提供')}
- 分开原因：{info.get('breakup_reason', '未说明')}

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
{info.get('raw_content', '暂无详细记录，请通过对话逐步补充。')}
"""
    
    def generate_persona_template(self, info: Dict[str, Any]) -> str:
        personality = info.get('personality', '')
        return f"""# 人物性格

## Layer 0: 硬规则
- 不说现实中绝不会说的话
- 不突然变得完美或无条件包容
- 保持真实的"棱角"

## Layer 1: 身份
- 名字：{info.get('name', '未命名')}
- {info.get('basic_info', '身份信息待补充')}

## Layer 2: 说话风格
- 性格描述：{personality or '待补充'}
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
- 分手后的态度：待补充
"""
    
    def get_relationship_context(self, info: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "relationship_type": "ex_partner",
            "together_duration": "",
            "apart_since": "",
            "breakup_reason": info.get('breakup_reason', '')
        }


class FriendType(RelationshipType):
    """朋友关系类型"""
    
    def __init__(self):
        super().__init__()
        self.category = RelationshipCategory.FRIEND
        self.display_name = "朋友"
        self.description = "友情关系，包含共同爱好、相处模式、难忘经历等"
        self.icon = "🤝"
    
    def get_intake_questions(self) -> List[QuestionTemplate]:
        return [
            QuestionTemplate(
                key="name",
                question="朋友称呼/昵称",
                placeholder="老王、阿杰",
                required=True
            ),
            QuestionTemplate(
                key="basic_info",
                question="认识多久了、怎么认识的、ta做什么的",
                placeholder="大学同学，认识8年了，现在是程序员",
                required=False
            ),
            QuestionTemplate(
                key="personality",
                question="性格特点（MBTI、兴趣爱好、你对ta的印象）",
                placeholder="INTJ 喜欢打游戏 话不多但很靠谱",
                required=False
            ),
            QuestionTemplate(
                key="friendship_dynamic",
                question="你们的相处模式",
                placeholder="经常一起开黑，偶尔约饭，有事直说",
                required=False
            )
        ]
    
    def get_memory_dimensions(self) -> List[MemoryDimension]:
        return [
            MemoryDimension(
                key="how_we_met",
                name="相识经历",
                description="怎么认识的，第一印象",
                prompt_template="提取相识场景和初印象"
            ),
            MemoryDimension(
                key="shared_hobbies",
                name="共同爱好",
                description="一起做的事、共同兴趣",
                prompt_template="提取共同活动和兴趣爱好"
            ),
            MemoryDimension(
                key="adventures",
                name="难忘经历",
                description="一起经历的特别时刻",
                prompt_template="提取旅行、冒险、难忘时刻"
            ),
            MemoryDimension(
                key="support_moments",
                name="互相支持",
                description="困难时刻的陪伴和帮助",
                prompt_template="提取互相支持、鼓励的时刻"
            ),
            MemoryDimension(
                key="hangout_spots",
                name="常聚地点",
                description="常去的地方",
                prompt_template="提取聚会地点、常去场所"
            ),
            MemoryDimension(
                key="friendship_rituals",
                name="友情仪式",
                description="固定的相处模式或传统",
                prompt_template="提取固定的活动、年度传统、专属仪式"
            )
        ]
    
    def get_tag_categories(self) -> List[TagCategory]:
        return [
            TagCategory(
                key="friendship_type",
                name="友情类型",
                options=["发小", "同学", "同事", "网友", "兴趣伙伴", "知己"],
                multi_select=False
            ),
            TagCategory(
                key="interaction_style",
                name="相处模式",
                options=["天天联系", "有事才找", "定期聚会", "默契型", "互怼型", "暖心型"],
                multi_select=True
            ),
            TagCategory(
                key="personality",
                name="性格标签",
                options=["靠谱", "幽默", "毒舌", "暖男/女", "技术宅", "社交达人",
                        "吃货", "旅行家", "游戏狂", "话痨", "倾听者"],
                multi_select=True
            )
        ]
    
    def generate_memory_template(self, info: Dict[str, Any]) -> str:
        return f"""# 友情记忆

## 基本信息
- 称呼：{info.get('name', '未命名')}
- 认识背景：{info.get('basic_info', '未提供')}
- 相处模式：{info.get('friendship_dynamic', '未说明')}

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
{info.get('raw_content', '暂无详细记录，请通过对话逐步补充。')}
"""
    
    def generate_persona_template(self, info: Dict[str, Any]) -> str:
        return f"""# 人物性格

## Layer 0: 硬规则
- 不说现实中绝不会说的话
- 保持朋友的真实性格
- 不刻意迎合或过度热情

## Layer 1: 身份
- 名字：{info.get('name', '未命名')}
- {info.get('basic_info', '身份信息待补充')}

## Layer 2: 说话风格
- 性格描述：{info.get('personality', '待补充')}
- 口头禅：待补充
- 聊天习惯：待补充（正式/随意/爱用梗）
- 回复速度：待补充

## Layer 3: 情感表达
- 关心方式：待补充
- 安慰模式：待补充
- 开玩笑风格：待补充

## Layer 4: 相处行为
- 主动程度：待补充
- 约人习惯：待补充
- 朋友圈互动：待补充
- 有事时的反应：待补充
"""
    
    def get_relationship_context(self, info: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "relationship_type": "friend",
            "known_since": "",
            "how_met": "",
            "friendship_dynamic": info.get('friendship_dynamic', '')
        }


class FamilyType(RelationshipType):
    """家人关系类型"""
    
    def __init__(self):
        super().__init__()
        self.category = RelationshipCategory.FAMILY
        self.display_name = "家人"
        self.description = "亲情关系，包含家庭角色、成长记忆、关怀方式等"
        self.icon = "🏠"
    
    def get_intake_questions(self) -> List[QuestionTemplate]:
        return [
            QuestionTemplate(
                key="name",
                question="称呼（如：妈妈、老爸、姐姐）",
                placeholder="老妈",
                required=True
            ),
            QuestionTemplate(
                key="relation",
                question="具体关系",
                placeholder="母亲",
                required=True
            ),
            QuestionTemplate(
                key="basic_info",
                question="基本信息（年龄、职业、居住地）",
                placeholder="55岁，退休教师，住在老家",
                required=False
            ),
            QuestionTemplate(
                key="personality",
                question="性格特点（你对ta的印象）",
                placeholder="严厉但关心人，爱唠叨，手艺很好",
                required=False
            ),
            QuestionTemplate(
                key="family_role",
                question="在家庭中的角色",
                placeholder="家里的主心骨，大事都听她的",
                required=False
            )
        ]
    
    def get_memory_dimensions(self) -> List[MemoryDimension]:
        return [
            MemoryDimension(
                key="childhood_memories",
                name="成长记忆",
                description="童年时期与ta的记忆",
                prompt_template="提取童年时期的共同记忆"
            ),
            MemoryDimension(
                key="care_expressions",
                name="关怀方式",
                description="ta表达关心的独特方式",
                prompt_template="提取关心、照顾的具体行为和言语"
            ),
            MemoryDimension(
                key="family_traditions",
                name="家庭传统",
                description="家庭特有的习惯和仪式",
                prompt_template="提取节日传统、家庭习惯、固定活动"
            ),
            MemoryDimension(
                key="life_lessons",
                name="人生教诲",
                description="ta常说的道理和教导",
                prompt_template="提取常说的道理、教导、口头禅"
            ),
            MemoryDimension(
                key="cooking_food",
                name="拿手菜/味道",
                description="ta做的特别的食物",
                prompt_template="提取拿手菜、特色食物、味道记忆"
            ),
            MemoryDimension(
                key="recent_changes",
                name="变化与衰老",
                description="观察到的ta的变化",
                prompt_template="提取外貌、性格、健康方面的变化"
            )
        ]
    
    def get_tag_categories(self) -> List[TagCategory]:
        return [
            TagCategory(
                key="family_role",
                name="家庭角色",
                options=["权威型", "温柔型", "幽默型", "沉默型", "操心型", "开明型"],
                multi_select=False
            ),
            TagCategory(
                key="care_style",
                name="关怀方式",
                options=["唠叨型", "行动型", "默默付出型", "直接表达型", "物质满足型"],
                multi_select=True
            ),
            TagCategory(
                key="personality",
                name="性格标签",
                options=["严厉", "慈爱", "节俭", "大方", "传统", "开明",
                        "要强", "随和", "细心", "粗心", "乐观", "悲观"],
                multi_select=True
            )
        ]
    
    def generate_memory_template(self, info: Dict[str, Any]) -> str:
        return f"""# 亲情记忆

## 基本信息
- 称呼：{info.get('name', '未命名')}
- 关系：{info.get('relation', '未说明')}
- 基本情况：{info.get('basic_info', '未提供')}
- 家庭角色：{info.get('family_role', '未说明')}

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
{info.get('raw_content', '暂无详细记录，请通过对话逐步补充。')}
"""
    
    def generate_persona_template(self, info: Dict[str, Any]) -> str:
        return f"""# 人物性格

## Layer 0: 硬规则
- 保持家人的真实性格
- 体现长辈的关怀或同辈的亲密
- 符合家庭角色的说话方式

## Layer 1: 身份
- 称呼：{info.get('name', '未命名')}
- 关系：{info.get('relation', '待补充')}
- {info.get('basic_info', '身份信息待补充')}

## Layer 2: 说话风格
- 性格描述：{info.get('personality', '待补充')}
- 说话特点：待补充（方言/普通话、语速、语气）
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
- 家庭事务中的角色：待补充
"""
    
    def get_relationship_context(self, info: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "relationship_type": "family",
            "relation": info.get('relation', ''),
            "family_role": info.get('family_role', '')
        }


class ColleagueType(RelationshipType):
    """同事关系类型"""
    
    def __init__(self):
        super().__init__()
        self.category = RelationshipCategory.COLLEAGUE
        self.display_name = "同事"
        self.description = "职场关系，包含工作风格、合作项目、职场互动等"
        self.icon = "💼"
    
    def get_intake_questions(self) -> List[QuestionTemplate]:
        return [
            QuestionTemplate(
                key="name",
                question="同事称呼/花名",
                placeholder="张哥、Lisa",
                required=True
            ),
            QuestionTemplate(
                key="basic_info",
                question="职位、部门、共事多久",
                placeholder="技术总监，研发部，共事3年",
                required=False
            ),
            QuestionTemplate(
                key="personality",
                question="工作风格和性格",
                placeholder="雷厉风行，细节控，对下属很好",
                required=False
            ),
            QuestionTemplate(
                key="work_relationship",
                question="你们的职场关系",
                placeholder="我带过ta的项目，现在是平级合作",
                required=False
            )
        ]
    
    def get_memory_dimensions(self) -> List[MemoryDimension]:
        return [
            MemoryDimension(
                key="projects",
                name="合作项目",
                description="一起完成的重要项目",
                prompt_template="提取合作项目、角色分工、成果"
            ),
            MemoryDimension(
                key="work_style",
                name="工作风格",
                description="ta的工作习惯和方式",
                prompt_template="提取工作风格、效率习惯、专业特点"
            ),
            MemoryDimension(
                key="office_interactions",
                name="职场互动",
                description="日常工作中的交流",
                prompt_template="提取会议、沟通、协作模式"
            ),
            MemoryDimension(
                key="crisis_moments",
                name="危机时刻",
                description="加班、赶项目、出问题的时刻",
                prompt_template="提取紧急项目、加班、问题解决"
            ),
            MemoryDimension(
                key="after_work",
                name="工作之外",
                description="团建、聚餐等非工作互动",
                prompt_template="提取团建、聚餐、私下交流"
            ),
            MemoryDimension(
                key="career_influence",
                name="职业影响",
                description="ta对你的职业发展的影响",
                prompt_template="提取指导、建议、职业影响"
            )
        ]
    
    def get_tag_categories(self) -> List[TagCategory]:
        return [
            TagCategory(
                key="work_style",
                name="工作风格",
                options=["雷厉风行", "稳扎稳打", "细节控", "大局观", "独狼型", "团队型"],
                multi_select=True
            ),
            TagCategory(
                key="position_relation",
                name="职位关系",
                options=["上级", "下属", "平级", "跨部门", "导师", "前同事"],
                multi_select=False
            ),
            TagCategory(
                key="personality",
                name="职场性格",
                options=["专业", "亲和", "严厉", "佛系", "进取", "保守",
                        "靠谱", "甩锅", "卷王", "准时下班"],
                multi_select=True
            )
        ]
    
    def generate_memory_template(self, info: Dict[str, Any]) -> str:
        return f"""# 职场记忆

## 基本信息
- 称呼：{info.get('name', '未命名')}
- 职位信息：{info.get('basic_info', '未提供')}
- 职场关系：{info.get('work_relationship', '未说明')}

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
{info.get('raw_content', '暂无详细记录，请通过对话逐步补充。')}
"""
    
    def generate_persona_template(self, info: Dict[str, Any]) -> str:
        return f"""# 人物性格

## Layer 0: 硬规则
- 保持职场专业性
- 符合职位身份的说话方式
- 体现真实的职场性格

## Layer 1: 身份
- 称呼：{info.get('name', '未命名')}
- {info.get('basic_info', '职位信息待补充')}

## Layer 2: 说话风格
- 工作风格：{info.get('personality', '待补充')}
- 沟通方式：待补充（直接/委婉、正式/随意）
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
- 工作之外的关系：待补充
"""
    
    def get_relationship_context(self, info: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "relationship_type": "colleague",
            "position_relation": "",
            "work_relationship": info.get('work_relationship', '')
        }


class IdolType(RelationshipType):
    """偶像/角色关系类型"""
    
    def __init__(self):
        super().__init__()
        self.category = RelationshipCategory.IDOL
        self.display_name = "偶像/角色"
        self.description = "偶像、虚拟角色或历史人物，基于公开资料或作品设定"
        self.icon = "⭐"
    
    def get_intake_questions(self) -> List[QuestionTemplate]:
        return [
            QuestionTemplate(
                key="name",
                question="名字（真实姓名或角色名）",
                placeholder="周杰伦、孙悟空、Sherlock Holmes",
                required=True
            ),
            QuestionTemplate(
                key="source",
                question="出处（作品、领域、时代）",
                placeholder="华语乐坛、《西游记》、英剧《神探夏洛克》",
                required=False
            ),
            QuestionTemplate(
                key="basic_info",
                question="基本设定（身份、背景、特点）",
                placeholder="天才侦探，观察力敏锐，有点反社会",
                required=False
            ),
            QuestionTemplate(
                key="personality",
                question="性格特征",
                placeholder="高冷、毒舌、对朋友很好",
                required=False
            ),
            QuestionTemplate(
                key="fandom_level",
                question="你对ta的了解程度",
                placeholder="看过所有作品/专辑，追了10年",
                required=False
            )
        ]
    
    def get_memory_dimensions(self) -> List[MemoryDimension]:
        return [
            MemoryDimension(
                key="character_arc",
                name="人物弧线",
                description="角色的成长变化",
                prompt_template="提取角色的成长轨迹、转变时刻"
            ),
            MemoryDimension(
                key="iconic_moments",
                name="经典时刻",
                description="最难忘的场景或表演",
                prompt_template="提取经典台词、场景、表演瞬间"
            ),
            MemoryDimension(
                key="relationships",
                name="人物关系",
                description="与其他角色的关系",
                prompt_template="提取与其他角色的互动模式"
            ),
            MemoryDimension(
                key="quotes",
                name="经典语录",
                description="标志性的台词或发言",
                prompt_template="提取经典语录、口头禅、标志性发言"
            ),
            MemoryDimension(
                key="fan_memories",
                name="粉丝记忆",
                description="你作为粉丝的经历",
                prompt_template="提取追星经历、演唱会、作品感受"
            ),
            MemoryDimension(
                key="interpretations",
                name="个人理解",
                description="你对ta的独特理解",
                prompt_template="提取个人解读、情感连接、特殊意义"
            )
        ]
    
    def get_tag_categories(self) -> List[TagCategory]:
        return [
            TagCategory(
                key="idol_type",
                name="类型",
                options=["真实人物", "虚构角色", "历史人物", "虚拟偶像", "AI角色"],
                multi_select=False
            ),
            TagCategory(
                key="character_traits",
                name="性格特质",
                options=["天才", "热血", "高冷", "幽默", "腹黑", "温柔",
                        "傲娇", "正直", "叛逆", "神秘"],
                multi_select=True
            ),
            TagCategory(
                key="appeal",
                name="魅力点",
                options=["颜值", "才华", "性格", "实力", "努力", "反差萌"],
                multi_select=True
            )
        ]
    
    def generate_memory_template(self, info: Dict[str, Any]) -> str:
        return f"""# 角色记忆

## 基本信息
- 名字：{info.get('name', '未命名')}
- 出处：{info.get('source', '未提供')}
- 基本设定：{info.get('basic_info', '未提供')}
- 粉丝程度：{info.get('fandom_level', '未说明')}

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
{info.get('raw_content', '暂无详细记录，请通过对话逐步补充。')}
"""
    
    def generate_persona_template(self, info: Dict[str, Any]) -> str:
        return f"""# 角色性格

## Layer 0: 硬规则
- 严格遵循原作/真实人物的设定
- 不说与角色性格不符的话
- 保持角色的一致性和真实感

## Layer 1: 身份
- 名字：{info.get('name', '未命名')}
- 出处：{info.get('source', '待补充')}
- {info.get('basic_info', '基本设定待补充')}

## Layer 2: 说话风格
- 性格特征：{info.get('personality', '待补充')}
- 语言特点：待补充（用词习惯、语气、口音）
- 经典台词：待补充
- 表达方式：待补充

## Layer 3: 情感模式
- 情感表达方式：待补充
- 对重要事物的态度：待补充
- 弱点和软肋：待补充

## Layer 4: 互动模式
- 与他人的互动方式：待补充
- 面对不同人的态度差异：待补充
- 特殊情境下的反应：待补充
"""
    
    def get_relationship_context(self, info: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "relationship_type": "idol",
            "source": info.get('source', ''),
            "idol_type": "",
            "fandom_level": info.get('fandom_level', '')
        }


# 关系类型注册表
RELATIONSHIP_TYPES: Dict[RelationshipCategory, RelationshipType] = {
    RelationshipCategory.EX_PARTNER: ExPartnerType(),
    RelationshipCategory.FRIEND: FriendType(),
    RelationshipCategory.FAMILY: FamilyType(),
    RelationshipCategory.COLLEAGUE: ColleagueType(),
    RelationshipCategory.IDOL: IdolType(),
}


def get_relationship_type(category: RelationshipCategory) -> RelationshipType:
    """获取关系类型实例"""
    return RELATIONSHIP_TYPES.get(category, ExPartnerType())


def list_relationship_types() -> List[Dict[str, str]]:
    """列出所有可用的关系类型"""
    return [
        {
            "key": rt.category.value,
            "name": rt.display_name,
            "description": rt.description,
            "icon": rt.icon
        }
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
                selected = types[idx]
                return get_relationship_type(RelationshipCategory(selected['key']))
            print("无效选择，请重试。")
        except (ValueError, IndexError):
            print("请输入数字 1-5。")
