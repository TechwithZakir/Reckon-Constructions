import frappe
from frappe.model.document import Document

from reckon_constructions.constructions.calculations import calculate_formula


class MeasurementSheet(Document):
    def validate(self):
        self.validate_boq_context()
        self.calculate_rows()

    def validate_boq_context(self):
        if not self.project or not self.boq or not self.boq_line_key:
            frappe.throw("Project, Construction BOQ, and BOQ Line Key are required.")

        boq = frappe.get_doc("Construction BOQ", self.boq)
        boq.check_permission("read")
        if boq.project != self.project:
            frappe.throw("The selected Construction BOQ does not belong to the selected Project.")

        item = next((row for row in boq.get("items") or [] if row.line_key == self.boq_line_key), None)
        if not item:
            frappe.throw(f"BOQ line key {self.boq_line_key} was not found.")

        if item.uom and self.output_uom and item.uom != self.output_uom:
            frappe.throw(f"Output UOM must match the BOQ line UOM ({item.uom}).")

        self.output_uom = self.output_uom or item.uom
        self.boq_item_description = item.description
        self.boq_item_quantity = item.quantity

    def before_submit(self):
        self.status = "Approved"
        self.calculate_rows()
        self.update_boq_quantity()

    def on_cancel(self):
        self.status = "Cancelled"

    def calculate_rows(self):
        total = 0
        for row in self.get("rows") or []:
            result = self.calculate_row(row)
            signed_result = result.result * (-1 if row.sign == "Deduction" else 1)
            row.row_result = signed_result
            row.explanation = result.explanation
            total += signed_result
        self.total_result = total

    def calculate_row(self, row):
        template = frappe.get_doc("Calculation Template", row.calculation_template)
        variables = {
            "length": row.length,
            "width": row.width,
            "height": row.height,
            "count": row.count or 1,
            "factor": row.factor or 1,
        }
        declared = {item.variable for item in template.get("variables") or []}
        return calculate_formula(
            template.formula,
            {key: value for key, value in variables.items() if key in declared},
        )

    def update_boq_quantity(self):
        if not self.boq or not self.boq_line_key:
            return

        boq = frappe.get_doc("Construction BOQ", self.boq)
        if boq.docstatus == 1:
            frappe.throw("Cannot update a submitted BOQ from a Measurement Sheet.")

        updated = False
        for item in boq.get("items") or []:
            if item.line_key == self.boq_line_key:
                item.quantity = self.total_result
                item.measurement_ref = self.name
                updated = True
                break

        if not updated:
            frappe.throw(f"BOQ line key {self.boq_line_key} was not found.")

        boq.save()


@frappe.whitelist()
def get_boq_line_context(boq, line_key=None):
    if not boq:
        frappe.throw("Construction BOQ is required.")

    doc = frappe.get_doc("Construction BOQ", boq)
    doc.check_permission("read")
    lines = [
        {
            "line_key": row.line_key,
            "description": row.description,
            "uom": row.uom,
            "quantity": row.quantity,
            "item_code": row.item_code,
        }
        for row in doc.get("items") or []
    ]
    selected = next((row for row in lines if row["line_key"] == line_key), None)
    return {"project": doc.project, "lines": lines, "selected": selected}


class MeasurementSheetRow(Document):
    pass
