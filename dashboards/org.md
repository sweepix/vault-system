---
type: dashboard
description: Teams and systems. Reverse edges derived, never stored.
---

# Teams

```dataview
TABLE WITHOUT ID file.link AS Team, lead, headcount, design_coverage, parent
FROM "03-Teams"
SORT parent ASC
```

# Systems, worst design debt first

```dataview
TABLE WITHOUT ID file.link AS System, owner_team, dri, ux_maturity, design_debt
FROM "04-Systems"
SORT choice(design_debt = "high", 3, choice(design_debt = "medium", 2, 1)) DESC
```

# Reverse edges, derived

Put this in a team file to list its members without storing them:

```
TABLE WITHOUT ID file.link AS Member, title, relation
FROM "02-People"
WHERE org = this.file.link
```
