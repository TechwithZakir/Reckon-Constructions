"""Deterministic demo data for the Reckon Constructions UAT flow.

Run from a bench with ``bench --site <site> execute``.  The seed uses an
existing Company and does not create or delete accounting setup records.
"""

DEMO_NAMES = {
    "customer": "RC Demo Customer",
    "project": "RC-DEMO-PROJECT",
    "construction_project": "RC-DEMO-PROJECT",
    "sales_order": "RC-DEMO-SO-001",
    "boq": "RC-DEMO-BOQ-001",
    "calculation_volume": "RC Demo Volume Calculation",
    "calculation_area": "RC Demo Area Calculation",
    "calculation_count": "RC Demo Count Calculation",
    "calculation_factor": "RC Demo Factor Calculation",
    "assembly_excavation": "RC Demo Excavation",
    "assembly_concrete": "RC Demo Concrete M20",
    "assembly_masonry": "RC Demo Masonry",
    "assembly_finishing": "RC Demo Floor Tiles",
    "rate_excavation": "RC-DEMO-RA-EXCAVATION",
    "rate_concrete": "RC-DEMO-RA-CONCRETE",
    "rate_masonry": "RC-DEMO-RA-MASONRY",
    "rate_finishing": "RC-DEMO-RA-FINISHING",
    "measurement_excavation": "RC-DEMO-MS-EXCAVATION",
    "measurement_concrete": "RC-DEMO-MS-CONCRETE",
    "measurement_masonry": "RC-DEMO-MS-MASONRY",
    "measurement_finishing": "RC-DEMO-MS-FINISHING",
    "baseline": "RC-DEMO-PB-001",
    "task_excavation": "RC-DEMO-TASK-EXCAVATION",
    "task_concrete": "RC-DEMO-TASK-CONCRETE",
    "task_masonry": "RC-DEMO-TASK-MASONRY",
    "task_finishing": "RC-DEMO-TASK-FINISHING",
    "engineering": "RC-DEMO-ED-001",
    "rfi": "RC-DEMO-RFI-001",
    "daily_report": "RC-DEMO-DSR-001",
    "site_issue": "RC-DEMO-SI-001",
    "material_preview": "RC-DEMO-MRP-001",
    "variation": "RC-DEMO-VO-001",
    "certificate": "RC-DEMO-PC-001",
}

ITEM_NAMES = {
    "excavation": "RC-DEMO-EXCAVATION",
    "concrete": "RC-DEMO-CONCRETE-M20",
    "block": "RC-DEMO-BLOCK-6",
    "tile": "RC-DEMO-TILE-600",
    "cement": "RC-DEMO-CEMENT",
    "sand": "RC-DEMO-SAND",
    "aggregate": "RC-DEMO-AGGREGATE",
}

LINE_KEYS = {
    "excavation": "EARTH-001",
    "concrete": "CON-001",
    "masonry": "MASON-001",
    "finishing": "FIN-001",
}

DEMO_PROJECT_COUNT = 100
DEMO_CUSTOMER_COUNT = 30
DEMO_SUPPLIER_COUNT = 8
DEMO_WAREHOUSE_COUNT = 6


def _frappe():
    import frappe

    return frappe


def demo_plan():
    """Return the deterministic records covered by the seed and clear actions."""
    return {
        "portfolio_project_count": DEMO_PROJECT_COUNT,
        "portfolio_customer_count": DEMO_CUSTOMER_COUNT,
        "portfolio_supplier_count": DEMO_SUPPLIER_COUNT,
        "portfolio_warehouse_count": DEMO_WAREHOUSE_COUNT,
        "custom_doctypes": [
            "Construction Settings",
            "Construction BOQ",
            "Construction BOQ Section",
            "Construction BOQ Item",
            "Calculation Template",
            "Calculation Template Variable",
            "Construction Assembly",
            "Construction Assembly Component",
            "Rate Analysis",
            "Rate Analysis Component",
            "Measurement Sheet",
            "Measurement Sheet Row",
            "Project Baseline",
            "Project Baseline Work Package",
            "Engineering Document",
            "Request For Information",
            "Daily Site Report",
            "Daily Site Report Progress",
            "Site Issue",
            "Material Requirement Preview",
            "Material Requirement Preview Item",
            "Variation Order",
            "Variation Order Item",
            "Progress Certificate",
            "Progress Certificate Item",
        ],
        "erpnext_doctypes": [
            "Customer",
            "Item",
            "Project",
            "Quotation",
            "Sales Order",
            "Task",
            "Material Request",
            "Supplier",
            "Warehouse",
            "Purchase Order",
            "Sales Invoice",
        ],
    }


def seed_demo_data(
    project_count=DEMO_PROJECT_COUNT,
    dry_run=True,
    confirm_demo_site=False,
    reset=False,
):
    """Preview or create the complete construction demo dataset.

    Dry-run is the default. Writes require ``confirm_demo_site=True`` because
    the seed creates many linked ERPNext transactions. Existing deterministic
    demo records are reused; pass ``reset=True`` with confirmation to rebuild.
    """
    frappe = _frappe()
    project_count = max(int(project_count or DEMO_PROJECT_COUNT), 1)
    company = _get_company(frappe)
    blockers = _preflight(frappe, company)
    if blockers:
        frappe.throw("Demo setup prerequisites are missing:\n- " + "\n- ".join(blockers))
    if dry_run:
        cleanup = clear_demo_data(dry_run=True)
        return {
            "writes": False,
            "company": company,
            "projects_requested": project_count,
            "reset_requested": bool(reset),
            "expected_documents": _expected_seed_counts(project_count),
            "existing_demo_records": cleanup["count"],
            "cleanup_preview": cleanup,
            "next_step": "Run with dry_run=False and confirm_demo_site=True on a dedicated demo site.",
        }
    if not confirm_demo_site:
        frappe.throw(
            "Refusing to create demo data without confirm_demo_site=True. "
            "Use a dedicated demo site."
        )
    if reset:
        clear_demo_data(dry_run=False, confirm_demo_site=True)

    currency = _get_currency(frappe, company)
    groups = _get_master_groups(frappe)
    user = frappe.session.user if frappe.session.user and frappe.session.user != "Guest" else "Administrator"
    dates = _demo_dates(frappe)
    summary = {"created": [], "existing": [], "names": {}}

    def ensure(doctype, name, values=None, children=None):
        doc, created = _ensure_doc(frappe, doctype, name, values or {}, children or {})
        summary["created" if created else "existing"].append(f"{doctype}: {doc.name}")
        summary["names"].setdefault(doctype, []).append(doc.name)
        return doc

    _ensure_uoms(frappe, ["m3", "m2", "m", "Nos", "Bag", "Hour"])
    customer = ensure(
        "Customer",
        DEMO_NAMES["customer"],
        {
            "customer_name": "Eastern Developments Ltd. (Demo)",
            "customer_type": "Company",
            "customer_group": groups["customer_group"],
            "territory": groups["territory"],
        },
    )
    customers = _ensure_demo_customers(frappe, customer, groups, ensure)
    suppliers = _ensure_demo_suppliers(frappe, groups, ensure)
    warehouses = _ensure_demo_warehouses(frappe, company, ensure)
    items = _ensure_items(frappe, company, groups["item_group"], ensure)
    project = ensure(
        "Project",
        DEMO_NAMES["project"],
        {
            "project_name": "Riverside Apartment Complex - Demo",
            "status": "Open",
            "company": company,
            "customer": customer.name,
            "construction_status": "Active",
            "construction_currency": currency,
            "construction_contract_start_date": dates["start"],
            "construction_contract_end_date": dates["end"],
            "construction_contract_value": 1983380,
            "construction_site_name": "Riverside Apartment Complex",
            "construction_site_address": "Riverside Road, Dhaka - Demo Site",
        },
    )
    portfolio_projects = _ensure_portfolio_projects(
        frappe, company, currency, customers, dates, ensure, project_count
    )

    settings = frappe.get_single("Construction Settings")
    settings.update(
        {
            "default_company": company,
            "default_currency": currency,
            "quantity_precision": 3,
            "currency_precision": 2,
            "default_retention_percent": 5,
            "require_customer_variation_approval": 1,
            "enable_sales_handoff": 1,
            "enable_procurement_generation": 1,
            "enable_progress_billing": 1,
        }
    )
    settings.save(ignore_permissions=True)
    summary["names"].setdefault("Construction Settings", []).append("Construction Settings")

    construction_project = project

    calculations = _ensure_calculations(frappe, currency, ensure)
    assemblies = _ensure_assemblies(frappe, items, ensure)
    boq = _ensure_boq(frappe, construction_project, customer, company, currency, items, ensure)
    line_keys = _get_boq_line_keys(boq)
    measurements = _ensure_measurements(
        frappe, construction_project, boq, calculations, dates, line_keys, ensure
    )
    for measurement in measurements:
        _submit_if_needed(measurement)

    rates = _ensure_rates(
        frappe, construction_project, boq, assemblies, items, dates, line_keys, ensure
    )
    for rate in rates:
        _submit_if_needed(rate)
    _submit_if_needed(boq)

    quotation = _ensure_quotation(frappe, boq, ensure)
    sales_order = _ensure_sales_order(
        frappe, company, customer, currency, project, quotation, items, dates, ensure
    )
    if not construction_project.sales_order:
        construction_project.sales_order = sales_order.name
        construction_project.save(ignore_permissions=True)

    tasks = _ensure_tasks(frappe, project, company, dates, ensure)
    baseline = _ensure_baseline(
        frappe,
        construction_project,
        boq,
        sales_order,
        assemblies,
        tasks,
        dates,
        line_keys,
        ensure,
    )
    _submit_if_needed(baseline)

    engineering = ensure(
        "Engineering Document",
        DEMO_NAMES["engineering"],
        {
            "project": construction_project.name,
            "document_number": "STR-ARC-001",
            "title": "Structural General Arrangement - Demo",
            "document_type": "Drawing",
            "revision": 1,
            "status": "Approved",
            "issue_date": dates["start"],
            "approval_date": dates["start"],
            "file_url": "/files/rc-demo-structural-drawing.pdf",
            "notes": "Demo engineering record for the UAT flow.",
        },
    )
    ensure(
        "Request For Information",
        DEMO_NAMES["rfi"],
        {
            "project": construction_project.name,
            "document": engineering.name,
            "raised_by": user,
            "assigned_to": user,
            "raised_on": dates["start"],
            "due_date": dates["rfi_due"],
            "status": "Answered",
            "subject": "Confirm concrete cover at transfer beam",
            "question": "Please confirm the specified concrete cover at the transfer beam.",
            "response": "Use the approved structural drawing revision 1: 40 mm cover.",
            "responded_on": dates["start"],
        },
    )
    daily_report = ensure(
        "Daily Site Report",
        DEMO_NAMES["daily_report"],
        {
            "project": construction_project.name,
            "boq_revision": boq.name,
            "report_date": dates["progress"],
            "site_engineer": user,
            "status": "Draft",
            "notes": "Demo daily report with verified excavation and concrete progress.",
        },
        {
            "progress": [
                {"boq_line_key": line_keys["excavation"], "work_package": "Earthwork", "quantity": 195, "uom": "m3", "remarks": "Foundation excavation complete in Zone A."},
                {"boq_line_key": line_keys["concrete"], "work_package": "Concrete Works", "quantity": 36, "uom": "m3", "remarks": "Footings poured and cured."},
            ]
        },
    )
    _submit_if_needed(daily_report)
    ensure(
        "Site Issue",
        DEMO_NAMES["site_issue"],
        {
            "project": construction_project.name,
            "site_report": daily_report.name,
            "issue_type": "Quality",
            "severity": "Medium",
            "title": "Concrete cube test certificate pending",
            "description": "The laboratory certificate for the latest concrete pour is pending upload.",
            "owner": user,
            "due_date": dates["rfi_due"],
            "status": "In Progress",
        },
    )

    preview = _ensure_material_preview(frappe, baseline, assemblies, ensure)
    _submit_if_needed(preview)
    material_request = _ensure_material_request(frappe, preview, construction_project, ensure)

    variation = ensure(
        "Variation Order",
        DEMO_NAMES["variation"],
        {
            "project": construction_project.name,
            "boq": boq.name,
            "baseline": baseline.name,
            "variation_type": "Addition",
            "variation_no": 1,
            "reason": "Additional drainage channel requested by the customer.",
            "status": "Draft",
            "customer_approved": 1,
        },
        {
            "items": [
                {"boq_line_key": line_keys["concrete"], "description": "Additional drainage channel concrete", "quantity_delta": 12, "uom": "m3", "rate": 9504, "measurement_ref": "VO-MEASURE-001"}
            ]
        },
    )
    _submit_if_needed(variation)

    certificate = ensure(
        "Progress Certificate",
        DEMO_NAMES["certificate"],
        {
            "project": construction_project.name,
            "boq": boq.name,
            "baseline": baseline.name,
            "certificate_no": 1,
            "period_start": dates["start"],
            "period_end": dates["progress"],
            "status": "Draft",
            "retention_percent": 5,
        },
        {
            "items": [
                {"boq_line_key": line_keys["excavation"], "description": "Excavation for foundation", "current_qty": 195, "previous_certified_qty": 0, "uom": "m3", "rate": 450},
                {"boq_line_key": line_keys["concrete"], "description": "RCC concrete M20", "current_qty": 36, "previous_certified_qty": 0, "uom": "m3", "rate": 9504},
            ]
        },
    )
    _submit_if_needed(certificate)
    invoice = _ensure_invoice(frappe, certificate, ensure)

    portfolio_sales_orders = _ensure_portfolio_sales_orders(
        frappe, company, currency, items, portfolio_projects
    )
    portfolio_records = _ensure_portfolio_construction_records(
        frappe,
        company,
        currency,
        items,
        assemblies,
        portfolio_projects,
        portfolio_sales_orders,
        warehouses,
        user,
        ensure,
    )
    portfolio_material_requests = _ensure_portfolio_material_requests(
        frappe, company, items, portfolio_projects, warehouses
    )
    portfolio_purchase_orders = _ensure_portfolio_purchase_orders(
        frappe,
        company,
        currency,
        items,
        suppliers,
        portfolio_projects,
        portfolio_material_requests,
        warehouses,
    )

    frappe.db.commit()
    summary["names"].update(
        {
            "Quotation": [quotation.name],
            "Sales Order": [sales_order.name],
            "Material Request": [material_request.name],
            "Sales Invoice": [invoice.name] if invoice else [],
            "Customer": [customer.name] + [item.name for item in customers[1:]],
            "Supplier": [item.name for item in suppliers],
            "Warehouse": [item.name for item in warehouses],
            "Portfolio Sales Order": [item.name for item in portfolio_sales_orders],
            "Portfolio Material Request": [item.name for item in portfolio_material_requests],
            "Portfolio Purchase Order": [item.name for item in portfolio_purchase_orders],
        }
    )
    summary["status"] = "seeded"
    summary["portfolio"] = {
        "projects": len(portfolio_projects) + 1,
        "generated_projects": len(portfolio_projects),
        "tasks": len(tasks) + sum(len(project.get("tasks", [])) for project in portfolio_projects),
        "progress_values": [project["progress"] for project in portfolio_projects],
        "customers": len(customers),
        "suppliers": len(suppliers),
        "warehouses": len(warehouses),
        "sales_orders": len(portfolio_sales_orders) + 1,
        "material_requests": len(portfolio_material_requests) + 1,
        "purchase_orders": len(portfolio_purchase_orders),
        "construction_records": portfolio_records,
    }
    return summary


def clear_demo_data(confirm=False, dry_run=True, confirm_demo_site=False):
    """Delete only the deterministic demo records.

    Use ``dry_run=True`` to inspect the target list. A real deletion requires
    ``confirm=True`` or ``confirm_demo_site=True`` so an accidental bench
    command cannot erase demo data.
    Submitted records are cancelled before deletion.
    """
    frappe = _frappe()
    targets = _find_demo_targets(frappe)
    if dry_run:
        populated_targets = {doctype: names for doctype, names in targets.items() if names}
        return {
            "status": "preview",
            "writes": False,
            "targets": populated_targets,
            "count": sum(len(v) for v in populated_targets.values()),
        }
    if not (confirm or confirm_demo_site):
        frappe.throw(
            "Demo data deletion requires confirm=True or confirm_demo_site=True. "
            "Use dry_run=True to preview."
        )

    deleted = []
    order = [
        "Sales Invoice",
        "Progress Certificate",
        "Variation Order",
        "Site Issue",
        "Daily Site Report",
        "Purchase Order",
        "Material Request",
        "Request For Information",
        "Engineering Document",
        "Material Requirement Preview",
        "Project Baseline",
        "Measurement Sheet",
        "Rate Analysis",
        "Quotation",
        "Construction BOQ",
        "Sales Order",
        "Task",
        "Project",
        "Warehouse",
        "Supplier",
        "Construction Assembly",
        "Calculation Template",
        "Item",
        "Customer",
    ]
    for doctype in order:
        for name in targets.get(doctype, []):
            if _delete_doc(frappe, doctype, name):
                deleted.append(f"{doctype}: {name}")

    settings = frappe.get_single("Construction Settings")
    if settings.get("default_company"):
        settings.update(
            {
                "default_company": None,
                "default_currency": None,
                "default_retention_percent": 0,
                "enable_sales_handoff": 0,
                "enable_procurement_generation": 0,
                "enable_progress_billing": 0,
            }
        )
        settings.save(ignore_permissions=True)
        deleted.append("Construction Settings: demo defaults cleared")

    frappe.db.commit()
    return {"status": "cleared", "writes": True, "deleted": deleted, "count": len(deleted)}


def _ensure_portfolio_projects(frappe, company, currency, customers, dates, ensure, count):
    """Create a rolling one-year project portfolio with deterministic task progress."""
    projects = []
    today = dates["start"]
    project_status_field = frappe.get_meta("Project").get_field("status")
    project_status_options = set((project_status_field.options or "").splitlines()) if project_status_field else set()
    for index in range(1, count):
        customer = customers[index % len(customers)]
        progress = (index * 17 + 7) % 101
        if index % 17 == 0:
            progress = 100

        duration = 140 + ((index * 29) % 220)
        start_offset = -330 + ((index * 11) % 361)
        if progress == 100:
            start_offset = -duration - (index % 45)
        start = frappe.utils.add_days(today, start_offset)
        end = frappe.utils.add_days(start, duration)

        if index % 29 == 0:
            construction_status, project_status = "Cancelled", "Cancelled"
            progress = min(progress, 45)
        elif index % 23 == 0:
            construction_status, project_status = "On Hold", "On Hold"
        elif progress == 100:
            construction_status, project_status = "Completed", "Completed"
        elif progress == 0:
            construction_status, project_status = "Draft", "Open"
        else:
            construction_status, project_status = "Active", "Open"
        if project_status_options and project_status not in project_status_options:
            project_status = "Open" if "Open" in project_status_options else next(iter(project_status_options))

        project = ensure(
            "Project",
            f"RC-DEMO-PROJECT-{index:03d}",
            {
                "project_name": f"RC Portfolio Project {index:03d}",
                "status": project_status,
                "company": company,
                "customer": customer.name,
                "percent_complete_method": "Task Completion",
                "percent_complete": progress,
                "expected_start_date": start,
                "expected_end_date": end,
                "actual_start_date": start if progress and start <= today else None,
                "actual_end_date": end if progress == 100 and end <= today else None,
                "construction_status": construction_status,
                "construction_currency": currency,
                "construction_contract_start_date": start,
                "construction_contract_end_date": end,
                "construction_contract_value": 750000 + (index * 42850),
                "construction_site_name": f"RC Portfolio Site {index:03d}",
                "construction_site_address": f"Project Zone {((index - 1) % 12) + 1}, Dhaka",
            },
        )
        if project.meta.has_field("customer") and project.customer != customer.name:
            frappe.db.set_value("Project", project.name, "customer", customer.name, update_modified=False)
            project.customer = customer.name
        tasks = _ensure_portfolio_tasks(
            frappe,
            project.name,
            company,
            start,
            end,
            progress,
            construction_status,
            ensure,
        )
        if project.meta.has_field("percent_complete"):
            frappe.db.set_value("Project", project.name, "percent_complete", progress, update_modified=False)
        projects.append(
            {
                "project": project.name,
                "progress": progress,
                "tasks": tasks,
                "customer": customer.name,
                "start": start,
                "end": end,
                "construction_status": construction_status,
                "index": index,
            }
        )
    return projects


def _ensure_portfolio_tasks(frappe, project, company, start, end, progress, construction_status, ensure):
    phases = [
        ("01", "Mobilization and site setup", 0, 45),
        ("02", "Earthwork and foundation", 30, 110),
        ("03", "Structure and concrete", 85, 230),
        ("04", "Masonry and finishing", 180, 340),
    ]
    task_meta = frappe.get_meta("Task")
    status_options = set((task_meta.get_field("status").options or "").splitlines())
    tasks = []
    for phase_number, subject, start_day, end_day in phases:
        threshold = (int(phase_number) - 1) * 25
        if construction_status == "Cancelled":
            task_status, task_progress = "Cancelled", 0
        elif progress >= threshold + 25:
            task_status, task_progress = "Completed", 100
        elif progress > threshold:
            task_status, task_progress = "Working", min(95, (progress - threshold) * 4)
        else:
            task_status, task_progress = "Open", 0

        if task_status not in status_options:
            task_status = "Open" if "Open" in status_options else next(iter(status_options), "Open")

        project_duration = frappe.utils.date_diff(end, start)
        task_start = frappe.utils.add_days(start, min(start_day, project_duration))
        task_end = frappe.utils.add_days(start, min(end_day, max(1, project_duration)))
        values = {
            "subject": subject,
            "status": task_status,
            "project": project,
            "company": company,
            "exp_start_date": task_start,
            "exp_end_date": task_end,
            "priority": "Medium",
            "progress": task_progress,
            "percent_complete": task_progress,
        }
        task = ensure("Task", f"RC-DEMO-TASK-{project.rsplit('-', 1)[-1]}-{phase_number}", values)
        for fieldname, value in values.items():
            if task.meta.has_field(fieldname):
                task.set(fieldname, value)
        task.save(ignore_permissions=True)
        tasks.append(task.name)
    return tasks


def _get_boq_line_keys(boq):
    fallback = ("excavation", "concrete", "masonry", "finishing")
    items = list(boq.get("items") or [])
    if len(items) < len(fallback):
        return dict(LINE_KEYS)
    return {
        key: items[index].line_key or LINE_KEYS[key]
        for index, key in enumerate(fallback)
    }


def _ensure_dynamic_doc(frappe, doctype, name, values, child_field, rows):
    if frappe.db.exists(doctype, name):
        return frappe.get_doc(doctype, name)
    doc = frappe.new_doc(doctype)
    if name:
        doc.name = name
        doc.flags.name_set = True
    for fieldname, value in values.items():
        if value is not None and doc.meta.has_field(fieldname):
            doc.set(fieldname, value)
    for values in rows or []:
        child = doc.append(child_field, {})
        for fieldname, value in values.items():
            if value is not None and child.meta.has_field(fieldname):
                child.set(fieldname, value)
    doc.insert(ignore_permissions=True)
    return doc


def _ensure_doc(frappe, doctype, name, values, children):
    if frappe.db.exists(doctype, name):
        return frappe.get_doc(doctype, name), False
    doc = frappe.new_doc(doctype)
    if name:
        doc.name = name
        doc.flags.name_set = True
    for fieldname, value in values.items():
        if doc.meta.has_field(fieldname):
            doc.set(fieldname, value)
    for fieldname, rows in children.items():
        for row in rows:
            doc.append(fieldname, row)
    doc.insert(ignore_permissions=True)
    return doc, True


def _submit_if_needed(doc):
    if doc and doc.docstatus == 0:
        # Related inserts can update modified timestamps during one seed run.
        # Reload before submit so Frappe's optimistic concurrency check sees
        # the current database version of the document.
        doc.reload()
        doc.submit()
    return doc


def _set_if_field_exists(doc, fieldname, value):
    if value is not None and doc.meta.has_field(fieldname):
        doc.set(fieldname, value)


def _preflight(frappe, company):
    blockers = []
    required = set(demo_plan()["custom_doctypes"] + demo_plan()["erpnext_doctypes"])
    required.update({"Company", "Currency", "UOM", "Customer Group", "Supplier Group", "Territory", "Item Group", "Price List"})
    for doctype in sorted(required):
        if not frappe.db.exists("DocType", doctype):
            blockers.append(f"Required ERPNext or Constructions DocType is unavailable: {doctype}")

    for doctype, preferred, leaf in (
        ("Customer Group", "All Customer Groups", True),
        ("Supplier Group", "All Supplier Groups", True),
        ("Territory", "All Territories", True),
        ("Item Group", "All Item Groups", True),
    ):
        try:
            _get_master_group_or_none(frappe, doctype, preferred, leaf)
        except Exception:
            blockers.append(f"No usable {doctype} is configured.")

    if frappe.db.exists("DocType", "Warehouse"):
        leaf_count = frappe.db.count("Warehouse", {"company": company, "is_group": 0})
        group_count = frappe.db.count("Warehouse", {"company": company, "is_group": 1})
        if not leaf_count and not group_count:
            blockers.append(f"No warehouse or warehouse group is configured for {company}.")
    return blockers


def _get_master_group_or_none(frappe, doctype, preferred, leaf=False):
    if frappe.db.exists(doctype, preferred) and (
        not leaf or not frappe.db.get_value(doctype, preferred, "is_group")
    ):
        return preferred
    filters = {"is_group": 0} if leaf else None
    return frappe.get_all(doctype, filters=filters, pluck="name", limit=1)[0]


def _expected_seed_counts(project_count):
    generated_projects = max(project_count - 1, 0)
    certificates = 0
    for index in range(1, project_count):
        progress = (index * 17 + 7) % 101
        if index % 17 == 0:
            progress = 100
        if index % 29 == 0:
            progress = min(progress, 45)
            construction_status = "Cancelled"
        else:
            construction_status = "Active"
        if construction_status != "Cancelled" and progress >= 20:
            certificates += 1
    return {
        "Customer": DEMO_CUSTOMER_COUNT,
        "Supplier": DEMO_SUPPLIER_COUNT,
        "Warehouse": DEMO_WAREHOUSE_COUNT,
        "Project": project_count,
        "Task": project_count * 4,
        "Sales Order": project_count,
        "Material Request": project_count,
        "Purchase Order": generated_projects,
        "Construction BOQ": project_count,
        "Project Baseline": project_count,
        "Daily Site Report": project_count,
        "Site Issue": project_count,
        "Progress Certificate": certificates + 1,
    }


def _get_company(frappe):
    company = frappe.db.get_single_value("Global Defaults", "default_company")
    if not company:
        companies = frappe.get_all("Company", pluck="name", order_by="creation asc", limit=1)
        company = companies[0] if companies else None
    if not company:
        frappe.throw("Seed requires at least one Company. Create accounting setup first.")
    return company


def _get_currency(frappe, company):
    currency = frappe.db.get_value("Company", company, "default_currency")
    if currency:
        return currency
    currencies = frappe.get_all("Currency", pluck="name", order_by="name asc", limit=1)
    if not currencies:
        frappe.throw("Seed requires at least one Currency.")
    return currencies[0]


def _get_master_groups(frappe):
    def first(doctype, preferred, leaf=False):
        if frappe.db.exists(doctype, preferred) and (
            not leaf or not frappe.db.get_value(doctype, preferred, "is_group")
        ):
            return preferred
        filters = {"is_group": 0} if leaf else None
        values = frappe.get_all(doctype, filters=filters, pluck="name", order_by="creation asc", limit=1)
        if not values:
            frappe.throw(f"Seed requires at least one {doctype}.")
        return values[0]

    return {
        "customer_group": first("Customer Group", "All Customer Groups", leaf=True),
        "supplier_group": first("Supplier Group", "All Supplier Groups", leaf=True),
        "territory": first("Territory", "All Territories", leaf=True),
        "item_group": first("Item Group", "All Item Groups", leaf=True),
    }


def _ensure_demo_customers(frappe, primary, groups, ensure):
    customers = [primary]
    for index in range(2, DEMO_CUSTOMER_COUNT + 1):
        customers.append(
            ensure(
                "Customer",
                f"RC-DEMO-CUSTOMER-{index:02d}",
                {
                    "customer_name": f"RC Demo Customer {index:02d}",
                    "customer_type": "Company",
                    "customer_group": groups["customer_group"],
                    "territory": groups["territory"],
                },
            )
        )
    return customers


def _ensure_demo_suppliers(frappe, groups, ensure):
    suppliers = []
    for index in range(1, DEMO_SUPPLIER_COUNT + 1):
        suppliers.append(
            ensure(
                "Supplier",
                f"RC-DEMO-SUPPLIER-{index:02d}",
                {
                    "supplier_name": f"RC Demo Materials Supplier {index:02d}",
                    "supplier_group": groups["supplier_group"],
                    "supplier_type": "Company",
                },
            )
        )
    return suppliers


def _ensure_demo_warehouses(frappe, company, ensure):
    """Return deterministic demo warehouses, reusing existing leaf warehouses when available."""
    warehouses = []
    existing = frappe.get_all(
        "Warehouse",
        filters={"company": company, "is_group": 0},
        pluck="name",
        order_by="creation asc",
        limit=DEMO_WAREHOUSE_COUNT,
    )
    warehouses.extend(frappe.get_doc("Warehouse", name) for name in existing)
    parent = frappe.get_all(
        "Warehouse",
        filters={"company": company, "is_group": 1},
        pluck="name",
        order_by="creation asc",
        limit=1,
    )
    for index in range(len(warehouses) + 1, DEMO_WAREHOUSE_COUNT + 1):
        name = f"RC Demo Warehouse {index:02d}"
        if not frappe.db.exists("Warehouse", name):
            values = {
                "warehouse_name": name,
                "company": company,
                "is_group": 0,
            }
            if parent:
                values["parent_warehouse"] = parent[0]
            warehouses.append(ensure("Warehouse", name, values))
        else:
            warehouses.append(frappe.get_doc("Warehouse", name))
    return warehouses[:DEMO_WAREHOUSE_COUNT]


def _ensure_uoms(frappe, names):
    for name in names:
        if frappe.db.exists("UOM", name):
            continue
        doc = frappe.new_doc("UOM")
        doc.name = name
        doc.uom_name = name
        doc.insert(ignore_permissions=True)


def _ensure_items(frappe, company, item_group, ensure):
    specs = {
        "excavation": (ITEM_NAMES["excavation"], "Excavation in soil", "m3"),
        "concrete": (ITEM_NAMES["concrete"], "RCC concrete M20", "m3"),
        "block": (ITEM_NAMES["block"], "6 inch concrete block wall", "m2"),
        "tile": (ITEM_NAMES["tile"], "600 x 600 ceramic floor tiles", "m2"),
        "cement": (ITEM_NAMES["cement"], "Portland cement", "Bag"),
        "sand": (ITEM_NAMES["sand"], "Fine aggregate sand", "m3"),
        "aggregate": (ITEM_NAMES["aggregate"], "20 mm coarse aggregate", "m3"),
    }
    result = {}
    for key, (item_code, item_name, stock_uom) in specs.items():
        result[key] = ensure(
            "Item",
            item_code,
            {
                "item_code": item_code,
                "item_name": item_name,
                "item_group": item_group,
                "stock_uom": stock_uom,
                "is_stock_item": 1,
                "description": f"Reckon Constructions demo item: {item_name}",
            },
        )
        _ensure_item_defaults(frappe, result[key], company)
    return result


def _ensure_item_defaults(frappe, item, company):
    if not item.meta.has_field("item_defaults"):
        return
    if any(row.company == company for row in item.get("item_defaults") or []):
        return

    defaults = {"company": company}
    company_meta = frappe.get_meta("Company")
    for fieldname, company_field in (
        ("income_account", "default_income_account"),
        ("expense_account", "default_expense_account"),
    ):
        if not company_meta.has_field(company_field):
            continue
        value = frappe.db.get_value("Company", company, company_field)
        if value:
            defaults[fieldname] = value
    if len(defaults) == 1:
        return
    item.append("item_defaults", defaults)
    item.save(ignore_permissions=True)


def _ensure_calculations(frappe, currency, ensure):
    del currency
    return {
        "volume": ensure(
            "Calculation Template",
            DEMO_NAMES["calculation_volume"],
            {"template_name": DEMO_NAMES["calculation_volume"], "description": "Calculate concrete, excavation, and other three-dimensional work from length x width x height.", "measurement_type": "Volume", "output_uom": "m3", "formula_version": 1, "formula": "length * width * height"},
            {"variables": [{"variable": "length", "label": "Length", "required": 1}, {"variable": "width", "label": "Width", "required": 1}, {"variable": "height", "label": "Height", "required": 1}]},
        ),
        "area": ensure(
            "Calculation Template",
            DEMO_NAMES["calculation_area"],
            {"template_name": DEMO_NAMES["calculation_area"], "description": "Calculate floor, wall, ceiling, and other surface areas from length x width.", "measurement_type": "Area", "output_uom": "m2", "formula_version": 1, "formula": "length * width"},
            {"variables": [{"variable": "length", "label": "Length", "required": 1}, {"variable": "width", "label": "Width", "required": 1}]},
        ),
        "count": ensure(
            "Calculation Template",
            DEMO_NAMES["calculation_count"],
            {"template_name": DEMO_NAMES["calculation_count"], "description": "Calculate repeated units such as doors, fixtures, or inspection points.", "measurement_type": "Count", "output_uom": "Nos", "formula_version": 1, "formula": "count"},
            {"variables": [{"variable": "count", "label": "Count", "required": 1}]},
        ),
        "factor": ensure(
            "Calculation Template",
            DEMO_NAMES["calculation_factor"],
            {"template_name": DEMO_NAMES["calculation_factor"], "description": "Apply a multiplier to repeated work, allowances, or productivity factors.", "measurement_type": "Factor", "output_uom": "Nos", "formula_version": 1, "formula": "count * factor"},
            {"variables": [{"variable": "count", "label": "Count", "required": 1}, {"variable": "factor", "label": "Factor", "required": 1}]},
        ),
    }


def _ensure_assemblies(frappe, items, ensure):
    def material(item, description, quantity_factor, uom, unit_rate, wastage=0):
        return {"component_kind": "Material", "item": items[item].name, "description": description, "quantity_factor": quantity_factor, "uom": uom, "unit_rate": unit_rate, "wastage_percent": wastage, "rate_source": "Demo rate card"}

    def labour(description, quantity_factor, unit_rate):
        return {"component_kind": "Labour", "description": description, "quantity_factor": quantity_factor, "uom": "Hour", "unit_rate": unit_rate, "wastage_percent": 0, "rate_source": "Demo labour schedule"}

    return {
        "excavation": ensure("Construction Assembly", DEMO_NAMES["assembly_excavation"], {"assembly_name": DEMO_NAMES["assembly_excavation"], "output_uom": "m3", "description": "Excavation production assembly", "overhead_percent": 0, "markup_percent": 0}, {"components": [labour("Excavator and operator", 1, 450)]}),
        "concrete": ensure("Construction Assembly", DEMO_NAMES["assembly_concrete"], {"assembly_name": DEMO_NAMES["assembly_concrete"], "output_uom": "m3", "description": "M20 reinforced concrete assembly", "overhead_percent": 10, "markup_percent": 8}, {"components": [material("cement", "Cement", 5, "Bag", 100), material("sand", "Fine aggregate", 0.5, "m3", 2000), material("aggregate", "Coarse aggregate", 0.8, "m3", 5000), labour("Concrete placing crew", 1, 2500)]}),
        "masonry": ensure("Construction Assembly", DEMO_NAMES["assembly_masonry"], {"assembly_name": DEMO_NAMES["assembly_masonry"], "output_uom": "m2", "description": "Concrete block masonry assembly", "overhead_percent": 5, "markup_percent": 10}, {"components": [material("block", "Concrete block", 1, "m2", 850), labour("Masonry crew", 1, 150)]}),
        "finishing": ensure("Construction Assembly", DEMO_NAMES["assembly_finishing"], {"assembly_name": DEMO_NAMES["assembly_finishing"], "output_uom": "m2", "description": "Ceramic floor tile assembly", "overhead_percent": 5, "markup_percent": 7.2}, {"components": [material("tile", "Ceramic floor tile", 1, "m2", 1000), labour("Tiling crew", 1, 100)]}),
    }


def _ensure_boq(frappe, construction_project, customer, company, currency, items, ensure):
    return ensure(
        "Construction BOQ",
        DEMO_NAMES["boq"],
        {"project": construction_project.name, "customer": customer.name, "company": company, "currency": currency, "boq_type": "Construction", "revision_no": 1, "status": "Draft", "revision_reason": "Initial demo tender and construction baseline."},
        {
            "sections": [
                {"section_code": "01", "section_name": "Earthwork", "description": "Excavation and foundation preparation"},
                {"section_code": "02", "section_name": "Concrete Works", "description": "Structural concrete works"},
                {"section_code": "03", "section_name": "Masonry Works", "description": "Block wall construction"},
                {"section_code": "04", "section_name": "Finishing Works", "description": "Floor finishes"},
            ],
            "items": [
                {"line_key": LINE_KEYS["excavation"], "section": "Earthwork", "item_code": items["excavation"].name, "description": "Excavation up to 1.5m depth including dressing and disposal", "quantity": 650, "uom": "m3", "rate": 450, "measurement_ref": DEMO_NAMES["measurement_excavation"]},
                {"line_key": LINE_KEYS["concrete"], "section": "Concrete Works", "item_code": items["concrete"].name, "description": "Supplying and casting RCC M20 including formwork", "quantity": 120, "uom": "m3", "rate": 8500, "measurement_ref": DEMO_NAMES["measurement_concrete"]},
                {"line_key": LINE_KEYS["masonry"], "section": "Masonry Works", "item_code": items["block"].name, "description": "6 inch concrete block wall including mortar", "quantity": 420, "uom": "m2", "rate": 1200, "measurement_ref": DEMO_NAMES["measurement_masonry"]},
                {"line_key": LINE_KEYS["finishing"], "section": "Finishing Works", "item_code": items["tile"].name, "description": "600x600 ceramic floor tiles including adhesive", "quantity": 200, "uom": "m2", "rate": 1234.4, "measurement_ref": DEMO_NAMES["measurement_finishing"]},
            ],
        },
    )


def _ensure_measurements(frappe, project, boq, calculations, dates, line_keys, ensure):
    specs = [
        ("measurement_excavation", line_keys["excavation"], "m3", calculations["volume"].name, [{"length": 10, "width": 10, "height": 6.5, "count": 1, "factor": 1}], "Foundation excavation drawing EX-001"),
        ("measurement_concrete", line_keys["concrete"], "m3", calculations["volume"].name, [{"length": 4, "width": 5, "height": 6, "count": 1, "factor": 1}], "Foundation concrete drawing ST-002"),
        ("measurement_masonry", line_keys["masonry"], "m2", calculations["area"].name, [{"length": 20, "width": 21, "height": 1, "count": 1, "factor": 1}], "Blockwork layout drawing AR-003"),
        ("measurement_finishing", line_keys["finishing"], "m2", calculations["area"].name, [{"length": 10, "width": 20, "height": 1, "count": 1, "factor": 1}], "Floor finish schedule AR-004"),
    ]
    result = []
    for key, line_key, uom, template, rows, drawing in specs:
        result.append(ensure("Measurement Sheet", DEMO_NAMES[key], {"project": project.name, "boq": boq.name, "boq_line_key": line_key, "output_uom": uom, "source_drawing": drawing, "status": "Draft"}, {"rows": [{"calculation_template": template, "sign": "Addition", **row} for row in rows]}))
    return result


def _ensure_rates(frappe, project, boq, assemblies, items, dates, line_keys, ensure):
    specs = [
        ("rate_excavation", line_keys["excavation"], "excavation", "m3", [{"component_kind": "Equipment", "description": "Excavator and operator", "quantity_factor": 1, "uom": "Hour", "unit_rate": 400}, {"component_kind": "Labour", "description": "Excavation labour", "quantity_factor": 1, "uom": "Hour", "unit_rate": 50}], 0, 0),
        ("rate_concrete", line_keys["concrete"], "concrete", "m3", [{"component_kind": "Material", "item": items["cement"].name, "description": "Cement", "quantity_factor": 5, "uom": "Bag", "unit_rate": 100}, {"component_kind": "Material", "item": items["sand"].name, "description": "Fine aggregate", "quantity_factor": 0.5, "uom": "m3", "unit_rate": 2000}, {"component_kind": "Material", "item": items["aggregate"].name, "description": "Coarse aggregate", "quantity_factor": 0.8, "uom": "m3", "unit_rate": 5000}, {"component_kind": "Labour", "description": "Concrete placing crew", "quantity_factor": 1, "uom": "Hour", "unit_rate": 2500}], 10, 8),
        ("rate_masonry", line_keys["masonry"], "masonry", "m2", [{"component_kind": "Material", "item": items["block"].name, "description": "Concrete block", "quantity_factor": 1, "uom": "m2", "unit_rate": 850}, {"component_kind": "Labour", "description": "Masonry crew", "quantity_factor": 1, "uom": "Hour", "unit_rate": 150}], 5, 10),
        ("rate_finishing", line_keys["finishing"], "finishing", "m2", [{"component_kind": "Material", "item": items["tile"].name, "description": "Ceramic floor tile", "quantity_factor": 1, "uom": "m2", "unit_rate": 1000}, {"component_kind": "Labour", "description": "Tiling crew", "quantity_factor": 1, "uom": "Hour", "unit_rate": 100}], 5, 7.2),
    ]
    result = []
    for key, line_key, assembly_key, uom, components, overhead, markup in specs:
        result.append(ensure("Rate Analysis", DEMO_NAMES[key], {"project": project.name, "boq": boq.name, "boq_line_key": line_key, "purpose": f"Price {line_key} work per {uom} for the construction BOQ.", "output_uom": uom, "assembly": assemblies[assembly_key].name, "effective_date": dates["start"], "status": "Draft", "overhead_percent": overhead, "markup_percent": markup}, {"components": components}))
    return result


def _ensure_quotation(frappe, boq, ensure):
    field = "construction_boq" if frappe.get_meta("Quotation").has_field("construction_boq") else None
    existing = frappe.db.get_value("Quotation", {field: boq.name, "docstatus": ["<", 2]}, "name") if field else None
    if existing:
        return frappe.get_doc("Quotation", existing)
    from reckon_constructions.constructions.integrations.sales_project import create_quotation_from_boq

    del ensure
    return frappe.get_doc("Quotation", create_quotation_from_boq(boq.name, "RC-DEMO-QUOTATION"))


def _ensure_sales_order(frappe, company, customer, currency, project, quotation, items, dates, ensure):
    if frappe.db.exists("Sales Order", DEMO_NAMES["sales_order"]):
        return frappe.get_doc("Sales Order", DEMO_NAMES["sales_order"])
    sales_order = frappe.new_doc("Sales Order")
    sales_order.name = DEMO_NAMES["sales_order"]
    sales_order.update({"customer": customer.name, "company": company, "currency": currency, "transaction_date": dates["start"], "delivery_date": dates["end"]})
    _set_if_field_exists(sales_order, "project", project.name)
    _set_if_field_exists(sales_order, "quotation", quotation.name)
    selling_price_list = _first_optional(frappe, "Price List", "Standard Selling")
    _set_if_field_exists(sales_order, "selling_price_list", selling_price_list)
    _set_if_field_exists(sales_order, "order_type", "Sales")
    for key, qty, rate, uom in [("excavation", 650, 450, "m3"), ("concrete", 120, 9504, "m3"), ("block", 420, 1200, "m2"), ("tile", 200, 1234.4, "m2")]:
        row = sales_order.append("items", {"item_code": items[key].name, "qty": qty, "rate": rate, "uom": uom, "schedule_date": dates["end"]})
        _set_if_field_exists(row, "project", project.name)
    sales_order.insert(ignore_permissions=True)
    return sales_order


def _ensure_portfolio_sales_orders(frappe, company, currency, items, projects):
    orders = []
    selling_price_list = _first_optional(frappe, "Price List", "Standard Selling")
    for project_data in projects:
        index = project_data["index"]
        name = f"RC-DEMO-SO-PORT-{index:03d}"
        transaction_date, schedule_date = _demo_transaction_dates(
            frappe, project_data["start"], project_data["end"]
        )
        values = {
            "customer": project_data["customer"],
            "company": company,
            "currency": currency,
            "transaction_date": transaction_date,
            "delivery_date": schedule_date,
            "project": project_data["project"],
            "selling_price_list": selling_price_list,
            "order_type": "Sales",
        }
        rows = [
            {"item_code": items["excavation"].name, "qty": 200 + index * 3, "rate": 450, "uom": "m3", "schedule_date": schedule_date},
            {"item_code": items["concrete"].name, "qty": 40 + index, "rate": 8500, "uom": "m3", "schedule_date": schedule_date},
        ]
        order = _ensure_dynamic_doc(frappe, "Sales Order", name, values, "items", rows)
        orders.append(order)
    return orders


def _ensure_portfolio_construction_records(
    frappe,
    company,
    currency,
    items,
    assemblies,
    projects,
    sales_orders,
    warehouses,
    user,
    ensure,
):
    counts = {"boqs": 0, "baselines": 0, "daily_reports": 0, "site_issues": 0, "progress_certificates": 0}
    for project_data, sales_order in zip(projects, sales_orders):
        index = project_data["index"]
        project_name = project_data["project"]
        scale = 0.72 + ((index * 13) % 29) / 100
        line_specs = [
            ("excavation", "Earthwork", "Excavation and foundation preparation", "m3", 650 * scale, 450),
            ("concrete", "Concrete Works", "Reinforced concrete M20", "m3", 120 * scale, 8500),
            ("block", "Masonry Works", "Concrete block wall", "m2", 420 * scale, 1200),
            ("tile", "Finishing Works", "Ceramic floor tiles", "m2", 200 * scale, 1234.4),
        ]
        line_keys = {key: f"PRJ{index:03d}-{key.upper()}-001" for key, *_ in line_specs}
        boq_name = f"RC-DEMO-BOQ-{index:03d}"
        boq = ensure(
            "Construction BOQ",
            boq_name,
            {
                "project": project_name,
                "customer": project_data["customer"],
                "company": company,
                "currency": currency,
                "boq_type": "Construction",
                "revision_no": 1,
                "status": "Draft",
                "revision_reason": "Portfolio demo BOQ for approval and project dashboard testing.",
            },
            {
                "sections": [
                    {"section_code": f"{position:02d}", "section_name": section, "description": description}
                    for position, (_, section, description, _, _, _) in enumerate(line_specs, start=1)
                ],
                "items": [
                    {
                        "line_key": line_keys[key],
                        "section": section,
                        "item_code": items[key].name,
                        "description": description,
                        "quantity": quantity,
                        "uom": uom,
                        "rate": rate,
                    }
                    for key, section, description, uom, quantity, rate in line_specs
                ],
            },
        )
        approved = project_data["progress"] >= 12 and project_data["construction_status"] != "Cancelled"
        if approved:
            _submit_if_needed(boq)
        elif boq.docstatus == 0 and index % 3 == 0 and boq.status == "Draft":
            boq.status = "Under Review"
            boq.save(ignore_permissions=True)
        counts["boqs"] += 1

        # Reuse the keys stored on an existing demo BOQ. This keeps reruns
        # compatible with records created by an earlier seed revision. The
        # portfolio calls the last two work types block/tile, while the
        # shared BOQ helper names them masonry/finishing.
        stored_line_keys = _get_boq_line_keys(boq)
        line_keys.update(
            {
                "excavation": stored_line_keys["excavation"],
                "concrete": stored_line_keys["concrete"],
                "block": stored_line_keys["masonry"],
                "tile": stored_line_keys["finishing"],
            }
        )
        approved_quantities = {
            row.line_key: float(row.quantity or 0)
            for row in boq.get("items") or []
        }

        duration = max(frappe.utils.date_diff(project_data["end"], project_data["start"]), 1)
        task_names = project_data["tasks"]
        work_packages = []
        for position, (key, section, _, uom, quantity, rate) in enumerate(line_specs):
            start_day = min(int(duration * position / 6), duration - 1)
            end_day = min(start_day + max(30, int(duration / 3)), duration)
            work_packages.append(
                {
                    "work_package": section,
                    "assembly": assemblies[{"excavation": "excavation", "concrete": "concrete", "block": "masonry", "tile": "finishing"}[key]].name,
                    "task": task_names[position - 1],
                    "boq_line_key": line_keys[key],
                    "planned_start": frappe.utils.add_days(project_data["start"], start_day),
                    "planned_end": frappe.utils.add_days(project_data["start"], end_day),
                    "planned_qty": quantity,
                    "uom": uom,
                    "planned_cost": quantity * rate * 0.82,
                    "planned_value": quantity * rate,
                    "depends_on": line_specs[position - 2][1] if position > 1 else None,
                    "milestone": 1 if position in (2, 4) else 0,
                }
            )
        baseline = ensure(
            "Project Baseline",
            f"RC-DEMO-PB-{index:03d}",
            {
                "project": project_name,
                "boq_revision": boq.name,
                "sales_order": sales_order.name,
                "baseline_version": 1,
                "status": "Draft",
            },
            {"work_packages": work_packages},
        )
        if approved:
            _submit_if_needed(baseline)
        counts["baselines"] += 1

        report_rows = []
        if approved and project_data["progress"] > 0:
            for key, section, _, uom, quantity, _ in line_specs:
                report_rows.append(
                    {
                        "boq_line_key": line_keys[key],
                        "work_package": section,
                        "quantity": _portfolio_progress_quantity(
                            approved_quantities[line_keys[key]], project_data["progress"]
                        ),
                        "uom": uom,
                        "remarks": f"Portfolio progress update for {section.lower()}.",
                    }
                )
        report = ensure(
            "Daily Site Report",
            f"RC-DEMO-DSR-{index:03d}",
            {
                "project": project_name,
                "boq_revision": boq.name if approved else None,
                "report_date": project_data["start"],
                "site_engineer": user,
                "status": "Draft",
                "notes": "Deterministic portfolio site report for dashboard and progress testing.",
            },
            {"progress": report_rows},
        )
        if approved and report_rows and index % 4 != 0:
            _submit_if_needed(report)
        counts["daily_reports"] += 1

        issue_status = ("Resolved", "In Progress", "Open")[index % 3]
        ensure(
            "Site Issue",
            f"RC-DEMO-SI-{index:03d}",
            {
                "project": project_name,
                "site_report": report.name,
                "issue_type": ("Safety", "Quality", "Material", "Access")[index % 4],
                "severity": ("Low", "Medium", "High", "Critical")[index % 4],
                "title": f"Portfolio site issue {index:03d}",
                "description": "Demo issue created to exercise construction controls and dashboard alerts.",
                "owner": user,
                "due_date": frappe.utils.add_days(project_data["start"], 21),
                "status": issue_status,
                "resolution": "Corrective action verified by the site team." if issue_status == "Resolved" else None,
            },
        )
        counts["site_issues"] += 1

        if approved and project_data["progress"] >= 20:
            certificate = ensure(
                "Progress Certificate",
                f"RC-DEMO-PC-{index:03d}",
                {
                    "project": project_name,
                    "boq": boq.name,
                    "baseline": baseline.name,
                    "certificate_no": 1,
                    "period_start": project_data["start"],
                    "period_end": project_data["end"],
                    "status": "Draft",
                    "retention_percent": 5,
                },
                {
                    "items": [
                        {
                            "boq_line_key": line_keys[key],
                            "description": description,
                            "current_qty": _portfolio_progress_quantity(
                                approved_quantities[line_keys[key]], project_data["progress"]
                            ),
                            "previous_certified_qty": 0,
                            "uom": uom,
                            "rate": rate,
                        }
                        for key, _, description, uom, quantity, rate in line_specs
                    ]
                },
            )
            if index % 5 == 0 and certificate.docstatus == 0 and certificate.status == "Draft":
                certificate.status = "Under Review"
                certificate.save(ignore_permissions=True)
            elif index % 5 != 0:
                _submit_if_needed(certificate)
            counts["progress_certificates"] += 1
    return counts


def _ensure_portfolio_material_requests(frappe, company, items, projects, warehouses):
    requests = []
    material_keys = ("cement", "sand", "aggregate")
    for project_data in projects:
        index = project_data["index"]
        warehouse = warehouses[(index - 1) % len(warehouses)]
        item_key = material_keys[(index - 1) % len(material_keys)]
        transaction_date, schedule_date = _demo_transaction_dates(
            frappe, project_data["start"], project_data["end"]
        )
        request = _ensure_dynamic_doc(
            frappe,
            "Material Request",
            f"RC-DEMO-MR-{index:03d}",
            {
                "material_request_type": "Purchase",
                "transaction_date": transaction_date,
                "schedule_date": schedule_date,
                "company": company,
                "set_warehouse": warehouse.name,
                "project": project_data["project"],
                "construction_project": project_data["project"],
                "replay_key": f"RC-DEMO-MR-{index:03d}",
            },
            "items",
            [
                {
                    "item_code": items[item_key].name,
                    "qty": 80 + index * 2,
                    "uom": items[item_key].stock_uom,
                    "schedule_date": schedule_date,
                    "warehouse": warehouse.name,
                    "project": project_data["project"],
                }
            ],
        )
        requests.append(request)
    return requests


def _ensure_portfolio_purchase_orders(
    frappe,
    company,
    currency,
    items,
    suppliers,
    projects,
    material_requests,
    warehouses,
):
    orders = []
    item_keys = ("cement", "sand", "aggregate")
    for project_data, material_request in zip(projects, material_requests):
        index = project_data["index"]
        warehouse = warehouses[(index - 1) % len(warehouses)]
        item_key = item_keys[(index - 1) % len(item_keys)]
        transaction_date, schedule_date = _demo_transaction_dates(
            frappe, project_data["start"], project_data["end"]
        )
        order = _ensure_dynamic_doc(
            frappe,
            "Purchase Order",
            f"RC-DEMO-PO-{index:03d}",
            {
                "supplier": suppliers[(index - 1) % len(suppliers)].name,
                "company": company,
                "currency": currency,
                "transaction_date": transaction_date,
                "schedule_date": schedule_date,
                "set_warehouse": warehouse.name,
                "project": project_data["project"],
                "construction_project": project_data["project"],
                "buying_price_list": _first_optional(frappe, "Price List", "Standard Buying"),
            },
            "items",
            [
                {
                    "item_code": items[item_key].name,
                    "qty": 80 + index * 2,
                    "rate": 100 + index * 3,
                    "schedule_date": schedule_date,
                    "warehouse": warehouse.name,
                    "project": project_data["project"],
                    "material_request": material_request.name,
                }
            ],
        )
        orders.append(order)
    return orders


def _first_optional(frappe, doctype, preferred):
    if frappe.db.exists(doctype, preferred):
        return preferred
    values = frappe.get_all(doctype, pluck="name", order_by="creation asc", limit=1)
    return values[0] if values else None


def _ensure_tasks(frappe, project, company, dates, ensure):
    specs = [("task_excavation", "Excavation and foundation preparation", dates["start"], dates["start_2"]), ("task_concrete", "Structural concrete works", dates["start_2"], dates["progress"]), ("task_masonry", "Masonry works", dates["progress"], dates["end"]), ("task_finishing", "Finishing works and handover", dates["progress"], dates["end"]) ]
    result = {}
    for key, subject, start, end in specs:
        result[key] = ensure("Task", DEMO_NAMES[key], {"subject": subject, "status": "Open", "project": project.name, "company": company, "exp_start_date": start, "exp_end_date": end, "priority": "Medium"})
    return result


def _ensure_baseline(frappe, project, boq, sales_order, assemblies, tasks, dates, line_keys, ensure):
    values = {"project": project.name, "boq_revision": boq.name, "sales_order": sales_order.name, "baseline_version": 1, "status": "Draft"}
    work_packages = [
        {"work_package": "Earthwork", "assembly": assemblies["excavation"].name, "task": tasks["task_excavation"].name, "boq_line_key": line_keys["excavation"], "planned_start": dates["start"], "planned_end": dates["start_2"], "planned_qty": 650, "uom": "m3", "planned_cost": 292500, "planned_value": 292500, "milestone": 0},
        {"work_package": "Concrete Works", "assembly": assemblies["concrete"].name, "task": tasks["task_concrete"].name, "boq_line_key": line_keys["concrete"], "planned_start": dates["start_2"], "planned_end": dates["progress"], "planned_qty": 120, "uom": "m3", "planned_cost": 960000, "planned_value": 1140480, "depends_on": "Earthwork", "milestone": 1},
        {"work_package": "Masonry Works", "assembly": assemblies["masonry"].name, "task": tasks["task_masonry"].name, "boq_line_key": line_keys["masonry"], "planned_start": dates["progress"], "planned_end": dates["end"], "planned_qty": 420, "uom": "m2", "planned_cost": 441000, "planned_value": 506100, "depends_on": "Concrete Works", "milestone": 0},
        {"work_package": "Finishing Works", "assembly": assemblies["finishing"].name, "task": tasks["task_finishing"].name, "boq_line_key": line_keys["finishing"], "planned_start": dates["progress"], "planned_end": dates["end"], "planned_qty": 200, "uom": "m2", "planned_cost": 220000, "planned_value": 247632, "depends_on": "Masonry Works", "milestone": 1},
    ]
    return ensure("Project Baseline", DEMO_NAMES["baseline"], values, {"work_packages": work_packages})


def _ensure_material_preview(frappe, baseline, assemblies, ensure):
    if frappe.db.exists("Material Requirement Preview", DEMO_NAMES["material_preview"]):
        return frappe.get_doc("Material Requirement Preview", DEMO_NAMES["material_preview"])

    from reckon_constructions.constructions.site import build_material_requirement_preview

    construction_project = frappe.get_doc("Project", baseline.project)
    assembly_data = {
        row.assembly: frappe.get_doc("Construction Assembly", row.assembly).as_dict()
        for row in baseline.get("work_packages") or []
        if row.assembly
    }
    requirements = build_material_requirement_preview(
        [row.as_dict() for row in baseline.get("work_packages") or []],
        assembly_data,
        {},
    )
    return ensure(
        "Material Requirement Preview",
        DEMO_NAMES["material_preview"],
        {
            "project": baseline.project,
            "baseline": baseline.name,
            "company": construction_project.company,
            "as_of_date": frappe.utils.nowdate(),
            "source_replay_key": "RC-DEMO-MATERIAL-PREVIEW",
            "status": "Draft",
        },
        {
            "requirements": [
                {
                    "item": requirement["item"],
                    "uom": requirement["uom"],
                    "required_qty": requirement["required_qty"],
                    "already_requested_qty": requirement["already_requested_qty"],
                    "outstanding_qty": requirement["outstanding_qty"],
                    "source_work_package": (requirement.get("sources") or [{}])[0].get("work_package"),
                    "source_boq_line_key": (requirement.get("sources") or [{}])[0].get("boq_line_key"),
                    "source_assembly": (requirement.get("sources") or [{}])[0].get("assembly"),
                }
                for requirement in requirements
            ]
        },
    )


def _ensure_material_request(frappe, preview, project, ensure):
    field = "material_requirement_preview" if frappe.get_meta("Material Request").has_field("material_requirement_preview") else None
    existing = frappe.db.get_value("Material Request", {field: preview.name, "docstatus": ["<", 2]}, "name") if field else None
    if existing:
        return frappe.get_doc("Material Request", existing)
    from reckon_constructions.constructions.integrations.site_procurement import create_material_request_from_preview

    del project, ensure
    return frappe.get_doc("Material Request", create_material_request_from_preview(preview.name, "RC-DEMO-MATERIAL-REQUEST"))


def _ensure_invoice(frappe, certificate, ensure):
    field = "progress_certificate" if frappe.get_meta("Sales Invoice").has_field("progress_certificate") else None
    existing = frappe.db.get_value("Sales Invoice", {field: certificate.name, "docstatus": ["<", 2]}, "name") if field else None
    if existing:
        return frappe.get_doc("Sales Invoice", existing)
    from reckon_constructions.constructions.integrations.commercial import create_sales_invoice_proposal

    del ensure
    return frappe.get_doc("Sales Invoice", create_sales_invoice_proposal(certificate.name))


def _demo_dates(frappe):
    now = frappe.utils.nowdate()
    return {
        "start": now,
        "start_2": frappe.utils.add_days(now, 14),
        "progress": frappe.utils.add_days(now, 45),
        "end": frappe.utils.add_days(now, 120),
        "rfi_due": frappe.utils.add_days(now, 7),
    }


def _demo_transaction_dates(frappe, project_start, project_end):
    """Keep ERPNext transactions inside the company's active fiscal year."""
    today = frappe.utils.nowdate()
    schedule_date = (
        project_end
        if frappe.utils.getdate(project_end) >= frappe.utils.getdate(today)
        else today
    )
    return today, schedule_date


def _portfolio_progress_quantity(approved_quantity, progress):
    """Keep generated progress within the BOQ quantity after field normalization."""
    approved_quantity = float(approved_quantity or 0)
    progress = float(progress or 0)
    if progress >= 100:
        return approved_quantity
    return min(approved_quantity, round(approved_quantity * progress / 100, 3))


def _find_demo_targets(frappe):
    targets = {doctype: [] for doctype in demo_plan()["custom_doctypes"] + demo_plan()["erpnext_doctypes"]}
    exact = {
        "Customer": [DEMO_NAMES["customer"]],
        "Project": [DEMO_NAMES["project"]],
        "Sales Order": [DEMO_NAMES["sales_order"]],
        "Construction BOQ": [DEMO_NAMES["boq"]],
        "Calculation Template": [DEMO_NAMES[key] for key in ("calculation_volume", "calculation_area", "calculation_count", "calculation_factor")],
        "Construction Assembly": [DEMO_NAMES[key] for key in ("assembly_excavation", "assembly_concrete", "assembly_masonry", "assembly_finishing")],
        "Rate Analysis": [DEMO_NAMES[key] for key in ("rate_excavation", "rate_concrete", "rate_masonry", "rate_finishing")],
        "Measurement Sheet": [DEMO_NAMES[key] for key in ("measurement_excavation", "measurement_concrete", "measurement_masonry", "measurement_finishing")],
        "Project Baseline": [DEMO_NAMES["baseline"]],
        "Task": [DEMO_NAMES[key] for key in ("task_excavation", "task_concrete", "task_masonry", "task_finishing")],
        "Engineering Document": [DEMO_NAMES["engineering"]],
        "Request For Information": [DEMO_NAMES["rfi"]],
        "Daily Site Report": [DEMO_NAMES["daily_report"]],
        "Site Issue": [DEMO_NAMES["site_issue"]],
        "Material Requirement Preview": [DEMO_NAMES["material_preview"]],
        "Variation Order": [DEMO_NAMES["variation"]],
        "Progress Certificate": [DEMO_NAMES["certificate"]],
        "Item": list(ITEM_NAMES.values()),
    }
    for doctype, names in exact.items():
        targets[doctype] = [name for name in names if frappe.db.exists(doctype, name)]
    legacy_boq_name = "BOQ-.YYYY.-.#####"
    if (
        frappe.db.exists("Construction BOQ", legacy_boq_name)
        and frappe.db.get_value("Construction BOQ", legacy_boq_name, "project") == DEMO_NAMES["project"]
    ):
        targets["Construction BOQ"].append(legacy_boq_name)
    for doctype, pattern in (
        ("Customer", "RC-DEMO-CUSTOMER-%"),
        ("Project", "RC-DEMO-PROJECT-%"),
        ("Task", "RC-DEMO-TASK-%"),
        ("Sales Order", "RC-DEMO-SO-PORT-%"),
        ("Construction BOQ", "RC-DEMO-BOQ-%"),
        ("Project Baseline", "RC-DEMO-PB-%"),
        ("Daily Site Report", "RC-DEMO-DSR-%"),
        ("Site Issue", "RC-DEMO-SI-%"),
        ("Progress Certificate", "RC-DEMO-PC-%"),
        ("Material Request", "RC-DEMO-MR-%"),
        ("Purchase Order", "RC-DEMO-PO-%"),
        ("Warehouse", "RC Demo Warehouse %"),
        ("Supplier", "RC-DEMO-SUPPLIER-%"),
    ):
        generated = frappe.get_all(doctype, filters={"name": ["like", pattern]}, pluck="name")
        targets[doctype] = sorted(set(targets[doctype] + generated))
    for doctype, field, value in (
        ("Quotation", "construction_boq", DEMO_NAMES["boq"]),
        ("Material Request", "material_requirement_preview", DEMO_NAMES["material_preview"]),
        ("Sales Invoice", "progress_certificate", DEMO_NAMES["certificate"]),
    ):
        if frappe.get_meta(doctype).has_field(field):
            targets[doctype] = frappe.get_all(doctype, filters={field: value}, pluck="name")
    return targets


def _delete_doc(frappe, doctype, name):
    if not frappe.db.exists(doctype, name):
        return False
    doc = frappe.get_doc(doctype, name)
    if doc.docstatus == 1:
        doc.cancel()
    frappe.delete_doc(doctype, name, force=True, ignore_permissions=True, ignore_missing=True)
    return True
