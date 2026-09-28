app_name = "reckon_constructions"
app_title = "Reckon Constructions"
app_publisher = "Reckon Technologies Ltd."
app_description = "Construction project management for Frappe and ERPNext"
app_email = "support@reckontechnologies.com"
app_license = "License pending confirmation"

required_apps = ["erpnext"]

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
        "dt": "Workspace Sidebar",
        "filters": [["name", "in", ["Constructions"]]],
    },
    {
        "dt": "Desktop Icon",
        "filters": [["name", "in", ["Constructions"]]],
    },
]

doc_events = {
    "Project": {
        "validate": "reckon_constructions.constructions.doctype.construction_project.construction_project.validate_linked_project_boundaries"
    }
}

website_context = {
    "favicon": "/assets/reckon_constructions/images/favicon.png",
    "splash_image": "/assets/reckon_constructions/images/favicon.png",
}
