import frappe
from frappe.model.document import Document
from frappe.utils import now_datetime

from reckon_constructions.constructions.commercial import calculate_variation_totals


class VariationOrder(Document):
    def validate(self):
        self.validate_scope()
        self.calculate_totals()

    def before_submit(self):
        self.calculate_totals()
        self.status = "Approved"
        self.approved_by = frappe.session.user
        self.approved_on = now_datetime()

    def on_cancel(self):
        self.status = "Cancelled"

    def validate_scope(self):
        if not self.boq:
            frappe.throw("Variation Order requires an approved BOQ revision.")
        boq = frappe.get_doc("Construction BOQ", self.boq)
        if boq.docstatus != 1:
            frappe.throw("Variation Order requires a submitted and approved BOQ revision.")
        if self.project:
            boq_project = boq.project
            if boq_project != self.project:
                frappe.throw("Variation Order and BOQ Revision must belong to the same project.")

    def calculate_totals(self):
        if self.variation_no is not None and self.variation_no < 1:
            frappe.throw("Variation No must be 1 or greater.")
        approved_scope = {}
        if self.boq:
            boq = frappe.get_doc("Construction BOQ", self.boq)
            approved_scope = {row.line_key: row.quantity or 0 for row in boq.get("items") or []}
        try:
            summary = calculate_variation_totals(
                [row.as_dict() for row in self.get("items") or []], approved_scope
            )
        except ValueError as error:
            frappe.throw(str(error))

        self.net_amount = summary["net_amount"]
        for row in self.get("items") or []:
            calculated = next(
                item for item in summary["items"] if item["boq_line_key"] == row.boq_line_key
            )
            row.amount = calculated["amount"]
        self.prospective_baseline_effect = self.net_amount


class VariationOrderItem(Document):
    pass
