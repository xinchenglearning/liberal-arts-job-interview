import sys
import unittest
from pathlib import Path


SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

import role_router


class RoleRouterTest(unittest.TestCase):
    def test_explicit_position_has_highest_priority(self):
        result = role_router.route_role(
            {
                "position": "采购专员",
                "jd": "负责供应商运营、市场调研和活动策划",
                "resume": "有社群运营经历",
            }
        )
        self.assertEqual(result["primary_role"], "procurement")

    def test_marketing_and_planning_can_form_primary_secondary_route(self):
        result = role_router.route_role(
            {
                "position": "市场营销策划",
                "jd": "负责品牌传播、营销活动策划和效果复盘",
            }
        )
        self.assertEqual(result["primary_role"], "marketing")
        self.assertIn("planning", result["secondary_roles"])
        self.assertLessEqual(len(result["knowledge_bases"]), 2)

    def test_user_research_routes_to_research_knowledge_base(self):
        result = role_router.route_role(
            {
                "position": "用户研究",
                "jd": "负责访谈、问卷、可用性测试和洞察输出",
            }
        )
        self.assertEqual(result["primary_role"], "user_research")
        self.assertEqual(
            result["knowledge_bases"][0],
            "knowledge_base/user_research_methodology.md",
        )

    def test_knowledge_base_is_fallback_not_user_evidence(self):
        result = role_router.build_knowledge_plan(
            route_result={
                "primary_role": "operations",
                "secondary_roles": [],
                "knowledge_bases": ["knowledge_base/operations_methodology.md"],
            },
            user_input={
                "resume": "负责社群运营，提供了完整目标、动作、指标和复盘",
                "jd": "负责用户运营与活动复盘",
            },
        )
        self.assertEqual(result["usage"], "gap_filling_only")
        self.assertNotIn("replace_user_evidence", result["allowed_uses"])
        self.assertIn("must_not_override_user_facts", result["constraints"])

    def test_sales_bd_role_is_supported(self):
        result = role_router.route_role(
            {
                "position": "商务拓展",
                "jd": "负责客户开发、商机管理、方案沟通和合同推进",
            }
        )
        self.assertEqual(result["primary_role"], "sales_bd")

    def test_hr_role_is_supported(self):
        result = role_router.route_role(
            {
                "position": "人力资源管培生",
                "jd": "参与招聘、培训、组织发展和员工关系工作",
            }
        )
        self.assertEqual(result["primary_role"], "human_resources")

    def test_publicity_role_uses_administration_publicity_library(self):
        result = role_router.route_role(
            {
                "position": "宣传岗",
                "industry": "烟草 国企",
                "jd": "负责新闻宣传、企业文化、材料撰写和舆情协同",
            }
        )
        self.assertEqual(result["primary_role"], "administration_publicity")
        self.assertIn(
            "knowledge_base/administration_publicity_methodology.md",
            result["knowledge_bases"],
        )

    def test_customer_success_project_delivery_is_supported(self):
        result = role_router.route_role(
            {
                "position": "客户成功",
                "jd": "负责客户上线、实施交付、使用推进、续约和风险管理",
            }
        )
        self.assertEqual(result["primary_role"], "customer_success_project")

    def test_state_owned_publicity_loads_role_and_industry_overlay(self):
        plan = role_router.build_plan(
            {
                "position": "宣传岗",
                "industry": "烟草",
                "organization_type": "央国企",
                "industry_route": "state_owned",
                "jd": "负责新闻宣传、企业文化和舆情管理",
            }
        )
        self.assertIn(
            "knowledge_base/administration_publicity_methodology.md",
            plan["knowledge_plan"]["role_knowledge_bases"],
        )
        self.assertEqual(
            plan["knowledge_plan"]["industry_overlay"],
            "knowledge_base/industry_state_owned.md",
        )
        self.assertLessEqual(len(plan["knowledge_plan"]["knowledge_bases"]), 3)

    def test_manufacturing_procurement_loads_manufacturing_overlay(self):
        plan = role_router.build_plan(
            {
                "position": "采购专员",
                "industry_route": "manufacturing",
                "jd": "负责生产物料寻源、供应商质量和交付保障",
            }
        )
        self.assertEqual(
            plan["knowledge_plan"]["industry_overlay"],
            "knowledge_base/industry_manufacturing.md",
        )


if __name__ == "__main__":
    unittest.main()
