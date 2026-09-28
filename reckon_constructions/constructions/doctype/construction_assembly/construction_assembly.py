import frappe
from frappe.model.document import Document

from reckon_constructions.constructions.rates import calculate_rate_summary


class ConstructionAssembly(Document):
    def validate(self):
        self.validate_components()
        self.calculate_totals()

    def validate_components(self):
        for component in self.get("components") or []:
            if component.quantity_factor is not None and component.quantity_factor < 0:
                frappe.throw("Assembly component quantity factor cannot be negative.")
            if component.wastage_percent is not None and component.wastage_percent < 0:
                frappe.throw("Assembly component wastage cannot be negative.")

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
        self.proposed_rate = summary.proposed_rate
