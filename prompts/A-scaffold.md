ROLE
You are installing a knowledge vault into an empty directory for a senior engineering UX
leader starting a new role, cold, with no org chart.

INPUT
docs/Vault-Build-Guide.md in this repo. Sections 2, 3, 4, 6 are the spec. Part III
supersedes Parts I and II wherever they conflict.

TASK
Prefer running ./install.sh, which does all of this deterministically. Use this prompt
only to verify the result or to rebuild a piece by hand.

Verify that the vault contains: the numbered folder tree; 99-Meta/schema.md;
99-Meta/config.md with START_DATE as a bare date at column 0; every template; the three
scripts; the six prompt files at their exact filenames; the dashboard query files;
08-Plan/30-60-90.md, discovery-questions.md, evidence-log.md, predictions.md,
survival.md; the empty directories 08-Plan/coaching, 08-Plan/reviews, 08-Plan/external,
99-Meta/logs, 00-Inbox/run, 00-Inbox/archive; and .cursor/rules/vault.mdc.

CONSTRAINTS
Invent no names, teams or systems. 02-People, 03-Teams, 04-Systems, 05-Rituals and
06-Projects stay empty until real humans are met.

OUTPUT
A tree listing, then one line per item in the spec you could not implement.
