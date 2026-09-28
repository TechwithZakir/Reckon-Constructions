import frappe
from frappe.model.document import Document


class ConstructionSettings(Document):
    def validate(self):
        self.validate_precision()
        self.validate_retention()

    def validate_precision(self):
        if self.quantity_precision is not None and self.quantity_precision < 0:
            frappe.throw("Quantity precision cannot be negative.")
        if self.currency_precision is not None and self.currency_precision < 0:
            frappe.throw("Currency precision cannot be negative.")

    def validate_retention(self):
        if self.default_retention_percent is None:
            return
        if self.default_retention_percent < 0 or self.default_retention_percent > 100:
            frappe.throw("Default retention percent must be between 0 and 100.")
