# Work OS Architecture

Work OS is a unified operating layer for OpenClaw-based work.

## Core entities
- Customer
- Contact
- Project (`PRxxxx`)
- Offer
- Activity

## Design rules
- One repo: `openclaw-workos`
- One CLI: `workctl`
- One unified schema
- Skill included in same repo
- Keep agent default context minimal
- Keep advanced command detail in skill references

## v1 goal
Deliver a working end-to-end workflow for:
1. creating customers
2. creating projects linked to customers
3. logging project events
4. creating offers linked to customer/project
5. logging activities
