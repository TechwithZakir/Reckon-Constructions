# Deployment Runbook

## First install

```bash
bench get-app /path/to/Reckon-Constructions
bench --site <site> install-app reckon_constructions
bench --site <site> migrate
bench build
bench restart
```

Verify `bench version`, confirm ERPNext v16 is installed, and take a site backup before migration.

## Upgrade

```bash
git fetch origin
git checkout main
git pull --ff-only origin main
bench --site <site> migrate
bench build
bench restart
bench --site <site> run-tests --app reckon_constructions
```

Review workflow fixtures and role permissions after migration. Approved construction documents must remain immutable.
The app also installs traceability Custom Fields on standard Quotation, Material Request, and Sales Invoice records so integration retries remain idempotent.

## Demo seed and cleanup

Run the complete UAT dataset only on a development or test site with an existing Company:

```bash
bench --site <site> execute reckon_constructions.demo.seed_demo_data --kwargs "{'dry_run': True}"
```

The dry-run command is the safe default and writes nothing. The full seed creates 100 ERPNext Projects in total: one complete UAT project plus 99
portfolio projects. It also creates 30 Customers distributed across the projects, 8 demo Suppliers,
6 warehouse locations, project-linked Sales Orders, material requests, and draft Purchase Orders.
Each portfolio project receives four phase Tasks, a BOQ and baseline, a Daily Site Report, a Site
Issue, and, where progress is far enough along, a Progress Certificate. BOQ, baseline, report, and
certificate records intentionally span draft, review, and approved states so the construction
approval workflows and Project Dashboard can be demonstrated across a realistic portfolio.
Dates are staggered across roughly one year and completion percentages vary. Use `project_count` to
request a different total. The command is idempotent. To rebuild the dataset, use `reset=True`
with `dry_run=False` and `confirm_demo_site=True`. Before deletion, preview the exact records
that will be removed. A real clear requires `confirm_demo_site=True`:

```bash
bench --site <site> execute reckon_constructions.demo.seed_demo_data --kwargs "{'project_count': 25, 'dry_run': True}"
bench --site <site> execute reckon_constructions.demo.seed_demo_data --kwargs "{'reset': True, 'dry_run': False, 'confirm_demo_site': True}"
bench --site <site> execute reckon_constructions.demo.clear_demo_data --kwargs "{'dry_run': True}"
bench --site <site> execute reckon_constructions.demo.clear_demo_data --kwargs "{'dry_run': False, 'confirm_demo_site': True}"
```

Cleanup is limited to deterministic `RC-DEMO-*` records plus generated demo Suppliers, Warehouses,
Quotation, Material Request, Purchase Order, and Sales Invoice records. It never removes existing
Company, Currency, UOM, item groups, customer groups, territory, chart of accounts, or warehouses
that were already present before the seed.

## Rollback

Stop workers, restore the last known-good site backup, and redeploy the matching application commit. Do not downgrade by editing DocType JSON directly on a live site. Re-run migration and the app test suite before reopening traffic.

## Release evidence

Record the deployed commit, bench and ERPNext versions, migration output, test output, backup reference, and UAT sign-off in the release ticket.
