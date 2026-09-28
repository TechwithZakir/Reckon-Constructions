import frappe
from frappe.model.document import Document

from reckon_constructions.constructions.rates import calculate_rate_summary


class RateAnalysis(Document):
    def validate(self):
        self.validate_boq_line()
        self.calculate_totals()

    def before_submit(self):
        self.status = "Approved"
        self.calculate_totals()
        self.update_boq_rate()

    def on_cancel(self):
        self.status = "Cancelled"

    def validate_boq_line(self):
        if not self.boq or not self.boq_line_key:
            return

        boq = frappe.get_doc("Construction BOQ", self.boq)
        if not any(row.line_key == self.boq_line_key for row in boq.get("items") or []):
            frappe.throw(f"BOQ line key {self.boq_line_key} was not found.")

    def calculate_totals(self):
        for component in self.get("components") or []:
            component.amount = (
                (component.quantity_factor or 0)
                * (component.unit_rate or 0)
                * (1 + (component.wastage_percent or 0) / 100)
            )

        summary = calculate_rate_summary(
            self.get("components") or [],
            self.overhead_percent,
            self.markup_percent,
        )
        self.direct_cost = summary.direct_cost
        self.overhead_amount = summary.overhead_amount
        self.markup_amount = summary.markup_amount
        self.proposed_rate = summary.proposed_rate

    def update_boq_rate(self):
        if not self.boq or not self.boq_line_key:
            return

        boq = frappe.get_doc("Construction BOQ", self.boq)
        if boq.docstatus == 1:
            frappe.throw("Cannot update a submitted BOQ from Rate Analysis.")

        updated = False
        for item in boq.get("items") or []:
            if item.line_key == self.boq_line_key:
                item.rate = self.proposed_rate
                item.assembly_ref = self.assembly
                updated = True
                break

        if not updated:
            frappe.throw(f"BOQ line key {self.boq_line_key} was not found.")

        boq.save()
