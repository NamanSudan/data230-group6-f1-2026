# Group 6: F1 2026 through Wilke Chapters 4, 5, 8 and 9

DATA 230 team presentations. Tara, Eliza, Naman, Steven.

We take the 2026 F1 season (15 of 23 races, through Azerbaijan on 9/26)
and use it for two deliverables:

- **Deliverable 1** (9/30): color scales (Ch 4) and the directory of
  chart types (Ch 5).
- **Deliverable 2** (10/14): ECDFs and Q-Q plots (Ch 8) and many
  distributions at once (Ch 9).

## Layout

```
analysis/
  data/raw/                  F1DB v2026.15.1 CSVs, untouched (shared)
  data/clean/                output of deliverable1/01 (shared)
  deliverable1/
    01_cleaning.ipynb        filter to 2026, names, checks
    02_color_scales.ipynb    Ch 4: distinguish, values, highlight
    03_directory.ipynb       Ch 5: one chart per family
    f1viz.py                 shared colors + plot settings for 02, 03
    figures/                 fig01 to fig12 as PNG (map also as HTML)
  deliverable2/
    04_distributions.ipynb   Ch 8 and 9: ECDF, Q-Q, box, violin, sina, ridgeline
    04_distributions.py      same code as 04, as a plain script
    figures/                 ch8_*, ch9_*, deck_cover_art
webui/                       deliverable 1 demos
  index.html                 single-page interactive demo (works offline)
  build_page.py              rebuilds index.html from data/clean
  template.html              page layout used by build_page.py
  app.py                     Streamlit app (filters, colorblind view)
  record_demo.py             scripted screen recordings (Playwright)
  recordings/                streamlit_demo.mp4, html_demo.mp4
deck/
  deliverable1/group6_f1_2026.pptx
  deliverable2/ch8-9_visualizing_distributions.pptx
```

## Setup

Python 3.13.

```
python3.13 -m venv venv
venv/bin/pip install -r requirements.txt
venv/bin/playwright install chromium   # only for record_demo.py
```

## Run

Deliverable 1 notebooks (run 01 first, then 02 and 03 in any order):

```
cd analysis/deliverable1
../../venv/bin/jupyter lab
```

Deliverable 2 reads `data/raw/` directly, so it does not need 01:

```
cd analysis/deliverable2
../../venv/bin/python 04_distributions.py   # or open the notebook in Jupyter Lab
```

Web demos, from the repo root:

```
venv/bin/python webui/build_page.py     # then open webui/index.html
venv/bin/streamlit run webui/app.py
venv/bin/python webui/record_demo.py    # re-record the demo videos (needs ffmpeg)
```

## Deliverable 2 figures

Race charts put races on the y axis, sorted by median pit lane time,
fastest at the top.

| Figure | Chart |
|---|---|
| `ch8_ecdf_pitstops` | ECDF of all 469 pit lane times, median marked |
| `ch8_starts_linear`, `ch8_starts_log` | career race starts, linear vs log axis |
| `ch8_loglog_careers` | descending ECDF of career starts and points, log-log |
| `ch8_qq_pitstops` | Q-Q of pit lane times vs a matching normal |
| `ch8_qq_log_starts` | Q-Q of log10 career starts vs a normal |
| `ch9_errorbars` | mean +/- 2 SD per race (the plot to avoid) |
| `ch9_boxplots`, `ch9_violins` | boxplots and violins per race |
| `ch9_points_strip`, `_jitter`, `_sina` | raw points for four races, three ways |
| `ch9_ridgeline_races` | density ridgeline per race |
| `ch9_ridgeline_years` | driver age at first start of each season, 1950-2026 |
| `deck_cover_art` | cover image for the deliverable 2 deck |

"Pit lane time" is F1DB's `timeMillis` per stop, pit entry to exit.
"Spain" in 2026 is the new Madrid circuit; "Barcelona" is Catalunya.

## Data

[F1DB](https://github.com/f1db/f1db), release
[v2026.15.1](https://github.com/f1db/f1db/releases/tag/v2026.15.1), CC BY 4.0.
Official team colors come from F1's live timing feed, read with
[FastF1](https://github.com/theOehrly/Fast-F1).
