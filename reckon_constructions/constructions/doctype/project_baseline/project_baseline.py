import frappe
from frappe.model.document import Document

from reckon_constructions.constructions.planning import has_dependency_cycle, validate_date_range


class ProjectBaseline(Document):
    def validate(self):
        self.validate_revision()
        self.validate_work_packages()
        self.calculate_totals()

    def before_submit(self):
        self.status = "Approved"
        self.calculate_totals()

    def on_cancel(self):
        self.status = "Cancelled"

    def validate_revision(self):
        if self.baseline_version is not None and self.baseline_version < 1:
            frappe.throw("Baseline Version must be 1 or greater.")
        if self.prior_baseline and self.prior_baseline == self.name:
            frappe.throw("Prior Baseline cannot reference the same baseline.")

    def validate_work_packages(self):
        edges = []
        for row in self.get("work_packages") or []:
            try:
                validate_date_range(row.planned_start, row.planned_end)
            except ValueError as error:
                frappe.throw(str(error))

            if row.depends_on:
                edges.append((row.depends_on, row.work_package))

        if has_dependency_cycle(edges):
            frappe.throw("Work Package dependencies cannot contain a cycle.")

    def calculate_totals(self):
        self.planned_cost = sum((row.planned_cost or 0) for row in self.get("work_packages") or [])
        self.planned_value = sum((row.planned_value or 0) for row in self.get("work_packages") or [])


class ProjectBaselineWorkPackage(Document):
    pass
