#!/usr/bin/env python3
"""校招面试 Skill 的题目前研究守卫。

输入用户材料 JSON，输出是否需要外部研究、行业路由、搜索预算、查询词和降级规则。
本脚本不联网，只生成受控搜索计划。
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Tuple


MAX_TOTAL_QUERIES = 8
MAX_RETRIES_PER_CATEGORY = 3
ANSWER_STAGE_MAX_QUERIES = 15


ROUTE_KEYWORDS: Dict[str, List[str]] = {
    "internet": [
        "互联网",
        "平台",
        "电商",
        "内容",
        "社区",
        "本地生活",
        "搜索",
        "推荐",
        "广告",
        "增长",
        "运营",
        "产品",
        "用户",
        "商业化",
        "gmv",
        "dau",
        "留存",
    ],
    "state_owned": [
        "央企",
        "国企",
        "能源",
        "电网",
        "运营商",
        "烟草",
        "铁路",
        "航司",
        "国有银行",
        "政策",
        "合规稳健",
    ],
    "public_institution": [
        "事业单位",
        "机关",
        "学校",
        "医院",
        "政务",
        "公共服务",
        "公文",
        "编制",
    ],
    "manufacturing": [
        "制造",
        "工业",
        "汽车",
        "半导体",
        "硬件",
        "供应链",
        "工厂",
        "生产",
        "质量",
        "交付",
        "设备",
        "良品率",
    ],
    "fmcg_retail": [
        "快消",
        "零售",
        "品牌",
        "渠道",
        "门店",
        "消费者",
        "新品",
        "动销",
        "货架",
        "营销",
        "复购",
    ],
    "finance": [
        "银行",
        "证券",
        "保险",
        "基金",
        "支付",
        "风控",
        "信贷",
        "财富管理",
        "投研",
        "金融",
    ],
    "consulting_professional": [
        "咨询",
        "战略",
        "研究",
        "审计",
        "法律",
        "投行",
        "fa",
        "专业服务",
        "客户项目",
    ],
    "education_healthcare": [
        "教育",
        "教培",
        "课程",
        "医疗",
        "药企",
        "健康",
        "患者",
        "医生",
        "学习效果",
    ],
}


AI_KEYWORDS = ["ai", "人工智能", "大模型", "智能化", "自动化", "算法", "agent", "智能体", "机器学习"]


ROUTE_QUERY_TEMPLATES: Dict[str, List[Tuple[str, str]]] = {
    "internet": [
        ("company_business", "{company} 官网 业务 产品"),
        ("company_business", "{company} 投资者关系 财报 业绩公告"),
        ("company_business", "{company} 核心业务 收入 利润 官方"),
        ("industry_context", "{industry} 核心指标 用户链路 商业模式"),
        ("competitor", "{company} 竞品 对比"),
        ("interview_signal", "{company} {position} 校招 面经"),
        ("interview_signal", "site:nowcoder.com {company} {position} 面经"),
        ("interview_signal", "site:xiaohongshu.com {company} {position} 面经"),
        ("ai_scenario", "{industry} AI 应用 产品 策略"),
    ],
    "state_owned": [
        ("company_business", "{company} 官网 业务"),
        ("company_business", "{company} 社会责任 报告"),
        ("industry_context", "{industry} 政策 趋势"),
        ("interview_signal", "{company} 校招 面经"),
        ("interview_signal", "{company} {position} 面试"),
        ("ai_scenario", "{industry} 数字化 AI 应用"),
    ],
    "public_institution": [
        ("company_business", "{company} 职责 业务 公共服务"),
        ("industry_context", "{industry} 政策 公共服务 趋势"),
        ("interview_signal", "{company} {position} 面试"),
        ("ai_scenario", "政务 公共服务 AI 应用 风险"),
    ],
    "manufacturing": [
        ("company_business", "{company} 产品 供应链 制造"),
        ("industry_context", "{industry} 成本 质量 交付 指标"),
        ("ai_scenario", "{industry} 智能制造 AI 质检 排产"),
        ("interview_signal", "{company} {position} 校招 面经"),
        ("competitor", "{company} 竞品 对比"),
    ],
    "fmcg_retail": [
        ("company_business", "{company} 品牌 渠道 动销"),
        ("competitor", "{company} 竞品 对比"),
        ("industry_context", "{industry} 消费者洞察 趋势"),
        ("ai_scenario", "{industry} AI 营销 消费者洞察"),
        ("interview_signal", "{company} {position} 校招 面经"),
    ],
    "finance": [
        ("company_business", "{company} 业务 金融产品"),
        ("industry_context", "{industry} 风险 合规 客户分层"),
        ("interview_signal", "{company} {position} 校招 面经"),
        ("ai_scenario", "{industry} AI 风控 合规 客服"),
    ],
    "consulting_professional": [
        ("company_business", "{company} 业务 专业服务"),
        ("industry_context", "{industry} 行业研究 框架"),
        ("interview_signal", "{company} {position} 校招 面经"),
        ("ai_scenario", "咨询 AI 研究效率 知识检索"),
    ],
    "education_healthcare": [
        ("company_business", "{company} 业务 产品 服务"),
        ("industry_context", "{industry} 效果 责任 合规"),
        ("interview_signal", "{company} {position} 校招 面经"),
        ("ai_scenario", "{industry} AI 应用 人工复核 风险"),
    ],
    "general_campus": [
        ("interview_signal", "{position} 校招 面经"),
        ("industry_context", "{position} 校招 面试 高频问题"),
    ],
}


@dataclass
class UserInput:
    target_company: str = ""
    industry: str = ""
    organization_type: str = ""
    position: str = ""
    jd: str = ""
    resume: str = ""
    interview_round: str = ""
    focus: str = ""
    no_external_research: bool = False
    selected_questions: List[str] | None = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "UserInput":
        normalized = {key: data.get(key, "") for key in cls.__dataclass_fields__}
        normalized["no_external_research"] = parse_bool(
            data.get("no_external_research", False)
        )
        selected = data.get("selected_questions", [])
        normalized["selected_questions"] = (
            [str(item).strip() for item in selected if str(item).strip()]
            if isinstance(selected, list)
            else []
        )
        return cls(**normalized)

    def searchable_text(self) -> str:
        return " ".join(
            str(value)
            for key, value in self.__dict__.items()
            if key not in {"no_external_research", "selected_questions"} and value
        ).lower()


def parse_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return value != 0
    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized in {"true", "1", "yes", "y", "是"}:
            return True
        if normalized in {"false", "0", "no", "n", "否", ""}:
            return False
    return False


def keyword_matches(text: str, keyword: str) -> bool:
    normalized_text = text.lower()
    normalized_keyword = keyword.lower()
    if re.fullmatch(r"[a-z0-9][a-z0-9 _+-]*", normalized_keyword):
        pattern = rf"(?<![a-z0-9]){re.escape(normalized_keyword)}(?![a-z0-9])"
        return re.search(pattern, normalized_text) is not None
    return normalized_keyword in normalized_text


def count_keywords(text: str, keywords: Iterable[str]) -> int:
    return sum(1 for keyword in keywords if keyword_matches(text, keyword))


def route_scores(text: str) -> Dict[str, int]:
    return {
        route: count_keywords(text, keywords)
        for route, keywords in ROUTE_KEYWORDS.items()
    }


def detect_route(user_input: UserInput) -> Dict[str, Any]:
    explicit_text = f"{user_input.industry} {user_input.organization_type}".strip().lower()
    explicit_scores = route_scores(explicit_text) if explicit_text else {}
    if explicit_scores and max(explicit_scores.values()) > 0:
        best_route, best_score = max(explicit_scores.items(), key=lambda item: item[1])
        return {
            "industry": best_route,
            "confidence": "high",
            "reason": "优先采用用户明确提供的行业或组织类型。",
            "scores": explicit_scores,
        }

    company_business_text = f"{user_input.target_company} {user_input.position}".strip().lower()
    company_scores = route_scores(company_business_text)
    jd_scores = route_scores(user_input.jd.lower())
    resume_scores = route_scores(user_input.resume.lower())
    scores = {
        route: company_scores[route] * 3 + jd_scores[route] * 2 + resume_scores[route]
        for route in ROUTE_KEYWORDS
    }
    best_route, best_score = max(scores.items(), key=lambda item: item[1])
    if best_score == 0:
        return {
            "industry": "general_campus",
            "confidence": "low",
            "reason": "未从用户信息中识别出明确行业或组织类型关键词。",
            "scores": scores,
        }
    confidence = "high" if best_score >= 4 else "medium"
    return {
        "industry": best_route,
        "confidence": confidence,
        "reason": "按公司/岗位、JD、简历的 3:2:1 权重识别主行业。",
        "scores": scores,
    }


def is_ai_relevant(user_input: UserInput) -> bool:
    return count_keywords(user_input.searchable_text(), AI_KEYWORDS) > 0


def should_research(user_input: UserInput, route: str) -> Tuple[bool, List[str]]:
    reasons: List[str] = []
    if user_input.no_external_research:
        return False, ["用户明确要求不联网或不做外部研究。"]
    if route == "general_campus" and not any(
        [user_input.target_company, user_input.industry, user_input.jd]
    ):
        return False, ["缺少公司、行业、产品或 JD，无法形成有效搜索词。"]
    if user_input.target_company:
        reasons.append("用户提供了目标公司。")
    if user_input.industry or user_input.organization_type:
        reasons.append("用户提供了明确行业或组织类型。")
    if any(word in user_input.focus for word in ["业务", "竞品", "面经", "AI", "ai", "反问"]):
        reasons.append("用户强化方向需要外部信息支撑。")
    if user_input.jd:
        reasons.append("用户提供了 JD，可结合岗位关键词搜集题目语境。")
    return bool(reasons), reasons or ["未触发必须研究条件。"]


def clean_query(query: str) -> str:
    query = re.sub(r"\s+", " ", query).strip()
    query = query.replace("{company}", "").replace("{position}", "").replace("{industry}", "")
    return re.sub(r"\s+", " ", query).strip()


def build_queries(user_input: UserInput, route: str, stage: str) -> List[Dict[str, Any]]:
    templates = ROUTE_QUERY_TEMPLATES.get(route, ROUTE_QUERY_TEMPLATES["general_campus"])
    limit = MAX_TOTAL_QUERIES if stage == "question" else ANSWER_STAGE_MAX_QUERIES
    values = {
        "company": user_input.target_company or user_input.organization_type or user_input.industry,
        "position": user_input.position or "校招",
        "industry": user_input.industry or user_input.organization_type or route,
    }
    queries: List[Dict[str, Any]] = []
    seen = set()
    if stage == "answer":
        for selected_question in (user_input.selected_questions or [])[:5]:
            topic = extract_question_topic(selected_question)
            if not topic:
                continue
            query = clean_query(
                f"{values['company']} {topic} 官方 数据 指标 案例"
            )
            if query and query not in seen:
                seen.add(query)
                queries.append(
                    {
                        "category": "answer_evidence",
                        "query": query,
                        "max_retry": MAX_RETRIES_PER_CATEGORY,
                        "source_policy": "只收集回答该题所需的公开业务事实、指标定义和案例；不得补写用户个人经历。",
                    }
                )
    for category, template in templates:
        query = clean_query(template.format(**values))
        if not query or query in seen:
            continue
        seen.add(query)
        queries.append(
            {
                "category": category,
                "query": query,
                "max_retry": MAX_RETRIES_PER_CATEGORY,
                "source_policy": source_policy_for_category(category),
            }
        )
        if len(queries) >= limit:
            break
    return queries


def extract_question_topic(question: str) -> str:
    text = re.sub(r"[？?，,。；;：:]", " ", question)
    stop_phrases = [
        "如何判断",
        "你会如何",
        "请说明",
        "请分析",
        "你认为",
        "为什么",
        "是否",
        "怎么",
    ]
    for phrase in stop_phrases:
        text = text.replace(phrase, " ")
    words = [word for word in re.split(r"\s+", text) if word]
    topic = " ".join(words[:2]).strip()
    return topic[:50]


def source_policy_for_category(category: str) -> str:
    if category == "interview_signal":
        return "面经/社区内容仅作题型信号，不作为事实依据；不可访问时不得绕过。"
    if category in {"company_business", "industry_context", "competitor", "ai_scenario"}:
        return "优先官网、财报、公告、政策文件、权威媒体、行业报告和技术博客。"
    if category == "answer_evidence":
        return "只收集回答选中问题所需的公开事实、指标和案例；不得推断用户个人经历。"
    return "按来源可信度分级记录。"


def missing_information(user_input: UserInput) -> List[str]:
    missing = []
    if not user_input.position:
        missing.append("目标岗位")
    if not user_input.target_company and not user_input.industry and not user_input.organization_type:
        missing.append("目标公司/行业/组织类型")
    if not user_input.jd:
        missing.append("JD 或岗位描述")
    if not user_input.resume:
        missing.append("简历或项目经历")
    if not user_input.interview_round:
        missing.append("面试轮次")
    return missing


def build_plan(data: Dict[str, Any], stage: str) -> Dict[str, Any]:
    user_input = UserInput.from_dict(data)
    route_result = detect_route(user_input)
    route = route_result["industry"]
    research, reasons = should_research(user_input, route)
    queries = build_queries(user_input, route, stage) if research else []
    return {
        "should_research": research,
        "stage": stage,
        "route": route_result,
        "is_ai_relevant": is_ai_relevant(user_input),
        "query_budget": {
            "max_total_queries": MAX_TOTAL_QUERIES if stage == "question" else ANSWER_STAGE_MAX_QUERIES,
            "max_retries_per_category": MAX_RETRIES_PER_CATEGORY,
        },
        "research_reasons": reasons,
        "queries": queries,
        "fallback": {
            "if_company_missing": "use_industry_context",
            "if_interview_signal_missing": "use_route_prompt_examples",
            "if_retries_exceeded": "stop_and_mark_missing",
            "if_site_blocked": "do_not_bypass; ask_user_to_provide_link_screenshot_or_text",
        },
        "missing_information": missing_information(user_input),
    }


def load_input(path: str | None) -> Dict[str, Any]:
    if path:
        with open(path, "r", encoding="utf-8") as file:
            return json.load(file)
    return json.load(sys.stdin)


def main() -> int:
    parser = argparse.ArgumentParser(description="生成校招面试题目前研究计划。")
    parser.add_argument("--input", help="用户输入 JSON 文件路径；不传则读取 stdin。")
    parser.add_argument(
        "--stage",
        choices=["question", "answer"],
        default="question",
        help="question 为题目前轻量研究，answer 为答案前深度研究。",
    )
    args = parser.parse_args()
    plan = build_plan(load_input(args.input), args.stage)
    print(json.dumps(plan, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
