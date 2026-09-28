import frappe
from frappe.model.document import Document

from reckon_constructions.constructions.calculations import calculate_formula


class CalculationTemplate(Document):
    def validate(self):
        self.validate_formula()

    def validate_formula(self):
        variables = self.get_declared_variables()
        calculate_formula(self.formula, {variable: 1 for variable in variables})

    def get_declared_variables(self):
        variables = [row.variable for row in self.get("variables") or [] if row.variable]
        if not variables:
            frappe.throw("At least one declared variable is required.")

        duplicates = {variable for variable in variables if variables.count(variable) > 1}
        if duplicates:
            frappe.throw(f"Duplicate variables are not allowed: {', '.join(sorted(duplicates))}.")

        return variables


class CalculationTemplateVariable(Document):
    pass
