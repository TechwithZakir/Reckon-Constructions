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

## Rollback

Stop workers, restore the last known-good site backup, and redeploy the matching application commit. Do not downgrade by editing DocType JSON directly on a live site. Re-run migration and the app test suite before reopening traffic.

## Release evidence

Record the deployed commit, bench and ERPNext versions, migration output, test output, backup reference, and UAT sign-off in the release ticket.
