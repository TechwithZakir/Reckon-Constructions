import unittest

from reckon_constructions.constructions.reports import validate_boq_import_rows


class ReportImportTest(unittest.TestCase):
    def test_import_reports_row_level_errors(self):
        result = validate_boq_import_rows(
            [
                {"line_key": "CIV-001", "quantity": 10, "rate": 50},
                {"line_key": "CIV-001", "quantity": -1, "rate": "bad"},
            ]
        )
        self.assertFalse(result["valid"])
        self.assertEqual({error["field"] for error in result["errors"]}, {"line_key", "quantity", "rate"})

    def test_valid_import_normalizes_numeric_values(self):
        result = validate_boq_import_rows([{"line_key": "CIV-001", "quantity": "10", "rate": "50"}])
        self.assertTrue(result["valid"])
        self.assertEqual(result["rows"][0]["quantity"], 10)


if __name__ == "__main__":
    unittest.main()
