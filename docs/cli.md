# workctl CLI (v1 scaffold)

## Top-level commands
- `workctl init`
- `workctl doctor`
- `workctl customer ...`
- `workctl project ...`
- `workctl offer ...`
- `workctl activity ...`
- `workctl task ...`
- `workctl search`

## Initial implemented groups in scaffold
- `init`
- `doctor`
- `customer create|list|show`
- `project create|list|show|event|status`
- `offer create|list|show|versions|status|revise|item add|list|update|remove|totals recalc`
- `activity add|list`
- `task create|list|show|status|comment add`

## Task command policy
Tasks are supported, but intentionally optional.

Default agent usage should still prefer:
- projects
- project events
- activities
- offers

Use task commands only when the user explicitly wants task tracking or when operating inside a board/kanban workflow.

## Task examples
```bash
workctl task create --project PR0002 --title "Prepare kanban model" --description "Draft optional task entity plan"
workctl task list --project PR0002 --table
workctl task show --task 1
workctl task status --task 1 --status in_progress --note "Started schema pass"
workctl task comment add --task 1 --body "Need board column mapping later"
```
