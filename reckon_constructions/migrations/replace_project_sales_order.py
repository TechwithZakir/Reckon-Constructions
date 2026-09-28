import frappe


def execute():
    """Move values from the retired Project construction sales-order field."""
    if not frappe.db.exists("DocType", "Project"):
        return

    meta = frappe.get_meta("Project")
    if not meta.has_field("construction_sales_order"):
        return
    if not meta.has_field("sales_order"):
        frappe.throw("ERPNext Project.sales_order is required for the construction app.")

    for project in frappe.get_all(
        "Project",
        fields=["name", "construction_sales_order", "sales_order"],
        limit_page_length=0,
    ):
        if project.construction_sales_order and not project.sales_order:
            frappe.db.set_value(
                "Project",
                project.name,
                "sales_order",
                project.construction_sales_order,
                update_modified=False,
            )

    for fieldname in ("construction_sales_order", "construction_column_break_2"):
        custom_field = frappe.db.get_value(
            "Custom Field",
            {"dt": "Project", "fieldname": fieldname},
            "name",
        )
        if custom_field:
            frappe.delete_doc("Custom Field", custom_field, force=True)

    frappe.clear_cache(doctype="Project")
