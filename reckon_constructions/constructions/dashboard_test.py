import unittest

from reckon_constructions.constructions.dashboard import calculate_dashboard_metrics


class DashboardCalculationTest(unittest.TestCase):
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
