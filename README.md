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
bench get-app /path/to/Reckon-Constructions
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

## Repository Layout

- `reckon_constructions/` - Frappe app package.
- `reckon_constructions/config/` - module desktop metadata.
- `reckon_constructions/fixtures/` - deterministic fixtures, including the workspace.
- `docs/bench_audit.md` - required target-bench audit and gap map before schema work.
- `docs/implementation_plan.md` - staged delivery plan derived from the supplied prompts.

## License

License terms still need confirmation from Reckon Technologies Ltd. before publishing or
distributing this app outside the project team.
