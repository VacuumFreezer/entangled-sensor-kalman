"""Figure 6: toy 4 with a limited supply of Bell pairs, k = 4 (linear Kalman filter calibrated to the exact simulation).
Tracking error of the target versus the pair supply rate for three simple allocation rules and the DP optimum.
Left: gradient target (case A).  Right: curvature target (case B)."""
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
D = json.load(open(os.path.join(HERE, "res_t4_supply.json")))
Rs = [0.25, 0.5, 1.0, 2.0, 4.0, 8.0, 16.0, 32.0, "inf"]
xpos = {R: i for i, R in enumerate(Rs)}; xpos["inf"] = 8.4
xs = [xpos[R] for R in Rs]

fig, axes = plt.subplots(1, 2, figsize=(9.6, 4.3), dpi=200)
for ax, case, title in zip(axes, "AB", ("Target: gradient.  Disturbance: uniform field", "Target: curvature.  Disturbances: uniform field, gradient")):
    rows = {r["R"]: r for r in D if r["case"] == case}
    get = lambda key: np.array([rows[R][key] for R in Rs])
    none = rows[Rs[0]]["none"]
    ax.plot([xs[0] - 0.3, xs[-1]], [none, none], color=BLUE, lw=1.8)
    def line(key, col, ls="-", z=2):
        ys = get(key)
        for seg in (slice(0, 8), slice(7, 9)):
            ax.plot(xs[seg], ys[seg], color=col, lw=1.8, ls=(ls if seg.start == 0 else (0, (1, 2))), zorder=z)
        ax.plot(xs, ys, marker="o", markersize=6, color=col, markeredgecolor=SURF, markeredgewidth=1.2, linestyle="none", zorder=z + 1)
        return ys
    yg = line("greedy", GRAY, ls=(0, (5, 2)))
    y1 = line("one_pair", AQUA)
    y3 = line("save_ghz", ORANGE, z=4)
    ax.plot(xs, get("dp"), marker="o", markersize=4.5, markerfacecolor="none", markeredgecolor=INK, markeredgewidth=1.0, linestyle="none", zorder=6)
    ax.set_yscale("log")
    if case == "A":
        ax.set_ylim(0.9, 2.2); yt = [1, 1.2, 1.5, 2]
        ax.text(xs[-1], none * 1.02, "no entanglement", ha="right", va="bottom", fontsize=8.8)
        ax.text(4.1, 1.72, "save three pairs,\nthen one GHZ state", ha="left", va="bottom", fontsize=8.8)
        ax.text(0.0, 1.42, "one pair per cycle\non the outer link", ha="left", va="top", fontsize=8.8)
    else:
        ax.set_ylim(1.0, 26); yt = [1, 2, 5, 10, 20]
        ax.text(xs[-1], none * 1.03, "no entanglement", ha="right", va="bottom", fontsize=8.8)
        ax.text(5.15, 11.4, "one pair per cycle", ha="left", va="bottom", fontsize=8.8)
        ax.text(0.0, 6.2, "save three pairs,\nthen one GHZ state", ha="left", va="top", fontsize=8.8)
    ax.set_yticks(yt); ax.set_yticklabels([str(v) for v in yt]); ax.minorticks_off()
    ax.set_xticks(xs); ax.set_xticklabels(["0.25", "0.5", "1", "2", "4", "8", "16", "32", "$\\infty$"])
    ax.set_xlim(xs[0] - 0.3, xs[-1] + 0.25)
    ax.grid(True, axis="y", color=GRID, lw=0.7); ax.set_axisbelow(True)
    ax.set_title(title, loc="left", fontsize=9.8, pad=8)
    ax.set_xlabel("supply rate of Bell pairs  $R\\,\\tau$")
axes[0].set_ylabel("tracking error of the target   $MSE/q_{target}^{2/3}$")
handles = [Line2D([], [], color=BLUE, lw=1.8, label="no entanglement"),
           Line2D([], [], color=GRAY, lw=1.8, ls=(0, (5, 2)), marker="o", markersize=5.5, markeredgecolor=SURF, label="use every stored pair at once"),
           Line2D([], [], color=AQUA, lw=1.8, marker="o", markersize=5.5, markeredgecolor=SURF, label="one pair per cycle on the outer link"),
           Line2D([], [], color=ORANGE, lw=1.8, marker="o", markersize=5.5, markeredgecolor=SURF, label="save three pairs, then one GHZ state"),
           Line2D([], [], marker="o", markersize=4.5, markerfacecolor="none", markeredgecolor=INK, linestyle="none", label="optimal policy (dynamic programming)")]
fig.legend(handles=handles, loc="lower center", ncol=3, fontsize=8.4, handlelength=2.4, columnspacing=1.6, bbox_to_anchor=(0.5, 0.0))
fig.suptitle("Four sensors, limited Bell pairs: the best allocation rule depends on the target mode", x=0.065, ha="left", fontsize=10.8)
fig.subplots_adjust(left=0.065, right=0.985, top=0.86, bottom=0.25, wspace=0.16)
fig.savefig(os.path.join(OUT, "fig6_supply.png"))
print("saved")
