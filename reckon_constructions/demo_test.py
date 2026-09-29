import unittest
from inspect import signature

from reckon_constructions.demo import (
    DEMO_ASSEMBLY_NAMES,
    DEMO_CALCULATION_NAMES,
    DEMO_CUSTOMER_NAMES,
    DEMO_ITEM_NAMES,
    DEMO_PROJECT_LOCATIONS,
    DEMO_PROJECT_TYPES,
    DEMO_SUPPLIER_NAMES,
    DEMO_WAREHOUSE_NAMES,
    DEMO_NAMES,
    ITEM_NAMES,
    _expected_seed_counts,
    _get_boq_line_keys,
    _portfolio_project_name,
    _portfolio_progress_quantity,
    clear_demo_data,
    demo_plan,
    seed_demo_data,
)


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

    def test_display_name_catalog_is_complete_and_unique(self):
        self.assertEqual(len(DEMO_CUSTOMER_NAMES), 30)
        self.assertEqual(len(DEMO_SUPPLIER_NAMES), 8)
        self.assertEqual(len(DEMO_WAREHOUSE_NAMES), 6)
        self.assertEqual(len(DEMO_ITEM_NAMES), 7)
        self.assertEqual(len(DEMO_CALCULATION_NAMES), 4)
        self.assertEqual(len(DEMO_ASSEMBLY_NAMES), 4)
        project_names = {_portfolio_project_name(index) for index in range(1, 100)}
        self.assertEqual(len(project_names), 99)
        self.assertEqual(len(DEMO_PROJECT_LOCATIONS), 20)
        self.assertEqual(len(DEMO_PROJECT_TYPES), 5)

    def test_seed_and_clear_are_safe_by_default(self):
        self.assertTrue(signature(seed_demo_data).parameters["dry_run"].default)
        self.assertTrue(signature(clear_demo_data).parameters["dry_run"].default)
        counts = _expected_seed_counts(100)
        self.assertEqual(counts["Project"], 100)
        self.assertEqual(counts["Customer"], 30)
        self.assertEqual(counts["Purchase Order"], 99)
        self.assertGreater(counts["Progress Certificate"], 1)

    def test_portfolio_progress_quantity_does_not_exceed_approved_quantity(self):
        self.assertEqual(_portfolio_progress_quantity(94.8, 100), 94.8)
        self.assertLessEqual(_portfolio_progress_quantity(94.8, 100), 94.8)

    def test_portfolio_reuses_stored_boq_line_keys(self):
        boq = {
            "items": [
                type("Row", (), {"line_key": "OLD-EXCAVATION"})(),
                type("Row", (), {"line_key": "OLD-CONCRETE"})(),
                type("Row", (), {"line_key": "OLD-MASONRY"})(),
                type("Row", (), {"line_key": "OLD-FINISHING"})(),
            ]
        }
        self.assertEqual(
            _get_boq_line_keys(boq),
            {
                "excavation": "OLD-EXCAVATION",
                "concrete": "OLD-CONCRETE",
                "masonry": "OLD-MASONRY",
                "finishing": "OLD-FINISHING",
            },
        )


if __name__ == "__main__":
    unittest.main()
