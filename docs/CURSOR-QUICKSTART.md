# Cursor quickstart

Dry run the whole system on your personal Mac before your start date, with fake data.
Roughly 60 minutes. At the end you will have proven the filing pass appends rather than
overwrites, which is the one behavior worth proving before you trust it with real notes.

**What this is not.** You are not starting the real vault. No git in the vault, no real
names, nothing Honeywell. See guide sections 22 and 26 for why.

---

## 1. Open the repo in Cursor

```
cd ~/claude/Honeywell/vault-system
cursor .
```

If the `cursor` command is missing: open Cursor, Cmd+Shift+P, "Shell Command: Install
'cursor' command", then reopen your terminal.

## 2. Install the machinery into a practice vault

In Cursor's terminal, Ctrl+`:

```
./install.sh ~/claude/Honeywell/Vault
```

It prints the tree it created and a four step next list. Re running it is safe: it
refreshes `99-Meta/` and the dashboards and never touches content folders.

## 3. Fill the config

Open `~/claude/Honeywell/Vault/99-Meta/config.md`. Set:

```
START_DATE: 2026-10-05
```

Use your real start date if you have it, otherwise today's date so the dry run produces
sensible day numbers. **Format is load bearing.** Bare date, column 0, no bold, no list
marker, no frontmatter. Both scripts exit loudly if it does not match, which is
deliberate: a silently missing START_DATE used to make every metric read n/a.

## 4. Prove the scripts run

```
cd ~/claude/Honeywell/Vault
python3 99-Meta/scripts/coach_metrics.py
python3 99-Meta/scripts/stakeholder_map.py
```

Expect mostly `n/a` and "wrote ... with 0 people". That is correct on an empty vault.
If you get the FATAL config message, step 3 is wrong. If `python3` is missing, install
the Xcode command line tools: `xcode-select --install`.

## 5. Obsidian

1. Obsidian, Open folder as vault, pick `~/claude/Honeywell/Vault`.
2. Core plugins on: Daily notes, Templates, Backlinks, Outgoing links, Graph view,
   Properties view, Unique note creator.
3. Community plugins, Browse, install **Dataview**. Enable it. This is the only community
   plugin you need. Do not install Obsidian Git.
4. Settings, Daily notes: folder `01-Daily`, format `YYYY-MM-DD`, template
   `99-Meta/templates/daily.md`.
5. Settings, Templates: folder `99-Meta/templates`.
6. Settings, Unique note creator: folder `00-Inbox`, format `YYYY-MM-DD-HHmm`. Bind it to
   a hotkey. This is your capture path when you are not using voice.
7. Graph view. Filters box: `-path:01-Daily -path:00-Inbox -path:99-Meta -path:09-Dashboards`
   Then add color groups: `path:02-People` blue, `path:03-Teams` orange,
   `path:04-Systems` green, `path:05-Rituals` yellow, `path:06-Projects` purple,
   `path:07-Decisions` red, `["status":"stub"]` grey.
   Display: Arrows on, Text fade off, link distance around 250.

Excluding `01-Daily` is the single setting that decides whether the graph is usable.
Daily notes link to everything, so leaving them in collapses it into one blob.

## 6. Cursor, pointed at the vault

Open a **second Cursor window** on the vault itself:

```
cursor ~/claude/Honeywell/Vault
```

Two windows on purpose. The vault window is where you file notes, and it is the only one
where `.cursor/rules/vault.mdc` loads. The repo window is where you improve the machinery.

Confirm the rules loaded: Cursor Settings, Rules. `vault` should be listed with
alwaysApply true. If it is not, check `.cursor/rules/vault.mdc` exists in the vault.

Then:

* **Cmd+I** opens the AI pane. **Shift+Tab** rotates modes. You want **Agent**, because
  the filing pass writes to many files at once and Ask mode will not.
* Pick the strongest model available in the model dropdown. Filing is the step where a
  weak model quietly mangles things.
* **Leave Auto-run off** while you are learning what the pass does. Agent applies file
  edits either way; Auto-run is about terminal commands and you do not need it.
* **Cmd+Return** accepts all changes, **Cmd+Backspace** rejects all.

## 7. The dry run that matters

Create three fake inbox notes. Real structure, invented people, no Honeywell anything.

```
cd ~/claude/Honeywell/Vault
cat > 00-Inbox/2026-09-08-1030-staffing.md <<'X'
# 2026-09-08 1030 · Staffing sync
Attendees: Alex Rivera, Sam Okafor
Purpose: explore

## Raw
alex owns the alerts platform. says design shows up after the spec is frozen, wants it
earlier. sam mentioned the shared component library has no owner since the reorg.
i said i'd send alex a draft intake by friday. alex owes me the program list monday.
alex is in the arch review board, thursdays, that's where roadmap actually gets set.

## My read
Design is being used as a rendering service, not a partner. Alex is the one to convince.
X
cat > 00-Inbox/2026-09-08-1400-1on1-sam.md <<'X'
# 2026-09-08 1400 · 1:1 Sam Okafor
Attendees: Sam Okafor
Purpose: inform

## Raw
sam has 4 designers, wants a 5th. frustrated that research doesn't exist anywhere.
last manager never gave feedback, wants direct feedback weekly. owns the operator console.
i committed to answering the headcount question by the 20th.

## My read
Strong, under supported. The research gap is going to come up from three directions.
X
```

Now in the vault Cursor window, Agent mode, paste:

```
Read 99-Meta/prompts/B-file-inbox.md and execute it exactly as written.
Source directory: 00-Inbox/. Today is 2026-09-08. Derive each note's date from its own
filename, never from today.
```

**Then check four things, in this order:**

1. `01-Daily/2026-09-08.md` exists and its commitments are in the exact checkbox form with
   `[owner:: me]`, `[to:: ...]` and `[due:: ...]`.
2. `02-People/Alex-Rivera.md` and `02-People/Sam-Okafor.md` exist with `status: stub`.
3. `05-Rituals/` has a file for the architecture review board with `decision_rights: decides`
   and `my_role: absent`. That pairing is the finding the whole ritual entity exists for.
4. `08-Plan/evidence-log.md` has rows. If it is empty, the pass skipped step 5 and you
   should say so and rerun.

**Then the test that actually matters.** Run the exact same prompt a second time on the
same inbox. Open `02-People/Sam-Okafor.md`. If the 1:1 Log has one entry, or two clearly
dated entries, the append only contract holds. If earlier content was rewritten or
replaced, stop and fix the rules file before you ever point this at real notes.

## 8. The nightly job, by hand first

```
cd ~/claude/Honeywell/Vault
git init            # only for the DRY RUN. See step 10.
bash 99-Meta/scripts/nightly.sh
cat 99-Meta/logs/$(date +%F).log
```

Run it three times. The log should show the next working day's note created once, the
inbox staged into `00-Inbox/run/`, a `pre-file` commit, filing, and a final commit. Files
only get archived when they carry a `.done` marker, so a crashed run resumes instead of
duplicating.

If `claude` is not found, install the Claude Code CLI or comment out that block. Everything
else in the job works without it.

## 9. launchd

```
cp ~/claude/Honeywell/vault-system/launchd/com.boniface.vault.nightly.plist ~/Library/LaunchAgents/
launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/com.boniface.vault.nightly.plist
launchctl kickstart -k gui/$(id -u)/com.boniface.vault.nightly
cat 99-Meta/logs/$(date +%F).log
```

To remove: `launchctl bootout gui/$(id -u)/com.boniface.vault.nightly`

The plist sets PATH explicitly. Without it launchd runs a login bash that reads
`.bash_profile`, not your `.zprofile`, and `claude` and `python3` from Homebrew are not on
the path.

## 10. Tear down the dry run

When it all works:

```
cd ~/claude/Honeywell/Vault
rm -rf .git 00-Inbox/* 01-Daily/* 02-People/* 05-Rituals/* 07-Decisions/* 08-Plan/coaching/* 09-Dashboards/coach-*
```

**Delete `.git` specifically.** The dry run repo has fake data in its history, and more
importantly this directory must not carry a personal repo into October. When the real
vault lands on the Honeywell machine you `git init` there, once, cleanly.

Keep the folder structure, the config, the templates, the prompts and the Obsidian
settings. Those are the thing you just spent an hour proving.

## 11. What not to do yet

* No `git init` in the vault after the dry run, and no personal GitHub remote for it ever.
  Guide section 29.
* No real names, no Honeywell program names, no org structure until you have read the
  actual IP and data privacy agreements. The two files in `Onboarding/` are empty loading
  shells, so you do not have them yet.
* No Obsidian Git plugin.
* Do not enable the scheduled tasks' expectations by filling START_DATE with a past date
  before you actually start. They check it and stay silent until it passes.
