import frappe
from frappe.model.document import Document


class ConstructionProject(Document):
    def validate(self):
        self.validate_unique_erpnext_project()
        self.validate_project_values()
        self.validate_sales_order_values()

    def validate_unique_erpnext_project(self):
        if not self.project:
            return

        existing = frappe.db.get_value(
            "Construction Project",
            {"project": self.project, "name": ["!=", self.name]},
            "name",
        )
        if existing:
            frappe.throw(
                f"ERPNext Project {self.project} is already linked to Construction Project {existing}."
            )

    def validate_project_values(self):
        if not self.project:
            return

        project_values = frappe.db.get_value(
            "Project",
            self.project,
            ["company", "customer"],
            as_dict=True,
        )
        if not project_values:
            frappe.throw(f"ERPNext Project {self.project} was not found.")

        self.validate_same_value("Company", self.company, project_values.get("company"))
        self.validate_same_value("Customer", self.customer, project_values.get("customer"))

    def validate_sales_order_values(self):
        if not self.sales_order:
            return

        sales_order_values = frappe.db.get_value(
            "Sales Order",
            self.sales_order,
            ["company", "customer", "currency"],
            as_dict=True,
        )
        if not sales_order_values:
            frappe.throw(f"Sales Order {self.sales_order} was not found.")

        self.validate_same_value("Company", self.company, sales_order_values.get("company"))
        self.validate_same_value("Customer", self.customer, sales_order_values.get("customer"))
        self.validate_same_value("Currency", self.currency, sales_order_values.get("currency"))

    def validate_same_value(self, label, local_value, source_value):
        if local_value and source_value and local_value != source_value:
            frappe.throw(f"{label} must match the linked ERPNext document.")


def validate_linked_project_boundaries(doc, method=None):
    construction_project = frappe.db.get_value(
        "Construction Project",
        {"project": doc.name},
        ["name", "company", "customer"],
        as_dict=True,
    )
    if not construction_project:
        return

    if construction_project.company and doc.get("company") and construction_project.company != doc.company:
        frappe.throw(
            f"Project company cannot differ from linked Construction Project {construction_project.name}."
        )
    if construction_project.customer and doc.get("customer") and construction_project.customer != doc.customer:
        frappe.throw(
            f"Project customer cannot differ from linked Construction Project {construction_project.name}."
        )
