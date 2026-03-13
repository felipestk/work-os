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

workctl task update \
  --task 1 \
  --title "Prepare task model" \
  --priority high \
  --assignee "Claw"

workctl task move \
  --task 1 \
  --board delivery \
  --column-key doing \
  --wip-order 20 \
  --status in_progress

workctl task archive --task 1 --note "Paused / not active"
workctl task unarchive --task 1 --status todo
```

## Task filtering
```bash
workctl task list --project PR0002 --board delivery --column-key doing --table
workctl task list --assignee Claw --table
workctl task list --due-before 2026-03-31T23:59:59Z --table
workctl task list --include-archived --table
```

## Attach files to tracked entities
```bash
workctl attach add --entity-type task --entity-ref 1 --file ./spec.md --mime-type text/markdown
workctl attach list --entity-type task --entity-ref 1 --table
workctl attach show --attachment-id 1
workctl attach remove --attachment-id 1
```

## Enriched project review
```bash
workctl project show --project PR0002 --include-tasks --include-attachments
workctl project show --project PR0002 --include-tasks --include-archived-tasks
```

## Search and review
```bash
workctl search --keyword northwind --table
workctl task show --task 1
```
