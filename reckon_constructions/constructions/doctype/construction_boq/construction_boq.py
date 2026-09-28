import frappe
from frappe.model.document import Document


APPROVED_STATUSES = {"Approved"}


class ConstructionBOQ(Document):
    def validate(self):
        self.set_missing_line_keys()
        self.validate_revision_links()
        self.validate_unique_line_keys()
        self.calculate_totals()

    def before_save(self):
        self.prevent_approved_mutation()

    def before_submit(self):
        self.status = "Approved"
        self.calculate_totals()

    def on_cancel(self):
        self.status = "Cancelled"

    def set_missing_line_keys(self):
        for idx, row in enumerate(self.get("items") or [], start=1):
            if not row.line_key:
                row.line_key = f"{self.name or 'NEW'}-{idx:04d}"

    def validate_revision_links(self):
        if self.revision_no is not None and self.revision_no < 1:
            frappe.throw("Revision No must be 1 or greater.")

        if self.prior_revision and self.prior_revision == self.name:
            frappe.throw("Prior Revision cannot reference the same BOQ.")

        if self.prior_revision:
            prior_project = frappe.db.get_value("Construction BOQ", self.prior_revision, "project")
            if prior_project and self.project and prior_project != self.project:
                frappe.throw("Prior Revision must belong to the same Construction Project.")

    def validate_unique_line_keys(self):
        seen = set()
        for row in self.get("items") or []:
            if not row.line_key:
                continue
            if row.line_key in seen:
                frappe.throw(f"Duplicate BOQ line key {row.line_key}.")
            seen.add(row.line_key)

    def calculate_totals(self):
        section_totals = {}
        grand_total = 0

        for row in self.get("items") or []:
            row.amount = (row.quantity or 0) * (row.rate or 0)
            grand_total += row.amount
            if row.section:
                section_totals[row.section] = section_totals.get(row.section, 0) + row.amount

        for section in self.get("sections") or []:
            section.amount = section_totals.get(section.section_name, 0)

        self.total_amount = grand_total

    def prevent_approved_mutation(self):
        if self.is_new():
            return

        previous = frappe.get_doc(self.doctype, self.name)
        if previous.docstatus != 1 and previous.status not in APPROVED_STATUSES:
            return

        protected_fields = ["project", "customer", "company", "currency", "revision_no", "prior_revision"]
        for fieldname in protected_fields:
            if self.get(fieldname) != previous.get(fieldname):
                frappe.throw("Approved BOQ revisions are immutable. Create a new revision instead.")

        if self.has_value_changed("items") or self.has_value_changed("sections"):
            frappe.throw("Approved BOQ revisions are immutable. Create a new revision instead.")


class ConstructionBOQSection(Document):
    pass


class ConstructionBOQItem(Document):
    pass
