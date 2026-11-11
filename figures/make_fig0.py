"""Figure 0 of the primer: a one-dimensional Kalman filter tracking a random walk.
Top: true value, noisy measurements, estimate with a +-1 sigma band. Bottom: the error variance P,
which grows between measurements (prediction) and drops at each measurement (update)."""
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

OUT = os.environ.get("OUT", ".")
SURF, INK, INK2, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#e4e3de"
BLUE, ORANGE = "#2a78d6", "#eb6834"
plt.rcParams.update({
    "font.size": 9.5, "axes.edgecolor": INK2, "axes.labelcolor": INK, "text.color": INK,
    "xtick.color": INK2, "ytick.color": INK2, "axes.spines.top": False, "axes.spines.right": False,
    "axes.linewidth": 0.8, "figure.facecolor": SURF, "axes.facecolor": SURF, "savefig.facecolor": SURF,
    "legend.frameon": False, "mathtext.default": "regular",
})

rng = np.random.default_rng(7)
q, r, Delta, n = 1.0, 1.0, 0.5, 24          # q*Delta = 0.5, r = 1: the worked example in the text
dt = 0.005
t_fine = np.arange(0, n * Delta + 1e-9, dt)
x_fine = np.concatenate([[0.0], np.cumsum(np.sqrt(q * dt) * rng.standard_normal(len(t_fine) - 1))])
tm = np.arange(1, n + 1) * Delta
idx = np.round(tm / dt).astype(int)
y = x_fine[idx] + np.sqrt(r) * rng.standard_normal(n)

xh, P = 0.0, 1.0
t_est, x_est, P_est = [0.0], [xh], [P]
for k in range(n):
    t0 = k * Delta
    seg = np.linspace(t0, tm[k], 50)
    t_est += list(seg[1:]); x_est += [xh] * 49; P_est += list(P + q * (seg[1:] - t0))   # prediction: P grows
    Pm = P + q * Delta
    K = Pm / (Pm + r)
    xh = xh + K * (y[k] - xh); P = (1 - K) * Pm                                          # update: P drops
    t_est.append(tm[k]); x_est.append(xh); P_est.append(P)
t_est, x_est, P_est = map(np.array, (t_est, x_est, P_est))

fig, (a1, a2) = plt.subplots(2, 1, figsize=(7.4, 5.0), dpi=200, sharex=True, gridspec_kw=dict(height_ratios=[2.2, 1]))
a1.fill_between(t_est, x_est - np.sqrt(P_est), x_est + np.sqrt(P_est), color=ORANGE, alpha=0.16, lw=0)
a1.plot(t_fine, x_fine, color=INK2, lw=1.1)
a1.plot(t_est, x_est, color=ORANGE, lw=1.8)
a1.plot(tm, y, marker="o", markersize=5, color=BLUE, markeredgecolor=SURF, markeredgewidth=1.0, linestyle="none")
a1.set_ylabel("field  $x$")
a1.grid(True, axis="y", color=GRID, lw=0.7); a1.set_axisbelow(True)
a1.set_title("A Kalman filter tracking a randomly drifting field", loc="left", fontsize=10.5, pad=8)
handles = [Line2D([], [], color=INK2, lw=1.1, label="true field (hidden)"),
           Line2D([], [], color=BLUE, marker="o", markersize=5, markeredgecolor=SURF, linestyle="none", label="noisy measurement $y_n$"),
           Line2D([], [], color=ORANGE, lw=1.8, label="estimate $\\hat x$"),
           plt.Rectangle((0, 0), 1, 1, color=ORANGE, alpha=0.16, label="$\\hat x \\pm \\sqrt{P}$")]
a1.legend(handles=handles, loc="lower left", fontsize=8.3, ncol=2, handlelength=1.8, columnspacing=1.2)
a2.plot(t_est, P_est, color=ORANGE, lw=1.6)
a2.hlines([0.5, 1.0], 0, n * Delta, color=INK2, lw=0.8, ls=(0, (4, 3)))
a2.text(n * Delta + 0.12, 1.0, "$P^-=1$", va="center", fontsize=8.5, color=INK2)
a2.text(n * Delta + 0.12, 0.5, "$P^+=0.5$", va="center", fontsize=8.5, color=INK2)
a2.annotate("grows while\nnobody measures", xy=(1.25, 0.86), xytext=(2.4, 1.32), fontsize=8.3, color=INK2,
            arrowprops=dict(arrowstyle="-", color=INK2, lw=0.7))
a2.annotate("drops at each\nmeasurement", xy=(2.0, 0.55), xytext=(3.6, 0.12), fontsize=8.3, color=INK2,
            arrowprops=dict(arrowstyle="-", color=INK2, lw=0.7))
a2.set_ylim(0, 1.75); a2.set_xlim(0, n * Delta + 1.1)
a2.set_ylabel("error variance  $P$")
a2.set_xlabel("time")
a2.grid(True, axis="y", color=GRID, lw=0.7); a2.set_axisbelow(True)
fig.subplots_adjust(left=0.10, right=0.95, top=0.92, bottom=0.10, hspace=0.12)
fig.savefig(os.path.join(OUT, "fig0_kalman_intro.png"))
print("P after updates:", np.round(P_est[np.isin(t_est, tm)][:6], 4))
