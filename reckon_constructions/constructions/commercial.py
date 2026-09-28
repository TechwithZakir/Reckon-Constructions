def calculate_variation_totals(items, approved_scope=None):
    """Calculate prospective variation values without mutating the approved scope."""
    approved_scope = approved_scope or {}
    totals = []
    seen_line_keys = set()
    net_amount = 0
    for item in items or []:
        line_key = item.get("boq_line_key")
        quantity_delta = float(item.get("quantity_delta") or 0)
        rate = float(item.get("rate") or 0)
        if not line_key:
            raise ValueError("Every variation item requires a BOQ line key.")
        if line_key in seen_line_keys:
            raise ValueError(f"Duplicate variation line key {line_key}.")
        seen_line_keys.add(line_key)
        if rate < 0:
            raise ValueError(f"Variation rate for {line_key} cannot be negative.")
        if line_key in approved_scope:
            new_quantity = float(approved_scope[line_key] or 0) + quantity_delta
            if new_quantity < 0:
                raise ValueError(f"Variation would make {line_key} quantity negative.")
        amount = quantity_delta * rate
        totals.append(
            {
                "boq_line_key": line_key,
                "quantity_delta": quantity_delta,
                "rate": rate,
                "amount": amount,
            }
        )
        net_amount += amount
    return {"items": totals, "net_amount": net_amount}


def calculate_certificate_totals(lines, retention_percent=0):
    """Calculate gross, retention, and net certificate values from frozen lines."""
    retention_percent = float(retention_percent or 0)
    if not 0 <= retention_percent <= 100:
        raise ValueError("Retention percent must be between 0 and 100.")

    gross_value = 0
    for line in lines or []:
        quantity = float(line.get("this_period_qty") or 0)
        rate = float(line.get("rate") or 0)
        if quantity < 0 or rate < 0:
            raise ValueError("Certificate quantities and rates cannot be negative.")
        gross_value += quantity * rate

    retention_amount = gross_value * retention_percent / 100
    return {
        "gross_value": gross_value,
        "retention_amount": retention_amount,
        "net_value": gross_value - retention_amount,
    }
