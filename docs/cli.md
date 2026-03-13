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
- `task create|list|show|update|move|archive|unarchive|status|comment add`

## Task command policy
Tasks are supported, but intentionally optional.
Archived tasks are **not shown by default** in task lists.

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
```

## Task examples
```bash
workctl task create \
  --project PR0002 \
  --title "Prepare kanban model" \
  --board delivery \
  --column-key todo \
  --wip-order 10

workctl task update --task 1 --title "Prepare task model" --priority high --assignee "Claw"
workctl task move --task 1 --board delivery --column-key doing --wip-order 20 --status in_progress
workctl task archive --task 1 --note "No longer active"
workctl task list --project PR0002 --table
workctl task list --project PR0002 --include-archived --table
workctl task unarchive --task 1 --status todo
```

## Task filter examples
```bash
workctl task list --project PR0002 --board delivery --column-key doing --table
workctl task list --assignee Claw --table
workctl task list --due-before 2026-03-31T23:59:59Z --table
```

## Enriched project view
```bash
workctl project show --project PR0002 --include-tasks --include-attachments
workctl project show --project PR0002 --include-tasks --include-archived-tasks
```
