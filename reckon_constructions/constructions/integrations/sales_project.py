import frappe
from frappe.utils import nowdate

from reckon_constructions.constructions.integrations.utils import build_quotation_description


@frappe.whitelist()
def create_quotation_from_boq(boq, replay_key=None):
    boq_doc = frappe.get_doc("Construction BOQ", boq)
    boq_doc.check_permission("read")

    if boq_doc.docstatus != 1:
        frappe.throw("Only submitted and approved BOQs can create Quotations.")
    if not boq_doc.customer:
        frappe.throw("BOQ requires a Customer before creating a Quotation.")

    existing = find_existing_quotation(boq_doc.name, replay_key)
    if existing:
        return existing

    quotation = frappe.new_doc("Quotation")
    quotation.quotation_to = "Customer"
    quotation.party_name = boq_doc.customer
    quotation.company = boq_doc.company
    quotation.currency = boq_doc.currency
    quotation.transaction_date = nowdate()

    set_if_field_exists(quotation, "construction_boq", boq_doc.name)
    set_if_field_exists(quotation, "reckon_construction_boq", boq_doc.name)
    set_if_field_exists(quotation, "replay_key", replay_key)

    for row in boq_doc.get("items") or []:
        quotation_row = quotation.append("items", {})
        quotation_row.item_code = row.item_code
        quotation_row.description = build_quotation_description(row)
        quotation_row.qty = row.quantity or 0
        quotation_row.uom = row.uom
        quotation_row.rate = row.rate or 0
        set_if_field_exists(quotation_row, "construction_boq", boq_doc.name)
        set_if_field_exists(quotation_row, "construction_boq_line_key", row.line_key)
        set_if_field_exists(quotation_row, "reckon_boq_line_key", row.line_key)

    quotation.insert()
    return quotation.name


@frappe.whitelist()
def link_or_create_project_from_sales_order(sales_order, existing_project=None, replay_key=None):
    sales_order_doc = frappe.get_doc("Sales Order", sales_order)
    sales_order_doc.check_permission("read")

    existing_profile = frappe.db.get_value(
        "Construction Project",
        {"sales_order": sales_order_doc.name},
        ["name", "project"],
        as_dict=True,
    )
    if existing_profile:
        return {
            "construction_project": existing_profile.name,
            "project": existing_profile.project,
            "created": False,
        }

    project_name = existing_project or get_project_from_sales_order(sales_order_doc)
    if project_name:
        project = frappe.get_doc("Project", project_name)
    else:
        project = create_project_from_sales_order(sales_order_doc)

    validate_sales_order_project_boundary(sales_order_doc, project)

    construction_project = frappe.new_doc("Construction Project")
    construction_project.project = project.name
    construction_project.company = sales_order_doc.company
    construction_project.customer = sales_order_doc.customer
    construction_project.currency = sales_order_doc.currency
    construction_project.sales_order = sales_order_doc.name
    construction_project.contract_start_date = sales_order_doc.get("transaction_date")
    construction_project.contract_value = sales_order_doc.get("base_grand_total") or sales_order_doc.get("grand_total")
    construction_project.status = "Active"
    set_if_field_exists(construction_project, "replay_key", replay_key)
    construction_project.insert()

    return {
        "construction_project": construction_project.name,
        "project": project.name,
        "created": not bool(existing_project),
    }


def find_existing_quotation(boq, replay_key=None):
    filters = {"docstatus": ["<", 2]}
    if frappe.get_meta("Quotation").has_field("construction_boq"):
        filters["construction_boq"] = boq
    elif frappe.get_meta("Quotation").has_field("reckon_construction_boq"):
        filters["reckon_construction_boq"] = boq
    elif replay_key and frappe.get_meta("Quotation").has_field("replay_key"):
        filters["replay_key"] = replay_key
    else:
        return None

    return frappe.db.get_value("Quotation", filters, "name")


def create_project_from_sales_order(sales_order):
    project = frappe.new_doc("Project")
    project.project_name = sales_order.name
    project.company = sales_order.company
    set_if_field_exists(project, "customer", sales_order.customer)
    set_if_field_exists(project, "sales_order", sales_order.name)
    project.insert()
    return project


def get_project_from_sales_order(sales_order):
    for fieldname in ("project", "project_name"):
        if sales_order.get(fieldname):
            return sales_order.get(fieldname)
    return None


def validate_sales_order_project_boundary(sales_order, project):
    if project.get("company") and sales_order.company and project.company != sales_order.company:
        frappe.throw("Project company must match the Sales Order company.")
    if project.get("customer") and sales_order.customer and project.customer != sales_order.customer:
        frappe.throw("Project customer must match the Sales Order customer.")


def set_if_field_exists(doc, fieldname, value):
    if value is not None and doc.meta.has_field(fieldname):
        doc.set(fieldname, value)
