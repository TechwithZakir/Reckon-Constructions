def build_quotation_description(row):
    parts = []
    if row.line_key:
        parts.append(f"BOQ Line: {row.line_key}")
    if row.description:
        parts.append(row.description)
    return "\n".join(parts) or row.item_code
