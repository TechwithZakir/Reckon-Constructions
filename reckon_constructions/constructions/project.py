import frappe


def validate_project_boundaries(doc, method=None):
    del method
    sales_order_name = doc.get("construction_sales_order")
    if sales_order_name:
        sales_order = frappe.db.get_value(
            "Sales Order",
            sales_order_name,
            ["company", "customer", "currency"],
            as_dict=True,
        )
        if not sales_order:
            frappe.throw(f"Sales Order {doc.construction_sales_order} was not found.")
        validate_same_value("Company", doc.company, sales_order.company)
        validate_same_value("Customer", doc.customer, sales_order.customer)
        validate_same_value("Construction Currency", doc.construction_currency, sales_order.currency)

    contract_start = doc.get("construction_contract_start_date")
    contract_end = doc.get("construction_contract_end_date")
    if contract_start and contract_end:
        if contract_end < contract_start:
            frappe.throw("Contract End Date cannot be before Contract Start Date.")


def validate_same_value(label, local_value, source_value):
    if local_value and source_value and local_value != source_value:
        frappe.throw(f"{label} must match the linked ERPNext document.")
