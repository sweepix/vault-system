# Frontmatter contract

Single source of truth. The guide, the rules file and the scripts all defer to this.

## Rules that are not preferences

* **No inline YAML comments.** `relation: direct   # direct | manager` parses as that
  entire literal string in anything that splits on the first colon. Enum legends live
  here and nowhere else.
* **Unknown means blank**, not the word "unknown", or the schema evolution pass can never
  see the field as empty.
* **Child side edges only.** A person carries `manager`, never `reports`. A team carries
  `lead`, never `members`. Reverse edges are derived: `WHERE manager = this.file.link`.
  An append only filer can add an edge and is forbidden to remove one, so any two sided
  relationship drifts into permanent phantoms.
* **Quote every wikilink in frontmatter.** `manager: "[[Ravi Desai]]"`. Unquoted parses
  as a nested list and is silently not a link.
* **`aliases` is how name variants are handled**, not a prompt instruction.

## Enums

| Field | Values |
|---|---|
| relation | direct, manager, skip, peer, partner, exec, external |
| influence | high, low. There is no medium. |
| interest | high, low. There is no medium. |
| relationship | strong, neutral, unknown, strained |
| cadence | weekly, biweekly, monthly, adhoc |
| status | active, stub, departed |
| decision_rights | decides, recommends, informs |
| my_role | chair, member, guest, absent |
| ux_maturity | none, ad-hoc, defined, measured |
| design_debt | high, medium, low |
| reversible | yes (two way door), no (one way door) |

## Entities

person: type, name, aliases, title, org, relation, manager, owns, location, timezone,
tenure_start, influence, interest, relationship, cadence, last_1on1, next_1on1, status, tags
Body: Snapshot, What they own, What they need from me, What I need from them,
Career and motivation, Commitments, 1:1 Log, Open questions.

team: type, lead, parent, owns, charter, headcount, design_coverage, status, tags

system: type, owner_team, dri, users, ux_maturity, design_debt, dependencies, status, tags

ritual: type, cadence, owner, attendees, decision_rights, my_role, what_it_decides, status, tags
`my_role: absent` on a forum with `decision_rights: decides` is a finding.

project: type, sponsor, dri, teams, outcome, status, horizon, inherited, source, tags
`inherited: yes` marks a commitment made before I arrived, with `source` naming who made it.

decision: type, date, owner, forum, status, reversible, revisit_by, stakeholders, tags

daily: type, date, day_number, tags

external: type, date, gate, source_role, tags

## Commitments

Inline Dataview fields on checkboxes, in daily notes only. Never mirrored into person
files: the metrics count 01-Daily only and a mirror double counts.

    - [ ] text [owner:: me] [to:: Full Name] [due:: YYYY-MM-DD]
    - [ ] text [owner:: them] [from:: Full Name] [due:: YYYY-MM-DD]
    - [-] cancelled, excluded from every metric

Only commitments go in checkboxes. Nothing else.
