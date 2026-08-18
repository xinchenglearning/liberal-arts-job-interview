#!/usr/bin/env python3
"""根据岗位、JD 和简历选择岗位方法论知识库。

知识库仅用于补足出题框架、指标和追问角度，不能覆盖用户事实。
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from typing import Any, Dict, Iterable, List


ROLE_CONFIG: Dict[str, Dict[str, Any]] = {
    "product": {
        "keywords": [
            "产品经理", "策略产品", "ai产品", "产品运营", "产品策划",
            "需求分析", "产品设计", "产品规划",
        ],
        "knowledge_base": "knowledge_base/product_methodology.md",
    },
    "operations": {
        "keywords": [
            "运营", "用户运营", "内容运营", "活动运营", "社群运营",
            "新媒体运营", "增长运营", "商家运营",
        ],
        "knowledge_base": "knowledge_base/operations_methodology.md",
    },
    "marketing": {
        "keywords": [
            "市场营销", "品牌营销", "品牌传播", "市场推广", "营销",
            "品牌", "公关", "广告投放",
        ],
        "knowledge_base": "knowledge_base/marketing_methodology.md",
    },
    "procurement": {
        "keywords": [
            "采购", "采购专员", "供应商管理", "寻源", "招标",
            "成本谈判", "供应链采购",
        ],
        "knowledge_base": "knowledge_base/procurement_methodology.md",
    },
    "planning": {
        "keywords": [
            "策划", "活动策划", "内容策划", "品牌策划", "营销策划",
            "宣传策划", "文案策划", "企业文化",
        ],
        "knowledge_base": "knowledge_base/planning_methodology.md",
    },
    "user_research": {
        "keywords": [
            "用户研究", "用研", "市场研究", "消费者研究", "调研",
            "用户访谈", "可用性测试", "问卷研究",
        ],
        "knowledge_base": "knowledge_base/user_research_methodology.md",
    },
    "sales_bd": {
        "keywords": [
            "销售", "商务拓展", "商务", "bd", "客户开发", "渠道拓展",
            "大客户", "商机管理", "解决方案销售",
        ],
        "knowledge_base": "knowledge_base/sales_bd_methodology.md",
    },
    "human_resources": {
        "keywords": [
            "人力资源", "人事", "招聘", "培训", "组织发展", "员工关系",
            "hrbp", "人力管培", "薪酬绩效",
        ],
        "knowledge_base": "knowledge_base/human_resources_methodology.md",
    },
    "administration_publicity": {
        "keywords": [
            "宣传岗", "新闻宣传", "企业文化", "材料撰写", "公文",
            "舆情", "党群", "行政", "综合管理", "品牌宣传",
        ],
        "knowledge_base": "knowledge_base/administration_publicity_methodology.md",
    },
    "customer_success_project": {
        "keywords": [
            "客户成功", "项目交付", "实施顾问", "项目管理", "客户实施",
            "续约", "上线交付", "交付经理", "客户服务",
        ],
        "knowledge_base": "knowledge_base/customer_success_project_methodology.md",
    },
}

ROLE_ORDER = [
    "product",
    "operations",
    "marketing",
    "procurement",
    "planning",
    "user_research",
    "sales_bd",
    "human_resources",
    "administration_publicity",
    "customer_success_project",
]

INDUSTRY_OVERLAYS = {
    "internet": "knowledge_base/industry_internet.md",
    "state_owned": "knowledge_base/industry_state_owned.md",
    "public_institution": "knowledge_base/industry_public_institution.md",
    "manufacturing": "knowledge_base/industry_manufacturing.md",
    "fmcg_retail": "knowledge_base/industry_fmcg_retail.md",
    "finance": "knowledge_base/industry_finance.md",
    "consulting_professional": "knowledge_base/industry_consulting_professional.md",
    "education_healthcare": "knowledge_base/industry_education_healthcare.md",
}


def normalize(value: Any) -> str:
    return re.sub(r"\s+", "", str(value or "")).lower()


def count_keywords(text: str, keywords: Iterable[str]) -> int:
    return sum(1 for keyword in keywords if normalize(keyword) in text)


def score_field(text: str, weight: int) -> Dict[str, int]:
    return {
        role: count_keywords(text, config["keywords"]) * weight
        for role, config in ROLE_CONFIG.items()
    }


def merge_scores(*score_maps: Dict[str, int]) -> Dict[str, int]:
    return {
        role: sum(score_map.get(role, 0) for score_map in score_maps)
        for role in ROLE_ORDER
    }


def route_role(data: Dict[str, Any]) -> Dict[str, Any]:
    position = normalize(data.get("position"))
    jd = normalize(data.get("jd"))
    resume = normalize(data.get("resume"))

    position_scores = score_field(position, 10)
    jd_scores = score_field(jd, 3)
    resume_scores = score_field(resume, 1)
    scores = merge_scores(position_scores, jd_scores, resume_scores)

    ranked = sorted(
        ROLE_ORDER,
        key=lambda role: (-scores[role], ROLE_ORDER.index(role)),
    )
    primary = ranked[0] if scores[ranked[0]] > 0 else "general"

    secondary: List[str] = []
    if primary != "general":
        primary_position_score = position_scores[primary]
        for role in ranked[1:]:
            if scores[role] <= 0:
                continue
            explicit_compound_role = position_scores[role] > 0
            material_secondary = scores[role] >= max(3, scores[primary] * 0.35)
            if explicit_compound_role or (
                primary_position_score == 0 and material_secondary
            ):
                secondary.append(role)
            if len(secondary) == 1:
                break

    selected_roles = [role for role in [primary, *secondary] if role != "general"]
    knowledge_bases = [
        ROLE_CONFIG[role]["knowledge_base"] for role in selected_roles[:2]
    ]

    return {
        "primary_role": primary,
        "secondary_roles": secondary,
        "confidence": (
            "high"
            if primary != "general" and position_scores[primary] > 0
            else "medium"
            if primary != "general"
            else "low"
        ),
        "reason": (
            "岗位名称优先，JD 次之，简历只作辅助；最多加载主岗位和一个复合岗位知识库。"
        ),
        "scores": scores,
        "knowledge_bases": knowledge_bases,
    }


def build_knowledge_plan(
    route_result: Dict[str, Any],
    user_input: Dict[str, Any],
) -> Dict[str, Any]:
    has_resume = bool(str(user_input.get("resume", "")).strip())
    has_jd = bool(str(user_input.get("jd", "")).strip())
    industry_route = str(user_input.get("industry_route", "")).strip()
    industry_overlay = INDUSTRY_OVERLAYS.get(industry_route, "")
    role_knowledge_bases = route_result.get("knowledge_bases", [])[:2]
    combined = [*role_knowledge_bases]
    if industry_overlay:
        combined.append(industry_overlay)
    return {
        "usage": "gap_filling_only",
        "role_knowledge_bases": role_knowledge_bases,
        "industry_overlay": industry_overlay,
        "knowledge_bases": combined[:3],
        "input_completeness": (
            "high" if has_resume and has_jd else "medium" if has_resume or has_jd else "low"
        ),
        "allowed_uses": [
            "supplement_competency_framework",
            "supplement_role_metrics",
            "supplement_followup_angles",
            "supplement_answer_structure",
            "adapt_role_framework_to_industry",
        ],
        "constraints": [
            "must_not_override_user_facts",
            "must_not_invent_resume_evidence",
            "must_not_replace_company_research",
            "must_label_knowledge_as_methodology_not_fact",
        ],
    }


def build_plan(data: Dict[str, Any]) -> Dict[str, Any]:
    route_result = route_role(data)
    return {
        "role_route": route_result,
        "knowledge_plan": build_knowledge_plan(route_result, data),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="生成岗位知识库路由计划。")
    parser.add_argument("--input", help="用户输入 JSON 文件；不传则读取 stdin。")
    args = parser.parse_args()
    if args.input:
        with open(args.input, "r", encoding="utf-8") as file:
            data = json.load(file)
    else:
        data = json.load(sys.stdin)
    print(json.dumps(build_plan(data), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
