import unittest

from reckon_constructions.constructions.commercial import (
    calculate_certificate_totals,
    calculate_variation_totals,
)


class CommercialCalculationTest(unittest.TestCase):
    def test_variation_keeps_negative_omission_value(self):
        result = calculate_variation_totals(
            [{"boq_line_key": "CIV-001", "quantity_delta": -10, "rate": 50}],
            {"CIV-001": 100},
        )
        self.assertEqual(result["net_amount"], -500)

    def test_variation_cannot_reduce_scope_below_zero(self):
        with self.assertRaises(ValueError):
            calculate_variation_totals(
                [{"boq_line_key": "CIV-001", "quantity_delta": -11, "rate": 50}],
                {"CIV-001": 10},
            )

    def test_variation_rejects_duplicate_line_keys(self):
        with self.assertRaises(ValueError):
            calculate_variation_totals(
                [
                    {"boq_line_key": "CIV-001", "quantity_delta": 1, "rate": 50},
                    {"boq_line_key": "CIV-001", "quantity_delta": 2, "rate": 50},
                ]
            )

    def test_certificate_applies_retention_to_gross_value(self):
        result = calculate_certificate_totals(
            [{"this_period_qty": 10, "rate": 250}], retention_percent=5
        )
        self.assertEqual(result["gross_value"], 2500)
        self.assertEqual(result["retention_amount"], 125)
        self.assertEqual(result["net_value"], 2375)


if __name__ == "__main__":
    unittest.main()
