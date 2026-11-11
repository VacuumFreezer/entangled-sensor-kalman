"""Primer figure: probability of outcome +1 versus the phase error, for one sensor (kappa = 1) and a
3-sensor GHZ state (kappa = 3). The GHZ fringe is 3 times steeper and its unambiguous range 3 times narrower."""
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT = os.environ.get("OUT", ".")
SURF, INK, INK2, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#e4e3de"
BLUE, ORANGE = "#2a78d6", "#eb6834"
plt.rcParams.update({
    "font.size": 9.5, "axes.edgecolor": INK2, "axes.labelcolor": INK, "text.color": INK,
    "xtick.color": INK2, "ytick.color": INK2, "axes.spines.top": False, "axes.spines.right": False,
    "axes.linewidth": 0.8, "figure.facecolor": SURF, "axes.facecolor": SURF, "savefig.facecolor": SURF,
    "legend.frameon": False, "mathtext.default": "regular",
})
e = np.linspace(-np.pi, np.pi, 1000)
fig, ax = plt.subplots(figsize=(7.4, 4.0), dpi=200)
for k, col in ((1, BLUE), (3, ORANGE)):
    ax.axvspan(-np.pi / (2 * k), np.pi / (2 * k), color=col, alpha=0.10, lw=0)
    ax.plot(e, 0.5 * (1 + np.sin(k * e)), color=col, lw=1.8)
from matplotlib.lines import Line2D
ax.legend(handles=[Line2D([], [], color=BLUE, lw=1.8, label="one sensor ($\\kappa=1$)"),
                   Line2D([], [], color=ORANGE, lw=1.8, label="GHZ state on 3 sensors ($\\kappa=3$)")],
          loc="upper center", bbox_to_anchor=(0.5, -0.2), ncol=2, fontsize=8.5, handlelength=1.8)
ax.annotate("", xy=(np.pi / 6, -0.07), xytext=(-np.pi / 6, -0.07), arrowprops=dict(arrowstyle="<->", color=ORANGE, lw=1.0))
ax.text(0, -0.15, "unambiguous range, $\\kappa=3$", ha="center", va="top", fontsize=8.5, color=INK2)
ax.annotate("", xy=(np.pi / 2, -0.30), xytext=(-np.pi / 2, -0.30), arrowprops=dict(arrowstyle="<->", color=BLUE, lw=1.0))
ax.text(0, -0.38, "unambiguous range, $\\kappa=1$", ha="center", va="top", fontsize=8.5, color=INK2)
ax.set_xlim(-np.pi, np.pi); ax.set_ylim(-0.5, 1.12)
ax.set_xticks([-np.pi, -np.pi / 2, 0, np.pi / 2, np.pi]); ax.set_xticklabels(["$-\\pi$", "$-\\pi/2$", "0", "$\\pi/2$", "$\\pi$"])
ax.set_yticks([0, 0.5, 1]); ax.spines["left"].set_bounds(0, 1)
ax.grid(True, axis="y", color=GRID, lw=0.7); ax.set_axisbelow(True)
ax.set_xlabel("phase error  $\\varphi-\\hat\\varphi$   (rad)")
ax.set_ylabel("Prob(outcome $=+1$)")
ax.set_title("Entanglement makes the fringe steeper and the usable range narrower", loc="left", fontsize=10.5, pad=8)
fig.subplots_adjust(left=0.10, right=0.97, top=0.90, bottom=0.24)
fig.savefig(os.path.join(OUT, "fig_fringe.png"))
