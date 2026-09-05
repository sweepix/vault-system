# Honeywell Vault: Build Guide

> **Revision 2, reviewed 2026-09-05.** Four independent reviews (architecture and failure modes, technical correctness with the scripts executed against fixtures, leadership efficacy, security and data boundary) found 40+ defects. The critical ones are fixed in place below. **Part III supersedes Parts I and II wherever they conflict. Read section 21 before building anything.**

Role: Senior Director, Engineering UX. Start: October 2026. Starting cold, no org chart in hand.

Stack: Obsidian vault of plain markdown, edited and generated in Cursor. Graph = Obsidian native graph plus a generated stakeholder 2x2. Upkeep = paste raw notes into an inbox, run a Cursor prompt, it files them.

Vault root: `~/claude/Honeywell/Vault`

---

## 1. Design principles

Five rules. Everything below follows from them.

1. **Capture is cheap, reconstruction is expensive.** Every name, system, acronym and forum you hear in the first 90 days gets a file within 24 hours, even a three line stub. You will not remember who "Dave from HCE" was in week 7.
2. **The graph is made of frontmatter, not prose.** Typed fields (`manager`, `owns`, `attendees`) are what make the vault queryable. Prose is for nuance. If it matters for a rollup, it is a field.
3. **Never let the AI overwrite.** The filing prompt appends into marked sections only, creates stubs for unknowns, and reports conflicts instead of resolving them. One silent overwrite and you stop trusting the system.
4. **Structure over chronology.** Daily notes are the write path. Entity files are the read path. Your graph view filters daily notes out by default, otherwise it becomes a hairball by week 3.
5. **Exit criteria, not activity lists.** A 30/60/90 that lists meetings you attended is theater. Each phase ends on a testable condition.

**One boundary check before you start.** This vault will hold Honeywell internal information: names, org structure, program status, people judgments. Read `Onboarding/IP .html` and `Onboarding/Data privacy.html` first, keep the vault on local disk only (not personal iCloud, Dropbox or OneDrive), and point your Honeywell corporate AI account at it rather than a personal one once you have credentials.

---

## 2. Folder structure

Numbered so Obsidian sorts them in reading order.

```
Vault/
├── 00-Inbox/          Raw unprocessed dumps. Emptied daily.
├── 01-Daily/          One note per working day. YYYY-MM-DD.md
├── 02-People/         One file per human. First-Last.md
├── 03-Teams/          Org units, including ones above you.
├── 04-Systems/        Products, platforms, design systems, tools, repos.
├── 05-Rituals/        Recurring meetings and governance forums.
├── 06-Projects/       Initiatives with a named outcome.
├── 07-Decisions/      One file per decision. Immutable once accepted.
├── 08-Plan/           30/60/90, hypotheses, evidence log, POV doc.
├── 09-Dashboards/     Dataview rollups. No hand written content.
├── 99-Meta/
│   ├── templates/     Note templates.
│   ├── prompts/       Saved Cursor prompts.
│   ├── schema.md      The frontmatter contract.
│   └── config.md      START_DATE and other constants.
└── .cursor/rules/     Cursor rules file.
```

`05-Rituals` is the folder most people skip and the one that matters most at your level. In a company the size of Honeywell, the map of which forum decides what, and whether you have a seat, is more actionable than the reporting chart.

---

## 3. Entity schema

Put this in `99-Meta/schema.md`. It is also what you paste into the Cursor rules file so the AI files consistently.

### Person

```yaml
---
type: person
name: Priya Nair
aliases: [Priya, P. Nair]
title: Director, Software Engineering
org: "[[Building Automation Software]]"
relation: direct
manager: "[[Ravi Desai]]"
owns: []
location: Atlanta
timezone: ET
tenure_start: 2019-03
influence: high
interest: high
relationship: unknown
cadence: weekly
last_1on1:
next_1on1:
status: active
tags: [person]
---
```

**No inline YAML comments, ever.** `relation: direct   # direct | manager | ...` parses as the literal string `direct   # direct | manager` in any tool that splits on the first colon. Enum legends live in `99-Meta/schema.md` and nowhere else. Allowed values:

* `relation`: direct, manager, skip, peer, partner, exec, external
* `influence` and `interest`: high, low. There is no `medium`. A medium is a low you have not decided about, and it silently disappears from every quadrant view.
* `relationship`: strong, neutral, unknown, strained
* `cadence`: weekly, biweekly, monthly, adhoc
* `status`: active, stub, departed
* Unknown means **leave the field blank**, not the word `unknown`, otherwise the schema evolution pass can never see it as empty.

**Only child side edges.** A person carries `manager`, never `reports`. A team carries `lead`, never `members`. Reverse edges are derived in Dataview (`WHERE manager = this.file.link`). An append only filer can add a new edge but is forbidden to delete the old one, so any two sided relationship drifts into permanent phantoms.

**`aliases` is the real fix for name variants**, not a prompt instruction. Obsidian resolves `[[Priya]]` to the file whose aliases list contains it.

Body sections, fixed order. The filing prompt writes only into the marked ones.

```markdown
## Snapshot
## What they own
## What they need from me
## What I need from them
## Career and motivation
## Commitments        <!-- append only -->
## 1:1 Log            <!-- append only, newest first -->
## Open questions     <!-- append only -->
```

`relation` is doing heavy lifting. Querying `WHERE relation = "direct"` is far more reliable in Dataview than comparing link values, so set it on every person file.

### Team

```yaml
---
type: team
lead: "[[Ravi Desai]]"
parent: "[[Honeywell Building Automation]]"
members: []
owns: []
charter:
headcount:
design_coverage:        # designers per N engineers, your key ratio
status: active
tags: [team]
---
```

### System

```yaml
---
type: system
owner_team: "[[Building Automation Software]]"
dri: "[[Priya Nair]]"
users:                  # who actually operates it
ux_maturity: unknown    # none | ad-hoc | defined | measured
design_debt: unknown    # low | medium | high
dependencies: []
status: active
tags: [system]
---
```

### Ritual

```yaml
---
type: ritual
cadence: weekly
owner: "[[Ravi Desai]]"
attendees: []
decision_rights: decides   # decides | recommends | informs
my_role: absent            # chair | member | guest | absent
what_it_decides:
status: active
tags: [ritual]
---
```

`my_role: absent` on a forum with `decision_rights: decides` is a finding. Query for those in week 4.

### Project

```yaml
---
type: project
sponsor: "[[]]"
dri: "[[]]"
teams: []
outcome:                # the measurable change, not the deliverable
status: active          # active | paused | at-risk | done
horizon: 30             # 30 | 60 | 90 | beyond
tags: [project]
---
```

### Decision

```yaml
---
type: decision
date: 2026-10-21
owner: "[[]]"
forum: "[[]]"
status: accepted        # proposed | accepted | reversed
reversible: yes         # yes = two way door, no = one way door
stakeholders: []
tags: [decision]
---
```

### Daily note

```yaml
---
type: daily
date: 2026-10-06
day_number: 2           # days since START_DATE
tags: [daily]
---
```

### Commitments

Commitments are inline Dataview fields on task lines, not a separate file type. This is what lets one query show everything you owe everyone.

```markdown
- [ ] Send org draft to [[Priya Nair]] [owner:: me] [to:: Priya Nair] [due:: 2026-10-14]
- [ ] Priya sends me the program staffing list [owner:: them] [from:: Priya Nair] [due:: 2026-10-09]
```

Rule: `owner:: me` means it is your debt. `owner:: them` means someone owes you. Nothing else goes in a checkbox.

---

## 4. Templates

Save each in `99-Meta/templates/`. Frontmatter is omitted here where section 3 already specifies it; the scaffold prompt in section 7 writes both halves.

### `daily.md`

```markdown
---
type: daily
date: {{date:YYYY-MM-DD}}
day_number: {{day_number}}
tags: [daily]
---

# {{date:YYYY-MM-DD}} · Day {{day_number}}

## Top 3
1.
2.
3.

## Meetings
<!-- one line each, link the ritual and the people -->

## People met
<!-- [[links]]. Any name not already a file becomes a stub tonight. -->

## Commitments made
<!-- format, copy the line, do not leave the placeholder as a live checkbox:
- [ ] text [owner:: me] [to:: Full Name] [due:: YYYY-MM-DD] -->

## Commitments received
<!-- - [ ] text [owner:: them] [from:: Full Name] [due:: YYYY-MM-DD] -->

## Decisions observed
<!-- who decided, in what forum, reversible or not -->

## Signals
<!-- what surprised me, what contradicted yesterday, what nobody would say out loud -->

## Open loops

## Tomorrow
```

"Signals" is the highest value section in the first 60 days and the one you will be tempted to skip. Surprise is data. Write the thing that did not fit.

### `meeting.md`

Lives in `00-Inbox/` during the meeting, gets filed at end of day.

```markdown
# {{date:YYYY-MM-DD HHmm}} · {{topic}}

Attendees:
Forum: 
Purpose: decide | inform | explore

## Raw
<!-- type badly and fast. structure is the AI's job, not yours. -->

## My read
<!-- 2 lines max, written within 5 minutes of the meeting ending -->
```

### `person.md`

```markdown
# {{name}}

## Snapshot
Role:
How they got here:
How they like to work:
What good looks like to them:

## What they own

## What they need from me

## What I need from them

## Career and motivation

## Commitments

## 1:1 Log

## Open questions
```

### `1on1-manager.md`

One rolling file, `02-People/<Manager Name>.md`, with a fixed agenda. Reuse the same five headings every week so drift is visible.

```markdown
## 1:1 Log

### 2026-10-08
**My top 3 this week**

**Decisions I need from you**

**What I am hearing that you may not be**

**Where I need air cover**

**Feedback for me**
```

The third heading is the one that makes you valuable in the first 90 days. You have a fresh set of eyes with a 90 day expiry.

### `decision.md`

```markdown
# {{title}}

**Question:**
**Decided:**
**Decided by:** 
**Forum:**
**Reversible:** yes | no
**Options considered:**
**Why this one:**
**What would make us revisit:**
```

### `ritual.md`

```markdown
# {{name}}

**What it actually decides:**
**What it claims to decide:**
**Who really drives it:**
**Pre-work that determines the outcome:**
**How to get an item on the agenda:**
**My path to a seat:**
```

The gap between "actually decides" and "claims to decide" is the map of where power sits.

---

## 5. Obsidian setup

### Install and enable

1. Open Obsidian, "Open folder as vault", pick `~/claude/Honeywell/Vault`.
2. Core plugins on: **Daily notes**, **Templates**, **Backlinks**, **Outgoing links**, **Graph view**, **Properties view**.
3. Community plugin: **Dataview**. In its settings enable **Enable JavaScript Queries** off (not needed) and **Enable Inline Field Highlighting** on. This is the only community plugin you need. Resist installing more until week 8.
4. Daily notes settings: folder `01-Daily`, format `YYYY-MM-DD`, template `99-Meta/templates/daily.md`.
5. Templates settings: folder `99-Meta/templates`.

If your Obsidian version ships the **Bases** core plugin, you can build the dashboards in section 6 as Bases views instead of Dataview. Dataview queries below are given because they work on every version and are plain text, which means Cursor can generate and edit them.

### Graph view configuration

This is the step that decides whether the graph is useful or noise.

**Filters box:** `-path:01-Daily -path:00-Inbox -path:99-Meta`

Daily notes link to everything, so leaving them in collapses the graph into a single blob centered on last Tuesday. Excluding them makes the graph show org structure, which is what you actually want to look at.

**Groups** (add each as a new group with the given query and color):

| Query | Color | Meaning |
|---|---|---|
| `path:02-People` | blue | humans |
| `path:03-Teams` | orange | org units |
| `path:04-Systems` | green | what gets built |
| `path:05-Rituals` | yellow | where decisions happen |
| `path:06-Projects` | purple | initiatives |
| `path:07-Decisions` | red | commitments made |
| `["status":"stub"]` | grey | unenriched, your backlog |

Grey nodes are your to do list. A graph that is mostly grey in week 6 means you are capturing but not following up.

**Display:** turn Arrows on. Set Link distance high (around 250) and Repel force high so clusters separate. Turn Text fade off so labels stay readable.

**Local graph:** open any person file, then use the local graph pane at depth 2. That answers "who is around this person" faster than any org chart.

### Frontmatter links in the graph

Obsidian counts links written in frontmatter as long as they are quoted wikilinks (`manager: "[[Ravi Desai]]"`) or list items of the same form. Unquoted `[[X]]` does not break YAML, it parses as a nested list and is therefore not a link at all, which is worse because nothing errors. Always quote.

---

## 6. Dashboards

Each is its own file in `09-Dashboards/`. No hand written content in these files, only queries, so they never go stale.

### `09-Dashboards/1on1-radar.md`

Who is overdue, sorted worst first.

````
```dataview
TABLE WITHOUT ID
  file.link AS Person,
  title AS Title,
  cadence AS Cadence,
  last_1on1 AS "Last 1:1",
  last_1on1 AS "Last"
FROM "02-People"
WHERE relation = "direct" AND status = "active"
SORT last_1on1 ASC
```
````

Add a second block with `WHERE relation = "peer"` and a third with `relation = "manager"`. Three tables, one screen, thirty seconds every Monday.

### `09-Dashboards/commitments.md`

````
```dataview
TASK
FROM "01-Daily" OR "02-People"
WHERE !completed AND owner = "me"
SORT due ASC
```
````

Second block, what you are owed:

````
```dataview
TASK
FROM "01-Daily" OR "02-People"
WHERE !completed AND owner = "them"
SORT due ASC
```
````

Third block, past due either direction:

````
```dataview
TASK
FROM "01-Daily" OR "02-People"
WHERE !completed AND due AND due < date(today)
SORT due ASC
```
````

### `09-Dashboards/stakeholder-map.md`

Four quadrants, Mendelow style. Manage closely, keep satisfied, keep informed, monitor.

````
```dataview
TABLE WITHOUT ID file.link AS Person, org, relationship, cadence, last_1on1
FROM "02-People"
WHERE influence = "high" AND interest = "high"
SORT choice(relationship = "strained", 1, choice(relationship = "unknown", 2, 3)) ASC
```
````

Repeat the block three more times with:

* `influence = "high" AND interest = "low"` under a **Keep satisfied** heading
* `influence = "low" AND interest = "high"` under **Keep informed**
* `influence = "low" AND interest = "low"` under **Monitor**

The column that matters is `relationship`. A `strained` or `unknown` in the manage closely quadrant is the single highest priority item in your week.

### `09-Dashboards/blind-spots.md`

Three queries that find what you have not done yet.

Stubs awaiting enrichment:

````
```dataview
TABLE WITHOUT ID file.link AS Entity, type, file.ctime AS "Captured"
FROM ""
WHERE status = "stub"
SORT file.ctime ASC
```
````

High influence people you have no read on:

````
```dataview
TABLE WITHOUT ID file.link AS Person, org, relation
FROM "02-People"
WHERE influence = "high" AND relationship = "unknown"
```
````

Forums that decide things and do not include you:

````
```dataview
TABLE WITHOUT ID file.link AS Forum, cadence, owner, what_it_decides
FROM "05-Rituals"
WHERE decision_rights = "decides" AND my_role = "absent"
```
````

That last query is the most strategically useful line of code in this vault.

### `09-Dashboards/org.md`

````
```dataview
TABLE WITHOUT ID file.link AS Team, lead, headcount, design_coverage, parent
FROM "03-Teams"
SORT parent ASC
```
````

````
```dataview
TABLE WITHOUT ID file.link AS System, owner_team, dri, ux_maturity, design_debt
FROM "04-Systems"
SORT choice(design_debt = "high", 3, choice(design_debt = "medium", 2, 1)) DESC
```
````

### Stakeholder 2x2 as a picture

Dataview gives you the four lists. If you want an actual plotted 2x2 to look at or screenshot, generate one. Save as `99-Meta/scripts/stakeholder_map.py` and run `python3 99-Meta/scripts/stakeholder_map.py` from the vault root.

```python
import os, re, html, json

PEOPLE = "02-People"
OUT = "09-Dashboards/stakeholder-map.html"
KEYS = ("name","title","org","relation","influence","interest","relationship","status")

def parse(path):
    txt = open(path, encoding="utf-8").read()
    m = re.match(r"^---\n(.*?)\n---", txt, re.S)
    if not m:
        print("SKIPPED, no frontmatter:", path); return None
    d = {}
    for line in m.group(1).splitlines():
        k, _, v = line.partition(":")
        k, v = k.strip(), re.sub(r"\s+#.*$", "", v).strip().strip('"').strip("'")
        if k in KEYS and v: d[k] = v
    d.setdefault("name", os.path.splitext(os.path.basename(path))[0])
    return d

rows = [p for p in (parse(os.path.join(PEOPLE,f)) for f in sorted(os.listdir(PEOPLE))
        if f.endswith(".md")) if p and p.get("status") != "departed"]

COLOR = {"strong":"#2e7d32","neutral":"#8a8a8a","unknown":"#b8860b","strained":"#c62828"}
QUAD = [("high","high","Manage closely"),("high","low","Keep satisfied"),
        ("low","high","Keep informed"),("low","low","Monitor"),
        (None,None,"Unclassified")]

def axis(v):
    return v if v in ("high","low") else None

cells = ""
for inf, inte, label in QUAD:
    if label == "Unclassified":
        people = [r for r in rows if axis(r.get("influence")) is None or axis(r.get("interest")) is None]
    else:
        people = [r for r in rows if axis(r.get("influence"))==inf and axis(r.get("interest"))==inte]
    items = "".join(
        '<li><span class="dot" style="background:%s"></span>%s <em>%s</em></li>' % (
            COLOR.get(r.get("relationship","unknown"), "#8a8a8a"),
            html.escape(r["name"]), html.escape(r.get("title",""))) for r in people)
    cells += '<div class="q"><h2>%s</h2><p class="ax">influence %s / interest %s</p><ul>%s</ul><p class="n">%d</p></div>' % (
        label, inf, inte, items or "<li class=empty>none yet</li>", len(people))

os.makedirs(os.path.dirname(OUT), exist_ok=True)
open(OUT,"w",encoding="utf-8").write("""<!doctype html><meta charset=utf-8>
<title>Stakeholder Map</title><style>
:root{color-scheme:light dark}
body{font:14px/1.5 -apple-system,system-ui,sans-serif;margin:0;padding:32px;background:#fafafa;color:#1a1a1a}
@media(prefers-color-scheme:dark){body{background:#141414;color:#eee}.q{background:#1e1e1e;border-color:#333}}
h1{font-size:20px;margin:0 0 24px}
.grid{display:grid;grid-template-columns:1fr 1fr;gap:16px;max-width:1100px}
.q{background:#fff;border:1px solid #e2e2e2;border-radius:10px;padding:16px 18px;position:relative}
.q h2{font-size:15px;margin:0 0 2px}
.ax{margin:0 0 12px;font-size:11px;text-transform:uppercase;letter-spacing:.06em;opacity:.55}
ul{list-style:none;margin:0;padding:0}
li{padding:5px 0;border-top:1px solid rgba(128,128,128,.18);display:flex;align-items:center;gap:8px}
li em{opacity:.6;font-style:normal;font-size:12px;margin-left:auto;text-align:right}
.dot{width:9px;height:9px;border-radius:50%;flex:0 0 9px}
.empty{opacity:.4}
.n{position:absolute;top:14px;right:16px;font-size:12px;opacity:.4;margin:0}
.key{margin-top:20px;font-size:12px;opacity:.7}
</style><h1>Stakeholder Map</h1><div class=grid>""" + cells + """</div>
<p class=key>Dot color = relationship. Green strong, grey neutral, amber unknown, red strained.</p>""")
print("wrote", OUT, "with", len(rows), "people")
```

---

## 7. Cursor setup

### Open the vault as a workspace

`File > Open Folder`, select `~/claude/Honeywell/Vault`. Obsidian and Cursor point at the same folder and both write plain files. The only rule: do not have the same file open and unsaved in both at once.

Use **Agent mode** (Cmd+I), not chat. The filing prompt writes to many files in one pass and chat mode will not do that.

### `.cursor/rules/vault.mdc`

This is the contract. It loads on every request, so you never re paste the schema.

```
---
description: Honeywell vault schema and filing rules
alwaysApply: true
---

You are maintaining a personal Obsidian knowledge vault for a Senior Director of
Engineering UX at Honeywell who started in October 2026.

## Absolute rules
1. NEVER delete or rewrite existing content. Append only, inside the marked sections.
2. NEVER invent a fact that is not present in the source text I gave you. If a
   detail is missing, write the field as empty and add a line to "Open questions".
3. Every new person, team, system, ritual or project mentioned gets its own file
   with `status: stub` if it does not already exist. Three lines is enough.
4. If new information contradicts existing information, do NOT resolve it.
   Append both under "Open questions" prefixed with CONFLICT: and flag it in your
   summary.
5. Filenames: `First-Last.md` for people, Title Case with hyphens for everything
   else. Match existing filenames exactly before creating a new one; check for
   name variants (Rav / Ravi / R. Desai) and ask rather than duplicating.
6. All wikilinks in YAML frontmatter must be quoted: `manager: "[[Ravi Desai]]"`.
   Unquoted breaks parsing.
7. Dates are ISO: YYYY-MM-DD.

## Folders
00-Inbox raw dumps · 01-Daily daily notes · 02-People · 03-Teams · 04-Systems
05-Rituals forums and recurring meetings · 06-Projects · 07-Decisions
08-Plan 30/60/90 and evidence · 09-Dashboards queries only, never edit
99-Meta templates, prompts, schema, scripts

## Schema
The frontmatter contract is in 99-Meta/schema.md. Read it before writing any file.

## Commitments
Only commitments go in checkboxes, in this exact form:
- [ ] text [owner:: me|them] [to:: Name] [from:: Name] [due:: YYYY-MM-DD]

## Output
End every run with a changelog: files created, files appended to, stubs created,
conflicts flagged, questions for me. Nothing else.
```

---

## 8. The operating prompts

Save each at the exact filename given, in `99-Meta/prompts/`, because the nightly job and the scheduled tasks load them by name. Paste them into Cursor Agent when you run one by hand. These prompts are the whole operating system. Everything else is storage.

Prompts A, B and C are below. Prompts D (weekly coach), E (monthly calibration) and F (gate interview) are in section 16.

### Prompt A: scaffold the vault (run once, before day one)

File: `99-Meta/prompts/A-scaffold.md`

````
ROLE
You are building a knowledge vault from an empty folder for a Senior Director of
Engineering UX starting at Honeywell in October 2026, who has no org chart and
knows almost nobody.

INPUT
This guide file: Vault-Build-Guide.md (sections 2, 3, 4, 6 are the spec).

TASK
Create the full folder tree from section 2. Then create:
1. 99-Meta/schema.md containing section 3 verbatim.
2. 99-Meta/config.md with: START_DATE, MANAGER, MY_ORG, SBU, and the computed
   dates for day 30, 60 and 90. Leave values blank for me to fill.
3. Every template from section 4 in 99-Meta/templates/.
4. Every dashboard from section 6 in 09-Dashboards/.
5. 99-Meta/scripts/stakeholder_map.py from section 6.
6. 08-Plan/30-60-90.md from section 10 of the guide, with the phase gates and
   exit criteria intact and dates left as placeholders.
7. 08-Plan/discovery-questions.md from section 9 of the guide.
8. 08-Plan/evidence-log.md: an empty table with columns Date, Claim, Source,
   Corroborated by, Confidence.
9. .cursor/rules/vault.mdc from section 7.
10. A single 02-People/_index.md explaining the naming convention.
11. 99-Meta/learned.md, 99-Meta/patterns.md and 08-Plan/predictions.md from
    sections 15.1, 15.3 and 15.2.
12. 99-Meta/scripts/coach_metrics.py from section 16.3, and
    99-Meta/scripts/nightly.sh from section 14.1 marked executable.
13. The six prompt files, verbatim: 99-Meta/prompts/A-scaffold.md,
    B-file-inbox.md, C-weekly-review.md, D-coach-weekly.md, E-coach-monthly.md,
    F-gate-interview.md. Exact filenames, they are loaded by name.
14. Empty directories with a .gitkeep: 08-Plan/coaching/, 08-Plan/reviews/,
    99-Meta/logs/, 00-Inbox/archive/.

CONSTRAINTS
Do not invent any names, teams or systems. The people, team and system folders
stay empty until I meet actual humans.

OUTPUT
The files, then a tree listing and a one line note on anything in the spec you
could not implement.
````

### Prompt B: file the inbox (run at end of every working day, takes 60 seconds)

File: `99-Meta/prompts/B-file-inbox.md`. The nightly job loads this file by name, so do not rename it.

This is the one that keeps the vault alive. Everything else decays without it.

````
ROLE
You are my chief of staff filing today's raw notes into the vault.

INPUT
Every file in 00-Inbox/. Today is <YYYY-MM-DD>.

READ FIRST
99-Meta/schema.md, .cursor/rules/vault.mdc, and the existing filenames in
02-People/, 03-Teams/, 04-Systems/, 05-Rituals/ so you match names instead of
duplicating them.

TASK, in this order
1. Create or open 01-Daily/<today>.md from the daily template. Fill Meetings,
   People met, Commitments made, Commitments received, Decisions observed,
   Signals and Open loops from the raw notes. Set day_number from START_DATE in
   99-Meta/config.md.
2. For every person named: if a file exists, append a dated entry under
   "## 1:1 Log" (newest first) with only what the notes actually say, and update
   last_1on1 if it was a 1:1. If no file exists, create a stub with
   status: stub and whatever fields the notes support.
3. Same for teams, systems, rituals and projects mentioned.
4. Extract every commitment into the daily note in the exact checkbox form, and
   mirror the ones tied to a person into that person's "## Commitments" section.
5. Any decision observed gets a file in 07-Decisions/ with reversible set if the
   notes make it clear, otherwise left blank.
6. Move the processed inbox files into 00-Inbox/archive/<today>/.

FRAMEWORKS to apply while reading
- Separate what was said from what I inferred. Inferences go under Signals, never
  into a person's Snapshot.
- Anything stated by exactly one person is a hypothesis, not a fact. If it lands
  in the evidence log, mark Confidence low until a second independent source.
- A commitment with no named owner and no date is not a commitment. Surface it as
  a question instead of filing it.

OUTPUT
Changelog only: created, appended, stubs, CONFLICTs, and a numbered list of
questions I should answer tomorrow. No prose summary of my day.
````

### Prompt C: weekly review (Friday, 15 minutes)

File: `99-Meta/prompts/C-weekly-review.md`. The weekly coaching task loads this file by name.

````
ROLE
You are auditing my first 90 days for drift and blind spots.

INPUT
01-Daily/ for the last 7 days, all of 02-People/, 05-Rituals/, 08-Plan/,
and 99-Meta/config.md.

ANALYSIS FRAMEWORKS
1. Coverage: which directs, peers and skips have gone past their cadence. Which
   high influence people still have relationship: unknown.
2. Commitment integrity: my open commitments past due, and what I am owed past
   due. Count, do not summarize.
3. Phase fit: am I doing work that belongs to a later phase. Naming week 3
   reorg opinions during a Learn phase is the failure mode. Quote the evidence.
4. Evidence quality: claims in 08-Plan/evidence-log.md still at a single source
   after 14 days. Those are the ones I am about to be wrong about in public.
5. Power map: rituals with decision_rights: decides where my_role is absent, and
   whether that changed this week.
6. Contradiction sweep: every CONFLICT logged this week, still open.

OUTPUT
Write 08-Plan/reviews/<YYYY-MM-DD>-week-N.md with six numbered sections matching
the frameworks above. Every claim cites the file it came from. End with exactly
three actions for next week, ranked, each with a named person and a date.

COMMUNICATION PROTOCOL
Direct, quantitative, no filler. Tell me what I am avoiding. If the data shows I
am on track, say so in one line rather than padding.
````

### Bonus prompt: meeting prep (paste before any meeting with a person you have met before)

````
Read 02-People/<Name>.md and every mention of them in 01-Daily/ from the last 30
days. Give me, in under 150 words: what I owe them, what they owe me, the last
thing they said that I have not acted on, one open question from their file worth
asking today, and anything in their file marked CONFLICT.
````

---

## 9. Cold start: the org discovery protocol

### Context that shapes your first 90 days

You are joining roughly three months after a corporate separation. Honeywell completed the spin off of Honeywell Aerospace on June 29, 2026, and the remaining automation business now operates as **Honeywell Technologies** (Nasdaq: HON), headquartered in Charlotte, CEO Vimal Kapur, around 50,000 employees, organized into three segments: **Buildings**, **Industrial**, and **Process**. Verify all of this on your first day against the internal org site, since post separation structures move fast.

What that means practically for a new Senior Director of Engineering UX:

* The operating model is not settled. Reporting lines, funding and tooling that predate June 2026 may be mid migration. Do not assume any org chart you are handed is current. Date stamp every one you receive.
* Systems are being untangled. Shared design systems, research repositories, tooling licenses and component libraries may still be jointly owned or under transition agreements. Find out in week 1 what your team actually controls versus what it borrows.
* Newly independent companies re examine every central function within 12 months. Your team will be asked to justify its existence in a way it would not have been in a 100,000 person conglomerate. Build the value narrative from day 1, not day 80.
* Three segments means three sets of engineering VPs with different products, different customers, and probably different opinions about design. Find out whether your team is centralized, federated, or chargeback funded before you promise anyone anything.

### The name capture rule

Every human name, team name, system name, acronym and forum you hear gets a file within 24 hours, even if the file is three lines and marked `status: stub`. No exceptions in the first 60 days. The cost of a stub is 15 seconds. The cost of not being able to reconstruct who said what in week 3 is a wrong org decision in month 4.

### The four maps

You are building four different maps and they will not agree with each other. The disagreements are the finding.

| Map | Lives in | Built from | Complete when |
|---|---|---|---|
| Formal org | `03-Teams/`, `manager` and `reports` fields | HR system, org charts | 2 levels up and 2 down from you, plus every peer of your manager |
| Work map | `04-Systems/`, `06-Projects/` | Roadmaps, backlogs, your team's actual calendar | You can name every thing your team touches and its DRI |
| Decision map | `05-Rituals/` | Meeting invites, "who approves this" questions | You know which forum sets roadmap, headcount and quality bar |
| Influence map | `influence` and `relationship` fields | Who gets deferred to in meetings, who gets consulted before decisions | Your high influence quadrant has no `unknown` relationships |

The formal org tells you who reports to whom. The influence map tells you who to convince. In a company three months past a spin off, the gap between them is unusually wide.

### Question bank

Put this in `08-Plan/discovery-questions.md`. Ask the same core questions of everyone so you can compare answers, which is where the signal is.

**Ask everyone (the comparison set)**
1. What is the single biggest thing slowing your team down right now?
2. If you could change one thing about how design and engineering work together here, what would it be?
3. Who do I need to meet that I would not think to ask for?
4. What is the thing everybody knows but nobody says?
5. What has someone in my seat tried before that did not work?

Question 5 is the one that saves you a quarter.

**Your manager**
1. What does success look like at day 90, and who else has to agree that it happened?
2. Which of my predecessors' commitments am I inheriting?
3. What are you personally measured on this year, and which part of it depends on my team?
4. Where do you want me to move fast and where do you want me to wait?
5. What is the budget and headcount calendar, and what is the date after which changes are not possible this cycle?
6. Is there anything about my team I should know before I meet them? **Ask this. Do not write the answer down.** See section 24.

**Directs, first meeting**
1. What do you own, and what do you wish you owned?
2. What is the hardest part of your job that has nothing to do with design?
3. What decisions do you currently have to escalate that you should not have to?
4. Who outside our team do you rely on most, and does that relationship work?
5. How do you want to be managed, and what did your last manager do that you want me to keep or stop?

**Engineering peers (VPs and directors whose roadmaps you staff)**
1. What do you currently ask my team for, and what do you wish you could ask for?
2. Where in your process does design show up, and is that the right point?
3. What would make you say the UX investment paid off this year?
4. How many designers do you think you need, and what is that number based on?
5. What happens today when design and engineering disagree?

Question 1 is diagnostic. What people ask for reveals how they perceive the function. If everyone asks for mockups, you are a service desk. If they ask for problem framing, you are a partner. Log the answers verbatim in the evidence log; the distribution is your baseline metric.

**Cross functional partners: product, program, quality, safety, service**
1. Where does my team create friction for you?
2. What regulatory, safety or certification constraint do designers here get wrong?
3. What does a good handoff from us look like?

**Skip levels (individual contributors, weeks 3 to 6)**
1. What do you spend time on that you think is wasted?
2. What is true about our products that leadership does not seem to know?
3. When was the last time you talked to a real user, and what happened?

### Facts to nail down in week 1

Write these into `99-Meta/config.md` as they land. Each blank is a decision you cannot make until it is filled.

* Which segments does my team serve: Buildings, Industrial, Process, or a mix
* Funding model: central budget, chargeback to segments, or hybrid
* Current headcount, open reqs, contractor versus FTE split, and locations
* Designer to engineer ratio, overall and per program
* Where research sits: in my org, elsewhere, or nonexistent
* Design system: how many exist, who owns them, what is post separation orphaned
* Which forums set roadmap, headcount and quality bar, and whether I am in them
* The annual operating plan calendar and the last date a headcount ask can land
* What my predecessor committed to and to whom
* What tooling my team has and which licenses were tied to the pre spin entity

---

## 10. The 30/60/90

Set `START_DATE` in `99-Meta/config.md`. Everything below is computed from it. Worked example assumes a Monday, October 5, 2026 start.

| Gate | Days | Example date | Phase |
|---|---|---|---|
| Start | 0 | Mon Oct 5, 2026 | |
| Gate 1 | 30 | Wed Nov 4, 2026 | Learn |
| Gate 2 | 60 | Fri Dec 4, 2026 | Diagnose and commit |
| Gate 3 | 90 | Mon Jan 4, 2027 | Deliver proof |

**Calendar warning.** With an October start, your day 60 to 90 window contains the December holiday period, which realistically removes 8 to 10 working days, and it overlaps annual operating plan finalization and the comp and performance cycle. Two consequences. First, treat day 90 as 80 working days, not 90. Second, your headcount and budget ask has a hard deadline set by the AOP calendar, not by your plan. Get that date in week 1 and work backward from it, because if it falls at day 55 then your Learn phase is 45 days long, not 30.

### Phase 1, days 1 to 30: Learn

Announce nothing. Change nothing. Your only output is understanding.

Targets:
* Every direct met 1:1 twice
* 20 stakeholder interviews using the comparison set questions
* Formal org map complete 2 up and 2 down
* Top 5 systems documented with DRI, ux_maturity and design_debt
* Every decision forum in `05-Rituals/` with `decision_rights` and `my_role` set
* One customer or end user session observed, live, not a recording

**Gate 1 exit criterion.** You can state the top 3 problems in one sentence each, and cite 3 independent sources for each one from the evidence log. Not 3 people who all report to the same person. If any problem has fewer than 3 independent sources, it is a hypothesis and it does not go in the day 60 document.

### Phase 2, days 31 to 60: Diagnose and commit

Now you write things down and let people argue with them.

Targets:
* A point of view document in `08-Plan/pov.md`: the 3 problems, the evidence, the 2 bets you propose, and the 1 thing you propose to stop
* Socialized with your manager and at least 5 peers before it goes wide
* Operating model drafted: intake, staffing model, design review cadence, quality bar, escalation path
* Headcount and budget ask sized and submitted to the AOP calendar
* First personnel read complete: who is strong, who is stuck, who is leaving

The "stop" item is not optional. A new leader who only adds is a new leader nobody has to make room for. Naming one thing to stop is the fastest way to find out where the real constraints are, and it buys the capacity for the bets.

**Gate 2 exit criterion.** Your manager and at least 3 peers have agreed in writing (email or a comment on the doc, not a nod in a meeting) that the problem list is right. Agreement on the problems, not yet on the solutions. If you cannot get that, you have a diagnosis problem or a trust problem, and both are worse at day 90.

### Phase 3, days 61 to 90: Deliver proof

Targets:
* One visible win shipped. Small and real beats large and announced. It must be attributable to your team and visible to someone who does not report to you.
* Operating model published and in use for at least 2 weeks
* 12 month plan with the headcount ask, tied to the segment roadmaps
* Every direct has written goals and a stated development path
* Your team can describe your priorities without you in the room

**Gate 3 exit criterion.** A decision has been made on your budget or headcount ask (yes or no both count, silence does not), and at least one artifact your team produced is circulating without you attached to it. The second half is the real test of whether the function is trusted or whether you personally are.

### Evidence log

`08-Plan/evidence-log.md`, one table, appended to continuously.

| Date | Claim | Source | Corroborated by | Confidence |
|---|---|---|---|---|

Rules: one row per claim per source. A claim with one source is `low` confidence no matter how senior the source. Two sources in the same reporting line count as one. The weekly review prompt audits this table, and single source claims older than 14 days are flagged, because those are the ones you are about to be publicly wrong about.

---

## 11. Operating rhythm

| When | Duration | What |
|---|---|---|
| During any meeting | live | Type raw into a new file in `00-Inbox/`. No formatting. |
| Within 5 min of a meeting | 2 min | Write the "My read" line while it is still true. |
| End of day | 60 sec | Run Prompt B in Cursor. Review the changelog. Answer nothing yet. |
| Next morning | 5 min | Answer the questions Prompt B raised. Enrich the top 2 stubs. |
| Monday | 10 min | Open `09-Dashboards/1on1-radar.md` and `commitments.md`. Book what is overdue. |
| Friday | 15 min | Run Prompt C. Read the three ranked actions. Put them in next week. |
| Every 2 weeks | 20 min | Run `stakeholder_map.py`, look at the picture, ask what changed. |
| Day 30, 60, 90 | 60 min | Test the gate exit criterion honestly. Do not advance a phase you did not exit. |

Total steady state cost: about 20 minutes a week plus the 60 seconds a day. If it costs more than that, the system is wrong, not you.

---

## 12. How this fails, and the countermeasure

| Failure | When it shows up | Countermeasure |
|---|---|---|
| Inbox not filed for 4 days | Week 2 | The 60 second rule. Filing is not review. Run it even on a bad day and read the changelog tomorrow. |
| Graph is a hairball | Week 3 | You did not exclude `01-Daily` from the graph filter. Section 5. |
| Every file is a stub | Week 6 | Stubs are fine. Enrich only when a stub becomes relevant to a decision. Use the blind spots dashboard to pick 2 per morning, not 20. |
| AI overwrote a person file | Any time | The append only rule in `.cursor/rules/vault.mdc`. If it happens once, add the file path to a "protected" list in the rules file. Git init the vault so you can recover. |
| Vault becomes a diary | Week 8 | Diaries have no entity files. If `02-People/` is not growing faster than `01-Daily/`, you are journaling, not mapping. |
| Duplicated people | Week 4 | Name variants. The filing prompt is told to check for these. Run a monthly dedupe pass by listing `02-People/` and asking Cursor to flag likely duplicates. |
| It all stops at day 91 | Month 4 | Expected and fine. The 90 day system converts into a permanent 1:1 and commitment tracker. Drop `08-Plan/` rollups, keep People, Rituals, Decisions and the commitment ledger. |

**Version control it.** `git init` in the vault on day 1 and commit nightly. It costs nothing and it is the only real protection against an AI pass that goes wrong. Add `.obsidian/workspace.json` to `.gitignore`.

---

## 13. Build order

Do this in Cursor before your start date. Roughly 90 minutes.

1. Create `~/claude/Honeywell/Vault`, `git init`, open the folder in Cursor.
2. Copy this guide into the vault root so Cursor can read it as the spec.
3. Paste **Prompt A**. Review the tree it produces against section 2.
4. Fill `99-Meta/config.md`: START_DATE and the three gate dates. Leave the rest blank.
5. Open the vault in Obsidian. Install Dataview. Configure daily notes and templates per section 5.
6. Configure the graph filter and the seven color groups. This takes 10 minutes and is the difference between a useful graph and an unusable one.
7. Create `02-People/<Your Manager>.md` and `02-People/<Recruiter>.md` by hand. These are your first two nodes and they prove the schema works.
8. Create three fake inbox files from a meeting you have already had, run **Prompt B**, and check that it appends rather than overwrites. Then delete the fakes and `git commit`.
9. Day 1: start typing into `00-Inbox/`.

Sources for the company context in section 9:
[Honeywell Technologies launches as independent automation company](https://www.honeywell.com/us/en/news/press-releases/2026/06/honeywell-technologies-launches-independent-pure-play-automation-company-following-honeywell-aerospace-spin-off) ·
[Board approves spin off of Honeywell Aerospace](https://www.honeywell.com/us/en/news/press-releases/2026/06/honeywell-board-of-directors-approves-spin-off-of-honeywell-aerospace) ·
[Updated business segment structure](https://investor.honeywell.com/news-releases/news-release-details/honeywell-announces-updated-business-segment-structure-ahead)

---
---

# Part II: Automation, self learning, and the coach

Part I gives you a vault you operate. Part II removes you from the loop wherever a machine can do the job, makes the system get better at filing without you retraining it by hand, and turns the accumulated data into coaching that is specific to you rather than generic new leader advice.

Three layers, and the split between them is deliberate:

| Layer | Runs where | Handles | Why there |
|---|---|---|---|
| **Mechanical** | Your Mac, launchd, no AI | Daily note skeleton, git commit, stakeholder map, metrics, backups | Deterministic. Never fails, never hallucinates, no content leaves the machine. |
| **Filing** | Your Mac, headless Claude Code, corporate account | Turning inbox notes into entity files | Honeywell internal content stays local and under corporate credentials. |
| **Coaching** | Cowork scheduled task, personal account | Weekly and monthly coaching, calibration scoring, pattern mining | Coaching is about your behavior, not Honeywell IP. It reaches your phone and you can argue with it. |

Keep that split. Filing touches program names, people judgments and org structure. Coaching touches your kept rate and your calibration. The first belongs on a corporate account, the second does not need to be there.

---

## 14. Automation layer

### 14.1 The nightly mechanical job

`99-Meta/scripts/nightly.sh`, chmod +x.

```bash
#!/bin/bash
# Nightly pass. Runs on whichever machine holds the operational vault.
set -uo pipefail
export PATH="/opt/homebrew/bin:/usr/local/bin:$HOME/.local/bin:/usr/bin:/bin:/usr/sbin:/sbin"
VAULT="$HOME/claude/Honeywell/Vault"
cd "$VAULT" || exit 1
git rev-parse --git-dir >/dev/null 2>&1 || { echo "NOT A GIT REPO, aborting" >&2; exit 1; }

TODAY=$(python3 -c 'import datetime;print(datetime.date.today())')
mkdir -p 99-Meta/logs 00-Inbox/run 00-Inbox/archive 01-Daily 09-Dashboards
LOG="99-Meta/logs/$TODAY.log"
exec >> "$LOG" 2>&1
echo "=== nightly $(date) ==="

START=$(grep -m1 -E '^START_DATE: [0-9]{4}-[0-9]{2}-[0-9]{2}$' 99-Meta/config.md | awk '{print $2}')
[ -n "$START" ] || { echo "FATAL: config.md needs a line 'START_DATE: YYYY-MM-DD' at column 0"; exit 1; }

# 1. next WORKING day's note. Weekend notes would make signal capture unreachable.
read -r NEXT DAYN < <(python3 -c "
import datetime,sys
s=datetime.date.fromisoformat(sys.argv[1]); d=datetime.date.today()+datetime.timedelta(days=1)
while d.weekday()>4: d+=datetime.timedelta(days=1)
print(d,(d-s).days)" "$START")
if [ ! -f "01-Daily/$NEXT.md" ]; then
  sed -e "s/{{date:YYYY-MM-DD}}/$NEXT/g" -e "s/{{day_number}}/$DAYN/g" 99-Meta/templates/daily.md > "01-Daily/$NEXT.md"
  echo "created 01-Daily/$NEXT.md (day $DAYN)"
fi

# 2. stage the inbox, snapshot BEFORE the AI writes, file, archive only what completed
mv -n 00-Inbox/*.md 00-Inbox/run/ 2>/dev/null
if compgen -G "00-Inbox/run/*.md" > /dev/null; then
  PROMPT=99-Meta/prompts/B-file-inbox.md
  [ -s "$PROMPT" ] || { echo "FATAL: $PROMPT missing or empty. Refusing to run an unconstrained agent."; exit 1; }
  git add -A && git commit -q -m "pre-file $TODAY" || true
  echo "filing $(ls 00-Inbox/run/*.md | wc -l) notes"
  claude -p "$(cat "$PROMPT")

Source directory: 00-Inbox/run/ . Today is $TODAY. Derive each note's date from its own filename, never from today. After you finish filing one file, create <that file>.done beside it." --permission-mode acceptEdits
  for f in 00-Inbox/run/*.md; do
    if [ -f "$f.done" ]; then mkdir -p "00-Inbox/archive/$TODAY"; mv "$f" "$f.done" "00-Inbox/archive/$TODAY/"; fi
  done
  LEFT=$(ls 00-Inbox/run/*.md 2>/dev/null | wc -l)
  [ "$LEFT" -gt 0 ] && echo "WARNING: $LEFT notes unfiled, retrying tomorrow"
else
  echo "inbox empty"
fi

# 3. derived views
python3 99-Meta/scripts/stakeholder_map.py
python3 99-Meta/scripts/coach_metrics.py

# 4. snapshot. The AI pass is isolated between the pre-file commit and this one.
git add -A && git commit -q -m "auto: $TODAY" && echo committed || echo "nothing to commit"
echo "=== done $(date) ==="
```

Notes. Date math goes through python3 rather than `date`, so the script behaves the same on macOS and on any Linux box you later move it to. Run `claude --help` once to confirm the permission flag name on your installed version before you trust the job unattended, and run the script by hand three times before you schedule it.

### 14.2 Schedule it with launchd

`~/Library/LaunchAgents/com.boniface.vault.nightly.plist`

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
  <key>Label</key><string>com.boniface.vault.nightly</string>
  <key>ProgramArguments</key>
  <array>
    <string>/bin/bash</string>
    <string>-lc</string>
    <string>$HOME/claude/Honeywell/Vault/99-Meta/scripts/nightly.sh</string>
  </array>
  <key>StartCalendarInterval</key>
  <dict><key>Hour</key><integer>18</integer><key>Minute</key><integer>45</integer></dict>
  <key>EnvironmentVariables</key>
  <dict><key>PATH</key><string>/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin</string></dict>
  <key>StandardErrorPath</key><string>/tmp/vault-nightly.err</string>
  <key>RunAtLoad</key><false/>
</dict></plist>
```

Load it: `launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/com.boniface.vault.nightly.plist`
Test it now: `launchctl kickstart -k gui/$(id -u)/com.boniface.vault.nightly`
Unload: `launchctl bootout gui/$(id -u)/com.boniface.vault.nightly`

launchd runs a missed calendar job when the Mac wakes, so a closed laptop at 18:45 does not lose the day.

### 14.3 Capture without typing a filename

The friction that kills capture is deciding where to put the note. Remove it. Add to your shell profile:

```bash
vault() { "${EDITOR:-open}" "$HOME/claude/Honeywell/Vault/00-Inbox/$(date +%Y-%m-%d-%H%M)-${1:-note}.md"; }
```

`vault standup` opens a timestamped file instantly. Pair it with a macOS Shortcut bound to a hotkey that creates the same file and opens Obsidian to it, so you can capture from a phone or without a terminal.

Also turn on Obsidian's **Unique note creator** core plugin pointed at `00-Inbox` and bind it to a hotkey. Two capture paths, zero decisions.

### 14.4 Calendar to vault

Your Honeywell calendar will be Microsoft 365, which the vault cannot read directly. Two options that work without any integration:

1. **Manual export, weekly.** Outlook, select the week, File > Save Calendar as .ics, drop it in `00-Inbox/`. The filing prompt reads it and creates ritual files and meeting stubs. One minute a week, and it catches every recurring forum you are in without you listing them.
2. **Better, from day 30.** Once you know which forums matter, `05-Rituals/` is a hand curated set of 15 files, not a calendar mirror. The calendar dump is a week 1 to 4 discovery tool, then you stop.

Do not build a calendar sync. The value is in the 15 curated ritual files, not in mirroring 200 meetings.

---

## 15. The self learning loop

Be precise about what this is. Nothing here retrains a model. What it does is accumulate a correction ledger and feed it into every prompt, so the same mistake is not repeated twice. That is retrieval, and it works, and it compounds. Anyone selling you more than that in a markdown vault is selling you something.

Four mechanisms.

### 15.1 The correction ledger

`99-Meta/learned.md`. Every prompt in this system reads it first. This is the single file that makes the system improve.

```markdown
---
type: meta
description: Corrections and conventions the filing AI must apply. Read before every run.
---

## Vocabulary
<!-- acronyms, product names, internal shorthand -->
- "BA" means Building Automation, never Business Analyst.

## Identity resolution
<!-- name variants that are the same person -->

## Filing rules I have corrected
<!-- format: DATE | what went wrong | the rule now -->

## My conventions
<!-- how I write, what my shorthand means -->
- When I write "??" the preceding line is a hypothesis, not a fact. File it under Open questions.
- When I write "!!" it is a commitment I made out loud. Extract it even if I did not format it.

## Confirmed patterns about me
<!-- promoted here from 99-Meta/patterns.md only after I confirm them -->
```

**The habit.** When the nightly run gets something wrong, do not fix the file and move on. Add one line to `learned.md`. It takes 10 seconds and it is the only thing that stops you re correcting the same error in week 9. Correction without a rule is wasted work.

Shortcut: keep this on a hotkey and type into it.

### 15.2 Predictions and calibration

`08-Plan/predictions.md`. This is the highest leverage thing in the entire system and almost nobody does it.

```markdown
| Made | Prediction | Resolves true if | Conf | Resolve by | Outcome | Correct |
|---|---|---|---|---|---|---|
| 2026-10-14 | Priya pushes back on a formal intake process | she declines it in writing or in a meeting I attend | 0.7 | 2026-11-15 | | |
| 2026-10-16 | Nobody owns the shared design system post spin | no named owner after two weeks of asking | 0.8 | 2026-11-01 | | |
| 2026-10-20 | My headcount ask gets cut by at least half | approved reqs under 50% of the ask | 0.6 | 2027-01-15 | | |
```

Three predictions a week, minimum, written before you find out. Confidence as a decimal. Resolve by date mandatory. Fill Outcome and Correct (yes/no) when the date arrives.

**Why this is the coaching device that matters.** Your job in the first 90 days is to build an accurate model of an organization you have never worked in. Calibration is the only direct measurement of whether that model is right. If you are stating 0.8 confidence and hitting 50%, your read of the org is wrong and you should not be proposing structural change yet, regardless of how confident you feel. That is a falsifiable gate on your own judgment, and it is worth more than any amount of reflection.

Add this to the Gate 2 exit criteria: **at 60 days, resolved predictions at 0.7 confidence or higher must be hitting at least 65%.** If they are not, extend the Learn phase rather than shipping a point of view you will have to walk back.

### 15.3 Monthly pattern mining

The system watches your behavior in the data and proposes patterns. You confirm or reject. Confirmed ones move into `learned.md` and change how the system talks to you.

Proposals land in `99-Meta/patterns.md` with evidence, never asserted as fact:

```markdown
## Proposed 2026-11-03
- **Claim:** commitments made in meetings with more than 6 attendees are kept 40% of the time versus 90% in 1:1s.
  **Evidence:** 01-Daily/2026-10-08, 10-15, 10-22, 10-29. 12 commitments, 5 kept.
  **Status:** unconfirmed
```

You mark it confirmed, rejected, or need more data. Only confirmed patterns get to influence the coach.

### 15.4 Schema evolution

Monthly, the system checks whether the schema still fits reality:

* Fields empty in more than 70% of files: propose deletion. An empty field is a lie about what you know.
* Facts that keep appearing in prose across many files with no field to hold them: propose a new field.
* Enum values you keep writing that are not in the schema: propose adding or standardizing them.

You approve the diff. The schema is a living contract, not a decision you made in September before you knew anything.

---

## 16. The coach

### 16.1 What the coach is and is not

The coach is a weekly and monthly pass over data you generated, scored against thresholds you set in advance. It is not a chatbot that tells you how you feel about your week. Two design rules make the difference:

1. **Every claim cites a file.** If the coach cannot point to `01-Daily/2026-11-12` or a row in the metrics JSON, it does not get to make the claim.
2. **It leads with the gap, not the win.** One line for what is working, then the thing you are avoiding. If the data says you are on track, it says so in one line and stops. Padding a review to fill a template is how coaching becomes wallpaper.

### 16.2 What it measures

All computed by `coach_metrics.py`, all from files you already write. Thresholds are the defaults; tune them in `99-Meta/config.md` after day 30 when you know your own baseline.

| Metric | How it is computed | Target | What a miss means |
|---|---|---|---|
| **Commitment kept rate** | checked / (checked + open past due), `owner:: me` | 85% | The single fastest way to lose trust in a new job. Below 70% at day 30 and your credibility problem is arithmetic, not perception. |
| **Broken commitments** | open, `owner:: me`, past due | 0 | Each one is a named person who noticed. |
| **Delegation ratio** | your open commitments as % of all open | under 60% | Above 70% at day 60 means you are doing the work instead of building the team that does it. |
| **1:1 coverage** | directs within their stated cadence | 100% | The first thing to slip and the last thing anyone tells you about. |
| **Signal capture rate** | daily notes with a non-empty Signals section | 80% | Below 50% means you stopped being surprised, which at day 40 means you stopped looking. |
| **People met, last 7 days** | distinct links under People met | rising to day 30 | A flat curve in week 3 means you are already in the bubble. |
| **Prediction hit rate** | resolved predictions marked correct | 65% | See below. |
| **Overconfidence gap** | mean stated confidence minus hit rate | under 10 points | The most important number in the system. |
| **Unenriched stubs** | `status: stub` anywhere | under 30 | Growing fast is fine to day 30. Growing after day 60 means capture without follow through. |

**On the overconfidence gap.** If you state 80% confidence and hit 55%, the gap is 25 points and your model of this organization is worse than you believe it is. That is not a character flaw, it is the expected state of a newcomer, and it is exactly why you measure it. The consequence is procedural: do not make irreversible structural moves while the gap is above 15 points. Reversible moves are fine and are in fact how you close the gap faster.

### 16.3 `99-Meta/scripts/coach_metrics.py`

Tested against a sample vault. Writes both a markdown dashboard and a JSON file, because the coach prompt reads the JSON and the markdown is for you.

```python
#!/usr/bin/env python3
"""Coaching metrics from the vault.
Writes three files:
  09-Dashboards/coach-metrics.md    for you
  09-Dashboards/coach-metrics.json  numbers only, safe to cross machines
  09-Dashboards/coach-local.md      names, never leaves the managed device
Commitments are counted from 01-Daily only. Person files link, they do not mirror.
"""
import os, re, json, glob, datetime as dt

V = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TODAY = dt.date.today()
WINDOW = 28
CADENCE = {"weekly": 7, "biweekly": 14, "monthly": 30, "adhoc": 60}

def read(p):
    try: return open(p, encoding="utf-8").read()
    except OSError: return ""

def clean(v):
    return re.sub(r"\s+#.*$", "", v).strip().strip('"').strip("'")

def fm(txt):
    m = re.match(r"^---\n(.*?)\n---", txt, re.S)
    if not m: return {}
    out = {}
    for line in m.group(1).splitlines():
        k, sep, v = line.partition(":")
        if sep: out[k.strip()] = clean(v)
    return out

def d(s):
    try: return dt.date.fromisoformat(str(s).strip())
    except Exception: return None

def fdate(path):
    return d(os.path.basename(path)[:-3])

_m = re.search(r"^START_DATE:\s*(\d{4}-\d{2}-\d{2})\s*$", read(os.path.join(V, "99-Meta/config.md")), re.M)
if not _m:
    raise SystemExit("FATAL: 99-Meta/config.md needs a line exactly like 'START_DATE: 2026-10-05' at column 0.")
start = d(_m.group(1))
day_n = (TODAY - start).days

# ---------- commitments, from 01-Daily only ----------
TASK = re.compile(r"^\s*[-*]\s+\[( |x|X|-)\]\s+(.*)$", re.M)
def blank(body): return not re.sub(r"\[[^\]]*\]", "", body).strip()

kept = broken = mine_open = theirs_open = 0
kept28 = broken28 = 0
repeat = {}
for f in glob.glob(os.path.join(V, "01-Daily", "*.md")):
    fd = fdate(f); recent = bool(fd and (TODAY - fd).days <= WINDOW)
    for done, body in TASK.findall(read(f)):
        if done == "-" or blank(body): continue          # cancelled, or an unfilled template placeholder
        mo = re.search(r"\[owner::\s*([^\]]+)\]", body)
        md = re.search(r"\[due::\s*([^\]]+)\]", body)
        mt = re.search(r"\[to::\s*([^\]]+)\]", body)
        owner = mo.group(1).strip().lower() if mo else ""
        due = d(md.group(1)) if md else None
        if owner == "me":
            if done.lower() == "x":
                kept += 1; kept28 += recent
            elif due and due < TODAY:
                broken += 1; broken28 += recent; mine_open += 1
                if mt:
                    who = mt.group(1).strip(); repeat[who] = repeat.get(who, 0) + 1
            else:
                mine_open += 1
        elif owner == "them" and done.lower() != "x":
            theirs_open += 1

def pct(a, b): return round(100 * a / b, 1) if b else None
kept_rate = pct(kept, kept + broken)
kept_rate28 = pct(kept28, kept28 + broken28)
repeat_breaks = sorted([k for k, v in repeat.items() if v >= 2])

# ---------- signals and reach: weekdays only, trailing window ----------
def section(txt, head):
    m = re.search(r"^##\s+" + re.escape(head) + r"\s*$(.*?)(?=^##\s|\Z)", txt, re.M | re.S)
    return re.sub(r"<!--.*?-->", "", m.group(1), flags=re.S).strip() if m else ""

def in_window(p):
    x = fdate(p)
    return bool(x) and x.weekday() < 5 and 0 <= (TODAY - x).days <= WINDOW

weekday_recent = [f for f in glob.glob(os.path.join(V, "01-Daily", "*.md")) if in_window(f)]
sig28 = pct(sum(1 for f in weekday_recent if section(read(f), "Signals")), len(weekday_recent))
people28 = set()
for f in weekday_recent:
    people28 |= set(re.findall(r"\[\[([^\]|#]+)", section(read(f), "People met")))

# ---------- coverage: two full cadence periods, all relations ----------
late = {"direct": [], "peer": [], "skip": [], "manager": []}
for f in glob.glob(os.path.join(V, "02-People", "*.md")):
    p = fm(read(f))
    r = p.get("relation")
    if r not in late or p.get("status") == "departed": continue
    last = d(p.get("last_1on1", ""))
    limit = CADENCE.get(p.get("cadence", "biweekly"), 14)
    over = 999 if not last else (TODAY - last).days
    if over > limit * 2:
        late[r].append((p.get("name") or os.path.basename(f)[:-3], over))

# ---------- calibration by bucket, plus what you are not grading ----------
buckets = {"0.5-0.69": [0, 0], "0.7-0.89": [0, 0], "0.9+": [0, 0]}
unresolved_overdue = 0
for line in read(os.path.join(V, "08-Plan/predictions.md")).splitlines():
    if not line.strip().startswith("|"): continue
    c = [x.strip() for x in line.strip().strip("|").split("|")]
    if len(c) < 7: continue
    try: conf = float(c[3])
    except (ValueError, IndexError): continue
    resolve_by, correct = d(c[4]), c[6].lower()
    if correct in ("yes", "no"):
        b = "0.9+" if conf >= 0.9 else "0.7-0.89" if conf >= 0.7 else "0.5-0.69"
        buckets[b][0] += 1; buckets[b][1] += correct == "yes"
    elif resolve_by and resolve_by < TODAY:
        unresolved_overdue += 1
resolved = sum(v[0] for v in buckets.values())
hit_all = pct(sum(v[1] for v in buckets.values()), resolved)

M = [
    ("day_number", day_n, "", ""),
    ("kept_rate_28d", kept_rate28, 85, "pct"),
    ("kept_rate_life", kept_rate, "", ""),
    ("repeat_breaks", len(repeat_breaks), 0, "countlow"),
    ("open_mine", mine_open, "", ""),
    ("open_theirs", theirs_open, "", ""),
    ("signal_rate_28d", sig28, 70, "pct"),
    ("people_met_28d", len(people28), "", ""),
    ("directs_late", len(late["direct"]), 0, "countlow"),
    ("peers_late", len(late["peer"]), "", ""),
    ("skips_late", len(late["skip"]), "", ""),
    ("predictions_resolved", resolved, "", ""),
    ("predictions_unresolved_overdue", unresolved_overdue, 2, "countlow"),
    ("hit_rate_all", hit_all, "", ""),
]

def flag(v, t, k):
    if v is None or t == "": return ""
    return ("ok" if v >= t else "LOW") if k == "pct" else ("ok" if v < t + 1 else "HIGH")

rows = "\n".join("| %s | %s | %s | %s |" % (n, "n/a" if v is None else v, t, flag(v, t, k)) for n, v, t, k in M)
bk = "\n".join("| %s | %d | %s |" % (b, v[0], pct(v[1], v[0]) if v[0] else "n/a") for b, v in buckets.items())
note = ("\n> Calibration below 20 resolved predictions is not a signal. "
        "Resolved so far: %d.\n" % resolved) if resolved < 20 else "\n"

os.makedirs(os.path.join(V, "09-Dashboards"), exist_ok=True)
open(os.path.join(V, "09-Dashboards/coach-metrics.md"), "w", encoding="utf-8").write(
    "---\ntype: dashboard\ndescription: Generated by coach_metrics.py. Do not edit.\n---\n\n"
    "# Coach metrics\n\nGenerated %s, day %s\n\n| Metric | Value | Target | Flag |\n|---|---|---|---|\n%s\n\n"
    "## Calibration by confidence bucket\n\n| Bucket | Resolved | Hit rate |\n|---|---|---|\n%s\n%s"
    % (TODAY, day_n, rows, bk, note))

open(os.path.join(V, "09-Dashboards/coach-local.md"), "w", encoding="utf-8").write(
    "---\ntype: dashboard\ndescription: Names. Managed device only. Never crosses machines.\n---\n\n"
    "# Who is late\n\n" + ("\n".join(
        "## %s\n%s" % (r, "\n".join("- %s, %d days" % (n, o) for n, o in sorted(v, key=lambda x: -x[1])) or "none")
        for r, v in late.items())) +
    "\n\n# Commitments broken twice to the same person\n" + ("\n".join("- " + n for n in repeat_breaks) or "none") + "\n")

json.dump({n: v for n, v, _, _ in M},
          open(os.path.join(V, "09-Dashboards/coach-metrics.json"), "w"), indent=2)
print("coach_metrics: day %s, kept28 %s%%, directs late %d, resolved predictions %d"
      % (day_n, kept_rate28, len(late["direct"]), resolved))
```

Requires Python 3.9 or later for the dict merge operator. `python3 --version` to check.

### 16.4 Prompt D: the weekly coach

Runs Friday, after Prompt C. File: `99-Meta/prompts/D-coach-weekly.md`, loaded by name by the weekly coaching task.

````
ROLE
You are my executive coach for the first 90 days of a Senior Director of
Engineering UX role at Honeywell Technologies, an automation company that became
independent in June 2026. You have full read access to my vault. You are not my
assistant and not my cheerleader. Your job is to tell me what the data says,
especially the part I would rather not look at.

DOCUMENT REVIEW
Read, in this order:
1. 09-Dashboards/coach-metrics.json  (the numbers)
2. 08-Plan/reviews/<most recent>.md  (this week's audit from Prompt C)
3. 01-Daily/ for the last 7 days     (what actually happened)
4. 08-Plan/30-60-90.md               (which phase I am in and its exit criteria)
5. 08-Plan/predictions.md            (my calibration)
6. 99-Meta/learned.md                (confirmed patterns about me)
7. 99-Meta/config.md                 (my thresholds, which override the defaults)

ANALYSIS FRAMEWORKS
1. Situation type. Classify my situation on the Watkins STARS model: startup,
   turnaround, accelerated growth, realignment, sustaining success. A function
   inside a three month old independent company is usually realignment or
   accelerated growth, and those need opposite playbooks. State which one the
   week's evidence supports, cite it, and say if the evidence changed.
2. Capital account. Score three separately: technical credibility, managerial
   credibility, political capital. Which am I spending, which am I building, and
   is the mix right for my phase and situation type.
3. Threshold breaches. Every metric flagged LOW or HIGH in the JSON. For each,
   name the specific people or files behind the number. "Kept rate 62%" is
   useless. "Kept rate 62%, the three misses were all to Priya Nair" is a finding.
4. Phase discipline. Am I doing work that belongs to a later phase. Quote the
   evidence line. Early structural opinions during a Learn phase are the most
   common and most expensive failure mode for a senior hire.
5. Calibration consequence. If the overconfidence gap is above 15 points, name
   the specific decision this week that I should not have made yet, or confirm
   there was none.
6. Avoidance. Find the thing present in my notes that I have not acted on: a
   person mentioned repeatedly with no 1:1 booked, a conflict logged twice and
   never resolved, a commitment quietly rolled forward three weeks. Name it.
7. Imported playbook check. I ran a design org at a government SaaS company and
   before that industrial IoT at GE and Rheem. Flag anywhere I applied a prior
   playbook to this org without evidence it fits here.

OUTPUT FORMAT
Write to 08-Plan/coaching/<YYYY-MM-DD>-coach.md, at most 600 words:
- Line 1: situation type and confidence, one sentence.
- "Working" : one line, only if true.
- "The gap" : the single most important thing, with evidence and the cost of
  leaving it another week.
- "Threshold breaches" : table of metric, value, the named people or files.
- "What you are avoiding" : one paragraph.
- "Three moves next week" : ranked, each with a named person and a date.
- "One question to sit with" : a real question, not a prompt for reflection.

COMMUNICATION PROTOCOL
Direct, quantitative, zero filler. No preamble, no summary of my week back to me,
no encouragement paragraph. Never open with praise. If the data says I am on
track, say so in one line and make the review short. Every claim cites a file.
If a metric is n/a because I did not capture the data, say that instead of
inferring. Disagree with me where the evidence supports it, including with
anything in 99-Meta/learned.md.
````

### 16.5 Prompt E: monthly calibration and pattern mining

First of each month. File: `99-Meta/prompts/E-coach-monthly.md`, loaded by name by the monthly task.

````
ROLE
Monthly audit of my judgment and of this system's accuracy. Two subjects: how
good my predictions were, and how good the vault's own filing has been.

DOCUMENT REVIEW
08-Plan/predictions.md, 08-Plan/evidence-log.md, all of 01-Daily/ for the month,
02-People/, 05-Rituals/, 99-Meta/learned.md, 99-Meta/patterns.md,
09-Dashboards/coach-metrics.json, and the four weekly coaching notes.

ANALYSIS FRAMEWORKS
1. Calibration. All predictions resolved this month, bucketed by stated
   confidence (0.5 to 0.6, 0.6 to 0.8, above 0.8). Hit rate per bucket. Name the
   bucket where I am most wrong, and the topic area where I am most wrong. I care
   more about which subjects I misjudge than the overall number.
2. Belief revision. Claims in evidence-log.md that were high confidence a month
   ago and are now contradicted. Each one is a lesson; state what the tell was
   that I missed at the time.
3. Pattern mining. Propose at most 5 patterns about my behavior, each with file
   citations and a count. Candidates: which meeting types produce commitments I
   do not keep, whose requests I defer, which topics I avoid writing Signals
   about, whether my 1:1 quality drops in weeks with more than N meetings. Write
   them to 99-Meta/patterns.md as unconfirmed. Do not assert them elsewhere.
4. Filing accuracy. Where did the nightly filing get things wrong this month,
   based on entries in learned.md and on files I edited by hand after a run.
   Propose specific additions to learned.md and to .cursor/rules/vault.mdc.
5. Schema evolution. Frontmatter fields empty in more than 70% of files, propose
   removal. Facts recurring in prose with no field, propose a field. Enum values
   in use that are not in the schema, propose standardizing.
6. Source diversity. In evidence-log.md, how many of my "corroborated" claims are
   corroborated by people in the same reporting line. Those are not corroborated.

OUTPUT
Write 08-Plan/coaching/<YYYY-MM>-monthly.md. Sections matching the six frameworks.
End with a diff proposal, not applied: the exact lines to add to learned.md, the
exact schema changes, and the exact rules file changes. I approve them, you do
not apply them yourself.

COMMUNICATION PROTOCOL
Same as the weekly coach. The most valuable output here is the topic area where I
am reliably wrong. Lead with that.
````

### 16.6 Prompt F: the gate interview

File: `99-Meta/prompts/F-gate-interview.md`. Run at day 30, 60 and 90, before you let yourself advance a phase. This one is adversarial on purpose.

````
ROLE
You are interviewing me on whether I have actually met the exit criterion for the
phase I claim to be finishing. Assume I want to advance and am motivated to
overstate my readiness. Your job is to check the evidence, not my confidence.

DOCUMENT REVIEW
08-Plan/30-60-90.md for the exit criterion, 08-Plan/evidence-log.md,
08-Plan/predictions.md, 09-Dashboards/coach-metrics.json, all of 01-Daily/,
02-People/, 05-Rituals/.

TEST, criterion by criterion
Gate 1: for each of my three stated problems, list the three sources. Reject any
source that reports to the same person as another source for the same problem.
State per problem: PASS or FAIL with the source count.
Gate 2: find the written agreement from my manager and three peers. A meeting
where nobody objected is not agreement. Quote the file and line, or FAIL.
Also check the day 60 calibration bar: resolved predictions at 0.7 or above must
be hitting 65% or better.
Gate 3: name the visible win, who outside my reporting line saw it, and the
artifact circulating without me attached. Name the budget or headcount decision
and its date. Silence is FAIL, not pending.

OUTPUT
A PASS or FAIL per criterion with the evidence, then one of exactly two verdicts:
ADVANCE, or HOLD with the shortest path to passing and a date.

COMMUNICATION PROTOCOL
No hedging, no partial credit, no encouragement. If I fail a gate, the useful
output is the shortest path to passing it, not reassurance that I am close.
````

---

## 17. Scheduled tasks

These run in Cowork on a schedule, bind to your Mac, read the vault through the connected folder, and deliver output to your phone. They are the layer that means you do not have to remember to run anything.

Each run starts a fresh session with no memory of any previous one, so every prompt is written standalone and every prompt begins by checking that the vault exists and exiting quietly if it does not. That guard is what lets these be created before your start date without generating noise for a month.

| Task | Schedule | Does |
|---|---|---|
| **Morning brief** | Weekdays 07:15 ET | Recomputes metrics, pushes counts and threshold breaches, and confirms the nightly job actually ran. Counts, never names. |
| **Weekly heartbeat** | Saturdays 08:00 ET | Reads the numbers file only. Flags threshold breaches and a stalled nightly job. The coaching itself runs locally on the managed device. |
| **Monthly calibration** | 1st of month 08:00 ET | Calibration scoring, pattern mining, filing accuracy, schema evolution. Writes a diff proposal you approve. |
| **Gate interviews** | One shot at day 30, 60, 90 | The adversarial gate check. Created once you confirm your start date. |

**Daylight saving.** Schedules are stored in UTC. These are set for Eastern Standard Time, which covers most of your first 90 days. Between now and November 1, 2026 they fire one hour later than the times above. After November 1 they are exact.

**Where the boundary sits.** These tasks read the vault, which contains Honeywell internal content. If your corporate policy requires internal content stay under corporate credentials, keep the scheduled tasks scoped to the metrics JSON and the coaching files only, and let the local nightly job do everything that touches person and program files. `09-Dashboards/coach-metrics.json` contains numbers and direct report first names, nothing else. Decide this in week 1 after reading the data privacy and IP documents in `Onboarding/`.

---

## 18. Build order, revised

Before your start date, about two hours total.

**Part I, the vault (90 minutes)**

1. `mkdir -p ~/claude/Honeywell/Vault && cd $_ && git init`
2. Copy this guide into the vault root. Open the folder in Cursor.
3. Run **Prompt A**. Check the tree against section 2.
4. Fill `99-Meta/config.md`: START_DATE and the three gate dates.
5. Obsidian: open vault, install Dataview, set daily notes and templates per section 5.
6. Configure the graph filter and the seven color groups. Ten minutes, high payoff.
7. Create your manager's person file by hand. First real node.
8. Run **Prompt B** against three fake inbox files. Confirm it appends and does not overwrite. Delete the fakes, commit.

**Part II, the automation (30 minutes)**

9. Create `99-Meta/learned.md`, `99-Meta/patterns.md`, `08-Plan/predictions.md` and `08-Plan/evidence-log.md` from sections 15 and 10.
10. Save `99-Meta/scripts/coach_metrics.py` from section 16.3 and run it once. It will report mostly `n/a`, which is correct on an empty vault.
11. Save `99-Meta/scripts/nightly.sh`, chmod +x, run it by hand three times.
12. Install the launchd plist. Kickstart it once and read `99-Meta/logs/`.
13. Add the `vault()` shell function and an Obsidian hotkey for the inbox.
14. Save prompts D, E and F into `99-Meta/prompts/`.
15. Confirm your start date so the gate interview tasks can be scheduled.

**Day 1**: type into `00-Inbox/`. Everything else runs itself.

---

## 19. What a fully running week looks like

| | You do | The system does |
|---|---|---|
| Mon 07:15 | Read a 5 line brief on your phone | Recomputed every metric, found who is overdue |
| Mon to Fri, in meetings | Type badly and fast into `00-Inbox` | |
| Mon to Fri, +5 min | One line: "My read" | |
| Mon to Fri 18:45 | Nothing | Files the inbox into daily note, people, teams, systems, decisions. Creates stubs. Rebuilds the stakeholder map and the metrics. Commits to git. |
| Tue to Fri 07:15 | Answer 2 questions the filing raised | Brief again |
| Weekly, 3 min | Write 3 predictions with confidence and a resolve date | |
| When the AI is wrong, 10 sec | One line into `learned.md` | Applies it forever after |
| Fri 16:30 | Read 600 words. Argue with it if it is wrong | Audits, coaches, writes the note, pushes the three moves |
| 1st of month, 15 min | Approve or reject a diff | Scores your calibration, mines patterns, proposes schema changes |
| Day 30, 60, 90 | Answer the gate interview honestly | Tests your evidence against the exit criteria and returns ADVANCE or HOLD |

Your total input is the typing you would do anyway, plus roughly 25 minutes a week. Everything else is generated from what you already wrote.

The one thing that cannot be automated is the ten second habit of adding a line to `learned.md` when the system gets something wrong. That single habit is the difference between a vault that decays and a vault that gets sharper every week.

---

## 20. Two machines: personal and Honeywell issued

Yes, syncing is technically easy. The technical question is not the one that matters. The one that matters is which machine is allowed to hold Honeywell content and where the sync endpoint sits, and that is answered by your IP agreement and your IT policy, not by Obsidian.

### The recommendation: split the vault, do not sync it

Two vaults with one narrow seam between them.

**Layer A, the operational vault.** `00-Inbox`, `01-Daily`, `02-People`, `03-Teams`, `04-Systems`, `05-Rituals`, `06-Projects`, `07-Decisions`. This is Honeywell content: names, org structure, program status, judgments about people. It lives on the Honeywell machine only and syncs only through company approved storage. It never touches a personal device or a personal cloud account.

**Layer B, the career vault.** `08-Plan` (your 30/60/90, predictions, calibration, coaching notes) and the parts of `99-Meta/learned.md` that describe your own habits rather than Honeywell vocabulary. No Honeywell names, no program names, no org structure. This is yours, it is about how you work, and it follows you to the job after this one.

**The seam.** `09-Dashboards/coach-metrics.json` is derived numbers plus the first names of overdue directs. Add an anonymizing mode to `coach_metrics.py` that replaces names with P1, P2, P3 before the file crosses to the personal side. The coaching layer then runs on numbers alone with zero Honeywell identifiers in it. That is the only file that needs to move between machines, and it is a few hundred bytes.

This split is not a compromise forced by policy. It is the correct design anyway. Your operational knowledge of one employer is theirs and it goes stale the day you leave. Your calibration record and your kept rate are yours and they compound across your whole career.

### If you do want one synced vault, ranked

| Method | Conflict safety | Policy risk | Notes |
|---|---|---|---|
| Company OneDrive or SharePoint, work machine only | medium | lowest | No cross device sync of Honeywell content at all. Simplest defensible answer. |
| Git remote on company GitHub Enterprise or Azure DevOps | highest | low, once approved | Explicit commits, real history, no silent overwrites. Best option if IT allows a repo. |
| Obsidian Sync, paid, end to end encrypted | high | needs approval | A third party processor holding company data. Ask, do not assume. |
| Personal iCloud, Dropbox or Google Drive | medium | high | Do not put Honeywell content here. |
| Personal GitHub, even a private repo | highest | high | Same answer. A private repo on a personal account is still off company systems. |

### Practical gotchas

* Obsidian on any file sync service produces "conflicted copy" duplicates when two machines write the same note. Exclude `.obsidian/workspace.json` from sync at minimum. Git avoids the problem entirely because commits are explicit.
* A corporate managed Mac will likely have MDM, disk encryption enforcement, DLP and restricted install rights. Obsidian, Cursor, git, python3 and Claude Code may each need approval. Make that one IT request in week 1, not five requests across two months.
* Do not symlink a personal folder into a company sync folder or the reverse. DLP tooling reads that as exfiltration and you will be having a conversation you do not want to have in week 3.
* Check whether your agreement treats notes you write about company matters as company property. Most do. That does not stop you keeping them, it determines where they may live.

### What this changes about the automation

The three scheduled tasks are bound to your personal MacBook and read `~/claude/Honeywell/Vault`. If Layer A moves to the Honeywell machine, they lose sight of it. The fix follows the split cleanly:

* The launchd nightly job and the headless Claude Code filing move to the Honeywell machine, operating on Layer A. That is where the content is and where it should be processed.
* The three coaching tasks stay on the personal machine, reading Layer B plus the anonymized metrics file.
* Whether the Claude desktop app is permitted on the corporate device is its own IT question. If it is not, the filing step runs as a local script under whatever AI tooling Honeywell has approved, and the rest of the design is unchanged.

### Sequence

1. **Now to day 1.** Everything on the personal machine. There is no Honeywell content in it yet, so there is nothing to get wrong.
2. **Day 1.** Read the real IP agreement and data privacy policy. Note: the two files currently in `Onboarding/` (`IP .html` and `Data privacy.html`) are empty loading shells, roughly 6 KB each with no document text in them. Get the actual documents.
3. **Week 1.** One IT request: Obsidian, Cursor, git, python3, Claude Code or the approved equivalent, confirmation of which storage is sanctioned for working notes, and whether a Honeywell GitHub Enterprise or Azure DevOps instance is available for a private repo. See section 29.
4. **Week 2.** Split. Layer A onto the work machine, Layer B stays personal, the anonymized metrics file is the only thing that crosses.

Until step 2 is done, keep every Honeywell name out of the personal vault. It costs you nothing in week 1, when you have barely any names anyway, and it means you never have to unwind a mistake.

---
---

# Part III: Post review revisions

Four independent reviews of Parts I and II: architecture and failure modes, technical correctness (scripts executed against fixtures, tool behavior verified against current documentation), leadership efficacy and adoption, and security and data boundary. This part records what changed and supersedes the earlier parts wherever they conflict.

## 21. What the review changed

### Fixed in place, already corrected above

| Defect | Where it was | What it would have done |
|---|---|---|
| Inline YAML comments in the schema | §3 | `relation: direct   # direct \| manager` parses as the literal string. Every direct report would have been invisible to the metrics, coverage would read `n/a`, and the coach is instructed to report `n/a` as "you did not capture the data". You would have been told you have no team. |
| Commitments counted twice | §16.3 | Prompt B mirrors commitments into person files and the script globbed both folders. Kept rate reported 62.5% where truth was 66.7%. Now counted from `01-Daily` only. |
| Template placeholders counted as real commitments | §4, §16.3 | Every daily note shipped a live empty checkbox, adding one phantom open commitment per day per side. By day 60 the delegation ratio was pinned near 50% regardless of behavior. Placeholders are now comments. |
| No transaction boundary on the nightly AI pass | §14.1 | A crash after filing 4 of 6 notes archived nothing, so the next run refiled all 6 against the wrong date, duplicating 1:1 log entries and commitments. Now: files staged into `00-Inbox/run/`, a `pre-file` git commit before the AI writes, per file `.done` markers, and only completed files archived. The AI pass is now an isolated revertible diff. |
| A missing prompt file launched an unconstrained agent | §14.1 | `cat` of a renamed prompt file failed silently, so `claude -p ""` ran write enabled against the vault with no schema and no append only rule. Now a hard guard that refuses to run. |
| launchd PATH | §14.2 | `bash -lc` reads `~/.bash_profile`, not `~/.zprofile`, so `/opt/homebrew/bin` was absent and `claude` would not have been found. PATH now set in the plist. |
| Dataview `.days` is month normalized | §6 | A direct 45 days overdue displayed as 15 and sorted below one at 25 days. The radar sorted the wrong people to the top. Now sorts on the bare date. |
| `status:stub` graph group | §5 | Not Obsidian property syntax, matched nothing. Now `["status":"stub"]`. |
| `medium` influence vanished | §3, §6 | The 2x2 tested only high and low, so a person marked medium disappeared from your flagship stakeholder artifact with no error. `medium` is removed from the schema and the script now has an Unclassified cell that catches anything unset. |
| Bidirectional relation fields | §3 | `manager` and `reports` must agree, but an append only filer can add an edge and never remove one, so a person who changes teams shows as a phantom report forever. Child side edges only now, reverse derived in Dataview. |
| Six smaller script and query defects | §6, §16.3 | Non numeric confidence silently dropped a prediction from the hit rate, past due own commitments were excluded from the delegation count, stub counting missed nested folders, `design_debt` and `relationship` sorted alphabetically rather than by severity, and both scripts crashed if `09-Dashboards/` did not exist. All fixed and rerun against fixtures. |

The corrected `coach_metrics.py` was executed against a fixture vault covering every one of these cases and hand checked. Placeholders skipped, cancelled tasks skipped, YAML comments stripped, a person file with no frontmatter skipped without crashing, an apostrophe in a name escaped correctly, an empty date field treated as never met.

### Changed by design, in the sections below

1. Days 1 to 30 run in degraded mode. Section 22.
2. Voice becomes the primary capture path. Section 23.
3. An external feedback loop is added, and it is now the most important thing in the system. Section 24.
4. The metric set is cut from nine to seven and every threshold is retargeted. Section 25.
5. The calibration gate is deleted and replaced with a disagreement test. Section 25.
6. The data boundary becomes structural rather than habitual. Section 26.
7. Four missing discovery items added. Section 27.

---

## 22. Days 1 to 30 run in degraded mode

The build order in section 18 assumed Cursor, Claude Code, git and python3 on a machine you will not have. Realistic provisioning at a 50,000 person company three months past a separation is two to six weeks, and it may be refused. That window is exactly days 1 to 30, when capture matters most and when losing names is unrecoverable.

**Assume no tooling until it exists.** Degraded mode is deliberately crude:

* One plain markdown file per day. Any editor, including TextEdit or the notes app on a company laptop.
* One file called `people.md`, a single table: Name, Role, Team, What they own, Last talked, Next step. Append a row the first time you hear a name.
* Commitments in one list at the bottom of the daily file, in the same `[owner:: me] [due:: date]` format, because it costs nothing now and parses later.
* Friday, 20 minutes: read the week, move anything durable into `people.md`, write three predictions.

That is the whole system. It captures 80% of the value of the full vault, and everything in it converts cleanly when the tooling lands.

**Automate at day 31, not day 1.** When the tooling is approved, one Cursor pass converts `people.md` into person files and the daily files into the vault structure. Nothing is lost by waiting, and a system that fails in week 2 because IT said no is worse than no system.

**What to cut first on a bad week**, in this order: the stakeholder HTML, the graph configuration, pattern mining, schema evolution, the calendar import, the weekly coach. What never gets cut: capture, and the commitment ledger. If you are only doing two things, do those two.

---

## 23. Capture is voice first

The design assumed you type during meetings. In twenty discovery interviews with VPs you have never met, you will not type, and back to back calendars remove the five minute window after. That single assumption was load bearing and it was wrong.

**The primary path.** Ninety second voice memo the moment a meeting ends, walking to the next one. Say the date, who was in the room, what surprised you, what you committed to and by when, and any name you heard for the first time. Transcribe it into `00-Inbox/` automatically: macOS dictation, a Shortcut that writes the transcript to the inbox folder, or a recorder app that exports text. Typing becomes the fallback, not the default.

**Why this specific shape.** The filing prompt needs five things: date, attendees, commitments with owner and date, new names, and your read. Saying them out loud in a fixed order takes ninety seconds and produces better raw material than notes typed while trying to listen. The one line that matters most is the last one: what surprised you. Say it before you rationalize it.

---

## 24. The external feedback loop

This is the largest gap the review found, and it is worth more than everything in Part II combined.

The system as designed had nine metrics, three coaching prompts, three gates, and not one data point from another human about how you are doing. You would be grading your own homework for 90 days while being evaluated on something else entirely.

**The mechanism.** At day 30, 60 and 90, send one written question to your manager, three peers, and your HR business partner:

> I am 30 days in. What is one thing I should be doing differently? Direct is more useful to me than kind.

Written, not verbal, because verbal answers are polite and unquotable. Five recipients, three times. Fifteen data points, and the delta between day 30 and day 60 tells you whether you changed anything.

File the answers verbatim in `08-Plan/external/<date>-<role>.md`, no interpretation. Then add one field to the metrics:

* **external_asks_sent** and **external_asks_returned** per gate. If returned is under 3, you have a different problem than anything the dashboard measures.

**The rule that makes it work.** The weekly coach and the gate interview must read `08-Plan/external/` and weight it above every internal metric. Add this line to Prompt D's document review list and to Prompt F:

```
0. 08-Plan/external/  All external feedback. If anything here contradicts my own
   notes or the metrics, the external source wins and you say so explicitly.
```

Self report loses to external report. Always. That one line converts the coaching layer from a mirror into something that can actually correct you.

---

## 25. Revised metrics and gates

### The metric set, cut from nine to seven

| Metric | Target | Change and why |
|---|---|---|
| **kept_rate_28d** | 85% | Now a trailing 28 day rate. The lifetime version could not be moved by a good week after day 60, so it stopped being actionable. Lifetime kept as context only, with no flag. |
| **repeat_breaks** | 0 | New, and it replaces "broken commitments = 0". Breaking one commitment is normal. Breaking two to the **same person** is the actual trust event, and it is the only broken commitment number worth a flag. Names live in `coach-local.md`. |
| **signal_rate_28d** | 70% | Weekdays only and trailing 28 days. The old version created weekend notes that could never contain a signal, capping the metric at about 71% against an 80% target, so it was permanently red by construction. |
| **directs_late** | 0 | Retargeted from "coverage = 100%" to "no direct exceeds two full cadence periods". A 100% target flags a 1:1 moved by one day, which trains you to ignore the number. |
| **peers_late**, **skips_late** | context, no flag | New. Peer and skip conversations are what actually slip, and nothing measured them. |
| **predictions_unresolved_overdue** | under 3 | New. You will resolve the predictions you remember, which are the memorable ones, which skews the hit rate upward. This counts the ones you are quietly not grading. |
| **hit_rate by confidence bucket** | context, no flag | See below. |

**Deleted outright:** delegation ratio (measured recorded commitments, not delegation, and punished correct week 2 behavior), broken commitments as a raw count (redundant with kept rate, and unreachable), unenriched stubs (a target that directly contradicts principle 1, since optimizing it means capturing less), people met as a rising target (correct for 30 days, actively wrong after, when depth on eight people beats breadth), and overconfidence gap as a threshold (dominated by which predictions you choose to write down).

### The calibration gate is deleted

Part II made calibration a hard gate: no irreversible structural moves above a 15 point overconfidence gap, and Gate 2 closed unless 0.7+ predictions hit 65%. The statistics do not support that.

Three predictions a week with resolve dates two to six weeks out yields roughly 12 to 16 resolved by day 60, of which maybe 8 to 10 sit in the 0.7+ band. At n equals 9, six hits is 67% and five is 56%, so one prediction flips the gate. The confidence interval around 6 of 9 runs from roughly 35% to 88%. Distinguishing a 50% forecaster from a 65% one takes on the order of 80 to 100 resolved predictions at that band, which arrives around month 8. And you author, confidence rate and grade your own predictions while knowing the gate depends on them.

**Keep the predictions, delete the gate.** The practice is valuable: writing a falsifiable claim before you learn the answer is how you find out your model is wrong, and the metrics script now reports hit rate by bucket with an explicit warning below 20 resolved. It is an observation, not a threshold. Two changes make the practice honest:

1. A mandatory **"Resolves true if"** column. "Priya pushes back" is not falsifiable. "Priya declines it in writing or in a meeting I attend" is. Already added to the table in section 15.2.
2. Overdue unresolved predictions are counted, so quietly dropping the ones you got wrong shows up.

### What replaces it at Gate 2

**The disagreement test.** For each of your three stated problems, name the most senior person who disagrees with you, and state their case in terms they would accept as fair.

If you cannot name a dissenter, you have not talked to enough people or you have been talking past them. If you can name one but cannot state their case fairly, you do not understand the objection and it will surface later at a worse time. This tests the same thing calibration was meant to test, works at n equals 3, and cannot be graded by you alone because the dissenter can check your summary.

Add to Prompt F, Gate 2: `For each problem, the file and line naming the dissenter and their case. Missing dissenter is FAIL.`

### Two prompt fixes

* **Prompt D framework 2, the capital account.** Delete the instruction to score technical credibility, managerial credibility and political capital. The vault contains no data on how anyone perceives you, so the model would generate three confident numbers out of your own notes. Replace with: *"cite the specific evidence of how each named stakeholder reads me, or state plainly that none exists."* Once section 24 is running, that evidence exists.
* **Prompts D and E, person level findings.** Add a hard rule: no claim about a named person's motives, competence or reliability below three independent observations across two or more dates, and every person finding must be phrased as a question to ask them, not a conclusion about them. A file citation makes three data points feel like a finding, and acting on that with someone you have known five weeks is the most likely way this system does you harm.
* **Prompt D output.** Add: *"If no threshold is breached and no avoidance item clears three observations, output exactly 'No finding this week' plus the three moves."* The instruction to always lead with a gap guarantees a manufactured finding in weeks that do not have one.
* **Timing.** Move the weekly coach from Friday 16:30 to Saturday 08:00. At 16:30 the 18:45 filing has not run, so every weekly review saw Friday as an empty day.

---

## 26. The data boundary becomes structural

Section 20 proposed splitting the vault and claimed the coaching layer touches only your behavior. The review found that claim contradicted by my own prompts. Prompt D orders reading `01-Daily/` for the last 7 days, the Prompt C review (which reads all of `02-People/`), and `learned.md`. So a Friday task on a personal account would have ingested a week of named 1:1 notes and program status. That was a real design error, not a theoretical one.

The fix is to make the boundary structural, so it holds without you maintaining a habit.

### Five changes

**1. The crossing file carries integers only.** `coach-metrics.json` now contains no names at all, not even anonymized ones. P1, P2, P3 does not de identify a team of eight: a stable mapping plus dates, cadences and a narrative coaching note written by the same account is trivially re identifiable, and under GDPR that is pseudonymized personal data, still fully in scope. `overdue_directs` as a list is gone; `directs_late` as an integer replaces it. All names now go to `09-Dashboards/coach-local.md`, which never leaves the managed device. Already implemented in the corrected script.

**2. The cloud tasks read one file: `09-Dashboards/coach-metrics.json`.** Nothing else. Any prompt line naming a folder that could hold a person's name is the bug.

This is a real downgrade in what the cloud tasks can say, and it buys a boundary that holds without you maintaining it. The division becomes:

* **Cloud tasks deliver and nag.** Numbers, thresholds, the heartbeat check, and a pointer. They reach your phone wherever you are.
* **The real coaching runs locally**, on the machine that holds the content, as part of the weekend job. Prompts C, D, E and F all run there, where they can read person files, the external feedback and the reviews without any of it leaving the device.

Move Prompt C and Prompt D into `nightly.sh` behind a Saturday check, and let the cloud task read only the resulting numbers. Prompt F you run by hand at each gate anyway.

**3. Push notifications carry numbers, not names.** The old Prompt D pushed "three moves, each with a named person and a date" to a phone lock screen. Named employees plus a judgment on a personal push channel. Push the count and a pointer; names stay in the file on the machine.

**4. `learned.md` splits in two.** Its own template contains `## Vocabulary` (company acronyms) and `## Identity resolution` (a roster of employee name variants), so it can never live on the personal side. Split it:

* `99-Meta/learned-org.md`: vocabulary, identity resolution, filing corrections. Managed device only. Read by the filing prompt.
* `99-Meta/learned-me.md`: your conventions, confirmed patterns about how you work. Personal side. Read by the coaching prompts.

**5. Do not `git init` the personal vault.** Section 18 step 1 said to. Combined with section 20's week 2 split, that leaves ten days of company content permanently in the personal repo's object store, because moving a file does not remove it from history. Initialize the repo on the managed device when the operational vault lands there. If content has already been committed on the personal machine, delete `.git` and re initialize rather than using `git rm`. Gitignore `99-Meta/logs/` and `00-Inbox/archive/` in either case.

### Never write these down, on any machine

* Third party allegations attributed to a source. "Ravi says Priya is checked out" is a dated document that reads, later, as bias formed on day three from hearsay.
* Flight risk or attrition predictions tied to a name. Ask your manager the question, act on the answer, record only the forward action: "1:1 with X, week 1, priority."
* Performance verdicts, PIP or termination or promotion speculation, comp figures.
* Health, family, pregnancy, visa or immigration status, age, religion, politics, or any protected characteristic.
* Anything touching an HR complaint, investigation, legal matter or safety incident. That belongs in HR's system of record and nowhere else.
* Motive attribution, and anything you would not read aloud to the person.
* Unannounced reorg, headcount reduction, unreleased financials or M&A. HON is publicly traded and that is material nonpublic information sitting in a personal cloud account.

Fine to write, and the system depends on it: role, ownership, cadence, what they need from you, commitments in both directions, dated first hand observations about work product, and open questions.

### Unattended AI and personnel files

Append only is a prompt instruction, not an enforcement. An unattended agent writing into files that contain judgments about named people, with name variants it may resolve wrongly, is the one automation in this design that can produce a genuinely damaging artifact.

The nightly filing pass may write: `01-Daily/`, new stub entities, commitments, and a dated verbatim entry under `## 1:1 Log`. It may **not** set or change `relationship` or `influence`, and it may not write into `## Snapshot` or `## Career and motivation`. Those are yours to write, deliberately, in daylight. Add that restriction to `.cursor/rules/vault.mdc` and to Prompt B.

The `pre-file` git commit added in section 14.1 means a bad pass is one `git diff HEAD~1` away from being seen and one revert away from being undone.

### Defensibility checklist

What must be true for this system to be uncontroversial if your manager, IT or legal learned it exists:

1. Zero Honeywell content in the personal vault until you have read the real IP, privacy and AI acceptable use policies. The two files in `Onboarding/` are empty loading shells, so you do not currently have them.
2. One week 1 email to IT and your manager naming the tools explicitly and asking which storage, which AI tooling and which git hosting are sanctioned. Keep the reply. That single email converts shadow tooling into approved tooling.
3. The operational vault lives only on the managed device, in company storage, inside MDM and DLP, so it can be held, produced and wiped like any other work record.
4. Every line about a named person survives being read aloud to that person, and to opposing counsel, three years from now.
5. The only file that crosses machines is one you could show your manager unredacted: integers, no names, no free text.
6. No unattended AI writes into the judgment fields of person files.
7. A stated retention rule: raw inbox purged at day 120, judgment language pruned once acted on.

---

## 27. Four things that were missing

### 1. The survival case for the function

Section 9 correctly names the risk that a newly independent company re examines every central function within 12 months, then instruments nothing against it. Track these as dated facts from week 1, in `08-Plan/survival.md`:

* The funding model and the annual run rate of your org.
* What each of the three segments receives for that spend, in their words, not yours.
* What breaks if the team is halved. Write it before anyone asks.
* **TSA expiry dates** and **pre spin tooling license renewal dates.** These are the most predictable forcing functions in any separation and they appeared nowhere in the design. A design system tool whose license was tied to the pre spin entity is a decision with a date on it, and it will arrive whether or not you are ready.

### 2. Four people who collapse most of the discovery work

Missing from the stakeholder design entirely. All four can be met in week 1:

* **HR business partner.** Hands you the org export, the real reporting lines, and the open req status.
* **Finance partner.** Hands you the cost center, the run rate, and the AOP calendar with its actual deadline.
* **Talent acquisition lead.** Hands you what is open, what is frozen, and what was promised.
* **Your predecessor**, if they are still in the company. And the question nobody asks in time: was there an internal candidate for this job who now reports to you.

Between them they replace roughly half of the section 9 discovery interviews with a document.

### 3. The inherited delivery ledger

What your org already promised the segment engineering VPs for Q1, with dates and names. You can be judged in month two on a commitment someone else made in July. Build this in week 1 as `06-Projects/` entries with `inherited: yes` and a source, and confirm each one with the person it was promised to. Confirming an inherited commitment is also, conveniently, an excellent reason for a first meeting with a peer.

### 4. Two calendar dates that outrank your own plan

Section 10 warns that the AOP deadline may not match your gates, then leaves the gates anchored to START_DATE anyway. Fix it: `AOP_DEADLINE` becomes the second constant in `99-Meta/config.md`, and the gate dates are generated backward from it, not forward from your start. If the headcount ask is due at day 45, your point of view document is a day 30 artifact and Gate 2 must close by day 40.

The second date is the **comp and performance calibration date**, usually December. A performance case not documented by roughly day 45 costs you another full year with that person. "First personnel read complete" at day 60, as Part I had it, is too late.

### On "one visible win"

Part I said ship one visible win by day 90 and left it undefined. For an engineering UX function inside an automation company, it must land inside **someone else's metric**. A measured before and after on an operator facing workflow in a shipping Buildings or Process product: task time, error rate, service call deflection, commissioning time. Or kill one of the duplicate post separation design systems and bank the license cost.

Not a design system launch. Not a research repository. Not a UX maturity assessment. Those are wins to designers, and designers are not who decides whether this function survives its first year as part of an independent company.

---

## 28. Findings considered and not adopted

Recorded so they are not relitigated later.

* **"Cut the stakeholder 2x2 and the graph configuration as decorative."** Rejected. You explicitly chose both, the graph configuration is ten minutes once, and the 2x2 is the artifact most likely to change a decision in week 6. The HTML render is optional; the Dataview quadrants are not.
* **"Take the AI filing step out of the unattended job entirely."** Partially adopted. Fully manual filing is the highest quality option and the one most likely to be abandoned in week 3, which is a worse outcome. Instead the write scope is restricted, the pass is isolated between two git commits, and the morning brief surfaces a failed run. Section 26.
* **"Delete pattern mining and schema evolution."** Deferred rather than deleted. Both are day 60 work presented as day 0 setup, which was the real complaint. They stay in the design and are switched on at day 60.
* **"Replace the whole coaching layer with the external feedback loop."** Partially adopted. The external loop is added and given precedence over every internal metric, which was the substance of the point. The internal metrics stay, cut from nine to seven, because commitment kept rate and directs late are genuinely useful and no external source will tell you about them weekly.
* **"Cut the calendar .ics import."** Kept, because as a week 1 to 4 discovery tool for finding forums you did not know existed it costs one minute a week and section 14.4 already says to stop using it after day 30.

---

## 29. GitHub and version control

Short answer: git is already in the design and it is doing the versioning. Adding **GitHub** adds a remote, and a remote is not a versioning feature. It buys exactly two things, off machine backup and cross machine sync, and both of them are the thing the data boundary in section 26 exists to control.

### What local git already gives you

Everything you actually meant by versioning, with no remote at all:

* Full history, `git log --follow 02-People/Priya-Nair.md` to see how your read on someone changed over eleven weeks.
* `git diff HEAD~1` after a nightly run, which is the whole point of the `pre-file` commit added in section 14.1. That one commit boundary is the reason a bad AI pass is visible and revertible.
* `git revert` on a single bad pass without losing the day you typed.
* `git show HEAD~7:09-Dashboards/coach-metrics.json` for week over week trend, which the weekly heartbeat task already uses.

None of that needs GitHub. If versioning is the goal, you are already done.

### Two repos, not one

The split from section 20 maps cleanly onto two repositories with different rules.

**Repo A, the operational vault.** Person files, daily notes, teams, systems, rituals, decisions. This is company content.

* Remote allowed: **Honeywell GitHub Enterprise or Azure DevOps**, if they have one and IT approves it. That is a company system inside company identity, logging and retention, and it is the best possible answer because it gives you backup and cross machine sync without the content ever leaving company control.
* Remote forbidden: **github.com on a personal account, private repo included.** A private personal repo is still off company systems, and this is the single most common way a well intentioned person creates an exfiltration finding. Private is an access control setting, not a jurisdiction.
* If IT says no remote: local git only. You lose backup, not versioning. Time Machine or the company backup agent covers the backup case.

**Repo B, the machinery.** The scripts, prompts, templates, schema, the launchd plist, and this guide. No names, no org structure, no program status. Just the system itself.

* Personal GitHub, private, is fine and is actually the better home for it. It is genuinely yours, it is portable to your next role, and it is the part worth improving over years.
* This is the split worth internalizing: **publish the machinery, keep the data.** The tooling is transferable and carries no company content. The vault contents are Honeywell's and go stale the day you leave.

### The rule that has no exceptions

History is permanent and `git rm` does not remove anything from it. If company content is ever committed and pushed to a personal remote, the remedy is deleting the repository, not a commit. Force pushing leaves dangling objects reachable through the API until garbage collection, on a schedule you do not control.

So: the operational vault never gets a personal remote, not once, not "just to test the sync." Set it up correctly the first time and there is nothing to unwind.

This is also why section 26 says do not `git init` the personal vault before the split. Initialize Repo A on the managed device when the content lands there.

### `.gitignore` for either repo

```
.obsidian/workspace.json
.obsidian/workspace-mobile.json
.obsidian/cache
.trash/
.DS_Store
99-Meta/logs/
00-Inbox/archive/
00-Inbox/run/
09-Dashboards/coach-local.md
09-Dashboards/stakeholder-map.html
```

Reasoning on the last three. `00-Inbox/archive/` holds raw unprocessed dumps, which are the least considered writing in the vault and the least defensible thing in a history. `coach-local.md` and the HTML map are both derived, regenerate in one second, and carry names. Nothing derived belongs in version control anyway.

Add a `.gitattributes` with `* text=auto eol=lf` so a future Windows machine does not rewrite every line ending and produce a diff of the entire vault.

### Do not install the Obsidian Git plugin with auto push

It is a good plugin and the auto push feature is exactly wrong for this design. An automatic push on an interval will eventually push a repo whose remote you set up months earlier and stopped thinking about. The boundary should be something you cross deliberately. The nightly script commits, and you push by hand or add one explicit line to `nightly.sh` once the remote is a company one you have confirmed.

Push protection and secret scanning on GitHub catch credentials and API keys. They do not detect company confidential prose. Do not treat them as a safety net for this.

### Add it to the week 1 IT email

The email in section 26 becomes one line longer. Ask specifically:

> Does Honeywell provide a GitHub Enterprise or Azure DevOps instance I can use for a private repository of working notes, and if so what is the process to get one?

If the answer is yes, Repo A gets a remote and you have backup, versioning and cross machine sync inside company control, which is the best outcome available. If the answer is no, local git is genuinely sufficient and the rest of the design is unchanged.
