import sys
import unittest
from pathlib import Path


SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

import question_validator as validator


def question(dimension: str, text: str, priority: str = "高频"):
    return {
        "dimension": dimension,
        "question": text,
        "interviewer_intent": f"验证{dimension}",
        "why_this_question": "用于校招岗位判断",
        "high_score_points": ["结论清楚", "有真实证据"],
        "followups": ["请补充一个具体细节。"],
        "material_connection": "关联用户提供的岗位、JD 或项目。",
        "industry_context": "关联目标行业业务。",
        "priority": priority,
    }


def reverse(index: int):
    return {
        "question": f"结合当前业务阶段，这个岗位第 {index} 个优先目标是什么？",
        "why_ask": "理解岗位真实目标",
        "shows_ability": ["业务理解"],
        "best_for_round": "业务面",
        "risk": "需确认公开信息",
        "safer_alternative": "这个岗位当前最重要的目标是什么？",
    }


class QuestionValidatorTest(unittest.TestCase):
    def test_missing_required_dimension_makes_output_invalid(self):
        dimensions = ["自我介绍", "简历/项目深挖", "岗位匹配", "业务理解", "问题分析"]
        questions = [
            question(dimensions[index % len(dimensions)], f"问题 {index}：请结合具体经历说明。")
            for index in range(18)
        ]
        result = validator.validate(
            {
                "route_result": {"enhancers": []},
                "question_map": questions,
                "reverse_questions": [reverse(1), reverse(2), reverse(3)],
            }
        )
        self.assertFalse(result["valid"])
        self.assertIn("metrics", result["missing_required_dimensions"])

    def test_fewer_than_three_reverse_questions_is_invalid(self):
        dimensions = ["自我介绍", "简历/项目深挖", "岗位匹配", "业务理解", "问题分析", "指标与结果"]
        questions = [
            question(dimensions[index % len(dimensions)], f"问题 {index}：请结合具体经历说明。")
            for index in range(18)
        ]
        result = validator.validate(
            {
                "route_result": {"enhancers": []},
                "question_map": questions,
                "reverse_questions": [reverse(1), reverse(2)],
            }
        )
        self.assertFalse(result["valid"])
        self.assertTrue(any("至少 3 个" in warning for warning in result["warnings"]))

    def test_invalid_list_items_return_errors_instead_of_crashing(self):
        result = validator.validate(
            {
                "route_result": {"enhancers": []},
                "question_map": ["问题", None, 3],
                "reverse_questions": ["反问"],
            },
            mode="insufficient",
        )
        self.assertFalse(result["valid"])
        self.assertGreaterEqual(len(result["removed_questions"]), 3)


if __name__ == "__main__":
    unittest.main()
