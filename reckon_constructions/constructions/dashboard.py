try:
    import frappe
except ImportError:
    frappe = None


def _whitelist(function):
    return frappe.whitelist()(function) if frappe else function


def calculate_dashboard_metrics(
    contract_value=0,
    boq_value=0,
    planned_value=0,
    variation_value=0,
    certified_value=0,
    committed_cost=0,
    actual_cost=0,
):
    approved_value = float(boq_value or 0) + float(variation_value or 0)
    contract_value = float(contract_value or 0) or approved_value
    certified_value = float(certified_value or 0)
    committed_cost = float(committed_cost or 0)
    actual_cost = float(actual_cost or 0)
    forecast_cost = actual_cost + committed_cost
    return {
        "contract_value": contract_value,
        "approved_value": approved_value,
        "planned_value": float(planned_value or 0),
        "variation_value": float(variation_value or 0),
        "certified_value": certified_value,
        "completion_percent": certified_value / approved_value * 100 if approved_value else 0,
        "committed_cost": committed_cost,
        "actual_cost": actual_cost,
        "forecast_cost": forecast_cost,
        "forecast_margin": contract_value - forecast_cost,
        "forecast_margin_percent": forecast_margin_percent(contract_value, forecast_cost),
    }


def forecast_margin_percent(contract_value, forecast_cost):
    contract_value = float(contract_value or 0)
    return (contract_value - float(forecast_cost or 0)) / contract_value * 100 if contract_value else 0


@_whitelist
def get_dashboard_projects():
    """Return projects that can be selected when the dashboard is opened directly."""
    if frappe is None:
        raise RuntimeError("Frappe is required for dashboard queries.")

    projects = frappe.get_all(
        "Project",
        fields=["name", "project_name", "customer", "company", "construction_currency", "construction_status", "construction_contract_value"],
        order_by="modified desc",
        limit=100,
    )
    return {"projects": projects}


@_whitelist
def get_project_dashboard(project=None, construction_project=None):
    if frappe is None:
        raise RuntimeError("Frappe is required for dashboard queries.")

    project_name = project or construction_project
    if not project_name:
        frappe.throw("Select a Project before opening the dashboard.")

    project_doc = frappe.get_doc("Project", project_name)
    project_doc.check_permission("read")

    boq = latest_submitted("Construction BOQ", project_name, "project")
    baseline = latest_submitted("Project Baseline", project_name, "project")
    variations = frappe.get_all(
        "Variation Order",
        filters={"project": project_name, "docstatus": 1},
        fields=["net_amount"],
    )
    certificates = frappe.get_all(
        "Progress Certificate",
        filters={"project": project_name, "docstatus": 1},
        fields=["gross_value"],
    )

    open_issues = frappe.db.count("Site Issue", {"project": project_name, "status": ["in", ["Open", "In Progress"]]})
    open_rfis = frappe.db.count("Request For Information", {"project": project_name, "status": ["in", ["Open"]]})
    variation_value = sum((row.net_amount or 0) for row in variations)
    certified_value = sum((row.gross_value or 0) for row in certificates)
    metrics = calculate_dashboard_metrics(
        contract_value=project_doc.construction_contract_value,
        boq_value=boq.total_amount if boq else 0,
        planned_value=baseline.planned_value if baseline else 0,
        variation_value=variation_value,
        certified_value=certified_value,
    )
    return {
        "project": project_name,
        "erpnext_project": project_doc.name,
        "status": project_doc.construction_status or project_doc.status,
        "metrics": metrics,
        "approvals": {
            "boq": boq.status if boq else "Missing",
            "baseline": baseline.status if baseline else "Missing",
        },
        "open_issues": open_issues,
        "open_rfis": open_rfis,
    }


def latest_submitted(doctype, project, fieldname):
    names = frappe.get_all(
        doctype,
        filters={fieldname: project, "docstatus": 1},
        fields=["name"],
        order_by="modified desc",
        limit=1,
    )
    return frappe.get_doc(doctype, names[0].name) if names else None
