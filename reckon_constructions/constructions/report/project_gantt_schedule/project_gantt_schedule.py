import frappe

from reckon_constructions.constructions.dashboard import _build_dashboard_payload


def execute(filters=None):
    filters = frappe.parse_json(filters) if isinstance(filters, str) else (filters or {})
    project = filters.get("project")
    payload = _build_dashboard_payload(project)
    rows = payload["gantt"]
    columns = [
        {"label": "Task", "fieldname": "name", "fieldtype": "Link", "options": "Task", "width": 170},
        {"label": "Work Activity", "fieldname": "subject", "fieldtype": "Data", "width": 240},
        {"label": "Project", "fieldname": "project", "fieldtype": "Link", "options": "Project", "width": 170},
        {"label": "Project Name", "fieldname": "project_name", "fieldtype": "Data", "width": 220},
        {"label": "Start", "fieldname": "start_date", "fieldtype": "Date", "width": 110},
        {"label": "End", "fieldname": "end_date", "fieldtype": "Date", "width": 110},
        {"label": "Progress %", "fieldname": "progress", "fieldtype": "Percent", "width": 100},
        {"label": "Status", "fieldname": "status", "fieldtype": "Data", "width": 110},
    ]
    return columns, rows, None, None, [
        {"label": "Scheduled Activities", "value": len(rows), "indicator": "blue"},
        {"label": "Completed Activities", "value": sum(row["progress"] >= 100 for row in rows), "indicator": "green"},
    ]
