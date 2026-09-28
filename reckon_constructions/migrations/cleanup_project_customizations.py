import frappe


def delete_customization(doctype, filters):
    name = frappe.db.get_value(doctype, filters, "name")
    if name:
        frappe.delete_doc(doctype, name, force=True)


def before_uninstall():
    """Remove app-owned customizations from standard ERPNext doctypes."""
    for custom_field in frappe.get_all(
        "Custom Field",
        filters={"module": "Constructions"},
        pluck="name",
    ):
        frappe.delete_doc("Custom Field", custom_field, force=True)

    for custom_field in frappe.get_all(
        "Custom Field",
        filters={"dt": "Project", "fieldname": ["like", "construction_%"]},
        pluck="name",
    ):
        frappe.delete_doc("Custom Field", custom_field, force=True)

    for property_setter in frappe.get_all(
        "Property Setter",
        filters={"module": "Constructions"},
        pluck="name",
    ):
        frappe.delete_doc("Property Setter", property_setter, force=True)

    for layout in frappe.get_all(
        "DocType Layout",
        filters={"module": "Constructions"},
        pluck="name",
    ):
        frappe.delete_doc("DocType Layout", layout, force=True)

    delete_customization(
        "Custom Field",
        {"dt": "Project", "fieldname": "construction_sales_order"},
    )
    delete_customization(
        "Custom Field",
        {"dt": "Project", "fieldname": "construction_column_break_2"},
    )
    delete_customization("Property Setter", {"name": "Project-field_order"})
    delete_customization("DocType Layout", {"name": "Constructions Project Single Page"})

    frappe.clear_cache(doctype="Project")
