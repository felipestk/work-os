# workctl CLI (v1 scaffold)

## Top-level commands
- `workctl init`
- `workctl doctor`
- `workctl customer ...`
- `workctl project ...`
- `workctl offer ...`
- `workctl activity ...`
- `workctl attach ...`
- `workctl task ...`
- `workctl search`

## Initial implemented groups in scaffold
- `init`
- `doctor`
- `customer create|list|show`
- `project create|list|show|event|status`
- `offer create|list|show|versions|status|revise|item add|list|update|remove|totals recalc`
- `activity add|list`
- `attach add|list|show|remove`
- `task create|list|show|update|move|status|comment add`

## Task command policy
Tasks are supported, but intentionally optional.

Default agent usage should still prefer:
- projects
- project events
- activities
- offers

Use task commands only when the user explicitly wants task tracking or when operating inside a board/kanban workflow.

## Attachment examples
```bash
workctl attach add --entity-type task --entity-ref 1 --file ./spec.md --mime-type text/markdown
workctl attach list --entity-type task --entity-ref 1 --table
workctl attach show --attachment-id 1
workctl attach remove --attachment-id 1

workctl attach add --entity-type project --entity-ref PR0002 --file ./brief.pdf
workctl attach list --entity-type project --entity-ref PR0002 --table

workctl attach add --entity-type offer --entity-ref QDEMO001 --file ./quote.pdf
workctl attach list --entity-type offer --entity-ref QDEMO001 --table
```

## Task examples
```bash
workctl task create \
  --project PR0002 \
  --title "Prepare kanban model" \
  --description "Draft optional task entity plan" \
  --board delivery \
  --column-key todo \
  --wip-order 10

workctl task update --task 1 --title "Prepare task model" --priority high --assignee "Claw"
workctl task move --task 1 --board delivery --column-key doing --wip-order 20 --status in_progress --note "Started schema pass"
workctl task show --task 1
workctl task comment add --task 1 --body "Need board column mapping later"
```
