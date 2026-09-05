# vault-system

The machinery for a leadership knowledge vault: an Obsidian markdown vault with typed
entities, AI filing, a nightly job, and a metrics based coaching layer.

**This repo holds the system, never the content.** Scripts, prompts, templates, schema
and docs live here. People, org structure, program status and daily notes live in a
separate vault directory that this repo installs into and never tracks.

That split is deliberate. The machinery is portable and improves over years. The
content belongs to one employer and goes stale the day you leave.

## Install

```
./install.sh ~/path/to/Vault
```

Creates the folder tree, copies templates, prompts, scripts and the schema in, and
writes a `config.md` you then fill in. Safe to re run: it never overwrites content,
only refreshes `99-Meta/` and the scripts.

## After installing

1. Fill `99-Meta/config.md`. `START_DATE:` must be a bare `YYYY-MM-DD` at column 0 or
   the scripts exit loudly. `AOP_DEADLINE:` drives the gate dates.
2. Open the vault in Obsidian. Install Dataview. Point daily notes at `01-Daily` and
   templates at `99-Meta/templates`.
3. Configure the graph filter and color groups. See `docs/Vault-Build-Guide.md` section 5.
4. `git init` **inside the vault directory**, separately from this repo. See section 29
   of the guide for which remotes are allowed for that repo. It is not this one.
5. Install the launchd job from `launchd/`. Run `scripts/nightly.sh` by hand three times first.

## Layout

| Path | What |
|---|---|
| `docs/Vault-Build-Guide.md` | The full design, the review findings, and the rationale |
| `scripts/coach_metrics.py` | Computes the seven coaching metrics. Numbers to JSON, names to a local only file |
| `scripts/stakeholder_map.py` | Renders the influence and interest 2x2 as standalone HTML |
| `scripts/nightly.sh` | The nightly pass: next working day note, staged filing, derived views, commit |
| `prompts/` | A scaffold, B file inbox, C weekly review, D weekly coach, E monthly, F gate interview |
| `templates/` | Daily, meeting, person, manager 1:1, decision, ritual |
| `dashboards/` | Dataview query files copied into `09-Dashboards/` |
| `schema.md` | The frontmatter contract. Single source of truth |
| `cursor/vault.mdc` | Cursor rules file, copied to `.cursor/rules/` in the vault |

## Rules that are not style preferences

* No inline YAML comments in any frontmatter. They break every parser that splits on
  the first colon, silently.
* Commitments are counted from `01-Daily` only. Person files link, they never mirror.
* Child side edges only. A person carries `manager`, never `reports`. Reverse edges
  are derived in Dataview.
* The AI filing pass may write daily notes, stubs, commitments and dated verbatim 1:1
  entries. It may not set `relationship` or `influence`, or write into `Snapshot` or
  `Career and motivation`.
* Nothing carrying a person's name leaves the machine that holds the vault.
