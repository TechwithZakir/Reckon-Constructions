import frappe

from reckon_constructions.constructions.dashboard import _build_dashboard_payload


def execute(filters=None):
    filters = frappe.parse_json(filters) if isinstance(filters, str) else (filters or {})
    project = filters.get("project")
    payload = _build_dashboard_payload(project)
    rows = payload["site_report_progress"]
    columns = [
        {"label": "Report", "fieldname": "name", "fieldtype": "Link", "options": "Daily Site Report", "width": 170},
        {"label": "Report Date", "fieldname": "report_date", "fieldtype": "Date", "width": 110},
        {"label": "Project", "fieldname": "project", "fieldtype": "Link", "options": "Project", "width": 170},
        {"label": "Project Name", "fieldname": "project_name", "fieldtype": "Data", "width": 230},
        {"label": "Progress %", "fieldname": "progress", "fieldtype": "Percent", "width": 100},
        {"label": "Verified Quantity", "fieldname": "verified_quantity", "fieldtype": "Float", "width": 130},
        {"label": "Status", "fieldname": "status", "fieldtype": "Data", "width": 110},
    ]
    chart_rows = list(reversed(rows[:30]))
    chart = {
        "data": {
            "labels": [row["report_date"] for row in chart_rows],
            "datasets": [{"name": "Site progress %", "values": [row["progress"] for row in chart_rows]}],
        },
        "type": "line",
        "height": 300,
    }
    report_summary = [
        {"label": "Site Visits", "value": payload["counts"]["site_visits"], "indicator": "blue"},
        {"label": "Reports", "value": payload["counts"]["site_reports"], "indicator": "green"},
        {"label": "Average Report Progress", "value": round(sum(row["progress"] for row in rows) / len(rows), 2) if rows else 0, "datatype": "Percent", "indicator": "orange"},
    ]
    return columns, rows, None, chart, report_summary
