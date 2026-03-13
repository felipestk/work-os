# Testing

## Smoke test
Run:

```bash
tests/smoke.sh
```

This initializes a clean repo-local database, loads generic demo data, and validates:
- customers
- contacts
- projects
- offers
- offer items
- activities
- tasks
- task comments
- board view
- attachments
- archive/unarchive lifecycle
- search

## Demo bootstrap
To create a local demo/testing DB only:

```bash
scripts/bootstrap.sh
```

## Environment overrides
Repo-local testing uses repo-local paths unless you override them with:
- `OPENCLAW_WORKSPACE`
- `WORKCTL_DB_PATH`
- `WORKCTL_PROJECTS_ROOT`
- `WORKCTL_CUSTOMERS_ROOT`

## Fixture policy
Keep only generic, safe fixture data in the repo.
Do not store personal or live customer data.
