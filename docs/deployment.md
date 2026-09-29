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
bench --site <site> execute reckon_constructions.demo.seed_demo_data
```

The default seed creates 100 ERPNext Projects in total: one complete UAT project plus 99
portfolio projects. Portfolio projects contain four phase Tasks each, with staggered dates across
roughly one year and varied completion percentages and statuses. Use `project_count` to request a
different total. The command is idempotent. To rebuild the dataset, use `reset=true`. Before
deletion, preview the exact records that will be removed. A real clear requires `confirm=true`:

```bash
bench --site <site> execute reckon_constructions.demo.seed_demo_data --kwargs '{"reset": true}'
bench --site <site> execute reckon_constructions.demo.seed_demo_data --kwargs '{"project_count": 25}'
bench --site <site> execute reckon_constructions.demo.clear_demo_data --kwargs '{"dry_run": true}'
bench --site <site> execute reckon_constructions.demo.clear_demo_data --kwargs '{"confirm": true}'
```

Cleanup is limited to deterministic `RC-DEMO-*` records plus generated Quotation, Material Request,
and Sales Invoice records linked to the demo documents. It never removes the Company, Currency,
UOM, item groups, customer groups, territory, chart of accounts, or other non-demo accounting setup.

## Rollback

Stop workers, restore the last known-good site backup, and redeploy the matching application commit. Do not downgrade by editing DocType JSON directly on a live site. Re-run migration and the app test suite before reopening traffic.

## Release evidence

Record the deployed commit, bench and ERPNext versions, migration output, test output, backup reference, and UAT sign-off in the release ticket.
