# Advanced workctl commands

Use these when the default customer → project → offer → activity flow is not enough.

## Board view
```bash
workctl task board --project PR0002
workctl task board --project PR0002 --board delivery
```

## Task comments
```bash
workctl task comment add --task 1 --body "Need future board column mapping"
workctl task comment list --task 1 --table
workctl task comment show --comment-id 1
workctl task comment edit --comment-id 1 --body "Updated note after review"
```

## Project filters based on task state
```bash
workctl project list --has-open-tasks --table
workctl project list --has-blocked-tasks --table
workctl project list --task-status in_progress --table
```

## Optional task workflow
```bash
workctl task create --project PR0002 --title "Prepare kanban model" --board delivery --column-key todo --wip-order 10
workctl task move --task 1 --board delivery --column-key doing --wip-order 20 --status in_progress
workctl task archive --task 1 --note "Paused / not active"
workctl task unarchive --task 1 --status todo
```
