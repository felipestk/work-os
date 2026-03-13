# Workflow rules

## Default handling
- Prefer reusing existing customers when clearly matched.
- Create a new project unless clear continuation rules are satisfied.
- Always link projects to customers through IDs, not free-text client names.
- Log major work events on the project timeline.
- Use activities for communication and decision records.
- Do not create tasks by default.

## Task handling
Use tasks only when the user explicitly wants task tracking or the workflow is clearly board/kanban based.

When tasks are used:
- require a project link
- infer customer context through the linked project
- keep comments in task comments, not in activities, unless the note also matters as a broader project/customer event
- prefer tasks for stateful work items, not for routine status logging

## Context discipline
Keep the default command usage small.
Only load advanced references or use advanced subcommands when the task truly needs them.
