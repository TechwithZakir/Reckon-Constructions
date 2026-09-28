import unittest
from types import SimpleNamespace

from reckon_constructions.constructions.integrations.utils import build_quotation_description


class TestSalesProjectIntegration(unittest.TestCase):
    def test_description_includes_stable_line_key(self):
        row = SimpleNamespace(line_key="BOQ-0001", description="Excavation in soil", item_code="EXC")

        self.assertEqual(
            build_quotation_description(row),
            "BOQ Line: BOQ-0001\nExcavation in soil",
        )

    def test_description_falls_back_to_item_code(self):
        row = SimpleNamespace(line_key=None, description=None, item_code="EXC")

        self.assertEqual(build_quotation_description(row), "EXC")
