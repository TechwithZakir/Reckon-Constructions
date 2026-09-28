import unittest

from reckon_constructions.constructions.calculations import calculate_formula


class TestMeasurementSheet(unittest.TestCase):
    def test_calculates_declared_variables(self):
        result = calculate_formula(
            "length * width * count * factor",
            {"length": 10, "width": 3, "count": 2, "factor": 1},
        )

        self.assertEqual(result.result, 60)

    def test_rejects_undeclared_variables(self):
        with self.assertRaises(Exception):
            calculate_formula("length + unsafe", {"length": 10})
