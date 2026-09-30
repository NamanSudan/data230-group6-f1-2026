"""Shared colors and plot settings for notebooks 02 and 03."""
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
CLEAN = HERE / "data" / "clean"
FIGS = HERE / "figures"
FIGS.mkdir(exist_ok=True)

# Okabe-Ito, the colorblind-safe qualitative scale from Ch 4.1
OKABE_ITO = {
    "orange": "#E69F00", "sky": "#56B4E9", "green": "#009E73",
    "yellow": "#F0E442", "blue": "#0072B2", "red": "#D55E00",
    "purple": "#CC79A7", "black": "#000000",
}
GRAY = "#BBBBBB"
DARK = "#333333"

# Top 4 teams get an Okabe-Ito color, everyone else is gray (Ch 4.3)
TOP4 = {
    "Mercedes": OKABE_ITO["green"],
    "Ferrari": OKABE_ITO["red"],
    "McLaren": OKABE_ITO["orange"],
    "Red Bull": OKABE_ITO["blue"],
}

plt.rcParams.update({
    "figure.figsize": (9, 5),
    "figure.dpi": 110,
    "savefig.dpi": 200,
    "savefig.bbox": "tight",
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.titlesize": 13,
    "axes.titleweight": "bold",
    "axes.titlelocation": "left",
    "axes.labelsize": 11,
    "font.size": 10,
})


def load(name):
    return pd.read_csv(CLEAN / f"{name}.csv")


def official_colors():
    tc = load("team_colors")
    return dict(zip(tc["team"], tc["official_hex"]))


def save(fig, name):
    fig.savefig(FIGS / f"{name}.png")


# Colorblind simulation (Machado et al. 2009, full severity).
# Applied in linear RGB, then converted back to sRGB.
CVD = {
    "deuteranopia": np.array([[0.367322, 0.860646, -0.227968],
                              [0.280085, 0.672501, 0.047413],
                              [-0.011820, 0.042940, 0.968881]]),
    "protanopia": np.array([[0.152286, 1.052583, -0.204868],
                            [0.114503, 0.786281, 0.099216],
                            [-0.003882, -0.048116, 1.051998]]),
}


def _to_linear(c):
    return np.where(c <= 0.04045, c / 12.92,
                    ((c + 0.055) / 1.055) ** 2.4)


def _to_srgb(c):
    c = np.clip(c, 0, 1)
    return np.where(c <= 0.0031308, c * 12.92,
                    1.055 * c ** (1 / 2.4) - 0.055)


def simulate(hex_color, kind="deuteranopia"):
    h = hex_color.lstrip("#")
    rgb = np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)]) / 255
    out = _to_srgb(CVD[kind] @ _to_linear(rgb))
    return "#" + "".join(f"{int(round(v * 255)):02X}" for v in out)
