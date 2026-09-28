import json

try:
    import frappe
except ImportError:
    frappe = None


def _whitelist(function):
    return frappe.whitelist()(function) if frappe else function


BOQ_IMPORT_COLUMNS = ("line_key", "section", "item_code", "description", "quantity", "uom", "rate")


def validate_boq_import_rows(rows):
    errors = []
    normalized = []
    seen_line_keys = set()
    for row_number, raw_row in enumerate(rows or [], start=2):
        row = {column: raw_row.get(column) for column in BOQ_IMPORT_COLUMNS}
        line_key = str(row.get("line_key") or "").strip()
        if not line_key:
            errors.append({"row": row_number, "field": "line_key", "message": "Line key is required."})
        elif line_key in seen_line_keys:
            errors.append({"row": row_number, "field": "line_key", "message": f"Duplicate line key {line_key}."})
        seen_line_keys.add(line_key)

        for fieldname in ("quantity", "rate"):
            try:
                value = float(row.get(fieldname) or 0)
            except (TypeError, ValueError):
                errors.append({"row": row_number, "field": fieldname, "message": "Must be numeric."})
                continue
            if value < 0:
                errors.append({"row": row_number, "field": fieldname, "message": "Cannot be negative."})
            row[fieldname] = value
        normalized.append(row)

    return {"valid": not errors, "errors": errors, "rows": normalized}


@_whitelist
def export_boq_rows(boq):
    if frappe is None:
        raise RuntimeError("Frappe is required for BOQ export.")

    boq_doc = frappe.get_doc("Construction BOQ", boq)
    boq_doc.check_permission("read")
    return {
        "columns": list(BOQ_IMPORT_COLUMNS),
        "rows": [
            {column: row.get(column) for column in BOQ_IMPORT_COLUMNS}
            for row in boq_doc.get("items") or []
        ],
    }


@_whitelist
def import_boq_rows(boq, rows):
    if frappe is None:
        raise RuntimeError("Frappe is required for BOQ import.")

    boq_doc = frappe.get_doc("Construction BOQ", boq)
    boq_doc.check_permission("write")
    if boq_doc.docstatus == 1 or boq_doc.status == "Approved":
        frappe.throw("Approved BOQ revisions are immutable. Create a new revision instead.")
    if isinstance(rows, str):
        rows = json.loads(rows)

    result = validate_boq_import_rows(rows)
    if not result["valid"]:
        frappe.throw(json.dumps(result["errors"]))

    boq_doc.set("items", [])
    for row in result["rows"]:
        boq_doc.append("items", row)
    boq_doc.save()
    return {"boq": boq_doc.name, "imported": len(result["rows"]), "errors": []}
