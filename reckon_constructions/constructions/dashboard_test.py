import unittest
from datetime import date, datetime

from reckon_constructions.constructions.dashboard import _date_sort_key, calculate_dashboard_metrics


class DashboardCalculationTest(unittest.TestCase):
    def test_dashboard_date_sort_key_normalizes_frappe_date_values(self):
        values = [date(2026, 1, 2), "2026-01-03", datetime(2026, 1, 1, 12, 30)]

        self.assertEqual(
            sorted(values, key=_date_sort_key),
            [datetime(2026, 1, 1, 12, 30), date(2026, 1, 2), "2026-01-03"],
        )

    def test_dashboard_calculates_progress_and_margin(self):
        result = calculate_dashboard_metrics(
            contract_value=1000,
            boq_value=900,
            variation_value=100,
            certified_value=250,
            committed_cost=400,
            actual_cost=200,
        )
        self.assertEqual(result["approved_value"], 1000)
        self.assertEqual(result["completion_percent"], 25)
        self.assertEqual(result["forecast_margin"], 400)


if __name__ == "__main__":
    unittest.main()
