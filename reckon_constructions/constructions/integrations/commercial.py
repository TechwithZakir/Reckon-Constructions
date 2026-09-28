import frappe
from frappe.utils import nowdate

from reckon_constructions.constructions.commercial import build_invoice_proposal_rows


@frappe.whitelist()
def create_sales_invoice_proposal(certificate):
    certificate_doc = frappe.get_doc("Progress Certificate", certificate)
    certificate_doc.check_permission("read")
    if certificate_doc.docstatus != 1 or certificate_doc.status != "Approved":
        frappe.throw("Only approved Progress Certificates can create Sales Invoice proposals.")
    if certificate_doc.generated_sales_invoice:
        return certificate_doc.generated_sales_invoice

    construction_project = frappe.get_doc("Construction Project", certificate_doc.project)
    boq = frappe.get_doc("Construction BOQ", certificate_doc.boq)
    boq_items = {row.line_key: row for row in boq.get("items") or []}

    invoice = frappe.new_doc("Sales Invoice")
    invoice.customer = construction_project.customer
    invoice.company = construction_project.company
    invoice.currency = construction_project.currency
    invoice.posting_date = nowdate()
    set_if_field_exists(invoice, "project", construction_project.project)
    set_if_field_exists(invoice, "construction_project", certificate_doc.project)
    set_if_field_exists(invoice, "progress_certificate", certificate_doc.name)

    certificate_items = [row.as_dict() for row in certificate_doc.get("items") or []]
    for row in build_invoice_proposal_rows(certificate_items, {key: value.as_dict() for key, value in boq_items.items()}):
        invoice_row = invoice.append("items", {})
        if row["item_code"]:
            invoice_row.item_code = row["item_code"]
        invoice_row.description = row["description"]
        invoice_row.qty = row["qty"]
        invoice_row.uom = row["uom"]
        invoice_row.rate = row["rate"]
        set_if_field_exists(invoice_row, "project", construction_project.project)
        set_if_field_exists(invoice_row, "construction_project", certificate_doc.project)
        set_if_field_exists(invoice_row, "progress_certificate", certificate_doc.name)
        set_if_field_exists(invoice_row, "construction_boq_line_key", row["boq_line_key"])

    if not invoice.get("items"):
        frappe.throw("Progress Certificate has no billable quantity.")
    invoice.insert()
    certificate_doc.generated_sales_invoice = invoice.name
    certificate_doc.save(ignore_permissions=True)
    return invoice.name


def set_if_field_exists(doc, fieldname, value):
    if value is not None and doc.meta.has_field(fieldname):
        doc.set(fieldname, value)
