import frappe
from frappe.model.document import Document


class EngineeringDocument(Document):
    def validate(self):
        if self.supersedes and self.supersedes == self.name:
            frappe.throw("Engineering Document cannot supersede itself.")
        if self.revision is not None and self.revision < 0:
            frappe.throw("Revision must be zero or greater.")
