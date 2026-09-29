# Reckon Constructions

Reckon Constructions is a Frappe and ERPNext v16 app for construction project management.
The installable app and Python package are `reckon_constructions`; the visible Desk module
and workspace are `Constructions`.

Copyright (c) Reckon Technologies Ltd.

## Scope

The app connects estimating, BOQ revisions, measurements, rate analysis, ERPNext sales,
ERPNext projects, procurement, site execution, variations, certificates, billing support
and project controls while keeping ERPNext standard transactions authoritative.

Initial development follows the supplied implementation sequence:

1. Audit the target bench and ERPNext v16 fields before schema work.
2. Scaffold the app identity, workspace, hooks and documentation.
3. Add construction DocTypes only where standard ERPNext does not cover the behavior.
4. Build deterministic, auditable calculations before any AI-assisted features.

## Supported Platform

- Frappe Framework v16
- ERPNext v16
- Optional guarded integrations: Frappe CRM and HRMS

No Frappe or ERPNext core files should be patched.

## Development Install

From a bench that already has Frappe and ERPNext v16 installed:

```bash
bench get-app https://github.com/TechwithZakir/Reckon-Constructions.git
bench --site your-site.local install-app reckon_constructions
bench --site your-site.local migrate
bench build
```

## Verification

Use these checks before sending a change for review:

```bash
python -m compileall -q reckon_constructions
python -m json.tool reckon_constructions/fixtures/workspace/constructions.json > /dev/null
```

On a real bench, also run the project test suite:

```bash
bench --site your-site.local run-tests --app reckon_constructions
```

## Demo Data

The app includes a deterministic demo dataset covering the BOQ-to-progress-certificate and
invoice-proposal flow, including ERPNext Customer, Item, Project, Quotation, Sales Order, Task,
Material Request and Sales Invoice records. It uses the first existing Company and does not
create or delete accounting setup.

```bash
bench --site your-site.local execute reckon_constructions.demo.seed_demo_data
bench --site your-site.local execute reckon_constructions.demo.seed_demo_data --kwargs '{"reset": true}'
bench --site your-site.local execute reckon_constructions.demo.update_demo_names
bench --site your-site.local execute reckon_constructions.demo.clear_demo_data --kwargs '{"dry_run": true}'
bench --site your-site.local execute reckon_constructions.demo.clear_demo_data --kwargs '{"confirm": true}'
```

The seed is idempotent and uses `RC-DEMO-*` technical IDs with realistic visible names. The clear operation cancels submitted demo
documents before deleting them and requires explicit confirmation; it does not delete Company,
Currency, UOM, Item Group, Customer Group, Territory or accounting records outside the demo set.

## Repository Layout

- `reckon_constructions/` - Frappe app package.
- `reckon_constructions/config/` - module desktop metadata.
- `reckon_constructions/fixtures/` - deterministic fixtures, including the workspace.
- `docs/bench_audit.md` - required target-bench audit and gap map before schema work.
- `docs/implementation_plan.md` - staged delivery plan derived from the supplied prompts.

## License

License terms still need confirmation from Reckon Technologies Ltd. before publishing or
distributing this app outside the project team.
