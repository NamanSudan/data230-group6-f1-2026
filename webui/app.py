"""Streamlit app: explore the 2026 season with Lecture 4 + 5 ideas.

Run from projects/:
    venv/bin/streamlit run webui/app.py
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from scipy import stats

ANALYSIS = Path(__file__).resolve().parent.parent / "analysis"
sys.path.insert(0, str(ANALYSIS / "deliverable1"))
from f1viz import OKABE_ITO, TOP4, GRAY, simulate  # noqa: E402

CLEAN = ANALYSIS / "data" / "clean"
ABBR = ["AUS", "CHN", "JPN", "MIA", "CAN", "MON", "BAR", "AUT",
        "GBR", "BEL", "HUN", "NED", "ITA", "ESP", "AZE"]

st.set_page_config(page_title="F1 2026 Explorer", layout="wide")


@st.cache_data
def load():
    return {n: pd.read_csv(CLEAN / f"{n}.csv") for n in
            ["results", "pit_stops", "team_standings",
             "driver_standings", "calendar", "team_colors"]}


d = load()
res, pit, ts = d["results"], d["pit_stops"], d["team_standings"]
ds, cal = d["driver_standings"], d["calendar"]
OFFICIAL = dict(zip(d["team_colors"]["team"],
                    d["team_colors"]["official_hex"]))
LAST = int(res["round"].max())
teams = (ts[ts["round"] == LAST].sort_values("position")["team"]
         .tolist())
drivers = (ds[ds["round"] == LAST].sort_values("position")
           [["code", "driver", "team"]])

# sidebar
st.sidebar.title("Controls")
palette = st.sidebar.radio(
    "Team colors", ["Top 4 + gray (Okabe-Ito)", "Official team colors"])
cvd = st.sidebar.selectbox(
    "View as", ["Normal vision", "Deuteranopia", "Protanopia"])
focus_team = st.sidebar.selectbox("Highlight a team", teams)
focus_driver = st.sidebar.selectbox(
    "Highlight a driver", drivers["code"],
    format_func=lambda c: drivers.set_index("code").loc[c, "driver"])
st.sidebar.caption("Data: F1DB v2026.15.1, 15 of 23 races.")


def see(hex_color):
    """Apply the colorblind simulation picked in the sidebar."""
    if cvd == "Normal vision":
        return hex_color
    return simulate(hex_color, cvd.lower())


def team_color(team, highlight=None):
    if palette.startswith("Official"):
        return see(OFFICIAL[team])
    if highlight and team == highlight:
        return see(TOP4.get(team, OKABE_ITO["sky"]))
    if highlight:
        return see(GRAY)
    return see(TOP4.get(team, GRAY))


def layout(fig, h=420, **kw):
    fig.update_layout(height=h, margin=dict(l=10, r=10, t=30, b=10),
                      plot_bgcolor="white", **kw)
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(gridcolor="#EEE")
    return fig


st.title("F1 2026: the season so far")
st.caption("Group 6, DATA 230. Lecture 4 (color) and Lecture 5 "
           "(directory of visualizations).")

c1, c2, c3, c4 = st.columns(4)
lead = drivers.iloc[0]
c1.metric("Leader", lead["driver"],
          f"{ds[(ds['round'] == LAST)]['points'].nlargest(2).diff().iloc[-1]:+.0f} pts gap")
c2.metric("Top team", teams[0],
          f"{ts[(ts['round'] == LAST) & (ts['team'] == teams[0])]['points'].iloc[0]:.0f} pts")
c3.metric("Races run", f"{LAST} of {len(cal)}")
c4.metric("Did not finish", f"{(res['status'] != 'Finished').mean():.0%}",
          "of all starts", delta_color="off")

tab4, tab5 = st.tabs(["Lecture 4: color", "Lecture 5: directory"])

with tab4:
    st.subheader("4.1 / 4.3  Team points, distinguish vs highlight")
    st.caption("Switch to official colors or a colorblind view in the "
               "sidebar and watch the lines merge.")
    fig = go.Figure()
    for t in teams[::-1]:
        on = t == focus_team
        g = ts[ts["team"] == t].sort_values("round")
        fig.add_scatter(x=g["round"], y=g["points"], name=t,
                        mode="lines",
                        line=dict(color=team_color(t, focus_team),
                                  width=4 if on else 1.6))
    fig.update_xaxes(tickvals=list(range(1, LAST + 1)), ticktext=ABBR)
    st.plotly_chart(layout(fig, yaxis_title="Team points",
                           legend_traceorder="reversed"),
                    width="stretch")

    st.subheader("4.2  Every result, three color scales")
    kind = st.radio("Scale", ["Sequential: finish position",
                              "Rainbow: finish position",
                              "Diverging: places gained"],
                    horizontal=True)
    code_order = drivers["code"].tolist()
    col = "gained" if kind.startswith("Diverging") else "finish"
    z = (res.pivot(index="code", columns="round", values=col)
            .reindex(code_order))
    if kind.startswith("Sequential"):
        scale, zmin, zmax = "Blues_r", 1, 22
    elif kind.startswith("Rainbow"):
        scale, zmin, zmax = "Jet_r", 1, 22
    else:
        scale, zmin, zmax = "RdBu", -10, 10
    hm = go.Figure(go.Heatmap(
        z=z.values, x=ABBR, y=code_order, colorscale=scale,
        zmin=zmin, zmax=zmax, xgap=1, ygap=1,
        hovertemplate="%{y} at %{x}: %{z}<extra></extra>"))
    hm.update_yaxes(autorange="reversed")
    hm = layout(hm, h=600)
    hm.update_layout(plot_bgcolor="#D9D9D9")  # gaps show as gray
    st.plotly_chart(hm, width="stretch")
    st.caption("Gray = did not finish or not entered. The diverging "
               "scale is capped at 10 places either way.")

    st.subheader("4.3  Highlight one driver's season")
    dw = ds.pivot(index="round", columns="code", values="points")
    fig = go.Figure()
    for c in dw.columns:
        if c != focus_driver:
            fig.add_scatter(x=dw.index, y=dw[c], mode="lines",
                            line=dict(color=see(GRAY), width=1.2),
                            name=c, showlegend=False)
    fig.add_scatter(x=dw.index, y=dw[focus_driver], mode="lines",
                    line=dict(color=see(OKABE_ITO["orange"]), width=4),
                    name=focus_driver)
    fig.update_xaxes(tickvals=list(range(1, LAST + 1)), ticktext=ABBR)
    st.plotly_chart(layout(fig, yaxis_title="Driver points"),
                    width="stretch")

with tab5:
    left, right = st.columns(2)

    with left:
        st.subheader("5.1  Amounts: team points")
        final = (ts[ts["round"] == LAST].sort_values("points"))
        fig = go.Figure(go.Bar(
            x=final["points"], y=final["team"], orientation="h",
            marker_color=[see(TOP4.get(t, OKABE_ITO["sky"]))
                          if t == focus_team else see("#4D6A8A")
                          for t in final["team"]],
            text=final["points"].astype(int), textposition="outside"))
        st.plotly_chart(layout(fig), width="stretch")

    with right:
        st.subheader("5.3  Proportions: points share per weekend")
        wide = ts.pivot(index="round", columns="team", values="points")
        per = wide.diff().fillna(wide.iloc[0])
        share = per.div(per.sum(axis=1), axis=0) * 100
        fig = go.Figure()
        for t in teams:
            fig.add_bar(x=ABBR, y=share[t], name=t,
                        marker_color=team_color(t))
        st.plotly_chart(layout(fig, barmode="stack",
                               yaxis_title="% of weekend points"),
                        width="stretch")

    st.subheader("5.2  Distributions: pit lane time by race")
    order = pit.groupby("round")["seconds"].median().sort_values().index
    fig = go.Figure()
    for r in order:
        g = pit[pit["round"] == r]
        fig.add_box(x=g["seconds"], name=ABBR[r - 1], boxpoints="all",
                    jitter=0.4, pointpos=0,
                    marker=dict(size=4, color=see(OKABE_ITO["blue"])),
                    line=dict(color="#777"), showlegend=False)
    st.plotly_chart(layout(fig, h=520,
                           xaxis_title="Pit lane time (s)"),
                    width="stretch")

    left, right = st.columns(2)
    with left:
        st.subheader("5.4  x-y: grid vs finish")
        fin = res.dropna(subset=["finish"])
        on = fin["code"] == focus_driver
        fig = go.Figure()
        fig.add_scatter(x=fin.loc[~on, "grid"], y=fin.loc[~on, "finish"],
                        mode="markers", name="everyone",
                        marker=dict(color=see(GRAY), size=7))
        fig.add_scatter(x=fin.loc[on, "grid"], y=fin.loc[on, "finish"],
                        mode="markers", name=focus_driver,
                        text=fin.loc[on, "gp"],
                        marker=dict(color=see(OKABE_ITO["orange"]),
                                    size=11))
        fig.add_scatter(x=[1, 22], y=[1, 22], mode="lines",
                        name="x = y", line=dict(color="#333",
                                                dash="dash"))
        st.plotly_chart(layout(fig, xaxis_title="Grid",
                               yaxis_title="Finish"),
                        width="stretch")

    with right:
        st.subheader("5.6  Uncertainty: pit speed by team")
        pit["vs_avg"] = pit["seconds"] - pit.groupby("round")[
            "seconds"].transform("mean")
        rows = []
        for t, s in pit.groupby("team")["vs_avg"]:
            h = stats.sem(s) * stats.t.ppf(0.975, len(s) - 1)
            rows.append((t, s.mean(), h))
        ci = pd.DataFrame(rows, columns=["team", "mean", "h"])
        ci = ci.sort_values("mean", ascending=False)
        fig = go.Figure(go.Scatter(
            x=ci["mean"], y=ci["team"], mode="markers",
            error_x=dict(type="data", array=ci["h"], thickness=2.5),
            marker=dict(size=10, color=[team_color(t) for t in
                                        ci["team"]])))
        fig.add_vline(x=0, line_dash="dash", line_color="#333")
        st.plotly_chart(layout(fig, xaxis_title="Seconds vs race "
                                                "average (left = quicker)"),
                        width="stretch")

    st.subheader("5.5  Geospatial: the calendar")
    win_team = res[res["finish"] == 1].set_index("round")["team"]
    cal["win_team"] = cal["round"].map(win_team).fillna("Upcoming")
    fig = go.Figure()
    for t, g in cal.groupby("win_team"):
        up = t == "Upcoming"
        fig.add_scattergeo(
            lat=g["lat"], lon=g["lon"], name=t, mode="markers",
            text=g["gp"] + "<br>" + g["winner"].fillna(g["date"]),
            marker=dict(size=12, color="white" if up else team_color(t),
                        line=dict(width=2,
                                  color="#888" if up else "white")))
    fig.update_geos(projection_type="robinson", showcountries=True,
                    countrycolor="#DDD", landcolor="#F2F2F2")
    st.plotly_chart(layout(fig, h=480), width="stretch")
