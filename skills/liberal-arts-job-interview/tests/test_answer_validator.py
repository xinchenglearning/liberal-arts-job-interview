import sys
import unittest
from pathlib import Path


SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

import answer_validator


def answer(question_type: str = "behavioral"):
    return {
        "question_id": "q1",
        "question": "请介绍你的项目贡献。",
        "question_type": question_type,
        "spoken_answer": "我的核心贡献是完成问题拆解和数据分析。项目背景是【待补充：真实背景】，我根据用户反馈提出假设，并用实际数据验证。结果部分需要补充真实指标。",
        "answer_outline": ["结论", "背景", "判断", "行动", "验证", "复盘"],
        "evidence": {
            "user_facts": ["负责用户调研和漏斗分析"],
            "public_facts": [],
            "assumptions": [],
            "placeholders": ["真实背景", "真实指标"],
        },
        "followup_answers": [
            {
                "question": "你具体看了哪些数据？",
                "answer_points": ["补充真实漏斗指标和口径"],
            }
        ],
        "risk_notes": ["不得把团队结果表述为个人独立成果"],
    }


class AnswerValidatorTest(unittest.TestCase):
    def test_personal_experience_answer_allows_empty_public_facts(self):
        result = answer_validator.validate(
            {"questions_confirmed": True, "verified_numbers": [], "answers": [answer()]}
        )
        self.assertTrue(result["valid"], result["warnings"])

    def test_unconfirmed_questions_cannot_generate_answers(self):
        result = answer_validator.validate(
            {"questions_confirmed": False, "answers": [answer()]}
        )
        self.assertFalse(result["valid"])
        self.assertTrue(any("尚未确认" in warning for warning in result["warnings"]))

    def test_unverified_specific_number_is_rejected(self):
        item = answer()
        item["spoken_answer"] += " 最终转化率提升了 35%。"
        result = answer_validator.validate(
            {"questions_confirmed": True, "verified_numbers": [], "answers": [item]}
        )
        self.assertFalse(result["valid"])
        self.assertTrue(any("35%" in warning for warning in result["warnings"]))

    def test_ai_answer_requires_action_evaluation_and_fallback(self):
        item = answer("ai_business")
        item["spoken_answer"] = "我会使用大模型提升效率。"
        item["ai_business_chain"] = {
            "business_task": "",
            "ai_role": "",
            "input": "",
            "output": "",
            "evaluation": "",
            "risk_control": "",
            "human_fallback": "",
        }
        result = answer_validator.validate(
            {"questions_confirmed": True, "verified_numbers": [], "answers": [item]}
        )
        self.assertFalse(result["valid"])
        self.assertTrue(any("AI 回答" in warning for warning in result["warnings"]))


if __name__ == "__main__":
    unittest.main()
