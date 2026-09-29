import frappe


def _available(doctype, fields):
    meta = frappe.get_meta(doctype)
    return [field for field in fields if field == "name" or meta.has_field(field)]


def execute(filters=None):
    filters = frappe.parse_json(filters) if isinstance(filters, str) else (filters or {})
    project = filters.get("project")
    po_fields = _available("Purchase Order", ["name", "project", "supplier", "supplier_name", "transaction_date", "schedule_date", "status", "grand_total", "docstatus"])
    mr_fields = _available("Material Request", ["name", "project", "transaction_date", "schedule_date", "status"])
    if "project" not in po_fields:
        return [], [], None, None, [{"label": "Purchase Orders", "value": 0, "indicator": "orange"}]

    po_filters = {"project": project} if project else {}
    purchase_orders = frappe.get_all("Purchase Order", filters=po_filters, fields=po_fields, order_by="transaction_date desc")
    material_requests = (
        frappe.get_all("Material Request", filters={"project": project} if project else {}, fields=mr_fields)
        if "project" in mr_fields
        else []
    )
    grouped = {}
    for order in purchase_orders:
        if order.get("docstatus", 0) >= 2:
            continue
        key = order.project
        row = grouped.setdefault(
            key,
            {
                "project": key,
                "project_name": frappe.db.get_value("Project", key, "project_name") or key,
                "supplier": order.get("supplier_name") or order.get("supplier") or "Multiple suppliers",
                "purchase_orders": 0,
                "committed_value": 0,
                "material_requests": 0,
                "latest_order_date": order.get("transaction_date"),
                "status": order.get("status") or "Draft",
            },
        )
        row["purchase_orders"] += 1
        row["committed_value"] += float(order.get("grand_total") or 0)
        row["latest_order_date"] = max(str(row["latest_order_date"] or ""), str(order.get("transaction_date") or ""))
        row["status"] = order.get("status") or row["status"]
    for request in material_requests:
        if request.get("project") in grouped:
            grouped[request.project]["material_requests"] += 1
        else:
            grouped[request.project] = {
                "project": request.project,
                "project_name": frappe.db.get_value("Project", request.project, "project_name") or request.project,
                "supplier": "",
                "purchase_orders": 0,
                "committed_value": 0,
                "material_requests": 1,
                "latest_order_date": None,
                "status": "Material Request Only",
            }
    rows = sorted(grouped.values(), key=lambda row: row["committed_value"], reverse=True)
    columns = [
        {"label": "Project", "fieldname": "project", "fieldtype": "Link", "options": "Project", "width": 170},
        {"label": "Project Name", "fieldname": "project_name", "fieldtype": "Data", "width": 220},
        {"label": "Supplier", "fieldname": "supplier", "fieldtype": "Data", "width": 190},
        {"label": "Material Requests", "fieldname": "material_requests", "fieldtype": "Int", "width": 130},
        {"label": "Purchase Orders", "fieldname": "purchase_orders", "fieldtype": "Int", "width": 120},
        {"label": "Committed Value", "fieldname": "committed_value", "fieldtype": "Currency", "width": 140},
        {"label": "Latest Order", "fieldname": "latest_order_date", "fieldtype": "Date", "width": 110},
        {"label": "Status", "fieldname": "status", "fieldtype": "Data", "width": 130},
    ]
    chart_rows = rows[:15]
    chart = {
        "data": {"labels": [row["project_name"] for row in chart_rows], "datasets": [{"name": "Committed value", "values": [row["committed_value"] for row in chart_rows]}]},
        "type": "bar",
        "height": 320,
    }
    return columns, rows, None, chart, [
        {"label": "Projects", "value": len(rows), "indicator": "blue"},
        {"label": "Purchase Orders", "value": sum(row["purchase_orders"] for row in rows), "indicator": "green"},
        {"label": "Material Requests", "value": sum(row["material_requests"] for row in rows), "indicator": "orange"},
        {"label": "Committed Value", "value": sum(row["committed_value"] for row in rows), "datatype": "Currency", "indicator": "red"},
    ]
