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

## Optional task workflow
Use only when task tracking is explicitly needed.

```bash
workctl task create \
  --project PR0002 \
  --title "Prepare kanban model" \
  --description "Draft first task entity and board mapping" \
  --board delivery \
  --column-key todo \
  --wip-order 10

workctl task list --project PR0002 --table
workctl task show --task 1
workctl task status --task 1 --status in_progress --board delivery --column-key doing --wip-order 20 --note "Started implementation"
workctl task comment add --task 1 --body "Need future board column mapping"
```

## Attach files to tracked entities
```bash
workctl attach add --entity-type task --entity-ref 1 --file ./spec.md --mime-type text/markdown
workctl attach list --entity-type task --entity-ref 1 --table

workctl attach add --entity-type project --entity-ref PR0002 --file ./brief.pdf
workctl attach add --entity-type offer --entity-ref QDEMO001 --file ./quote.pdf
```

## Search and review
```bash
workctl search --keyword northwind --table
workctl project show --project PR0002
workctl customer show --customer "Northwind Systems"
workctl offer show --offer QDEMO001
workctl task show --task 1
```

## Runtime/path assumptions
Normal installed usage expects:
- toolkit under `~/.local/share/openclaw-workos`
- runtime DB under `~/.openclaw/workspace/ops/workos/workos.db`
- projects under `~/.openclaw/workspace/work/projects`
- customers under `~/.openclaw/workspace/work/customers`

These may be overridden through environment variables when needed.
