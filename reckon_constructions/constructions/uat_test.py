import unittest

from reckon_constructions.constructions.commercial import (
    build_invoice_proposal_rows,
    calculate_certificate_totals,
    calculate_variation_totals,
)
from reckon_constructions.constructions.dashboard import calculate_dashboard_metrics
from reckon_constructions.constructions.reports import validate_boq_import_rows
from reckon_constructions.constructions.site import (
    build_material_requirement_preview,
    summarize_progress,
)


class DocumentedUATFlowTest(unittest.TestCase):
    """Offline execution of the documented BOQ-to-invoice flow without a Frappe site."""

    def test_boq_to_progress_certificate_and_invoice_flow(self):
        boq = validate_boq_import_rows(
            [{"line_key": "CIV-001", "description": "Concrete", "quantity": 10, "rate": 250, "uom": "m3"}]
        )
        self.assertTrue(boq["valid"])
        self.assertEqual(boq["rows"][0]["quantity"], 10)

        progress = summarize_progress([{"boq_line_key": "CIV-001", "quantity": 4}], {"CIV-001": 10})
        self.assertEqual(progress[0]["percent_complete"], 40)

        material = build_material_requirement_preview(
            [{"work_package": "Concrete", "planned_qty": 10, "assembly": "CON-M25"}],
            {"CON-M25": {"components": [{"component_kind": "Material", "item": "Cement", "uom": "Bag", "quantity_factor": 5}]}},
            {},
        )
        self.assertEqual(material[0]["outstanding_qty"], 50)

        variation = calculate_variation_totals(
            [{"boq_line_key": "CIV-001", "quantity_delta": 2, "rate": 250}], {"CIV-001": 10}
        )
        certificate = calculate_certificate_totals(
            [{"boq_line_key": "CIV-001", "this_period_qty": 4, "rate": 250}], 5
        )
        invoice_rows = build_invoice_proposal_rows(
            [{"boq_line_key": "CIV-001", "description": "Concrete", "this_period_qty": 4, "uom": "m3", "rate": 250}],
            {"CIV-001": {"item_code": "CONCRETE-M25"}},
        )
        dashboard = calculate_dashboard_metrics(
            contract_value=3000,
            boq_value=2500,
            variation_value=variation["net_amount"],
            certified_value=certificate["gross_value"],
        )
        self.assertEqual(invoice_rows[0]["item_code"], "CONCRETE-M25")
        self.assertEqual(dashboard["approved_value"], 3000)


if __name__ == "__main__":
    unittest.main()
