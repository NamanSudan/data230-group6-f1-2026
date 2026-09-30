"""Build webui/index.html: one self-contained interactive page.

Reads analysis/data/clean, embeds it as JSON, writes a single HTML file
(plotly.js inlined, works offline). Run from projects/:
    venv/bin/python webui/build_page.py
"""
import json
from pathlib import Path

import pandas as pd
import plotly

ROOT = Path(__file__).resolve().parent
CLEAN = ROOT.parent / "analysis" / "data" / "clean"


def load(name):
    return pd.read_csv(CLEAN / f"{name}.csv")


res = load("results")
ts = load("team_standings")
ds = load("driver_standings")
cal = load("calendar")
tc = load("team_colors")

last = int(res["round"].max())
order = (ds[ds["round"] == last].sort_values("position")["code"]
         .tolist())
teams = (ts[ts["round"] == last].sort_values("position")["team"]
         .tolist())

podium = {}
top3 = res[res["finish"] <= 3].sort_values(["round", "finish"])
for r in top3.itertuples():
    podium.setdefault(r.round, []).append(
        f"P{int(r.finish)} {r.driver} ({r.team})")
win_team = res[res["finish"] == 1].set_index("round")["team"]

data = {
    "last": last,
    "abbr": ["AUS", "CHN", "JPN", "MIA", "CAN", "MON", "BAR", "AUT",
             "GBR", "BEL", "HUN", "NED", "ITA", "ESP", "AZE"],
    "teams": teams,
    "official": dict(zip(tc["team"], tc["official_hex"])),
    "teamPts": {t: ts[ts["team"] == t].sort_values("round")["points"]
                .tolist() for t in teams},
    "drivers": order,
    "driverTeam": ds[ds["round"] == last].set_index("code")["team"]
                    .to_dict(),
    "driverName": res.drop_duplicates("code").set_index("code")
                     ["driver"].to_dict(),
    "finish": [[None if pd.isna(v) else int(v) for v in
                res[res["code"] == c].set_index("round")["finish"]
                .reindex(range(1, last + 1))] for c in order],
    "status": [[s if isinstance(s, str) else "Not entered" for s in
                res[res["code"] == c].set_index("round")["status"]
                .reindex(range(1, last + 1))] for c in order],
    "cal": [{
        "round": int(r["round"]), "gp": r["gp"], "circuit": r["circuit"],
        "country": r["country"], "date": r["date"], "lat": r["lat"],
        "lon": r["lon"], "raced": bool(r["raced"]),
        "winner": r["winner"] if isinstance(r["winner"], str) else "",
        "winTeam": win_team.get(r["round"], ""),
        "podium": podium.get(r["round"], []),
    } for _, r in cal.iterrows()],
}

html = (ROOT / "template.html").read_text()
html = html.replace("/*DATA*/null", json.dumps(data))
# inline plotly.js so the page works with no internet
js = (Path(plotly.__file__).parent / "package_data" / "plotly.min.js")
html = html.replace("/*PLOTLY*/", js.read_text())
(ROOT / "index.html").write_text(html)
print("wrote", ROOT / "index.html", f"{len(html) / 1024:.0f} KB")
