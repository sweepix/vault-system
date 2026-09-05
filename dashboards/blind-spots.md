---
type: dashboard
description: What has not been done yet. Read this before the weekly review.
---

# Stubs awaiting enrichment

```dataview
TABLE WITHOUT ID file.link AS Entity, type, file.ctime AS Captured
FROM ""
WHERE status = "stub"
SORT file.ctime ASC
```

# High influence, no read on them

```dataview
TABLE WITHOUT ID file.link AS Person, org, relation
FROM "02-People"
WHERE influence = "high" AND (!relationship OR relationship = "unknown")
```

# Forums that decide, without me

```dataview
TABLE WITHOUT ID file.link AS Forum, cadence, owner, what_it_decides
FROM "05-Rituals"
WHERE decision_rights = "decides" AND my_role = "absent"
```

# Decisions due for revisit

```dataview
TABLE WITHOUT ID file.link AS Decision, date, revisit_by, reversible
FROM "07-Decisions"
WHERE revisit_by AND revisit_by <= date(today)
SORT revisit_by ASC
```

# Inherited commitments not yet confirmed

```dataview
TABLE WITHOUT ID file.link AS Project, sponsor, source, outcome, status
FROM "06-Projects"
WHERE inherited = "yes"
```
