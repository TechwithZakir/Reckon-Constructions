import frappe

from reckon_constructions.constructions.dashboard import _build_dashboard_payload


def execute(filters=None):
    filters = frappe.parse_json(filters) if isinstance(filters, str) else (filters or {})
    project = filters.get("project")
    payload = _build_dashboard_payload(project)
    rows = payload["project_progress"]
    columns = [
        {"label": "Project", "fieldname": "name", "fieldtype": "Link", "options": "Project", "width": 170},
        {"label": "Project Name", "fieldname": "project_name", "fieldtype": "Data", "width": 240},
        {"label": "Customer", "fieldname": "customer", "fieldtype": "Data", "width": 200},
        {"label": "Progress %", "fieldname": "progress", "fieldtype": "Percent", "width": 110},
        {"label": "Construction Status", "fieldname": "construction_status", "fieldtype": "Data", "width": 140},
        {"label": "Contract Value", "fieldname": "contract_value", "fieldtype": "Currency", "width": 140},
        {"label": "Expected Start", "fieldname": "expected_start_date", "fieldtype": "Date", "width": 110},
        {"label": "Expected End", "fieldname": "expected_end_date", "fieldtype": "Date", "width": 110},
    ]
    chart = {
        "data": {
            "labels": [row["project_name"] for row in rows[:20]],
            "datasets": [{"name": "Progress %", "values": [row["progress"] for row in rows[:20]]}],
        },
        "type": "bar",
        "height": 320,
    }
    report_summary = [
        {"label": "Projects", "value": payload["counts"]["projects"], "indicator": "blue"},
        {"label": "Average Progress", "value": round(sum(row["progress"] for row in rows) / len(rows), 2) if rows else 0, "datatype": "Percent", "indicator": "green"},
        {"label": "Open Issues", "value": payload["counts"]["open_issues"], "indicator": "orange"},
    ]
    return columns, rows, None, chart, report_summary
