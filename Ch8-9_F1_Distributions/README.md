# Group 6 · DATA 230 · Chapters 8–9: Visualizing distributions

Wilke, *Fundamentals of Data Visualization*, chapter 8 (ECDFs and Q-Q plots) and chapter 9 (many distributions at once), applied to the same F1DB data as our Lecture 4–5 project: 469 pit stops from the first 15 races of the 2026 season, plus career totals for all 917 drivers in F1 history.

## Layout

This folder mirrors the layout of [data230-group6-f1-2026](https://github.com/NamanSudan/data230-group6-f1-2026), so its pieces drop straight into the repo.

```
analysis/
  04_distributions.ipynb   chapter 8–9 charts, executed (outputs included)
  04_distributions.py      the same code as a plain script
  data/raw/                F1DB v2026.15.1 CSVs, unmodified
  data/f1db-csv.zip        the original release download
  figures/                 every chart as PNG: ch8_*.png, ch9_*.png, deck_cover_art.png
deck/
  ch8-9_visualizing_distributions.pptx
requirements.txt
```

**Adding it to the repo:** copy `analysis/04_distributions.*` into the repo's `analysis/`, the PNGs into `analysis/figures/`, and the .pptx into `deck/`. The repo already has the same CSVs in `analysis/data/raw/`, so don't copy them again. The figure names are prefixed `ch8_` and `ch9_` so they don't overwrite the Lecture 5 charts.

## Setup and run

Python 3.13, matching the repo:

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cd analysis
python 04_distributions.py        # or open 04_distributions.ipynb in Jupyter Lab
```

Unlike notebooks 02 and 03, this one reads `data/raw/` directly (pit stops, races, race results, drivers), so it doesn't need `01_cleaning.ipynb` to run first.

## What each figure shows

| Figure | Slide | Chart |
|---|---|---|
| `ch8_ecdf_pitstops` | 5 | ECDF of all 469 pit lane times, with the median marked |
| `ch8_starts_linear`, `ch8_starts_log` | 6 | Density of career race starts on linear vs log axes |
| `ch8_loglog_careers` | 7 | Descending ECDF of career starts and points on log–log axes |
| `ch8_qq_pitstops` | 8 | Q-Q plot of pit lane times against a normal with the same mean and SD |
| `ch8_qq_log_starts` | (notes) | Q-Q plot of log₁₀ career starts against a normal |
| `ch9_errorbars` | 10 | Mean ± 2 SD per race: the plot to avoid |
| `ch9_boxplots` | 11 | Boxplots per race |
| `ch9_violins` | 12 | Violin plots per race |
| `ch9_points_strip` / `_jitter` / `_sina` | 13 | Raw points for four races, three ways |
| `ch9_ridgeline_races` | 14 | Density ridgeline per race |
| `ch9_ridgeline_years` | 15 | Driver age at each season's first start, by 5-year period, 1950–2026 |
| `deck_cover_art` | 1 | Cover preview: the ECDF and age ridgeline on a dark background |

All race charts put races on the y axis, sorted by median pit lane time, fastest at the top.

## Data

[F1DB](https://github.com/f1db/f1db) release v2026.15.1 (through the Azerbaijan Grand Prix, round 15), CC BY 4.0. "Pit lane time" is F1DB's `timeMillis` for each stop: time from pit entry to exit.
