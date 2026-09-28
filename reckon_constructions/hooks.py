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
    }
]

website_context = {
    "favicon": "/assets/reckon_constructions/images/favicon.png",
    "splash_image": "/assets/reckon_constructions/images/favicon.png",
}
