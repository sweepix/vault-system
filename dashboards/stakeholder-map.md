---
type: dashboard
description: Influence and interest quadrants. Strained and unknown sort first.
---

# Manage closely

```dataview
TABLE WITHOUT ID file.link AS Person, org, relationship, cadence, last_1on1
FROM "02-People"
WHERE influence = "high" AND interest = "high"
SORT choice(relationship = "strained", 1, choice(relationship = "unknown", 2, 3)) ASC
```

# Keep satisfied

```dataview
TABLE WITHOUT ID file.link AS Person, org, relationship, cadence, last_1on1
FROM "02-People"
WHERE influence = "high" AND interest = "low"
SORT choice(relationship = "strained", 1, choice(relationship = "unknown", 2, 3)) ASC
```

# Keep informed

```dataview
TABLE WITHOUT ID file.link AS Person, org, relationship, cadence
FROM "02-People"
WHERE influence = "low" AND interest = "high"
```

# Monitor

```dataview
TABLE WITHOUT ID file.link AS Person, org, relationship
FROM "02-People"
WHERE influence = "low" AND interest = "low"
```

# Unclassified, fix these

```dataview
TABLE WITHOUT ID file.link AS Person, influence, interest
FROM "02-People"
WHERE status != "departed" AND (!influence OR !interest OR influence = "medium" OR interest = "medium")
```
