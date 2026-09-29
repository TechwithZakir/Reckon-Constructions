import unittest
from inspect import signature

from reckon_constructions.demo import DEMO_NAMES, ITEM_NAMES, _expected_seed_counts, clear_demo_data, demo_plan, seed_demo_data


class DemoDataPlanTest(unittest.TestCase):
    def test_plan_covers_the_construction_flow(self):
        plan = demo_plan()
        self.assertEqual(plan["portfolio_project_count"], 100)
        self.assertEqual(plan["portfolio_customer_count"], 30)
        self.assertEqual(plan["portfolio_supplier_count"], 8)
        self.assertEqual(plan["portfolio_warehouse_count"], 6)
        self.assertIn("Construction BOQ", plan["custom_doctypes"])
        self.assertIn("Progress Certificate", plan["custom_doctypes"])
        self.assertIn("Sales Invoice", plan["erpnext_doctypes"])
        self.assertIn("Material Request", plan["erpnext_doctypes"])
        self.assertIn("Purchase Order", plan["erpnext_doctypes"])
        self.assertIn("Supplier", plan["erpnext_doctypes"])
        self.assertIn("Warehouse", plan["erpnext_doctypes"])

    def test_demo_names_are_deterministic_and_namespaced(self):
        self.assertTrue(all(name.startswith("RC") for name in DEMO_NAMES.values()))
        self.assertTrue(all(name.startswith("RC") for name in ITEM_NAMES.values()))
        self.assertEqual(DEMO_NAMES["project"], DEMO_NAMES["construction_project"])

    def test_seed_and_clear_are_safe_by_default(self):
        self.assertTrue(signature(seed_demo_data).parameters["dry_run"].default)
        self.assertTrue(signature(clear_demo_data).parameters["dry_run"].default)
        counts = _expected_seed_counts(100)
        self.assertEqual(counts["Project"], 100)
        self.assertEqual(counts["Customer"], 30)
        self.assertEqual(counts["Purchase Order"], 99)
        self.assertGreater(counts["Progress Certificate"], 1)


if __name__ == "__main__":
    unittest.main()
