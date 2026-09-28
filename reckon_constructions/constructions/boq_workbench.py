try:
    import frappe
except ImportError:
    frappe = None


def _whitelist(function):
    return frappe.whitelist()(function) if frappe else function


@_whitelist
def get_boq_workbench_context(boq=None):
    if frappe is None:
        raise RuntimeError("Frappe is required for the BOQ workbench.")

    context = {
        "projects": frappe.get_all(
            "Project",
            fields=["name", "project_name", "customer", "company", "construction_currency", "construction_status"],
            order_by="modified desc",
            limit=100,
        ),
        "items": frappe.get_all(
            "Item",
            filters={"disabled": 0},
            fields=["name", "item_name", "stock_uom"],
            order_by="modified desc",
            limit=250,
        ),
        "templates": frappe.get_all(
            "Calculation Template",
            fields=["name", "template_name", "measurement_type", "output_uom", "formula", "description"],
            order_by="template_name asc",
            limit=100,
        ),
        "uoms": frappe.get_all("UOM", fields=["name"], order_by="name asc", limit=100),
    }

    if boq:
        doc = frappe.get_doc("Construction BOQ", boq)
        doc.check_permission("read")
        context["boq"] = serialize_boq(doc)

    return context


@_whitelist
def save_boq_draft(payload):
    if frappe is None:
        raise RuntimeError("Frappe is required for the BOQ workbench.")

    payload = frappe.parse_json(payload) if isinstance(payload, str) else payload
    if not isinstance(payload, dict):
        frappe.throw("BOQ data must be an object.")

    project_name = payload.get("project")
    if not project_name:
        frappe.throw("Select a Project before saving the BOQ.")

    project = frappe.get_doc("Project", project_name)
    project.check_permission("read")

    boq_name = payload.get("name")
    if boq_name:
        doc = frappe.get_doc("Construction BOQ", boq_name)
        doc.check_permission("write")
        if doc.docstatus == 1 or doc.status == "Approved":
            frappe.throw("Approved BOQs are immutable. Create a new revision instead.")
    else:
        doc = frappe.new_doc("Construction BOQ")
        doc.check_permission("create")

    doc.project = project_name
    doc.customer = payload.get("customer") or project.customer
    doc.company = payload.get("company") or project.company
    doc.currency = payload.get("currency") or project.get("construction_currency")
    doc.boq_type = payload.get("boq_type") or "Construction"
    doc.revision_no = int(payload.get("revision_no") or 1)
    doc.revision_reason = payload.get("revision_reason") or None
    doc.status = "Draft"
    doc.set("sections", [])
    doc.set("items", [])

    sections = payload.get("sections") or []
    items = payload.get("items") or []
    section_names = set()
    for index, section in enumerate(sections, start=1):
        section_name = (section.get("section_name") or "").strip()
        if not section_name:
            frappe.throw(f"Section {index} needs a name.")
        if section_name in section_names:
            frappe.throw(f"Section {section_name} is repeated. Use one section per name.")
        section_names.add(section_name)
        doc.append(
            "sections",
            {
                "section_code": section.get("section_code") or f"{index:02d}",
                "section_name": section_name,
                "description": section.get("description"),
            },
        )

    for index, item in enumerate(items, start=1):
        description = (item.get("description") or "").strip()
        section_name = (item.get("section") or "").strip()
        if not section_name:
            frappe.throw(f"Line {index} needs a section.")
        if not description and not item.get("item_code"):
            frappe.throw(f"Line {index} needs an item or description.")
        doc.append(
            "items",
            {
                "line_key": item.get("line_key") or f"{doc.name or 'BOQ'}-{index:04d}",
                "section": section_name,
                "item_code": item.get("item_code") or None,
                "description": description,
                "quantity": float(item.get("quantity") or 0),
                "uom": item.get("uom") or None,
                "rate": float(item.get("rate") or 0),
                "measurement_ref": item.get("measurement_ref") or None,
            },
        )

    if not doc.items:
        frappe.throw("Add at least one BOQ line before saving.")

    if doc.is_new():
        doc.insert()
    else:
        doc.save()

    return {
        "name": doc.name,
        "project": doc.project,
        "status": doc.status,
        "revision_no": doc.revision_no,
        "total_amount": doc.total_amount,
        "items": serialize_boq(doc)["items"],
    }


def serialize_boq(doc):
    return {
        "name": doc.name,
        "project": doc.project,
        "customer": doc.customer,
        "company": doc.company,
        "currency": doc.currency,
        "boq_type": doc.boq_type,
        "revision_no": doc.revision_no,
        "revision_reason": doc.revision_reason,
        "status": doc.status,
        "sections": [
            {
                "section_code": row.section_code,
                "section_name": row.section_name,
                "description": row.description,
            }
            for row in doc.sections
        ],
        "items": [
            {
                "line_key": row.line_key,
                "section": row.section,
                "item_code": row.item_code,
                "description": row.description,
                "quantity": row.quantity,
                "uom": row.uom,
                "rate": row.rate,
                "amount": row.amount,
                "measurement_ref": row.measurement_ref,
            }
            for row in doc.items
        ],
    }
