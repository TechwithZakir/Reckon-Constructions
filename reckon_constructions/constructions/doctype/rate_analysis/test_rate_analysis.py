import unittest

from reckon_constructions.constructions.rates import RateComponentInput, calculate_rate_summary


class TestRateAnalysis(unittest.TestCase):
    def test_calculates_direct_overhead_markup(self):
        summary = calculate_rate_summary(
            [
                RateComponentInput(quantity_factor=2, unit_rate=100, wastage_percent=10),
                RateComponentInput(quantity_factor=1, unit_rate=50),
            ],
            overhead_percent=5,
            markup_percent=10,
        )

        self.assertEqual(summary.direct_cost, 270)
        self.assertEqual(summary.overhead_amount, 13.5)
        self.assertEqual(summary.markup_amount, 28.35)
        self.assertEqual(summary.proposed_rate, 311.85)
