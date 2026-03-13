# Usage

This document shows the main Work OS flows using `workctl`.

## Core flow: customer → project → offer/activity

### 1) Create a private/internal customer
```bash
workctl customer create --type private --name "Felipe"
```

### 2) Create a company customer
```bash
workctl customer create --type company --name "Northwind Systems" --website "https://northwind.example"
```

### 3) Add a contact
```bash
workctl contact add \
  --customer "Northwind Systems" \
  --first-name Ana \
  --last-name Silva \
  --role "Operations Lead" \
  --email ana@northwind.example \
  --primary
```

### 4) Create a project under a customer
```bash
workctl project create \
  --customer "Northwind Systems" \
  --title "Northwind pilot rollout" \
  --objective "Deliver initial pilot scope"
```

### 5) Log a project event
```bash
workctl project event \
  --project PR0002 \
  --type updated \
  --note "Pilot scope reviewed and approved"
```

### 6) Create an offer linked to the customer/project
```bash
workctl offer create \
  --customer "Northwind Systems" \
  --project PR0002 \
  --title "Northwind Pilot Proposal" \
  --subtotal 8000 \
  --tax 1840 \
  --total 9840 \
  --summary "Pilot proposal for automation and reporting"
```

### 7) Add line items to an offer
```bash
workctl offer item add \
  --offer QDEMO001 \
  --billing-type one_time \
  --name "Discovery and setup" \
  --quantity 1 \
  --unit project \
  --unit-price 2500 \
  --tax-rate 23

workctl offer item add \
  --offer QDEMO001 \
  --billing-type recurring \
  --name "Monthly support" \
  --quantity 1 \
  --unit month \
  --unit-price 450 \
  --tax-rate 23
```

### 8) Recalculate totals
```bash
workctl offer totals recalc --offer QDEMO001
```

### 9) Revise an offer
```bash
workctl offer revise \
  --offer QDEMO001 \
  --summary "Expanded pilot scope with reporting add-on" \
  --note "Expanded scope after review"
```

### 10) Log an activity
```bash
workctl activity add \
  --customer "Northwind Systems" \
  --project PR0002 \
  --offer QDEMO001 \
  --type meeting \
  --direction outbound \
  --subject "Pilot review" \
  --body "Reviewed pilot scope, timeline, and pricing."
```

## Optional task / board workflow
Use this only when explicit task tracking is needed.

```bash
workctl task create --project PR0002 --title "Prepare rollout board" --board delivery --column-key todo --wip-order 10
workctl task move --task 1 --board delivery --column-key doing --wip-order 20 --status in_progress
workctl task comment add --task 1 --body "Waiting on customer confirmation"
workctl task board --project PR0002
workctl task archive --task 1 --note "No longer active"
workctl task list --project PR0002 --include-archived --table
```

## Attachments
```bash
workctl attach add --entity-type project --entity-ref PR0002 --file ./brief.pdf
workctl attach add --entity-type task --entity-ref 1 --file ./notes.md --mime-type text/markdown
workctl attach list --entity-type task --entity-ref 1 --table
```

## Review and filtering
```bash
workctl customer list --table
workctl project list --has-open-tasks --table
workctl project show --project PR0002 --include-tasks --include-attachments
workctl task list --project PR0002 --board delivery --column-key doing --table
workctl search --keyword northwind --table
```

## Suggested operating pattern
For most real workflows:
1. create or reuse customer
2. create or reuse project
3. log major project events
4. create/revise offer if commercial work appears
5. log important activities and decisions
6. use tasks only if explicit operational task tracking is needed
