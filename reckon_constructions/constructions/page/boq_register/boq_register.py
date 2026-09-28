try:
    import frappe
except ImportError:
    frappe = None


def _whitelist(function):
    return frappe.whitelist()(function) if frappe else function


@_whitelist
def get_boq_register(search=None, status=None, page=1, page_length=20):
    if frappe is None:
        raise RuntimeError("Frappe is required for the BOQ register.")

    if not frappe.has_permission("Construction BOQ", "read"):
        frappe.throw("You do not have permission to view Construction BOQs.", frappe.PermissionError)

    page = max(int(page or 1), 1)
    page_length = min(max(int(page_length or 20), 1), 100)
    filters = []
    or_filters = []
    search = (search or "").strip()
    status = (status or "").strip()

    if status:
        filters.append(["status", "=", status])
    if search:
        like = f"%{search}%"
        or_filters = [
            ["name", "like", like],
            ["project", "like", like],
            ["customer", "like", like],
            ["company", "like", like],
        ]

    total = len(
        frappe.get_list(
            "Construction BOQ",
            filters=filters,
            or_filters=or_filters,
            fields=["name"],
            limit_page_length=0,
            order_by=None,
        )
    )
    rows = frappe.get_list(
        "Construction BOQ",
        filters=filters,
        or_filters=or_filters,
        fields=[
            "name",
            "project",
            "customer",
            "company",
            "currency",
            "boq_type",
            "revision_no",
            "status",
            "total_amount",
            "modified",
        ],
        order_by="modified desc",
        limit_start=(page - 1) * page_length,
        limit_page_length=page_length,
    )

    return {
        "rows": rows,
        "total": total,
        "page": page,
        "page_length": page_length,
    }


@_whitelist
def delete_boq(name):
    if frappe is None:
        raise RuntimeError("Frappe is required for the BOQ register.")

    doc = frappe.get_doc("Construction BOQ", name)
    doc.check_permission("delete")
    if doc.docstatus != 0 or doc.status in {"Approved", "Superseded"}:
        frappe.throw("Only draft BOQs can be deleted.")
    frappe.delete_doc("Construction BOQ", name)
    return {"name": name}
