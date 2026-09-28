import frappe
from frappe.model.document import Document


class MaterialRequirementPreview(Document):
    def validate(self):
        self.calculate_totals()
        for row in self.get("requirements") or []:
            if (row.required_qty or 0) < 0 or (row.already_requested_qty or 0) < 0:
                frappe.throw("Material requirement quantities cannot be negative.")
            if (row.outstanding_qty or 0) > (row.required_qty or 0):
                frappe.throw("Outstanding quantity cannot exceed required quantity.")

    def before_submit(self):
        self.status = "Reviewed"
        self.calculate_totals()

    def on_cancel(self):
        self.status = "Cancelled"

    def calculate_totals(self):
        self.total_outstanding_qty = sum(
            (row.outstanding_qty or 0) for row in self.get("requirements") or []
        )


class MaterialRequirementPreviewItem(Document):
    pass
