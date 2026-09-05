# Vault config

Copy to `99-Meta/config.md` in the vault. Both scripts and the nightly job parse these
lines with an anchored regex, so the format is not cosmetic: bare value, column 0, no
bold, no frontmatter, no list marker.

START_DATE: 2026-10-05
AOP_DEADLINE:
COMP_CALIBRATION:
MANAGER:
MY_ORG:
SEGMENTS:

## Gate dates

Generated backward from AOP_DEADLINE when it is known, not forward from START_DATE.
If the headcount ask is due at day 45, the point of view document is a day 30 artifact
and Gate 2 must close by day 40.

GATE_1:
GATE_2:
GATE_3:

## Threshold overrides

Defaults live in scripts/coach_metrics.py. Override here after day 30, once you know
your own baseline rather than my guesses.
