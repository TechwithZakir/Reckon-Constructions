# Reckon Constructions Implementation Plan

This plan converts the supplied project prompts into repository milestones. Each milestone should
remain independently testable and should avoid assumptions that belong to the target company setup.

## Stage 0 - Audit

- Capture installed Frappe, ERPNext, CRM and HRMS versions.
- Verify standard DocType fields for Project, Task, Quotation, Sales Order, Material Request,
  Timesheet, Stock Entry and Sales Invoice.
- Record company-specific commercial decisions before implementing approvals or billing.

Exit condition: `docs/bench_audit.md` is completed for the target bench.

## Stage 1 - Foundation

- Installable app package `reckon_constructions`.
- Module and Desk workspace named `Constructions`.
- Hooks, fixtures, role strategy and project documentation.
- Construction Settings singleton for default company, precision, commercial controls and feature flags.
- Construction Project profile linked uniquely to ERPNext Project with project/company/customer boundary checks.
- No core patches and no optional app hard dependency.

Exit condition: clean install, migrate and workspace visibility on a v16 site.

## Stage 2 - Estimation

- Construction Settings.
- Construction Project profile linked uniquely to ERPNext Project.
- BOQ, sections and items with stable line keys, calculated totals and immutable approved revisions.
- Measurement calculator with safe formulas, declared variables, signed rows and deterministic tests.
- Rate analysis and assemblies with component quantities, wastage, overhead, markup and accepted-rate snapshots.

Exit condition: approved BOQ revision is reproducible after source rates change.

## Stage 3 - Sales And Award

- Approved BOQ to draft ERPNext Quotation.
- Accepted Sales Order to linked or created ERPNext Project.
- Idempotent creation using source keys and company/customer validation.

Exit condition: retries do not create duplicate Quotations, Projects or Construction Project profiles.

## Stage 4 - Planning

- Project Baseline and Work Package mapping.
- ERPNext Task creation or linking with dates, dependencies and BOQ quantities.
- Cycle and date validation.

Exit condition: baseline scope, schedule and ownership are traceable from the project workspace.

## Stage 5 - Site And Procurement

- Daily Site Report, verified progress and site issue records.
- Material requirement preview from approved assemblies.
- Draft Material Request generation with duplicate demand deduction.

Exit condition: verified quantity and procurement demand reconcile to approved scope.

## Stage 6 - Commercial And Documents

- Engineering document register and RFI.
- Variation Order with prospective baseline effect.
- Progress Certificate and draft Sales Invoice proposal through ERPNext.

Exit condition: changes and billing are auditable without mutating previous approved snapshots.

## Stage 7 - Release

- Dashboards and reports for revisions, progress, cost, commitments, actuals, margin and approvals.
- Import and export with row-level errors and rollback behavior.
- Fresh install, upgrade, permissions and UAT documentation.

Exit condition: release checks pass on the target v16 bench.
