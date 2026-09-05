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
