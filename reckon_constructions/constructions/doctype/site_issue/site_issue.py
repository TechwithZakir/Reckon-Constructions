import frappe
from frappe.model.document import Document


class SiteIssue(Document):
    def validate(self):
        if self.site_report:
            report_project = frappe.db.get_value("Daily Site Report", self.site_report, "project")
            if report_project and self.project and report_project != self.project:
                frappe.throw("Site Issue and Daily Site Report must belong to the same project.")
        if self.status in {"Resolved", "Closed"} and not self.resolution:
            frappe.throw("A resolution is required before closing a Site Issue.")
