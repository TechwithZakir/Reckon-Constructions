import frappe


def _project_filters(filters):
    project = (filters or {}).get("project")
    return {"project": project} if project else {}


def _project_label(project):
    if not project:
        return ""
    return frappe.db.get_value("Project", project, "project_name") or project


def execute(filters=None):
    filters = frappe.parse_json(filters) if isinstance(filters, str) else (filters or {})
    project_filters = _project_filters(filters)
    rows = []
    reports = frappe.get_all(
        "Daily Site Report",
        filters=project_filters,
        fields=["name", "project", "report_date", "status", "total_verified_quantity"],
        order_by="report_date desc",
    )
    for report in reports:
        rows.append(
            {
                "activity_type": "Site Visit",
                "activity_date": report.report_date,
                "project": report.project,
                "project_name": _project_label(report.project),
                "activity": "Daily site progress report",
                "severity": "",
                "status": report.status or "Draft",
                "resolution": f"Verified quantity: {report.total_verified_quantity or 0}",
            }
        )

    issues = frappe.get_all(
        "Site Issue",
        filters=project_filters,
        fields=["name", "project", "title", "severity", "status", "resolution", "resolved_on", "creation"],
        order_by="creation desc",
    )
    for issue in issues:
        rows.append(
            {
                "activity_type": "Issue",
                "activity_date": issue.creation,
                "project": issue.project,
                "project_name": _project_label(issue.project),
                "activity": issue.title or issue.name,
                "severity": issue.severity or "",
                "status": issue.status or "Open",
                "resolution": issue.resolution or "Pending resolution",
            }
        )

    rows.sort(key=lambda row: str(row.get("activity_date") or ""), reverse=True)
    columns = [
        {"label": "Type", "fieldname": "activity_type", "fieldtype": "Data", "width": 100},
        {"label": "Date", "fieldname": "activity_date", "fieldtype": "Datetime", "width": 145},
        {"label": "Project", "fieldname": "project", "fieldtype": "Link", "options": "Project", "width": 170},
        {"label": "Project Name", "fieldname": "project_name", "fieldtype": "Data", "width": 220},
        {"label": "Activity / Issue", "fieldname": "activity", "fieldtype": "Data", "width": 280},
        {"label": "Severity", "fieldname": "severity", "fieldtype": "Data", "width": 100},
        {"label": "Status", "fieldname": "status", "fieldtype": "Data", "width": 120},
        {"label": "Resolution / Visit Result", "fieldname": "resolution", "fieldtype": "Data", "width": 280},
    ]
    return columns, rows, None, None, [
        {"label": "Activities and Visits", "value": len(reports), "indicator": "blue"},
        {"label": "Issues", "value": len(issues), "indicator": "orange"},
        {"label": "Resolved", "value": sum(issue.status in {"Resolved", "Closed"} for issue in issues), "indicator": "green"},
    ]
