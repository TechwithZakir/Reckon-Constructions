import frappe


def _fields(doctype, names):
    meta = frappe.get_meta(doctype)
    return [name for name in names if name == "name" or meta.has_field(name)]


def _rows(doctype, project=None, fields=None, order_by=None):
    available = _fields(doctype, fields or [])
    if not available:
        return []
    if project and "project" not in available:
        return []
    query_filters = {}
    if project and "project" in available:
        query_filters["project"] = project
    return frappe.get_all(doctype, filters=query_filters, fields=available, order_by=order_by)


def _amount(rows, fieldname):
    return sum(float(row.get(fieldname) or 0) for row in rows)


def execute(filters=None):
    filters = frappe.parse_json(filters) if isinstance(filters, str) else (filters or {})
    project = filters.get("project")
    project_filters = {"name": project} if project else {}
    projects = frappe.get_all(
        "Project",
        filters=project_filters,
        fields=_fields(
            "Project",
            ["name", "project_name", "customer", "status", "percent_complete", "construction_status", "construction_contract_value"],
        ),
        order_by="modified desc",
        limit=100,
    )
    customer_names = {}
    customer_ids = [row.customer for row in projects if row.get("customer")]
    if customer_ids:
        customer_names = {
            row.name: row.customer_name or row.name
            for row in frappe.get_all("Customer", filters={"name": ["in", customer_ids]}, fields=["name", "customer_name"])
        }

    rows = []
    for project_row in projects:
        project_name = project_row.name
        boqs = _rows("Construction BOQ", project_name, ["name", "total_amount", "status", "docstatus"])
        baselines = _rows("Project Baseline", project_name, ["name", "planned_value", "status", "docstatus"])
        variations = _rows("Variation Order", project_name, ["name", "net_amount", "status", "docstatus"])
        certificates = _rows("Progress Certificate", project_name, ["name", "gross_value", "net_value", "status", "docstatus"])
        purchase_orders = _rows("Purchase Order", project_name, ["name", "grand_total", "docstatus"])
        boq_value = _amount([row for row in boqs if row.get("docstatus") == 1], "total_amount")
        planned_value = _amount([row for row in baselines if row.get("docstatus") == 1], "planned_value")
        variation_value = _amount([row for row in variations if row.get("docstatus") == 1], "net_amount")
        certified_value = _amount([row for row in certificates if row.get("docstatus") == 1], "gross_value")
        committed_value = _amount([row for row in purchase_orders if row.get("docstatus", 0) < 2], "grand_total")
        approved_value = boq_value + variation_value
        rows.append(
            {
                "project": project_name,
                "project_name": project_row.get("project_name") or project_name,
                "customer": customer_names.get(project_row.get("customer"), project_row.get("customer") or ""),
                "status": project_row.get("construction_status") or project_row.get("status") or "Open",
                "progress": round(float(project_row.get("percent_complete") or 0), 2),
                "contract_value": float(project_row.get("construction_contract_value") or 0),
                "approved_value": approved_value,
                "planned_value": planned_value,
                "variation_value": variation_value,
                "certified_value": certified_value,
                "committed_value": committed_value,
                "remaining_value": approved_value - certified_value,
                "variance_value": approved_value - planned_value,
            }
        )

    rows.sort(key=lambda row: row["approved_value"], reverse=True)
    columns = [
        {"label": "Project", "fieldname": "project", "fieldtype": "Link", "options": "Project", "width": 170},
        {"label": "Project Name", "fieldname": "project_name", "fieldtype": "Data", "width": 220},
        {"label": "Customer", "fieldname": "customer", "fieldtype": "Data", "width": 180},
        {"label": "Progress %", "fieldname": "progress", "fieldtype": "Percent", "width": 100},
        {"label": "Approved Value", "fieldname": "approved_value", "fieldtype": "Currency", "width": 140},
        {"label": "Planned Value", "fieldname": "planned_value", "fieldtype": "Currency", "width": 140},
        {"label": "Certified Value", "fieldname": "certified_value", "fieldtype": "Currency", "width": 140},
        {"label": "Committed Procurement", "fieldname": "committed_value", "fieldtype": "Currency", "width": 160},
        {"label": "Remaining Value", "fieldname": "remaining_value", "fieldtype": "Currency", "width": 140},
        {"label": "Approved vs Planned", "fieldname": "variance_value", "fieldtype": "Currency", "width": 150},
        {"label": "Status", "fieldname": "status", "fieldtype": "Data", "width": 120},
    ]
    chart_rows = rows[:15]
    chart = {
        "data": {
            "labels": [row["project_name"] for row in chart_rows],
            "datasets": [
                {"name": "Approved", "values": [row["approved_value"] for row in chart_rows]},
                {"name": "Certified", "values": [row["certified_value"] for row in chart_rows]},
                {"name": "Committed", "values": [row["committed_value"] for row in chart_rows]},
            ],
        },
        "type": "bar",
        "height": 340,
    }
    return columns, rows, None, chart, [
        {"label": "Projects", "value": len(rows), "indicator": "blue"},
        {"label": "Approved Value", "value": sum(row["approved_value"] for row in rows), "datatype": "Currency", "indicator": "green"},
        {"label": "Certified Value", "value": sum(row["certified_value"] for row in rows), "datatype": "Currency", "indicator": "orange"},
        {"label": "Remaining Value", "value": sum(row["remaining_value"] for row in rows), "datatype": "Currency", "indicator": "red"},
    ]
