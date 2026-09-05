#!/bin/bash
# Install the vault machinery into a content vault directory.
# Safe to re run: refreshes 99-Meta and the dashboards, never touches content folders.
set -euo pipefail
SRC="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
V="${1:-}"
[ -n "$V" ] || { echo "usage: ./install.sh /path/to/Vault"; exit 1; }

mkdir -p "$V"/{00-Inbox/run,00-Inbox/archive,01-Daily,02-People,03-Teams,04-Systems,05-Rituals,06-Projects,07-Decisions}
mkdir -p "$V"/08-Plan/{coaching,reviews,external}
mkdir -p "$V"/09-Dashboards "$V"/99-Meta/{templates,prompts,scripts,logs} "$V"/.cursor/rules

cp "$SRC"/templates/*.md      "$V"/99-Meta/templates/
cp "$SRC"/prompts/*.md        "$V"/99-Meta/prompts/
cp "$SRC"/scripts/*           "$V"/99-Meta/scripts/
cp "$SRC"/dashboards/*.md     "$V"/09-Dashboards/
cp "$SRC"/schema.md           "$V"/99-Meta/schema.md
cp "$SRC"/cursor/vault.mdc    "$V"/.cursor/rules/vault.mdc
cp "$SRC"/.gitignore          "$V"/.gitignore
cp "$SRC"/.gitattributes      "$V"/.gitattributes
cp "$SRC"/cursorignore.template "$V"/.cursorignore
chmod +x "$V"/99-Meta/scripts/nightly.sh

new() { [ -f "$V/$1" ] || { cat > "$V/$1"; echo "  created $1"; } }

[ -f "$V/99-Meta/config.md" ] || { cp "$SRC/config.example.md" "$V/99-Meta/config.md"; echo "  created 99-Meta/config.md, FILL IN START_DATE"; }

new 99-Meta/learned-org.md <<'X'
---
name: learned-org
description: Vocabulary, identity resolution and filing corrections. Managed device only.
---

## Vocabulary

## Identity resolution
<!-- name variants that are the same person. prefer fixing this in the person file's aliases. -->

## Filing rules I have corrected
<!-- DATE | what went wrong | the rule now -->
X

new 99-Meta/learned-me.md <<'X'
---
name: learned-me
description: My conventions and confirmed patterns about how I work. Portable, personal.
---

## My conventions
- "??" means the preceding line is a hypothesis, not a fact. File it under Open questions.
- "!!" means a commitment I made out loud. Extract it even if I did not format it.

## Confirmed patterns about me
<!-- promoted from 99-Meta/patterns.md only after I confirm them -->
X

new 99-Meta/patterns.md <<'X'
---
name: patterns
description: Proposed patterns about my behavior. Unconfirmed until I say otherwise.
---
X

new 08-Plan/predictions.md <<'X'
---
type: plan
description: Falsifiable predictions with a resolution criterion. Three a week.
---

Conf must be a bare decimal. "Resolves true if" is mandatory: a prediction with no
falsification condition cannot be graded and does not count.

| Made | Prediction | Resolves true if | Conf | Resolve by | Outcome | Correct |
|---|---|---|---|---|---|---|
X

new 08-Plan/evidence-log.md <<'X'
---
type: plan
description: Every claim with its source. Gate 1 is tested against this file alone.
---

Two sources in the same reporting line count as one. Confidence stays low until a second
independent source.

| Date | Claim | Source | Corroborated by | Confidence |
|---|---|---|---|---|
X

new 08-Plan/survival.md <<'X'
---
type: plan
description: The case for the function existing, tracked as dated facts from week 1.
---

- Funding model (central, chargeback, hybrid):
- Annual run rate:
- What each segment receives for it, in their words:
- What breaks if the team is halved:
- TSA expiry dates:
- Pre separation tooling license renewal dates:
X

touch "$V"/08-Plan/coaching/.gitkeep "$V"/08-Plan/reviews/.gitkeep "$V"/08-Plan/external/.gitkeep

echo
echo "installed into $V"
echo "next:"
echo "  1. fill $V/99-Meta/config.md, START_DATE must be a bare YYYY-MM-DD at column 0"
echo "  2. open the vault in Obsidian, install Dataview, point daily notes at 01-Daily"
echo "  3. cd $V && git init   (a SEPARATE repo from this one, see guide section 29)"
echo "  4. run 99-Meta/scripts/nightly.sh by hand three times before scheduling it"
