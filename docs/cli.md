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
- `task create|list|show|board|update|move|archive|unarchive|status|comment add|list|show|edit`

## Project filters
`project list` supports task-aware filtering:
- `--task-status`
- `--has-open-tasks`
- `--has-blocked-tasks`
- `--include-archived-tasks`

## Task command policy
Tasks are supported, but intentionally optional.
Archived tasks are **not shown by default** in task lists and board views.

## Task examples
```bash
workctl task create --project PR0002 --title "Prepare kanban model" --board delivery --column-key todo --wip-order 10
workctl task board --project PR0002
workctl task board --project PR0002 --board delivery

workctl task comment add --task 1 --body "Need board column mapping later"
workctl task comment list --task 1 --table
workctl task comment show --comment-id 1
workctl task comment edit --comment-id 1 --body "Updated comment"
```

## Project view examples
```bash
workctl project list --has-open-tasks --table
workctl project list --task-status blocked --table
workctl project show --project PR0002 --include-tasks --include-attachments
```
