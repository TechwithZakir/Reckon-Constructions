from collections import defaultdict


def summarize_progress(rows, approved_scope=None):
    """Validate report quantities and return per-line progress totals."""
    approved_scope = approved_scope or {}
    totals = defaultdict(float)
    for row in rows or []:
        line_key = row.get("boq_line_key")
        quantity = float(row.get("quantity") or 0)
        if not line_key:
            raise ValueError("Every progress row requires a BOQ line key.")
        if quantity < 0:
            raise ValueError(f"Progress quantity for {line_key} cannot be negative.")
        if approved_scope and line_key not in approved_scope:
            raise ValueError(f"Progress line {line_key} is outside the approved BOQ scope.")
        totals[line_key] += quantity

    if approved_scope:
        for line_key, quantity in totals.items():
            allowed = float(approved_scope[line_key] or 0)
            if quantity > allowed:
                raise ValueError(
                    f"Progress quantity for {line_key} cannot exceed approved quantity {allowed:g}."
                )

    return [
        {
            "boq_line_key": line_key,
            "quantity": quantity,
            "percent_complete": (
                quantity / float(approved_scope[line_key]) * 100
                if approved_scope and approved_scope[line_key]
                else None
            ),
        }
        for line_key, quantity in sorted(totals.items())
    ]


def build_material_requirement_preview(work_packages, assemblies, already_requested=None):
    """Expand approved work packages into material demand and deduct prior demand."""
    already_requested = already_requested or {}
    totals = defaultdict(float)
    sources = defaultdict(list)

    for work_package in work_packages or []:
        planned_qty = float(work_package.get("planned_qty") or 0)
        if planned_qty <= 0:
            continue
        assembly_name = work_package.get("assembly")
        assembly = assemblies.get(assembly_name) if isinstance(assemblies, dict) else None
        if not assembly:
            continue

        for component in assembly.get("components") or []:
            if component.get("component_kind") != "Material" or not component.get("item"):
                continue
            item = component["item"]
            uom = component.get("uom") or ""
            factor = float(component.get("quantity_factor") or 0)
            wastage = float(component.get("wastage_percent") or 0)
            quantity = planned_qty * factor * (1 + wastage / 100)
            key = (item, uom)
            totals[key] += quantity
            sources[key].append(
                {
                    "work_package": work_package.get("work_package"),
                    "boq_line_key": work_package.get("boq_line_key"),
                    "assembly": assembly_name,
                }
            )

    result = []
    for (item, uom), required_qty in sorted(totals.items()):
        requested_qty = float(already_requested.get((item, uom), 0) or 0)
        result.append(
            {
                "item": item,
                "uom": uom,
                "required_qty": required_qty,
                "already_requested_qty": requested_qty,
                "outstanding_qty": max(required_qty - requested_qty, 0),
                "sources": sources[(item, uom)],
            }
        )
    return result
