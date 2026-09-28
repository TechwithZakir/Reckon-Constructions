# Reckon Constructions Bench Audit

This audit is the required first implementation step before production schema work. The supplied
design documents are planning inputs; the installed Frappe and ERPNext v16 code remains the final
authority for exact fields, workflows and APIs.

## Product Identity

| Concern | Decision |
| --- | --- |
| App and Python package | `reckon_constructions` |
| Visible module and workspace | `Constructions` |
| Product name | Reckon Constructions |
| Owner | Reckon Technologies Ltd. |
| Core stance | No Frappe or ERPNext core patches |

## Target Bench Inventory

Record these values on the development bench before adding DocTypes:

| Item | Command or source | Result |
| --- | --- | --- |
| Frappe version | `bench version` | Pending |
| ERPNext version | `bench version` | Pending |
| Installed apps | `bench --site <site> list-apps` | Pending |
| Optional CRM installed | `bench --site <site> list-apps` | Pending |
| Optional HRMS installed | `bench --site <site> list-apps` | Pending |
| Worker and scheduler status | `bench doctor` | Pending |

## ERPNext Field Map To Verify

| ERPNext record | Fields and behavior to inspect |
| --- | --- |
| Project | Company, customer, expected dates, status, costing fields, permission behavior |
| Task | Project link, dependencies, assignments, expected dates, progress fields |
| Quotation | Customer, company, currency, taxes, item rows, source reference fields |
| Sales Order | Project link support, customer/company/currency, amendment and cancellation constraints |
| Item and UOM | Stock/service distinction, conversion factors, disabled status |
| Material Request | Project link field, schedule date, warehouse fields, item row custom reference strategy |
| Timesheet | Project and Task links, costing behavior |
| Stock Entry | Project dimension support and valuation behavior |
| Sales Invoice | Sales Order mapping, project field support, tax and retention assumptions |

## Gap Map

| Domain | Standard ERPNext authority | Construction extension |
| --- | --- | --- |
| Sales | Customer, Opportunity, Quotation, Sales Order | Tender context, BOQ source mapping and accepted estimate reference |
| Projects | Project, Task, Timesheet | Construction Project profile, baseline, work package and progress quantity rules |
| Estimating | Item, UOM, price lists where applicable | BOQ revisions, sections, line keys, measurement calculator and rate analysis |
| Procurement | Material Request, RFQ, Purchase Order, Stock Entry | Requirement preview, source traceability and duplicate demand protection |
| Commercial | Sales Invoice, Payment Entry, GL Entry | Variation Order and Progress Certificate proposals |
| Documents | File, Comment, Version, Assignment | Engineering document register and RFI workflow |

## Open Decisions

- License terms for repository metadata and distribution.
- Whether one Sales Order may govern multiple ERPNext Projects.
- Whether one BOQ may include multiple customer currencies.
- Approval thresholds for BOQ, baseline, variation and certificate workflows.
- Retention, holdback, advance recovery and tax handling.
- Site warehouse structure and subcontracting workflow.
- Whether Frappe CRM and HRMS are required in the first deployment.

## Implementation Order

1. Confirm bench inventory and standard DocType field map.
2. Keep the `Constructions` workspace available with standard links.
3. Review the initial Construction Settings and Construction Project fields against the target bench.
4. Review the initial BOQ, section and item model against company estimating requirements.
5. Review the measurement template grammar, UOM policy and BOQ quantity update rule.
6. Review rate component kinds, UOM conversion policy, overhead and markup approval policy.
7. Verify ERPNext Quotation and Sales Order custom field strategy for BOQ source references.
8. Verify ERPNext Task dependency fields before automated Task creation is enabled.
9. Add remaining ERPNext integrations only after target document requirements are verified.
