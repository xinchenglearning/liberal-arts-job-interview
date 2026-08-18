#!/usr/bin/env python3
"""校招面试题 JSON 校验与压缩工具。

输入题目生成 JSON，输出校验结果、删除题目原因、覆盖度和压缩后的结果。
本脚本不调用模型，只做结构和规则约束。
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from copy import deepcopy
from typing import Any, Dict, List, Tuple


MAX_TOTAL_QUESTIONS = 28
DEFAULT_MIN_QUESTIONS = 18
DEFAULT_MAX_QUESTIONS = 24
INSUFFICIENT_INFO_MIN_QUESTIONS = 12
INSUFFICIENT_INFO_MAX_QUESTIONS = 16
SPRINT_MIN_QUESTIONS = 10
SPRINT_MAX_QUESTIONS = 12
MAX_REVERSE_QUESTIONS = 5
MIN_REVERSE_QUESTIONS = 3
ALLOWED_PRIORITIES = {"必答", "高频", "补充"}

QUESTION_COUNT_RULES = {
    "default": (DEFAULT_MIN_QUESTIONS, DEFAULT_MAX_QUESTIONS),
    "insufficient": (INSUFFICIENT_INFO_MIN_QUESTIONS, INSUFFICIENT_INFO_MAX_QUESTIONS),
    "sprint": (SPRINT_MIN_QUESTIONS, SPRINT_MAX_QUESTIONS),
}

REQUIRED_QUESTION_FIELDS = [
    "dimension",
    "question",
    "interviewer_intent",
    "why_this_question",
    "high_score_points",
    "followups",
    "material_connection",
    "priority",
]

REQUIRED_REVERSE_FIELDS = [
    "question",
    "why_ask",
    "shows_ability",
    "best_for_round",
    "risk",
    "safer_alternative",
]

DIMENSION_KEYWORDS = {
    "self_intro": ["自我介绍", "个人定位", "经历主线"],
    "resume_deep_dive": ["简历", "项目", "经历深挖", "项目深挖"],
    "job_fit": ["岗位", "JD", "胜任", "匹配"],
    "business_understanding": ["业务", "行业", "公司", "竞品"],
    "problem_solving": ["问题分析", "结构化", "场景", "拆解"],
    "metrics": ["指标", "结果", "验证", "归因"],
    "ai_if_relevant": ["AI", "ai", "人工智能", "大模型", "智能化", "算法", "Agent"],
}

DIMENSION_ALIASES = {
    "self_intro": {"自我介绍", "个人定位"},
    "resume_deep_dive": {"简历/项目深挖", "简历深挖", "项目深挖"},
    "job_fit": {"岗位匹配", "岗位胜任力"},
    "business_understanding": {"业务理解", "行业与公司研究"},
    "problem_solving": {"问题分析", "场景分析"},
    "metrics": {"指标与结果", "指标体系"},
    "ai_if_relevant": {"AI 业务认知", "AI能力面", "AI 能力面"},
}

REQUIRED_COVERAGE_KEYS = [
    "self_intro",
    "resume_deep_dive",
    "job_fit",
    "business_understanding",
    "problem_solving",
    "metrics",
    "reverse_questions",
]

GENERIC_PATTERNS = [
    r"你有什么优点",
    r"你的缺点是什么",
    r"你怎么看AI[？?]?$",
    r"你怎么看人工智能[？?]?$",
    r"你怎么看我们公司[？?]?$",
    r"你觉得自己适合吗",
    r"你怎么看这个行业[？?]?$",
    r"你为什么选择我们公司[？?]?$",
]

AI_GENERIC_PATTERNS = [
    r"怎么看.*chatgpt",
    r"ai.*替代.*产品经理",
    r"用过哪些.*ai.*工具",
]

PRIORITY_RANK = {"必答": 0, "高频": 1, "补充": 2}

STRATEGY_ROLE_KEYWORDS = [
    "策略产品",
    "产品经理",
    "产品运营",
    "用户运营",
    "增长",
    "商业分析",
    "数据分析",
    "经营分析",
    "策略分析",
    "AI 产品",
    "ai 产品",
]

METHODOLOGY_BUCKETS = {
    "business_goal_problem": ["业务目标", "目标", "问题", "瓶颈", "根因", "为什么做"],
    "metrics_definition": ["指标", "口径", "过程指标", "核心指标", "护栏指标", "北极星"],
    "strategy_lever": ["策略", "抓手", "人群", "分层", "规则", "优先级", "排序", "触达"],
    "validation_attribution": ["验证", "归因", "AB", "实验", "对照", "前后对比", "分层分析"],
    "risk_review": ["风险", "副作用", "复盘", "回滚", "长期", "投诉", "留存下降"],
    "ai_business_action": ["AI", "ai", "大模型", "智能化", "输入", "输出", "人工兜底", "模型"],
}


def extract_json(text: str) -> Dict[str, Any]:
    """从纯 JSON 或 Markdown 代码块中提取 JSON。"""
    stripped = text.strip()
    if stripped.startswith("{"):
        data = json.loads(stripped)
        if not isinstance(data, dict):
            raise ValueError("顶层 JSON 必须是对象。")
        return data
    match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", stripped, re.S)
    if match:
        data = json.loads(match.group(1))
        if not isinstance(data, dict):
            raise ValueError("顶层 JSON 必须是对象。")
        return data
    raise ValueError("输入不是合法 JSON，也未找到 Markdown JSON 代码块。")


def load_input(path: str | None) -> Dict[str, Any]:
    if path:
        with open(path, "r", encoding="utf-8") as file:
            return extract_json(file.read())
    return extract_json(sys.stdin.read())


def is_blank(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, str):
        return not value.strip()
    if isinstance(value, list):
        return len(value) == 0
    return False


def missing_required_fields(item: Dict[str, Any], required: List[str]) -> List[str]:
    return [field for field in required if field not in item or is_blank(item[field])]


def is_generic_question(question: str) -> bool:
    normalized = question.strip().lower()
    return any(re.search(pattern, normalized, re.I) for pattern in GENERIC_PATTERNS + AI_GENERIC_PATTERNS)


def has_followups(item: Dict[str, Any]) -> bool:
    followups = item.get("followups")
    return isinstance(followups, list) and len([x for x in followups if str(x).strip()]) > 0


def has_context_connection(item: Dict[str, Any]) -> bool:
    return bool(str(item.get("material_connection", "")).strip()) or bool(
        str(item.get("industry_context", "")).strip()
    )


def question_signature(item: Dict[str, Any]) -> str:
    text = f"{item.get('dimension', '')} {item.get('interviewer_intent', '')} {item.get('question', '')}"
    tokens = re.findall(r"[\u4e00-\u9fffA-Za-z0-9]+", text.lower())
    meaningful = [token for token in tokens if len(token) > 1]
    return "|".join(sorted(set(meaningful))[:8])


def validate_and_filter_questions(questions: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], List[Dict[str, str]]]:
    kept: List[Dict[str, Any]] = []
    removed: List[Dict[str, str]] = []
    seen_signatures = set()

    for item in questions:
        if not isinstance(item, dict):
            removed.append({"question": str(item), "reason": "题目条目必须是 JSON 对象"})
            continue
        question = str(item.get("question", "")).strip()
        missing = missing_required_fields(item, REQUIRED_QUESTION_FIELDS)
        if missing:
            removed.append({"question": question, "reason": f"缺少必填字段：{', '.join(missing)}"})
            continue
        if is_generic_question(question):
            removed.append({"question": question, "reason": "泛题或泛 AI 题，缺少校招/岗位/行业指向"})
            continue
        if not has_followups(item):
            removed.append({"question": question, "reason": "缺少可追问方向"})
            continue
        if not has_context_connection(item):
            removed.append({"question": question, "reason": "缺少用户材料或行业语境关联"})
            continue
        if str(item.get("priority", "")) not in ALLOWED_PRIORITIES:
            removed.append({"question": question, "reason": "priority 必须是：必答、高频或补充"})
            continue
        signature = question_signature(item)
        if signature in seen_signatures:
            removed.append({"question": question, "reason": "与已有题目考察点重复"})
            continue
        seen_signatures.add(signature)
        kept.append(item)

    return kept, removed


def compress_questions(questions: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], List[Dict[str, str]]]:
    if len(questions) <= MAX_TOTAL_QUESTIONS:
        return questions, []

    sorted_questions = sorted(
        questions,
        key=lambda item: (
            PRIORITY_RANK.get(str(item.get("priority", "")), 3),
            str(item.get("dimension", "")),
        ),
    )
    kept = sorted_questions[:MAX_TOTAL_QUESTIONS]
    removed = [
        {
            "question": str(item.get("question", "")),
            "reason": "超过题量上限，优先删除低优先级或重复价值较低的问题",
        }
        for item in sorted_questions[MAX_TOTAL_QUESTIONS:]
    ]
    return kept, removed


def validate_reverse_questions(reverse_questions: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], List[Dict[str, str]]]:
    kept: List[Dict[str, Any]] = []
    removed: List[Dict[str, str]] = []
    seen = set()

    for item in reverse_questions:
        if not isinstance(item, dict):
            removed.append({"question": str(item), "reason": "反问条目必须是 JSON 对象"})
            continue
        question = str(item.get("question", "")).strip()
        missing = missing_required_fields(item, REQUIRED_REVERSE_FIELDS)
        if missing:
            removed.append({"question": question, "reason": f"反问缺少必填字段：{', '.join(missing)}"})
            continue
        if is_generic_question(question):
            removed.append({"question": question, "reason": "反问过泛，缺少公司/业务/岗位指向"})
            continue
        signature = question_signature({"dimension": "反问", "question": question, "interviewer_intent": item.get("why_ask", "")})
        if signature in seen:
            removed.append({"question": question, "reason": "反问重复"})
            continue
        seen.add(signature)
        kept.append(item)

    if len(kept) > MAX_REVERSE_QUESTIONS:
        overflow = kept[MAX_REVERSE_QUESTIONS:]
        kept = kept[:MAX_REVERSE_QUESTIONS]
        removed.extend(
            {
                "question": str(item.get("question", "")),
                "reason": "反问超过 5 个上限",
            }
            for item in overflow
        )
    return kept, removed


def contains_any(text: str, keywords: List[str]) -> bool:
    return any(keyword.lower() in text.lower() for keyword in keywords)


def should_require_strategy_methodology(data: Dict[str, Any], force: bool = False) -> bool:
    if force:
        return True
    text = json.dumps(data, ensure_ascii=False)
    return contains_any(text, STRATEGY_ROLE_KEYWORDS)


def build_methodology_check(questions: List[Dict[str, Any]]) -> Dict[str, Any]:
    all_text = json.dumps(questions, ensure_ascii=False)
    buckets = {
        bucket: contains_any(all_text, keywords)
        for bucket, keywords in METHODOLOGY_BUCKETS.items()
    }
    covered = [bucket for bucket, ok in buckets.items() if ok]
    return {
        "covered_buckets": covered,
        "covered_count": len(covered),
        "required_minimum": 3,
        "details": buckets,
    }


def build_coverage_check(
    data: Dict[str, Any],
    questions: List[Dict[str, Any]],
    reverse_questions: List[Dict[str, Any]],
    raw_questions: List[Any],
) -> Dict[str, Any]:
    dimensions = {
        str(item.get("dimension", "")).strip()
        for item in questions
        if isinstance(item, dict)
    }
    coverage = {
        key: bool(dimensions & aliases)
        for key, aliases in DIMENSION_ALIASES.items()
    }
    ai_relevant = bool(data.get("route_result", {}).get("enhancers")) and any(
        "ai" in str(enhancer).lower() or "AI" in str(enhancer)
        for enhancer in data.get("route_result", {}).get("enhancers", [])
    )
    if not ai_relevant:
        coverage["ai_if_relevant"] = True
    coverage["reverse_questions"] = len(reverse_questions) > 0

    generic_count = sum(
        1
        for item in raw_questions
        if isinstance(item, dict)
        and is_generic_question(str(item.get("question", "")))
    )
    ratio = generic_count / max(len(raw_questions), 1)
    coverage["generic_question_ratio"] = "low" if ratio <= 0.1 else "medium" if ratio <= 0.25 else "high"
    return coverage


def build_top_5(questions: List[Dict[str, Any]], reverse_questions: List[Dict[str, Any]]) -> List[str]:
    priority_questions = [
        item
        for item in questions
        if str(item.get("priority", "")) == "必答"
    ]
    if len(priority_questions) < 5:
        priority_questions.extend(
            item for item in questions if item not in priority_questions and str(item.get("priority", "")) == "高频"
        )
    top = [str(item.get("question", "")).strip() for item in priority_questions[:4]]
    if reverse_questions:
        top.append(str(reverse_questions[0].get("question", "")).strip())
    return [item for item in top if item][:5]


def validate(data: Dict[str, Any], mode: str = "default", require_strategy_methodology: bool = False) -> Dict[str, Any]:
    if not isinstance(data, dict):
        return {
            "valid": False,
            "mode": mode,
            "warnings": ["顶层输入必须是 JSON 对象。"],
            "removed_questions": [],
            "removed_reverse_questions": [],
            "missing_required_dimensions": REQUIRED_COVERAGE_KEYS,
        }
    result = deepcopy(data)
    questions = result.get("question_map", [])
    reverse_questions = result.get("reverse_questions", [])
    if not isinstance(questions, list):
        questions = []
    if not isinstance(reverse_questions, list):
        reverse_questions = []
    raw_questions = list(questions)

    kept_questions, removed_questions = validate_and_filter_questions(questions)
    kept_questions, compressed_removed = compress_questions(kept_questions)
    removed_questions.extend(compressed_removed)

    kept_reverse, removed_reverse = validate_reverse_questions(reverse_questions)

    result["question_map"] = kept_questions
    result["reverse_questions"] = kept_reverse
    result["coverage_check"] = build_coverage_check(
        result, kept_questions, kept_reverse, raw_questions
    )
    strategy_required = should_require_strategy_methodology(result, require_strategy_methodology)
    result["strategy_methodology_check"] = build_methodology_check(kept_questions)
    result["strategy_methodology_check"]["required"] = strategy_required
    result["top_5_priority_questions"] = build_top_5(kept_questions, kept_reverse)

    warnings: List[str] = []
    min_questions, max_questions = QUESTION_COUNT_RULES[mode]
    if len(kept_questions) < min_questions:
        warnings.append(f"{mode} 模式要求至少 {min_questions} 道主问题，当前为 {len(kept_questions)} 道。")
    if len(kept_questions) > max_questions:
        warnings.append(f"{mode} 模式要求最多 {max_questions} 道主问题，当前为 {len(kept_questions)} 道。")
    if len(kept_questions) > MAX_TOTAL_QUESTIONS:
        warnings.append("主问题数量超过 28 道上限。")
    if len(kept_reverse) < MIN_REVERSE_QUESTIONS:
        warnings.append(f"反问至少 {MIN_REVERSE_QUESTIONS} 个，当前为 {len(kept_reverse)} 个。")
    if result["coverage_check"].get("generic_question_ratio") != "low":
        warnings.append("泛题比例偏高。")
    if strategy_required and result["strategy_methodology_check"]["covered_count"] < 3:
        warnings.append("策略/产品相关场景要求至少覆盖 3 类方法论要素。")
    missing_required_dimensions = [
        key
        for key in REQUIRED_COVERAGE_KEYS
        if not result["coverage_check"].get(key, False)
    ]
    if result["coverage_check"].get("ai_if_relevant") is False:
        missing_required_dimensions.append("ai_if_relevant")
    if missing_required_dimensions:
        warnings.append(
            "缺少必需题目维度：" + "、".join(missing_required_dimensions)
        )

    return {
        "valid": not warnings,
        "mode": mode,
        "expected_question_range": {
            "min": min_questions,
            "max": max_questions,
        },
        "final_question_count": len(kept_questions),
        "reverse_question_count": len(kept_reverse),
        "removed_questions": removed_questions,
        "removed_reverse_questions": removed_reverse,
        "warnings": warnings,
        "missing_required_dimensions": missing_required_dimensions,
        "coverage_check": result["coverage_check"],
        "strategy_methodology_check": result["strategy_methodology_check"],
        "validated_output": result,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="校验并压缩校招面试题 JSON。")
    parser.add_argument("--input", help="题目 JSON 文件路径；不传则读取 stdin。")
    parser.add_argument(
        "--mode",
        choices=sorted(QUESTION_COUNT_RULES),
        default="default",
        help="题量模式：default=18-24，insufficient=12-16，sprint=10-12。",
    )
    parser.add_argument(
        "--require-strategy-methodology",
        action="store_true",
        help=argparse.SUPPRESS,
    )
    parser.add_argument(
        "--require-role-methodology",
        action="store_true",
        help="强制要求题目覆盖岗位方法论至少 3 类要素。",
    )
    args = parser.parse_args()
    data = load_input(args.input)
    output = validate(
        data,
        args.mode,
        args.require_strategy_methodology or args.require_role_methodology,
    )
    print(json.dumps(output, ensure_ascii=False, indent=2))
    return 0 if output["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
