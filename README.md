# Group 6: F1 2026 through Lectures 4 and 5

DATA 230, team presentation 9/30. Tara, Eliza, Naman, Steven.

We take the 2026 F1 season (15 of 23 races, through Azerbaijan on 9/26)
and use it to show color scales (Lecture 4) and the directory of chart
types (Lecture 5).

## Layout

```
analysis/
  data/raw/                  F1DB v2026.15.1 CSVs, untouched
  data/clean/                output of 01
  01_cleaning.ipynb          filter to 2026, names, checks
  02_color_scales.ipynb      Lecture 4: distinguish, values, highlight
  03_directory.ipynb         Lecture 5: one chart per family
  f1viz.py                   shared colors + plot settings
  figures/                   every chart as PNG (map also as HTML)
webui/
  index.html                 single-page interactive demo (works offline)
  build_page.py              rebuilds index.html from data/clean
  template.html              page layout used by build_page.py
  app.py                     Streamlit app (filters, colorblind view)
  record_demo.py             scripted screen recordings (Playwright)
  recordings/                streamlit_demo.mp4, html_demo.mp4
deck/group6_f1_2026.pptx     slides
```

## Setup

Python 3.13.

```
python3.13 -m venv venv
venv/bin/pip install -r requirements.txt
venv/bin/playwright install chromium   # only for record_demo.py
```

## Run

Notebooks (run 01 first, then 02 and 03 in any order):

```
cd analysis
../venv/bin/jupyter lab
```

Web demos, from the repo root:

```
venv/bin/python webui/build_page.py     # then open webui/index.html
venv/bin/streamlit run webui/app.py
venv/bin/python webui/record_demo.py    # re-record the demo videos (needs ffmpeg)
```

## Data

[F1DB](https://github.com/f1db/f1db), release
[v2026.15.1](https://github.com/f1db/f1db/releases/tag/v2026.15.1), CC BY 4.0.
Official team colors come from F1's live timing feed, read with
[FastF1](https://github.com/theOehrly/Fast-F1).
