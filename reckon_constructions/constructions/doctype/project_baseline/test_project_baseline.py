import unittest

from reckon_constructions.constructions.planning import has_dependency_cycle, validate_date_range


class TestProjectBaseline(unittest.TestCase):
    def test_detects_dependency_cycle(self):
        self.assertTrue(has_dependency_cycle([("A", "B"), ("B", "C"), ("C", "A")]))

    def test_allows_acyclic_dependencies(self):
        self.assertFalse(has_dependency_cycle([("A", "B"), ("B", "C")]))

    def test_rejects_invalid_date_range(self):
        with self.assertRaises(ValueError):
            validate_date_range("2026-02-02", "2026-02-01")
