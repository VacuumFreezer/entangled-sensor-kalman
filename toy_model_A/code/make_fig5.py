"""Figure 5: toy 4, k = 4 sensors.  Tracking error of the target mode versus the intensity of the disturbance modes,
for unentangled sensors (two strategies), mirror Bell pairs and one GHZ state.
Left: target = gradient, disturbance = uniform field.  Right: target = curvature, disturbances = uniform field + gradient."""
import json, os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.dirname(HERE)
SURF, INK, INK2, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#e4e3de"
BLUE, ORANGE, AQUA, GRAY = "#2a78d6", "#eb6834", "#1baf7a", "#62615c"
plt.rcParams.update({
    "font.size": 9.5, "axes.edgecolor": INK2, "axes.labelcolor": INK, "text.color": INK,
    "xtick.color": INK2, "ytick.color": INK2, "axes.spines.top": False, "axes.spines.right": False,
    "axes.linewidth": 0.8, "figure.facecolor": SURF, "axes.facecolor": SURF, "savefig.facecolor": SURF,
    "legend.frameon": False, "mathtext.default": "regular",
})
S = json.load(open(os.path.join(HERE, "res_t4_summary.json")))
rows = {(r["case"], r["k"]): r for r in S["rows"]}
Sx = json.load(open(os.path.join(HERE, "res_t4_S.json")))

fig, axes = plt.subplots(1, 2, figsize=(9.6, 4.3), dpi=200)
panels = [("A", "Target: gradient.  Disturbance: uniform field", (0.8, 4.6), [1, 1.5, 2, 3, 4]),
          ("B", "Target: curvature.  Disturbances: uniform field, gradient", (1.0, 30), [1, 2, 5, 10, 20])]
for ax, (case, title, ylim, yt) in zip(axes, panels):
    r = rows[(case, 4)]
    rho = np.array([float(a) for a in r["S_lin"] if float(a) > 0]); Js = np.array([r["S_lin"][a] for a in r["S_lin"] if float(a) > 0])
    x0, x1 = 1.0, 1e6
    ax.plot(rho, Js, color=BLUE, lw=1.8)
    ax.plot([x0, x1], [r["sep"]["J"]] * 2, color=BLUE, lw=1.8, ls=(0, (5, 2)))
    ax.plot([x0, x1], [r["pairs"]["J"]] * 2, color=AQUA, lw=1.8)
    ax.plot([x0, x1], [r["ghz"]["J"]] * 2, color=ORANGE, lw=1.8)
    ex = {}
    for q in Sx:
        if q["case"] == case and q["k"] == 4: ex.setdefault(q["rho"], []).append(q["mse"])
    for rr, v in ex.items():
        ax.plot([rr], [np.mean(v)], marker="D", markersize=6, color=BLUE, markeredgecolor=INK, markeredgewidth=1.0, linestyle="none", zorder=5)
    ax.set_xscale("log"); ax.set_yscale("log"); ax.set_xlim(x0, x1); ax.set_ylim(*ylim)
    ax.set_yticks(yt); ax.set_yticklabels([str(v) for v in yt]); ax.minorticks_off()
    ax.set_xticks([1, 1e2, 1e4, 1e6])
    ax.grid(True, axis="y", color=GRID, lw=0.7); ax.set_axisbelow(True)
    ax.set_title(title, loc="left", fontsize=9.8, pad=8)
    ax.set_xlabel("disturbance intensity  $q_{disturbance}/q_{target}$")
    # direct labels
    if case == "A":
        ax.text(2e3, 3.42, "tracks every mode", color=INK, fontsize=8.8, ha="right", va="bottom")
        ax.text(1e6 / 1.4, r["sep"]["J"] * 1.035, "disturbance-blind correlations", fontsize=8.8, va="bottom", ha="right")
        ax.text(1.4, r["pairs"]["J"] * 1.03, "two Bell pairs", fontsize=8.8, va="bottom")
        ax.text(1.4, r["ghz"]["J"] * 0.965, "one GHZ state", fontsize=8.8, va="top")
    else:
        ax.text(3e3, 8.6, "tracks every mode", color=INK, fontsize=8.8, ha="right", va="bottom")
        ax.text(1.4, r["sep"]["J"] * 1.05, "disturbance-blind correlations", fontsize=8.8, va="bottom")
        ax.text(1e6 / 1.4, r["pairs"]["J"] * 0.95, "two Bell pairs", fontsize=8.8, va="top", ha="right")
        ax.text(1e6 / 1.4, r["ghz"]["J"] * 0.95, "one GHZ state", fontsize=8.8, va="top", ha="right")
axes[0].set_ylabel("tracking error of the target   $MSE/q_{target}^{2/3}$")
handles = [Line2D([], [], color=BLUE, lw=1.8, label="unentangled, tracks every mode"),
           Line2D([], [], color=BLUE, lw=1.8, ls=(0, (5, 2)), label="unentangled, disturbance-blind correlations"),
           Line2D([], [], color=AQUA, lw=1.8, label="two Bell pairs"),
           Line2D([], [], color=ORANGE, lw=1.8, label="one GHZ state"),
           Line2D([], [], marker="D", markersize=6, color=BLUE, markeredgecolor=INK, linestyle="none", label="exact simulation of the solid line")]
fig.legend(handles=handles, loc="lower center", ncol=3, fontsize=8.4, handlelength=2.4, columnspacing=1.6, bbox_to_anchor=(0.5, 0.0))
fig.suptitle("Four sensors, one target mode: what the disturbance modes cost with and without entanglement", x=0.065, ha="left", fontsize=10.8)
fig.subplots_adjust(left=0.065, right=0.985, top=0.86, bottom=0.25, wspace=0.16)
fig.savefig(os.path.join(OUT, "fig5_nuisance.png"))
print("saved")
