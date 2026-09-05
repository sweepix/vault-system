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
