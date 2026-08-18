import sys
import unittest
from pathlib import Path


SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

import research_guard


class ResearchGuardTest(unittest.TestCase):
    def test_explicit_industry_beats_generic_jd_keywords(self):
        user_input = research_guard.UserInput.from_dict(
            {
                "industry": "制造业",
                "position": "产品经理",
                "jd": "负责产品、用户、运营、增长相关协作，深入工厂和供应链现场。",
            }
        )
        result = research_guard.detect_route(user_input)
        self.assertEqual(result["industry"], "manufacturing")

    def test_string_false_does_not_disable_research(self):
        user_input = research_guard.UserInput.from_dict(
            {
                "target_company": "示例公司",
                "industry": "互联网",
                "position": "产品经理",
                "no_external_research": "false",
            }
        )
        self.assertFalse(user_input.no_external_research)

    def test_retail_does_not_trigger_ai(self):
        user_input = research_guard.UserInput.from_dict(
            {
                "industry": "retail",
                "position": "marketing trainee",
            }
        )
        self.assertFalse(research_guard.is_ai_relevant(user_input))

    def test_answer_stage_queries_include_selected_question_topic(self):
        plan = research_guard.build_plan(
            {
                "target_company": "示例公司",
                "industry": "互联网",
                "position": "策略产品经理",
                "selected_questions": [
                    "如何判断推荐策略提升点击率后是否伤害长期留存？"
                ],
            },
            stage="answer",
        )
        queries = " ".join(item["query"] for item in plan["queries"])
        self.assertIn("推荐策略", queries)
        self.assertIn("长期留存", queries)


if __name__ == "__main__":
    unittest.main()
