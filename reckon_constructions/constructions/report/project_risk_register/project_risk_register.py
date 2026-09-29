import frappe


def _age_days(value):
    if not value:
        return 0
    try:
        return max(0, frappe.utils.date_diff(frappe.utils.getdate(), frappe.utils.getdate(value)))
    except (TypeError, ValueError):
        return 0


def execute(filters=None):
    filters = frappe.parse_json(filters) if isinstance(filters, str) else (filters or {})
    project = filters.get("project")
    project_filters = {"project": project} if project else {}
    rows = []
    issues = frappe.get_all(
        "Site Issue",
        filters=project_filters,
        fields=["name", "project", "title", "issue_type", "severity", "status", "due_date", "resolved_on", "creation", "resolution"],
        order_by="creation desc",
    )
    for issue in issues:
        rows.append(
            {
                "record_type": "Site Issue",
                "record": issue.name,
                "project": issue.project,
                "project_name": frappe.db.get_value("Project", issue.project, "project_name") or issue.project,
                "subject": issue.title or issue.name,
                "category": issue.issue_type or "Other",
                "severity": issue.severity or "Medium",
                "status": issue.status or "Open",
                "due_date": issue.due_date,
                "age_days": _age_days(issue.creation),
                "resolution": issue.resolution or "Pending resolution",
            }
        )
    rfis = frappe.get_all(
        "Request For Information",
        filters=project_filters,
        fields=["name", "project", "subject", "status", "raised_on", "due_date", "responded_on", "response"],
        order_by="raised_on desc",
    )
    for rfi in rfis:
        rows.append(
            {
                "record_type": "RFI",
                "record": rfi.name,
                "project": rfi.project,
                "project_name": frappe.db.get_value("Project", rfi.project, "project_name") or rfi.project,
                "subject": rfi.subject or rfi.name,
                "category": "Design / Information",
                "severity": "Medium",
                "status": rfi.status or "Open",
                "due_date": rfi.due_date,
                "age_days": _age_days(rfi.raised_on),
                "resolution": rfi.response or "Pending response",
            }
        )
    rows.sort(key=lambda row: (row["status"] in {"Resolved", "Closed", "Answered"}, -row["age_days"]))
    open_rows = [row for row in rows if row["status"] not in {"Resolved", "Closed", "Answered"}]
    critical_rows = [row for row in open_rows if row["severity"] == "Critical"]
    columns = [
        {"label": "Type", "fieldname": "record_type", "fieldtype": "Data", "width": 110},
        {"label": "Record", "fieldname": "record", "fieldtype": "Data", "width": 160},
        {"label": "Project", "fieldname": "project", "fieldtype": "Link", "options": "Project", "width": 160},
        {"label": "Project Name", "fieldname": "project_name", "fieldtype": "Data", "width": 210},
        {"label": "Subject", "fieldname": "subject", "fieldtype": "Data", "width": 260},
        {"label": "Category", "fieldname": "category", "fieldtype": "Data", "width": 150},
        {"label": "Severity", "fieldname": "severity", "fieldtype": "Data", "width": 100},
        {"label": "Status", "fieldname": "status", "fieldtype": "Data", "width": 120},
        {"label": "Due Date", "fieldname": "due_date", "fieldtype": "Date", "width": 110},
        {"label": "Age (Days)", "fieldname": "age_days", "fieldtype": "Int", "width": 100},
        {"label": "Resolution / Response", "fieldname": "resolution", "fieldtype": "Data", "width": 260},
    ]
    status_counts = {}
    for row in rows:
        status_counts[row["status"]] = status_counts.get(row["status"], 0) + 1
    chart = {
        "data": {"labels": list(status_counts), "datasets": [{"name": "Records", "values": list(status_counts.values())}]},
        "type": "bar",
        "height": 280,
    }
    return columns, rows, None, chart, [
        {"label": "Open Items", "value": len(open_rows), "indicator": "orange"},
        {"label": "Critical Open", "value": len(critical_rows), "indicator": "red"},
        {"label": "Site Issues", "value": len(issues), "indicator": "blue"},
        {"label": "RFIs", "value": len(rfis), "indicator": "green"},
    ]
