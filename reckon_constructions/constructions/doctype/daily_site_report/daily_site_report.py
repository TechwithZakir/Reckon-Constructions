import frappe
from frappe.model.document import Document
from frappe.utils import now_datetime

from reckon_constructions.constructions.site import summarize_progress


class DailySiteReport(Document):
    def validate(self):
        self.validate_project_scope()
        self.calculate_progress()

    def before_submit(self):
        self.calculate_progress()
        self.status = "Verified"
        self.verified_by = frappe.session.user
        self.verified_on = now_datetime()

    def on_cancel(self):
        self.status = "Cancelled"

    def validate_project_scope(self):
        if not self.boq_revision:
            return
        boq_project = frappe.db.get_value("Construction BOQ", self.boq_revision, "project")
        if boq_project and self.project and boq_project != self.project:
            frappe.throw("Daily Site Report and BOQ Revision must belong to the same project.")

    def calculate_progress(self):
        approved_scope = {}
        if self.boq_revision:
            boq = frappe.get_doc("Construction BOQ", self.boq_revision)
            if boq.docstatus != 1:
                frappe.throw("Daily Site Report requires a submitted and approved BOQ revision.")
            approved_scope = {row.line_key: row.quantity or 0 for row in boq.get("items") or []}

        try:
            summary = summarize_progress(
                [row.as_dict() for row in self.get("progress") or []], approved_scope
            )
        except ValueError as error:
            frappe.throw(str(error))

        self.total_verified_quantity = sum(row["quantity"] for row in summary)
        for row in self.get("progress") or []:
            match = next(
                (item for item in summary if item["boq_line_key"] == row.boq_line_key), None
            )
            row.percent_complete = match["percent_complete"] if match else 0


class DailySiteReportProgress(Document):
    pass
