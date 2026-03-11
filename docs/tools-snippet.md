# TOOLS.md snippet for Work OS

Add the following block to the receiving OpenClaw host's `TOOLS.md` after installing Work OS.

```md
## Work OS (customers, projects, offers, activities)

### Purpose
Unified operating system for tracked work in OpenClaw, covering:
- customers (`private` or `company`)
- contacts
- projects with persistent `PRxxxx` IDs
- project events
- offers with immutable version history
- offer line items and totals
- activities / continuity logging

Use this instead of separate ad-hoc project tracking + CRM notes when work needs continuity, customer linkage, pricing, or operational follow-up.

### Source of truth
- Toolkit install: `~/.local/share/openclaw-workos`
- CLI: `~/.local/bin/workctl`
- DB: `~/.openclaw/workspace/ops/workos/workos.db`
- Schema: `~/.local/share/openclaw-workos/schema/workos.sql`
- Skill: `~/.openclaw/workspace/skills/work-os/`
- Project folders: `~/.openclaw/workspace/work/projects/PRxxxx-<slug>/`
- Customer folders: `~/.openclaw/workspace/work/customers/<customer_code>/`

### Core rules
- Every substantive work item should belong to a customer and a project.
- Customers may be `private` or `company`.
- Projects keep the `PRxxxx` ID format.
- Use project events for lifecycle changes.
- Use activities for important communication, notes, and decisions.
- Use offers when work involves pricing, scope, or proposal revisions.
- Prefer offer line items over opaque top-level total edits whenever pricing structure matters.

### Notable behavior
- `customer_code` format: `CUST0001`
- project code format: `PR0001`
- offer code: obfuscated public-style code beginning with `Q...`
- runtime paths can be overridden via:
  - `OPENCLAW_WORKSPACE`
  - `WORKCTL_DB_PATH`
  - `WORKCTL_PROJECTS_ROOT`
  - `WORKCTL_CUSTOMERS_ROOT`
- `workctl doctor` reports current DB and active root paths

### Most-used commands
```bash
# init + health
workctl init
workctl doctor

# customers
workctl customer create --type private --name "Felipe"
workctl customer create --type company --name "Northwind Systems"
workctl customer list --table
workctl customer show --customer "Northwind Systems"

# contacts
workctl contact add --customer "Northwind Systems" --first-name Ana --email ana@example.com --primary
workctl contact list --customer "Northwind Systems" --table

# projects
workctl project create --customer "Northwind Systems" --title "Northwind pilot rollout" --objective "Deliver initial pilot scope"
workctl project list --table
workctl project show --project PR0002
workctl project event --project PR0002 --type updated --note "Pilot scope reviewed"
workctl project status --project PR0002 --status blocked --note "Waiting on client input"

# activities
workctl activity add --customer "Northwind Systems" --project PR0002 --type meeting --direction outbound --body "Kickoff summary"
workctl activity list --project PR0002 --table

# search
workctl search --keyword northwind --table
```

### Offers + version history
```bash
# create + revise
workctl offer create --customer "Northwind Systems" --project PR0002 --title "Pilot" --subtotal 8000 --tax 1840 --total 9840
workctl offer revise --offer QDEMO001 --summary "Expanded scope" --note "Scope revised after review"
workctl offer status --offer QDEMO001 --status sent

# list/view versions
workctl offer list --customer "Northwind Systems" --table
workctl offer show --offer QDEMO001
workctl offer show --offer QDEMO001 --version 2
workctl offer versions --offer QDEMO001 --table
```

### Offer line items
```bash
workctl offer item add --offer QDEMO001 --billing-type one_time --name "Discovery" --quantity 1 --unit-price 2500 --tax-rate 23
workctl offer item add --offer QDEMO001 --billing-type recurring --name "Support" --quantity 1 --unit month --unit-price 450 --tax-rate 23
workctl offer item list --offer QDEMO001 --table
workctl offer item update --item-id 3 --unit-price 500
workctl offer item remove --item-id 3
workctl offer totals recalc --offer QDEMO001
```
```

## Notes
This block is meant to replace the old split mental model of:
- project registry as one system
- CRM as a second system

Work OS unifies them into one command surface and one continuity model.
