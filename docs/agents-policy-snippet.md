# AGENTS.md policy snippet for Work OS

Add the following block to the receiving OpenClaw host's `AGENTS.md` after installing Work OS.

```md
## Work OS Tracking Policy (Mandatory)

### Purpose
All substantive work must be traceable through Work OS for cross-session continuity, retrieval, auditability, and customer linkage.

Every tracked work item must belong to:
1. a **Customer** (`private` or `company`), and
2. a **Project** with a `PRxxxx` identifier.

No project may be created or reused without first assigning customer context.

### Core Entity Rule
Before substantive work begins, the agent must establish:
- a **Customer**
- a **Project** (`PRxxxx`)

A project may never exist without customer context.

### Customer Rule (Hard Requirement)
Every project must be linked to a customer.

Customer types:
- **private** — internal, personal, operator-only, or non-client work
- **company** — external client or customer work

Default behavior:
- if the work is internal and no external client is involved, use or create the private customer record
- if the work is for a business or client, use or create the relevant company customer

If uncertain, resolve customer context before substantive work continues.

### Project ID Standard
- Project IDs are sequential and zero-padded: `PR0001`, `PR0002`, ...
- Project folders use: `work/projects/PRxxxx-<slug>/`

### Default Rule (No Ambiguity)
Every new user request creates a **new project by default**, unless strict reuse conditions are satisfied.

A new request must never be handled as untracked work.

### Reuse Rule (Strict)
Reuse an existing project only when:
1. the user explicitly references a `PRxxxx` ID, or
2. the request is clearly a continuation, meaning all are true:
   - same customer/context
   - same objective/deliverable stream
   - recent activity (within 14 days) or explicit user confirmation

If uncertain, create a new project.

If customer context has changed, do **not** reuse the old project automatically.

### Execution Gate (Hard Requirement Per User Turn)
Before generating any substantive user-visible response (except explicit heartbeat acknowledgements), the agent must:
1. determine whether the work is **private/internal** or belongs to a **company/customer**
2. create or reuse the correct **customer**
3. decide **reuse vs create** for the project
4. if reuse criteria are not fully satisfied, create a new `PRxxxx` project immediately
5. ensure the Work OS record exists
6. ensure the project folder exists
7. log or update the lifecycle event for the turn when work is performed
8. reference the `PRxxxx` ID in outputs where practical

If customer context and project decision are not recorded, do not proceed with substantive work.

### Storage Rule
- Deliverables, notes, and artifacts must be stored under the project folder
- Projects must remain linked to their customer context
- Outputs should include the `PRxxxx` ID in headers or filenames where practical

### Continuity Rule
Important communication, decisions, milestones, and commercial activity should be logged in Work OS so the project is reconstructible later.

Use:
- **project events** for lifecycle and execution milestones
- **activities** for important communication, notes, and decisions
- **offers** when pricing, scope, or commercial proposals are involved

### Commercial Rule
If work includes pricing, proposal drafting, offer revision, or customer-facing scope definition, the project should also use the **offer** workflow linked to the same customer and, where applicable, the same project.
```

## Why this snippet matters
The Work OS installer can place the toolkit and skill on the host, but the receiving agent will behave much more reliably if its `AGENTS.md` also states that tracked work must use customer-linked projects.

That is the policy bridge between:
- installing the toolkit
- installing the skill
- actually changing agent behavior
