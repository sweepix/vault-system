---
type: dashboard
description: Open commitments in both directions. Daily notes only, never mirrored.
---

# I owe

```dataview
TASK
FROM "01-Daily"
WHERE !completed AND owner = "me"
SORT due ASC
```

# Owed to me

```dataview
TASK
FROM "01-Daily"
WHERE !completed AND owner = "them"
SORT due ASC
```

# Past due, either direction

```dataview
TASK
FROM "01-Daily"
WHERE !completed AND due AND due < date(today)
SORT due ASC
```
