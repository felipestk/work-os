# Testing

## Smoke test
Run:

```bash
tests/smoke.sh
```

This will:
1. initialize a clean Work OS database
2. load generic demo data
3. run basic CLI checks across customer/contact/project/offer/activity/search

By default, repo-local testing uses repo-local paths unless you override them with:
- `OPENCLAW_WORKSPACE`
- `WORKCTL_DB_PATH`
- `WORKCTL_PROJECTS_ROOT`
- `WORKCTL_CUSTOMERS_ROOT`

## Demo bootstrap
To create a local demo/testing DB only:

```bash
scripts/bootstrap.sh
```

## Fixture policy
Keep only generic, safe fixture data in the repo.
Do not store personal or live customer data.
