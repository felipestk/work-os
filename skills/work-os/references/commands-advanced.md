# Advanced workctl commands

Use these when the default customer → project → offer → activity flow is not enough.

## Offer line items
```bash
workctl offer item add \
  --offer QDEMO001 \
  --billing-type one_time \
  --name "Discovery" \
  --quantity 1 \
  --unit project \
  --unit-price 2500 \
  --tax-rate 23

workctl offer item list --offer QDEMO001 --table

workctl offer item update \
  --item-id 3 \
  --unit-price 500

workctl offer item remove --item-id 3

workctl offer totals recalc --offer QDEMO001
```

## Offer revisions
```bash
workctl offer revise \
  --offer QDEMO001 \
  --summary "Expanded scope" \
  --note "Scope revised after review"

workctl offer versions --offer QDEMO001 --table
workctl offer show --offer QDEMO001 --version 2
```

## Search and review
```bash
workctl search --keyword northwind --table
workctl project show --project PR0002
workctl customer show --customer "Northwind Systems"
workctl offer show --offer QDEMO001
```

## Runtime/path assumptions
Normal installed usage expects:
- toolkit under `~/.local/share/openclaw-workos`
- runtime DB under `~/.openclaw/workspace/ops/workos/workos.db`
- projects under `~/.openclaw/workspace/work/projects`
- customers under `~/.openclaw/workspace/work/customers`

These may be overridden through environment variables when needed.
