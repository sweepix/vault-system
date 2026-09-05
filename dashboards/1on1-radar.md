---
type: dashboard
description: Who is overdue, by relation. Oldest contact first.
---

# Directs

```dataview
TABLE WITHOUT ID file.link AS Person, title AS Title, cadence AS Cadence, last_1on1 AS Last
FROM "02-People"
WHERE relation = "direct" AND status != "departed"
SORT last_1on1 ASC
```

# Peers

```dataview
TABLE WITHOUT ID file.link AS Person, org, cadence, last_1on1 AS Last
FROM "02-People"
WHERE relation = "peer" AND status != "departed"
SORT last_1on1 ASC
```

# Skips

```dataview
TABLE WITHOUT ID file.link AS Person, org, last_1on1 AS Last
FROM "02-People"
WHERE relation = "skip" AND status != "departed"
SORT last_1on1 ASC
```

> Sorted on the raw date, not a computed day count. Dataview's `.days` on a date
> subtraction is month normalized and returns only the day remainder, so 45 days overdue
> displays as 15. The exact counts are in `coach-local.md`, computed in Python.
