"""Figure 4: tracking cost versus the supply rate of entangled pairs for different scheduling policies
(toy 3, rho = 1000, cost = MSE_b / rho^(2/3) + MSE_g; linear Kalman filter model, exact-simulation points overlaid)."""
import json, os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.dirname(HERE) if os.path.basename(HERE) == "code" else HERE
SURF, INK, INK2, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#e4e3de"
BLUE, ORANGE, AQUA, GRAY = "#2a78d6", "#eb6834", "#1baf7a", "#62615c"
plt.rcParams.update({
    "font.size": 9.5, "axes.edgecolor": INK2, "axes.labelcolor": INK, "text.color": INK,
    "xtick.color": INK2, "ytick.color": INK2, "axes.spines.top": False, "axes.spines.right": False,
    "axes.linewidth": 0.8, "figure.facecolor": SURF, "axes.facecolor": SURF, "savefig.facecolor": SURF,
    "legend.frameon": False, "mathtext.default": "regular",
})

rows = [r for r in json.load(open(os.path.join(HERE, "res3_sweep.json"))) if r["rho"] == 1000 and r["lam"] == 1.0]
Rs = [0.5, 1.0, 2.0, 4.0, 8.0, 16.0, "inf"]
xpos = {0.5: -1, 1.0: 0, 2.0: 1, 4.0: 2, 8.0: 3, 16.0: 4, "inf": 5.3}
get = lambda key: [next(r[key] for r in rows if r["R"] == R) for R in Rs]
xs = [xpos[R] for R in Rs]
none = rows[0]["S_only"]
YMAX = 5.9

fig, ax = plt.subplots(figsize=(7.4, 4.5), dpi=200)
ax.plot([-1.3, 5.3], [none, none], color=BLUE, lw=1.8)
def line(key, col, ls="-", z=2):
    ys = np.array(get(key))
    for seg in (slice(0, 6), slice(5, 7)):             # the last segment (16 -> infinity) is drawn dotted: axis break
        ax.plot(xs[seg], np.minimum(ys[seg], 99), color=col, lw=1.8, ls=(ls if seg.start == 0 else (0, (1, 2))), zorder=z, clip_on=True)
    ok = ys <= YMAX
    ax.plot(np.array(xs)[ok], ys[ok], marker="o", markersize=6.5, color=col, markeredgecolor=SURF, markeredgewidth=1.3, linestyle="none", zorder=z + 1)
    return ys
ye = line("eager_alt", GRAY, ls=(0, (5, 2)))
yt = line("thin", AQUA)
ys_ = line("timer", ORANGE, z=4)
yd = np.array(get("dp"))
ax.plot(xs, yd, marker="o", markersize=4.5, markerfacecolor="none", markeredgecolor=INK, markeredgewidth=1.0, linestyle="none", zorder=6)
# exact simulation points (binary outcomes + particle filter)
ex = json.load(open(os.path.join(HERE, "res3_exact.json")))
for r in ex:
    if r["policy"] == "timer" and ((r["R"] == "inf" and r["par"] == 0.2) or (r["R"] == 2.0 and r["par"] == 0.15)):
        J = float(np.mean(r["mse_b"]) + np.mean(r["mse_g"]))
        ax.plot([xpos[r["R"]]], [J], marker="D", markersize=6.5, color=ORANGE, markeredgecolor=INK, markeredgewidth=1.0, linestyle="none", zorder=7)

# no-entanglement baseline, exact simulation at c = 0.5 (seeds with a phase slip excluded)
ex2 = json.load(open(os.path.join(HERE, "res3_exact2.json")))
Js = [b + g for r in ex + ex2 if r["policy"] == "S" and r.get("c", 0.5) == 0.5 for b, g in zip(r["mse_b"], r["mse_g"])]
Js = np.array(Js); keep = Js < 1.3 * Js.min()
ax.plot([xpos["inf"]], [Js[keep].mean()], marker="D", markersize=6.5, color=BLUE, markeredgecolor=INK, markeredgewidth=1.0, linestyle="none", zorder=7)
print("exact no-entanglement J:", Js, "kept mean", Js[keep].mean())

ax.annotate("%.1f at $R=\\infty$" % ye[-1], xy=(4.42, YMAX - 0.01), xytext=(4.62, YMAX - 0.12), fontsize=8.8, color=INK2, ha="left", va="center")
xl = 5.45
ax.text(xl, none - 0.02, "no entanglement", va="center", fontsize=9)
ax.text(xl, yt[-1] + 0.02, "random use\n(no filter state)", va="center", fontsize=9)
ax.text(xl, ys_[-1] - 0.03, "minimum-spacing\nschedule", va="center", fontsize=9)
ax.text(3.2, 4.42, "every pair used\non arrival", va="center", ha="right", fontsize=9)
ax.set_xlim(-1.3, 5.4); ax.set_ylim(3.5, YMAX)
ax.set_xticks(xs); ax.set_xticklabels(["0.5", "1", "2", "4", "8", "16", "$\\infty$"])
ax.grid(True, axis="y", color=GRID, lw=0.7); ax.set_axisbelow(True)
ax.set_xlabel("supply rate of entangled pairs  $R\\,\\tau_g$")
ax.set_ylabel("tracking cost   $MSE_b/q_b^{2/3}+MSE_g/q_g^{2/3}$")
ax.set_title("Two sensors, two modes: the schedule decides whether entanglement helps", loc="left", fontsize=10.5, pad=10)
handles = [Line2D([], [], color=BLUE, lw=1.8, label="no entanglement"),
           Line2D([], [], color=GRAY, lw=1.8, ls=(0, (5, 2)), marker="o", markersize=5.5, markeredgecolor=SURF, label="every pair used on arrival (alternating modes)"),
           Line2D([], [], color=AQUA, lw=1.8, marker="o", markersize=5.5, markeredgecolor=SURF, label="pair used with fixed probability"),
           Line2D([], [], color=ORANGE, lw=1.8, marker="o", markersize=5.5, markeredgecolor=SURF, label="minimum-spacing schedule (one parameter)"),
           Line2D([], [], marker="o", markersize=4.5, markerfacecolor="none", markeredgecolor=INK, linestyle="none", label="optimal policy (dynamic programming)"),
           Line2D([], [], marker="D", markersize=6, color=GRAY, markeredgecolor=INK, linestyle="none", label="diamond: exact simulation (binary outcomes)")]
ax.legend(handles=handles, loc="upper left", bbox_to_anchor=(0.0, 1.0), fontsize=8.0, handlelength=2.4, labelspacing=0.35, borderaxespad=0.1)
fig.subplots_adjust(left=0.10, right=0.80, top=0.90, bottom=0.13)
fig.savefig(os.path.join(OUT, "fig4_scheduling.png"))
print("saved")
