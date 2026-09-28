import frappe


def execute(filters=None):
    columns = [
        {"label": "Record Type", "fieldname": "record_type", "fieldtype": "Data", "width": 180},
        {"label": "Record", "fieldname": "record", "fieldtype": "Dynamic Link", "options": "record_type", "width": 180},
        {"label": "Project", "fieldname": "project", "fieldtype": "Link", "options": "Construction Project", "width": 180},
        {"label": "Status", "fieldname": "status", "fieldtype": "Data", "width": 120},
        {"label": "Value", "fieldname": "value", "fieldtype": "Currency", "width": 130},
        {"label": "Modified", "fieldname": "modified", "fieldtype": "Datetime", "width": 160},
    ]
    data = []
    pending_records = (
        ("Construction BOQ", "BOQ", "total_amount"),
        ("Variation Order", "Variation Order", "net_amount"),
        ("Progress Certificate", "Progress Certificate", "net_value"),
    )
    for doctype, label, value_field in pending_records:
        records = frappe.get_all(
            doctype,
            filters={"status": ["in", ["Draft", "Under Review"]], "docstatus": ["<", 2]},
            fields=["name", "project", "status", value_field, "modified"],
            order_by="modified desc",
        )
        for record in records:
            data.append(
                {
                    "record_type": label,
                    "record": record.name,
                    "project": record.project,
                    "status": record.status,
                    "value": record.get(value_field) or 0,
                    "modified": record.modified,
                }
            )
    return columns, data
