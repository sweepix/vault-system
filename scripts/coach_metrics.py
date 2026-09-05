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
