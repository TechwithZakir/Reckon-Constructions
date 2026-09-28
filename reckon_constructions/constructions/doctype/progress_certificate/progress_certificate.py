import frappe
from frappe.model.document import Document
from frappe.utils import now_datetime

from reckon_constructions.constructions.commercial import calculate_certificate_totals
from reckon_constructions.constructions.planning import validate_date_range


class ProgressCertificate(Document):
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
            frappe.throw("Progress Certificate requires an approved BOQ revision.")
        if self.certificate_no is not None and self.certificate_no < 1:
            frappe.throw("Certificate No must be 1 or greater.")
        try:
            validate_date_range(self.period_start, self.period_end)
        except ValueError as error:
            frappe.throw(str(error))

        boq = frappe.get_doc("Construction BOQ", self.boq)
        if boq.docstatus != 1:
            frappe.throw("Progress Certificate requires a submitted and approved BOQ revision.")
        if self.project and boq.project != self.project:
            frappe.throw("Progress Certificate and BOQ Revision must belong to the same project.")

    def calculate_totals(self):
        try:
            boq = frappe.get_doc("Construction BOQ", self.boq)
            approved_scope = {row.line_key: row.quantity or 0 for row in boq.get("items") or []}
            lines = []
            for row in self.get("items") or []:
                current_qty = float(row.current_qty or 0)
                previous_qty = float(row.previous_certified_qty or 0)
                if row.boq_line_key not in approved_scope:
                    raise ValueError(f"Certificate line {row.boq_line_key} is outside the approved BOQ scope.")
                if current_qty < 0 or previous_qty < 0:
                    raise ValueError("Certified quantities cannot be negative.")
                if current_qty < previous_qty:
                    raise ValueError(
                        f"Current quantity for {row.boq_line_key} cannot be below previously certified quantity."
                    )
                if current_qty > float(approved_scope[row.boq_line_key] or 0):
                    raise ValueError(
                        f"Current quantity for {row.boq_line_key} cannot exceed approved BOQ quantity."
                    )
                row.this_period_qty = current_qty - previous_qty
                lines.append(row.as_dict())
            summary = calculate_certificate_totals(lines, self.retention_percent)
        except ValueError as error:
            frappe.throw(str(error))

        self.gross_value = summary["gross_value"]
        self.retention_amount = summary["retention_amount"]
        self.net_value = summary["net_value"]
        for row in self.get("items") or []:
            row.amount = (row.this_period_qty or 0) * (row.rate or 0)


class ProgressCertificateItem(Document):
    pass
