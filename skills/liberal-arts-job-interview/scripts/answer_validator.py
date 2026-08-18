#!/usr/bin/env python3
"""校招面试答案 JSON 校验工具。

校验用户是否已确认题目、答案结构、事实与数字来源、AI 业务链完整性。
本脚本不生成答案，只返回可定位的校验问题，便于局部重写。
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from copy import deepcopy
from typing import Any, Dict, List


REQUIRED_ANSWER_FIELDS = [
    "question_id",
    "question",
    "question_type",
    "spoken_answer",
    "answer_outline",
    "evidence",
    "followup_answers",
    "risk_notes",
]

REQUIRED_EVIDENCE_FIELDS = [
    "user_facts",
    "public_facts",
    "assumptions",
    "placeholders",
]

REQUIRED_AI_FIELDS = [
    "business_task",
    "ai_role",
    "input",
    "output",
    "evaluation",
    "risk_control",
    "human_fallback",
]

VAGUE_EXPRESSIONS = [
    "积极沟通",
    "持续优化",
    "提升效率",
    "赋能业务",
    "加强协作",
]

NUMBER_PATTERN = re.compile(
    r"(?<![\w])(?:\d+(?:\.\d+)?%|[¥￥$]\s*\d+(?:\.\d+)?|"
    r"\d+(?:\.\d+)?\s*(?:万元|亿元|万|亿|元))(?![\w])"
)


def extract_json(text: str) -> Dict[str, Any]:
    stripped = text.strip()
    if stripped.startswith("{"):
        data = json.loads(stripped)
    else:
        match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", stripped, re.S)
        if not match:
            raise ValueError("输入不是合法 JSON，也未找到 Markdown JSON 代码块。")
        data = json.loads(match.group(1))
    if not isinstance(data, dict):
        raise ValueError("顶层 JSON 必须是对象。")
    return data


def is_blank(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, str):
        return not value.strip()
    if isinstance(value, list):
        return not value
    return False


def missing_fields(item: Dict[str, Any], fields: List[str]) -> List[str]:
    return [field for field in fields if field not in item or is_blank(item[field])]


def find_unverified_numbers(text: str, verified_numbers: List[Any]) -> List[str]:
    verified_text = " ".join(str(item) for item in verified_numbers)
    return [
        number
        for number in NUMBER_PATTERN.findall(text)
        if number not in verified_text
    ]


def validate_public_facts(public_facts: Any) -> List[str]:
    warnings: List[str] = []
    if not isinstance(public_facts, list):
        return ["evidence.public_facts 必须是列表。"]
    for index, fact in enumerate(public_facts):
        if not isinstance(fact, dict):
            warnings.append(f"第 {index + 1} 条公开事实必须包含 claim 和 source。")
            continue
        if is_blank(fact.get("claim")) or is_blank(fact.get("source")):
            warnings.append(f"第 {index + 1} 条公开事实缺少 claim 或 source。")
    return warnings


def validate_ai_chain(item: Dict[str, Any]) -> List[str]:
    if item.get("question_type") != "ai_business":
        return []
    chain = item.get("ai_business_chain")
    if not isinstance(chain, dict):
        return ["AI 回答缺少 ai_business_chain。"]
    missing = missing_fields(chain, REQUIRED_AI_FIELDS)
    if missing:
        return ["AI 回答缺少业务动作、输入输出、评估、风险或人工兜底：" + "、".join(missing)]
    return []


def validate_answer_item(
    item: Any,
    verified_numbers: List[Any],
    index: int,
) -> List[str]:
    prefix = f"第 {index + 1} 个答案"
    if not isinstance(item, dict):
        return [f"{prefix}必须是 JSON 对象。"]

    warnings: List[str] = []
    missing = missing_fields(item, REQUIRED_ANSWER_FIELDS)
    if missing:
        warnings.append(f"{prefix}缺少字段：" + "、".join(missing))
        return warnings

    evidence = item.get("evidence")
    if not isinstance(evidence, dict):
        warnings.append(f"{prefix}的 evidence 必须是对象。")
    else:
        evidence_missing = [
            field for field in REQUIRED_EVIDENCE_FIELDS if field not in evidence
        ]
        if evidence_missing:
            warnings.append(f"{prefix}的 evidence 缺少：" + "、".join(evidence_missing))
        for field in REQUIRED_EVIDENCE_FIELDS:
            if field in evidence and not isinstance(evidence[field], list):
                warnings.append(f"{prefix}的 evidence.{field} 必须是列表。")
        warnings.extend(
            f"{prefix}：{warning}"
            for warning in validate_public_facts(evidence.get("public_facts", []))
        )

    spoken_answer = str(item.get("spoken_answer", ""))
    unverified = find_unverified_numbers(spoken_answer, verified_numbers)
    if unverified:
        warnings.append(
            f"{prefix}包含未经用户确认的具体数字：" + "、".join(unverified)
        )

    if any(expression in spoken_answer for expression in VAGUE_EXPRESSIONS):
        if len(spoken_answer) < 80:
            warnings.append(f"{prefix}主要由空泛表达组成，需要补充具体判断、动作或证据。")

    warnings.extend(f"{prefix}：{warning}" for warning in validate_ai_chain(item))
    return warnings


def validate(data: Any) -> Dict[str, Any]:
    warnings: List[str] = []
    if not isinstance(data, dict):
        return {"valid": False, "warnings": ["顶层输入必须是 JSON 对象。"]}

    questions_confirmed = data.get("questions_confirmed") is True
    if not questions_confirmed:
        warnings.append("题目尚未确认，禁止生成或交付答案。")

    answers = data.get("answers", [])
    if not isinstance(answers, list) or not answers:
        warnings.append("answers 必须是非空列表。")
        answers = []

    selected_question_ids = data.get("selected_question_ids", [])
    if selected_question_ids and isinstance(selected_question_ids, list):
        answer_ids = {
            str(item.get("question_id"))
            for item in answers
            if isinstance(item, dict)
        }
        missing_ids = [
            str(question_id)
            for question_id in selected_question_ids
            if str(question_id) not in answer_ids
        ]
        if missing_ids:
            warnings.append("选中题目缺少答案：" + "、".join(missing_ids))

    verified_numbers = data.get("verified_numbers", [])
    if not isinstance(verified_numbers, list):
        verified_numbers = []

    answer_warnings: Dict[str, List[str]] = {}
    for index, item in enumerate(answers):
        item_warnings = validate_answer_item(item, verified_numbers, index)
        if item_warnings:
            question_id = (
                str(item.get("question_id", index + 1))
                if isinstance(item, dict)
                else str(index + 1)
            )
            answer_warnings[question_id] = item_warnings
            warnings.extend(item_warnings)

    result = deepcopy(data)
    result["answers"] = answers
    return {
        "valid": not warnings,
        "answer_count": len(answers),
        "warnings": warnings,
        "answer_warnings": answer_warnings,
        "validated_output": result,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="校验校招面试答案 JSON。")
    parser.add_argument("--input", help="答案 JSON 文件路径；不传则读取 stdin。")
    args = parser.parse_args()
    if args.input:
        with open(args.input, "r", encoding="utf-8") as file:
            data = extract_json(file.read())
    else:
        data = extract_json(sys.stdin.read())
    output = validate(data)
    print(json.dumps(output, ensure_ascii=False, indent=2))
    return 0 if output["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
