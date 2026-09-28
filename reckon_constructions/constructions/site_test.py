import unittest

from reckon_constructions.constructions.site import (
    build_material_requirement_preview,
    summarize_progress,
)


class SiteCalculationTest(unittest.TestCase):
    def test_progress_is_scoped_and_percent_is_deterministic(self):
        result = summarize_progress(
            [{"boq_line_key": "CIV-001", "quantity": 25}],
            {"CIV-001": 100},
        )
        self.assertEqual(result[0]["quantity"], 25)
        self.assertEqual(result[0]["percent_complete"], 25)

    def test_material_demand_deducts_previous_requests(self):
        result = build_material_requirement_preview(
            [{"work_package": "Foundations", "planned_qty": 10, "assembly": "CON-M25"}],
            {
                "CON-M25": {
                    "components": [
                        {
                            "component_kind": "Material",
                            "item": "Cement",
                            "uom": "Bag",
                            "quantity_factor": 5,
                            "wastage_percent": 10,
                        }
                    ]
                }
            },
            {("Cement", "Bag"): 20},
        )
        self.assertAlmostEqual(result[0]["required_qty"], 55)
        self.assertAlmostEqual(result[0]["outstanding_qty"], 35)

    def test_progress_cannot_exceed_approved_scope(self):
        with self.assertRaises(ValueError):
            summarize_progress([{"boq_line_key": "CIV-001", "quantity": 101}], {"CIV-001": 100})


if __name__ == "__main__":
    unittest.main()
