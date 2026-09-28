import frappe


CONSTRUCTION_FIELDS = [
    {
        "fieldname": "construction_section",
        "label": "Construction Controls",
        "fieldtype": "Section Break",
        "insert_after": "actual_end_date",
        "collapsible": 1,
    },
    {
        "fieldname": "construction_status",
        "label": "Construction Status",
        "fieldtype": "Select",
        "options": "Draft\nActive\nOn Hold\nCompleted\nCancelled",
        "default": "Draft",
        "in_list_view": 1,
        "insert_after": "construction_section",
    },
    {"fieldname": "construction_column_break_1", "fieldtype": "Column Break", "insert_after": "construction_status"},
    {
        "fieldname": "construction_currency",
        "label": "Construction Currency",
        "fieldtype": "Link",
        "options": "Currency",
        "insert_after": "construction_column_break_1",
    },
    {
        "fieldname": "construction_commercial_section",
        "label": "Construction Commercial Baseline",
        "fieldtype": "Section Break",
        "insert_after": "construction_currency",
        "collapsible": 1,
    },
    {
        "fieldname": "construction_accepted_boq",
        "label": "Accepted BOQ",
        "fieldtype": "Data",
        "read_only": 1,
        "insert_after": "construction_commercial_section",
    },
    {"fieldname": "construction_column_break_3", "fieldtype": "Column Break", "insert_after": "construction_accepted_boq"},
    {
        "fieldname": "construction_contract_start_date",
        "label": "Contract Start Date",
        "fieldtype": "Date",
        "insert_after": "construction_column_break_3",
    },
    {"fieldname": "construction_column_break_4", "fieldtype": "Column Break", "insert_after": "construction_contract_start_date"},
    {
        "fieldname": "construction_contract_end_date",
        "label": "Contract End Date",
        "fieldtype": "Date",
        "insert_after": "construction_column_break_4",
    },
    {
        "fieldname": "construction_contract_value",
        "label": "Contract Value",
        "fieldtype": "Currency",
        "options": "construction_currency",
        "insert_after": "construction_contract_end_date",
    },
    {
        "fieldname": "construction_site_section",
        "label": "Construction Site",
        "fieldtype": "Section Break",
        "insert_after": "construction_contract_value",
        "collapsible": 1,
    },
    {
        "fieldname": "construction_site_name",
        "label": "Site Name",
        "fieldtype": "Data",
        "insert_after": "construction_site_section",
    },
    {"fieldname": "construction_column_break_5", "fieldtype": "Column Break", "insert_after": "construction_site_name"},
    {
        "fieldname": "construction_site_address",
        "label": "Site Address",
        "fieldtype": "Small Text",
        "insert_after": "construction_column_break_5",
    },
]


def execute():
    """Copy legacy construction-project values into ERPNext Project records."""
    if not frappe.db.exists("DocType", "Project"):
        return

    missing_fields = [
        field["fieldname"]
        for field in CONSTRUCTION_FIELDS
        if not frappe.get_meta("Project").has_field(field["fieldname"])
    ]
    if missing_fields:
        frappe.throw(
            "Project construction fields are not available yet: " + ", ".join(missing_fields)
        )

    if not frappe.db.exists("DocType", "Construction Project"):
        return

    for legacy in frappe.get_all(
        "Construction Project",
        fields=[
            "name",
            "project",
            "company",
            "customer",
            "currency",
            "sales_order",
            "accepted_boq",
            "contract_start_date",
            "contract_end_date",
            "contract_value",
            "site_name",
            "site_address",
            "status",
        ],
        limit_page_length=0,
    ):
        project_name = legacy.project or legacy.name
        if not frappe.db.exists("Project", project_name):
            frappe.log_error(
                f"Could not migrate Construction Project {legacy.name}: Project {project_name} was not found.",
                "Reckon Constructions project migration",
            )
            continue

        values = {
            "construction_status": legacy.status or "Draft",
            "construction_currency": legacy.currency,
            "sales_order": legacy.sales_order,
            "construction_accepted_boq": legacy.accepted_boq,
            "construction_contract_start_date": legacy.contract_start_date,
            "construction_contract_end_date": legacy.contract_end_date,
            "construction_contract_value": legacy.contract_value,
            "construction_site_name": legacy.site_name,
            "construction_site_address": legacy.site_address,
        }
        if legacy.company and not frappe.db.get_value("Project", project_name, "company"):
            values["company"] = legacy.company
        if legacy.customer and not frappe.db.get_value("Project", project_name, "customer"):
            values["customer"] = legacy.customer
        frappe.db.set_value("Project", project_name, values, update_modified=False)
