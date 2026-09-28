app_name = "reckon_constructions"
app_title = "Reckon Constructions"
app_publisher = "Reckon Technologies Ltd."
app_description = "Construction project management for Frappe and ERPNext"
app_email = "support@reckontechnologies.com"
app_license = "License pending confirmation"

required_apps = ["erpnext"]

doctype_list_js = {
    "Construction BOQ": "public/js/construction_boq_list.js",
}

doctype_js = {
    "Project": "public/js/construction_forms.js",
    "Construction BOQ": "public/js/construction_forms.js",
    "Rate Analysis": "public/js/construction_forms.js",
}

fixtures = [
    {
        "dt": "Workspace",
        "filters": [["name", "in", ["Constructions"]]],
    },
    {
        "dt": "Workflow",
        "filters": [["name", "in", [
            "Construction BOQ Approval",
            "Variation Order Approval",
            "Progress Certificate Approval",
        ]]],
    },
    {
        "dt": "Custom Field",
        "filters": [["name", "in", [
            "Project-construction_section",
            "Project-construction_status",
            "Project-construction_column_break_1",
            "Project-construction_currency",
            "Project-construction_commercial_section",
            "Project-construction_accepted_boq",
            "Project-construction_column_break_3",
            "Project-construction_contract_start_date",
            "Project-construction_column_break_4",
            "Project-construction_contract_end_date",
            "Project-construction_contract_value",
            "Project-construction_site_section",
            "Project-construction_site_name",
            "Project-construction_column_break_5",
            "Project-construction_site_address",
            "Quotation-construction_boq",
            "Quotation-replay_key",
            "Quotation Item-construction_boq",
            "Quotation Item-construction_boq_line_key",
            "Material Request-construction_project",
            "Material Request-construction_baseline",
            "Material Request-material_requirement_preview",
            "Material Request-replay_key",
            "Material Request Item-construction_baseline",
            "Material Request Item-construction_boq_line_key",
            "Sales Invoice-construction_project",
            "Sales Invoice-progress_certificate",
            "Sales Invoice Item-construction_project",
            "Sales Invoice Item-progress_certificate",
            "Sales Invoice Item-construction_boq_line_key",
        ]]],
    },
    {
        "dt": "DocType Layout",
        "filters": [["name", "in", ["Constructions Project Single Page"]]],
    },
]

doc_events = {
    "Project": {
        "validate": "reckon_constructions.constructions.project.validate_project_boundaries"
    }
}

never_skip_patches = [
    "reckon_constructions.migrations.migrate_construction_project",
    "reckon_constructions.migrations.replace_project_sales_order",
]

website_context = {
    "favicon": "/assets/reckon_constructions/images/favicon.png",
    "splash_image": "/assets/reckon_constructions/images/favicon.png",
}
