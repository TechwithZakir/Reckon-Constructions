# Release Checklist

## Automated checks

- Compile Python sources with `python -m compileall -q reckon_constructions`.
- Parse every DocType and fixture JSON file.
- Run the app unit tests with `bench --site <site> run-tests --app reckon_constructions`.
- Run `git diff --check` and verify the working tree is clean before release.

## Target bench checks

- Confirm Frappe and ERPNext are v16-compatible with `bench version`.
- Install on a disposable site, run migrate, and confirm the Constructions workspace loads.
- Create an approved BOQ, baseline, assembly, site report, variation, certificate, and draft ERPNext transaction.
- Retry each whitelisted integration action and confirm it does not create duplicates.
- Confirm standard ERPNext records remain authoritative and no core file is modified.

## Operational checks

- Verify role access for System Manager, Projects Manager, and Projects User.
- Confirm approved BOQ, baseline, variation, and certificate records cannot be edited in place.
- Export and re-import a BOQ with one invalid row; confirm row errors are returned and the document is unchanged.
- Confirm backup, restore, scheduler, and worker health before production enablement.
