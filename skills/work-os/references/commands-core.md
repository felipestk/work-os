# Core workctl commands

```bash
workctl init
workctl doctor

workctl customer create --type private --name "Felipe"
workctl customer list --table
workctl customer show --customer Felipe

workctl contact add --customer "Northwind Systems" --first-name Ana --email ana@example.com
workctl contact list --customer "Northwind Systems" --table

workctl project create --customer Felipe --title "Work OS planning" --objective "Design unified system"
workctl project list --table
workctl project show --project PR0001
workctl project event --project PR0001 --type updated --note "Architecture drafted"
workctl project status --project PR0001 --status blocked --note "Waiting on decision"

workctl offer create --customer "Northwind Systems" --project PR0002 --title "Pilot" --subtotal 8000 --tax 1840 --total 9840
workctl offer list --customer "Northwind Systems" --table
workctl offer versions --offer QDEMO001 --table
workctl offer item add --offer QDEMO001 --billing-type one_time --name "Discovery" --quantity 1 --unit-price 2500 --tax-rate 23
workctl offer item list --offer QDEMO001 --table
workctl offer totals recalc --offer QDEMO001

workctl activity add --customer "Northwind Systems" --project PR0002 --type meeting --direction outbound --body "Kickoff summary"
workctl activity list --project PR0002 --table

workctl search --keyword northwind --table
```
