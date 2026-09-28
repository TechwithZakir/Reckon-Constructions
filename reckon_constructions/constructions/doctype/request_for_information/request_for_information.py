import frappe
from frappe.model.document import Document


class RequestForInformation(Document):
    def validate(self):
        if self.status in {"Answered", "Closed"} and not self.response:
            frappe.throw("A response is required before answering or closing an RFI.")
        if self.document and self.project:
            document_project = frappe.db.get_value("Engineering Document", self.document, "project")
            if document_project and document_project != self.project:
                frappe.throw("RFI and Engineering Document must belong to the same project.")
