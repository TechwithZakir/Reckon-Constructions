import unittest

from reckon_constructions.demo import DEMO_NAMES, ITEM_NAMES, demo_plan


class DemoDataPlanTest(unittest.TestCase):
    def test_plan_covers_the_construction_flow(self):
        plan = demo_plan()
        self.assertEqual(plan["portfolio_project_count"], 100)
        self.assertIn("Construction BOQ", plan["custom_doctypes"])
        self.assertIn("Progress Certificate", plan["custom_doctypes"])
        self.assertIn("Sales Invoice", plan["erpnext_doctypes"])
        self.assertIn("Material Request", plan["erpnext_doctypes"])

    def test_demo_names_are_deterministic_and_namespaced(self):
        self.assertTrue(all(name.startswith("RC") for name in DEMO_NAMES.values()))
        self.assertTrue(all(name.startswith("RC") for name in ITEM_NAMES.values()))
        self.assertEqual(DEMO_NAMES["project"], DEMO_NAMES["construction_project"])


if __name__ == "__main__":
    unittest.main()
