---
name: work-os
description: Unified customer, project, offer, activity, and optional task workflow for OpenClaw using the Work OS toolkit (`workctl`). Use when work should be tracked through reusable customer records, PR-coded projects, offer creation or revision, activity logging, or explicit task/board workflows inside an OpenClaw workspace.
---

Use this skill when the task should be recorded in Work OS rather than handled as untracked ad-hoc work.

## Runtime assumptions
Assume the Work OS toolkit is installed and `workctl` is available.
Assume live data is stored in the active OpenClaw workspace, typically through these configured paths:
- workspace database
- workspace `work/projects/`
- workspace `work/customers/`

If `workctl` is unavailable, stop and tell the operator that the Work OS toolkit must be installed first.

## Default workflow
1. Identify whether the work belongs to an existing customer or a new one.
2. Create or reuse the customer.
3. Create or reuse the project (`PRxxxx`).
4. Link the project to the customer.
5. Log major project events.
6. If proposal or commercial work appears, create or reuse an offer.
7. Log important activities when communication or decisions matter.

## Customer rule
Treat customers as first-class records.
A customer may be:
- `company`
- `private`

Use a private customer record for internal or personal work.

## Project rule
Projects are the main work containers.
Keep the `PRxxxx` identifier format for continuity.
Prefer linking projects to customers through Work OS IDs instead of free-text client names.

## Offer rule
Use offers when the work includes pricing, commercial scope, proposal revisions, or client-facing costing.
When an offer exists, prefer line items over ad-hoc total changes so the pricing structure remains inspectable.

## Activity rule
Use activities for notable communication and decisions:
- calls
- meetings
- emails
- summaries
- decisions
- important notes

Do not log every trivial step. Log the moments that matter for continuity.

## Task rule
Tasks are **super optional**.
Do not create or update tasks by default.

Prefer projects, project events, and activities for normal execution logging.
Use tasks only when:
- the user explicitly asks for task tracking
- the workflow is clearly task/board/kanban based
- or a dedicated automation depends on task records

When tasks are used:
- link every task to a project
- infer customer context through the project
- keep task comments inside the task comment thread, not in activities, unless the comment also matters as a broader project/customer event

## Context discipline
Keep the default command usage small.
Use the core flow first.
Only read advanced references when the task actually needs them.

## Command references
Read these only when needed:
- `references/commands-core.md`
- `references/commands-advanced.md`
- `references/entity-model.md`
- `references/workflow-rules.md`
