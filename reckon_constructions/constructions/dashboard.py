try:
    import frappe
except ImportError:
    frappe = None


def _whitelist(function):
    return frappe.whitelist()(function) if frappe else function


def _number(value):
    try:
        return float(value or 0)
    except (TypeError, ValueError):
        return 0.0


def calculate_dashboard_metrics(
    contract_value=0,
    boq_value=0,
    planned_value=0,
    variation_value=0,
    certified_value=0,
    committed_cost=0,
    actual_cost=0,
):
    approved_value = _number(boq_value) + _number(variation_value)
    contract_value = _number(contract_value) or approved_value
    certified_value = _number(certified_value)
    committed_cost = _number(committed_cost)
    actual_cost = _number(actual_cost)
    forecast_cost = actual_cost + committed_cost
    return {
        "contract_value": contract_value,
        "approved_value": approved_value,
        "planned_value": _number(planned_value),
        "variation_value": _number(variation_value),
        "certified_value": certified_value,
        "completion_percent": certified_value / approved_value * 100 if approved_value else 0,
        "committed_cost": committed_cost,
        "actual_cost": actual_cost,
        "forecast_cost": forecast_cost,
        "forecast_margin": contract_value - forecast_cost,
        "forecast_margin_percent": forecast_margin_percent(contract_value, forecast_cost),
    }


def forecast_margin_percent(contract_value, forecast_cost):
    contract_value = _number(contract_value)
    return (contract_value - _number(forecast_cost)) / contract_value * 100 if contract_value else 0


def _project_filter(project_names):
    if not project_names:
        return {}
    return {"project": project_names[0] if len(project_names) == 1 else ["in", project_names]}


def _available_fields(doctype, fields):
    meta = frappe.get_meta(doctype)
    return [field for field in fields if field == "name" or meta.has_field(field)]


def _scoped_rows(doctype, project_names, fields, filters=None, order_by=None, limit=None):
    query_filters = dict(filters or {})
    query_filters.update(_project_filter(project_names))
    return frappe.get_all(
        doctype,
        filters=query_filters,
        fields=_available_fields(doctype, fields),
        order_by=order_by,
        limit=limit,
    )


def _status_counts(rows, fieldname):
    counts = {}
    for row in rows:
        value = row.get(fieldname) or "Unspecified"
        counts[value] = counts.get(value, 0) + 1
    return counts


def _customer_names(projects):
    names = {row.customer for row in projects if row.get("customer")}
    if not names:
        return {}
    customers = frappe.get_all(
        "Customer",
        filters={"name": ["in", list(names)]},
        fields=["name", "customer_name"],
    )
    return {row.name: row.customer_name or row.name for row in customers}


def _portfolio_project_rows(projects, customer_names):
    rows = []
    for project in projects:
        rows.append(
            {
                "name": project.name,
                "project_name": project.project_name or project.name,
                "customer": customer_names.get(project.customer, project.customer),
                "status": project.get("status") or "Open",
                "construction_status": project.get("construction_status") or project.get("status") or "Open",
                "progress": round(_number(project.get("percent_complete")), 2),
                "contract_value": _number(project.get("construction_contract_value")),
                "expected_start_date": project.get("expected_start_date"),
                "expected_end_date": project.get("expected_end_date"),
            }
        )
    return rows


def _site_report_progress(reports, progress_rows, project_display_names):
    by_report = {}
    for row in progress_rows:
        by_report.setdefault(row.parent, []).append(_number(row.percent_complete))

    result = []
    for report in reports:
        values = by_report.get(report.name, [])
        progress = sum(values) / len(values) if values else 0
        result.append(
            {
                "name": report.name,
                "project": report.project,
                "project_name": project_display_names.get(report.project, report.project),
                "report_date": report.report_date,
                "status": report.status or "Draft",
                "verified_quantity": round(_number(report.total_verified_quantity), 3),
                "progress": round(progress, 2),
            }
        )
    return sorted(result, key=lambda row: (row.get("report_date") or "", row["name"]), reverse=True)


def _gantt_rows(tasks, project_display_names):
    rows = []
    for task in tasks:
        rows.append(
            {
                "name": task.name,
                "subject": task.subject or task.name,
                "project": task.project,
                "project_name": project_display_names.get(task.project, task.project),
                "start_date": task.exp_start_date,
                "end_date": task.exp_end_date,
                "progress": round(_number(task.get("progress") or task.get("percent_complete")), 2),
                "status": task.get("status") or "Open",
            }
        )
    return sorted(rows, key=lambda row: (row.get("start_date") or "", row["project_name"], row["subject"]))


def _recent_activity(project_names, project_display_names):
    activities = []
    sources = (
        ("Daily Site Report", "Site visit", "report_date", "status"),
        ("Site Issue", "Site issue", "creation", "status"),
        ("Request For Information", "RFI", "raised_on", "status"),
        ("Engineering Document", "Engineering document", "issue_date", "status"),
        ("Progress Certificate", "Progress certificate", "modified", "status"),
    )
    for doctype, activity_type, date_field, status_field in sources:
        records = _scoped_rows(
            doctype,
            project_names,
            ["name", "project", date_field, status_field],
            order_by="modified desc",
            limit=30,
        )
        for record in records:
            activities.append(
                {
                    "doctype": doctype,
                    "type": activity_type,
                    "name": record.name,
                    "project": project_display_names.get(record.project, record.project),
                    "date": record.get(date_field),
                    "status": record.get(status_field) or "Draft",
                }
            )
    return sorted(activities, key=lambda row: row.get("date") or "", reverse=True)[:16]


def _build_dashboard_payload(project=None):
    selected_project = project or None
    project_filters = {"name": selected_project} if selected_project else {}
    projects = frappe.get_all(
        "Project",
        filters=project_filters,
        fields=_available_fields("Project", [
            "name",
            "project_name",
            "customer",
            "company",
            "status",
            "construction_status",
            "construction_contract_value",
            "construction_currency",
            "percent_complete",
            "expected_start_date",
            "expected_end_date",
        ]),
        order_by="modified desc",
        limit=100,
    )
    project_names = [row.name for row in projects]
    customer_names = _customer_names(projects)
    project_rows = _portfolio_project_rows(projects, customer_names)
    project_display_names = {row["name"]: row["project_name"] for row in project_rows}

    boqs = _scoped_rows(
        "Construction BOQ",
        project_names,
        ["name", "project", "status", "total_amount", "docstatus", "modified"],
        filters={"docstatus": 1},
        order_by="modified desc",
    )
    baselines = _scoped_rows(
        "Project Baseline",
        project_names,
        ["name", "project", "status", "planned_value", "docstatus", "modified"],
        filters={"docstatus": 1},
        order_by="modified desc",
    )
    variations = _scoped_rows(
        "Variation Order",
        project_names,
        ["name", "project", "status", "net_amount", "docstatus"],
        filters={"docstatus": 1},
    )
    certificates = _scoped_rows(
        "Progress Certificate",
        project_names,
        ["name", "project", "status", "gross_value", "net_value", "docstatus", "modified"],
        filters={"docstatus": 1},
        order_by="modified desc",
    )
    purchase_orders = _scoped_rows(
        "Purchase Order",
        project_names,
        ["name", "project", "grand_total", "docstatus"],
        filters={"docstatus": ["<", 2]},
    )
    reports = _scoped_rows(
        "Daily Site Report",
        project_names,
        ["name", "project", "report_date", "status", "total_verified_quantity", "modified"],
        order_by="report_date desc",
    )
    report_names = [row.name for row in reports]
    progress_rows = (
        frappe.get_all(
            "Daily Site Report Progress",
            filters={"parent": ["in", report_names]},
            fields=["parent", "percent_complete"],
        )
        if report_names
        else []
    )
    issues = _scoped_rows(
        "Site Issue",
        project_names,
        ["name", "project", "title", "status", "severity", "creation", "resolved_on", "modified"],
        order_by="modified desc",
    )
    rfis = _scoped_rows(
        "Request For Information",
        project_names,
        ["name", "project", "subject", "status", "raised_on", "modified"],
        order_by="modified desc",
    )
    engineering = _scoped_rows(
        "Engineering Document",
        project_names,
        ["name", "project", "title", "status", "issue_date", "modified"],
    )
    tasks = _scoped_rows(
        "Task",
        project_names,
        ["name", "subject", "project", "exp_start_date", "exp_end_date", "progress", "percent_complete", "status"],
        order_by="exp_start_date asc",
    )

    total_contract = sum(_number(row.get("contract_value")) for row in project_rows)
    boq_value = sum(_number(row.total_amount) for row in boqs)
    planned_value = sum(_number(row.planned_value) for row in baselines)
    variation_value = sum(_number(row.net_amount) for row in variations)
    certified_value = sum(_number(row.gross_value) for row in certificates)
    committed_cost = sum(_number(row.grand_total) for row in purchase_orders)
    metrics = calculate_dashboard_metrics(
        contract_value=total_contract,
        boq_value=boq_value,
        planned_value=planned_value,
        variation_value=variation_value,
        certified_value=certified_value,
        committed_cost=committed_cost,
    )

    issue_status = _status_counts(issues, "status")
    issue_severity = _status_counts(issues, "severity")
    certificate_status = _status_counts(certificates, "status")
    open_issue_statuses = {"Open", "In Progress"}
    open_rfi_statuses = {"Open", "In Progress"}
    site_reports = _site_report_progress(reports, progress_rows, project_display_names)
    project_progress = sorted(project_rows, key=lambda row: row["progress"], reverse=True)
    status_breakdown = _status_counts(project_rows, "construction_status")
    gantt = _gantt_rows(tasks, project_display_names)

    return {
        "project": selected_project,
        "scope": "project" if selected_project else "portfolio",
        "currency": (projects[0].get("construction_currency") if projects else None)
        or frappe.db.get_single_value("Global Defaults", "default_currency"),
        "metrics": metrics,
        "counts": {
            "projects": len(project_rows),
            "active_projects": sum(row["construction_status"] == "Active" for row in project_rows),
            "completed_projects": sum(row["construction_status"] == "Completed" for row in project_rows),
            "on_hold_projects": sum(row["construction_status"] == "On Hold" for row in project_rows),
            "boqs": len(boqs),
            "site_reports": len(reports),
            "site_visits": len(reports),
            "tasks": len(tasks),
            "open_issues": sum(issue.status in open_issue_statuses for issue in issues),
            "resolved_issues": sum(issue.status in {"Resolved", "Closed"} for issue in issues),
            "open_rfis": sum(rfi.status in open_rfi_statuses for rfi in rfis),
            "certificates": len(certificates),
            "engineering_documents": len(engineering),
        },
        "project_progress": project_progress,
        "site_report_progress": site_reports,
        "gantt": gantt[:40],
        "status_breakdown": status_breakdown,
        "issue_summary": {"status": issue_status, "severity": issue_severity},
        "certificate_status": certificate_status,
        "activity_summary": {
            "tasks": len(tasks),
            "site_visits": len(reports),
            "issues": len(issues),
            "resolved_issues": sum(issue.status in {"Resolved", "Closed"} for issue in issues),
            "rfis": len(rfis),
            "engineering_documents": len(engineering),
            "certificates": len(certificates),
        },
        "recent_activity": _recent_activity(project_names, project_display_names),
        "approvals": {
            "boq": boqs[0].status if boqs else "Missing",
            "baseline": baselines[0].status if baselines else "Missing",
            "pending": sum(row.status in {"Draft", "Under Review"} for row in boqs + baselines),
        },
    }


@_whitelist
def get_dashboard_projects():
    """Return projects that can be selected when the dashboard is opened directly."""
    if frappe is None:
        raise RuntimeError("Frappe is required for dashboard queries.")

    projects = frappe.get_all(
        "Project",
        fields=_available_fields("Project", ["name", "project_name", "customer", "company", "construction_currency", "construction_status", "construction_contract_value"]),
        order_by="modified desc",
        limit=100,
    )
    customer_names = _customer_names(projects)
    for project in projects:
        project.customer_name = customer_names.get(project.customer, project.customer)
    return {"projects": projects}


@_whitelist
def get_project_dashboard(project=None, construction_project=None):
    if frappe is None:
        raise RuntimeError("Frappe is required for dashboard queries.")

    project_name = project or construction_project
    if project_name:
        project_doc = frappe.get_doc("Project", project_name)
        project_doc.check_permission("read")
    return _build_dashboard_payload(project_name)


def latest_submitted(doctype, project, fieldname):
    names = frappe.get_all(
        doctype,
        filters={fieldname: project, "docstatus": 1},
        fields=["name"],
        order_by="modified desc",
        limit=1,
    )
    return frappe.get_doc(doctype, names[0].name) if names else None
