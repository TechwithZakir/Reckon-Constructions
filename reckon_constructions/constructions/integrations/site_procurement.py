import frappe
from frappe.utils import nowdate

from reckon_constructions.constructions.site import build_material_requirement_preview


@frappe.whitelist()
def create_material_requirement_preview(baseline, replay_key=None):
    baseline_doc = frappe.get_doc("Project Baseline", baseline)
    baseline_doc.check_permission("read")
    if baseline_doc.docstatus != 1:
        frappe.throw("Only submitted and approved baselines can create material previews.")

    existing = find_existing_preview(baseline_doc.name, replay_key)
    if existing:
        return existing

    assemblies = {}
    work_packages = []
    for row in baseline_doc.get("work_packages") or []:
        work_packages.append(row.as_dict())
        if row.assembly and row.assembly not in assemblies:
            assembly = frappe.get_doc("Construction Assembly", row.assembly)
            assemblies[row.assembly] = assembly.as_dict()

    already_requested = collect_existing_material_demand(baseline_doc.name)
    requirements = build_material_requirement_preview(work_packages, assemblies, already_requested)
    construction_project = frappe.get_doc("Construction Project", baseline_doc.project)
    preview = frappe.new_doc("Material Requirement Preview")
    preview.project = baseline_doc.project
    preview.baseline = baseline_doc.name
    preview.company = construction_project.company
    preview.as_of_date = nowdate()
    preview.source_replay_key = replay_key
    for requirement in requirements:
        source = (requirement.get("sources") or [{}])[0]
        preview.append(
            "requirements",
            {
                "item": requirement["item"],
                "uom": requirement["uom"],
                "required_qty": requirement["required_qty"],
                "already_requested_qty": requirement["already_requested_qty"],
                "outstanding_qty": requirement["outstanding_qty"],
                "source_work_package": source.get("work_package"),
                "source_boq_line_key": source.get("boq_line_key"),
                "source_assembly": source.get("assembly"),
            },
        )
    preview.insert()
    return preview.name


@frappe.whitelist()
def create_material_request_from_preview(preview, replay_key=None):
    preview_doc = frappe.get_doc("Material Requirement Preview", preview)
    preview_doc.check_permission("read")
    if preview_doc.docstatus != 1 or preview_doc.status != "Reviewed":
        frappe.throw("Only reviewed material previews can create a Material Request.")
    if preview_doc.generated_material_request:
        return preview_doc.generated_material_request

    request = frappe.new_doc("Material Request")
    request.material_request_type = "Purchase"
    request.transaction_date = nowdate()
    set_if_field_exists(request, "company", preview_doc.company)
    construction_project = frappe.get_doc("Construction Project", preview_doc.project)
    set_if_field_exists(request, "project", construction_project.project)
    set_if_field_exists(request, "construction_project", preview_doc.project)
    set_if_field_exists(request, "construction_baseline", preview_doc.baseline)
    set_if_field_exists(request, "material_requirement_preview", preview_doc.name)
    set_if_field_exists(request, "replay_key", replay_key)

    for row in preview_doc.get("requirements") or []:
        if not row.outstanding_qty:
            continue
        item = request.append("items", {})
        item.item_code = row.item
        item.qty = row.outstanding_qty
        item.uom = row.uom
        item.schedule_date = preview_doc.as_of_date
        set_if_field_exists(item, "project", construction_project.project)
        set_if_field_exists(item, "construction_baseline", preview_doc.baseline)
        set_if_field_exists(item, "construction_boq_line_key", row.source_boq_line_key)

    if not request.get("items"):
        frappe.throw("Material preview has no outstanding demand.")
    request.insert()
    preview_doc.generated_material_request = request.name
    preview_doc.status = "Generated"
    preview_doc.save(ignore_permissions=True)
    return request.name


def find_existing_preview(baseline, replay_key=None):
    filters = {"baseline": baseline, "docstatus": ["<", 2]}
    if replay_key:
        filters["source_replay_key"] = replay_key
    return frappe.db.get_value("Material Requirement Preview", filters, "name")


def collect_existing_material_demand(baseline):
    meta = frappe.get_meta("Material Request")
    if not meta.has_field("construction_baseline"):
        return {}

    demand = {}
    names = frappe.get_all(
        "Material Request",
        filters={"construction_baseline": baseline, "docstatus": ["<", 2]},
        pluck="name",
    )
    for name in names:
        request = frappe.get_doc("Material Request", name)
        for row in request.get("items") or []:
            key = (row.item_code, row.uom or "")
            demand[key] = demand.get(key, 0) + (row.qty or 0)
    return demand


def set_if_field_exists(doc, fieldname, value):
    if value is not None and doc.meta.has_field(fieldname):
        doc.set(fieldname, value)
