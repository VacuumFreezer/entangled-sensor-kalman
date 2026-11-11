"""Figures for the toy-model analysis. Reads the simulation results (res*.json) in this folder and
computes the linear-Kalman-filter curves with lin_fast.py.  Units: q = 1, coupling = 1."""
import json, os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from lin_fast import best, sep, ghz

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.dirname(HERE)          # figures go next to the write-up
SURF, INK, INK2, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#e4e3de"
BLUE, ORANGE, AQUA = "#2a78d6", "#eb6834", "#1baf7a"
RAMP = ["#9a9992", "#62615c", "#1f1f1e"]          # ordinal ramp for k = 2, 3, 4
plt.rcParams.update({
    "font.size": 9.5, "axes.edgecolor": INK2, "axes.labelcolor": INK, "text.color": INK,
    "xtick.color": INK2, "ytick.color": INK2, "axes.spines.top": False, "axes.spines.right": False,
    "axes.linewidth": 0.8, "figure.facecolor": SURF, "axes.facecolor": SURF, "savefig.facecolor": SURF,
    "legend.frameon": False, "mathtext.default": "regular",
})
MK = dict(markersize=7, markeredgecolor=SURF, markeredgewidth=1.4, linestyle="none")


def load(name):
    return json.load(open(os.path.join(HERE, name)))


def sim_value(rows, name, c, key=None):
    for r in rows:
        if r["name"] == name and abs(r["c"] - c) < 1e-9 and (key is None or key(r)):
            return float(np.mean(r["mse"]))
    raise KeyError((name, c))


# ---------------------------------------------------------------- figure 1
def fig_scaling():
    r4, r7, r9 = load("res4.json"), load("res7.json"), load("res9.json")
    ks = np.arange(1, 17)
    lin_sep = [best(sep(k), 0.5)[1] for k in ks]
    lin_ghz = [best(ghz(k), 0.5)[1] for k in ks]
    plain = lambda r: not r.get("kw")
    sim_sep = {1: sim_value(r4, "ghz1", 0.5), 2: sim_value(r4, "sep2", 0.5), 3: sim_value(r4, "sep3", 0.5),
               4: sim_value(r4, "sep4", 0.5)}
    for r in r9:
        if r["name"].startswith("sep"):
            sim_sep[int(r["name"][3:])] = float(np.mean(r["mse"]))
    sim_ghz = {1: sim_value(r4, "ghz1", 0.5), 2: sim_value(r4, "ghz2", 0.5),
               3: sim_value(r7, "ghz3", 0.5, plain), 4: sim_value(r7, "ghz4", 0.5, plain)}

    fig, ax = plt.subplots(figsize=(7.4, 4.5), dpi=200)
    ax.set_xscale("log"); ax.set_yscale("log")
    ax.plot(ks, lin_sep, color=BLUE, lw=1.8, zorder=2)
    ax.plot(ks, lin_ghz, color=ORANGE, lw=1.8, zorder=2)
    ax.plot(list(sim_sep), list(sim_sep.values()), marker="o", color=BLUE, zorder=3, **MK)
    ax.plot(list(sim_ghz), list(sim_ghz.values()), marker="o", color=ORANGE, zorder=4, **MK)
    # resource reading: GHZ(4) versus the separable curve
    y4 = sim_ghz[4]
    ksim = sorted(sim_sep)                      # number of separable sensors with the same simulated MSE
    k_eq = float(np.exp(np.interp(-np.log(y4), [-np.log(sim_sep[k]) for k in ksim], np.log(ksim))))
    ax.plot([4, k_eq], [y4, y4], color=INK2, lw=0.9, ls=(0, (4, 3)), zorder=1)
    ax.text(3.82, y4 * 0.955, "same tracking error:\n4 entangled $\\approx$ %d unentangled" % round(k_eq),
            ha="right", va="top", fontsize=8.8, color=INK2)
    ax.text(16.8, lin_sep[-1], "no entanglement\n$\\propto k^{-1/3}$", va="center", ha="left", fontsize=9, color=INK)
    ax.text(16.8, lin_ghz[-1], "GHZ state\n$\\propto k^{-2/3}$", va="center", ha="left", fontsize=9, color=INK)
    ax.set_xticks([1, 2, 3, 4, 6, 8, 12, 16]); ax.set_xticklabels(["1", "2", "3", "4", "6", "8", "12", "16"])
    ax.set_yticks([0.3, 0.5, 1.0, 2.0]); ax.set_yticklabels(["0.3", "0.5", "1", "2"])
    ax.minorticks_off()
    ax.set_xlim(0.92, 17); ax.set_ylim(0.25, 2.3)
    ax.grid(True, which="major", color=GRID, lw=0.7); ax.set_axisbelow(True)
    ax.set_xlabel("number of sensors  $k$")
    ax.set_ylabel("time-averaged tracking MSE   (units of $q^{2/3}$)")
    ax.set_title("Tracking a random-walk field: entangled vs unentangled sensors", loc="left", fontsize=10.5, pad=10)
    handles = [Line2D([], [], color=BLUE, lw=1.8, label="no entanglement ($k$ separable sensors)"),
               Line2D([], [], color=ORANGE, lw=1.8, label="one GHZ state on all $k$ sensors"),
               Line2D([], [], color=INK2, lw=1.4, label="line: linear Kalman filter, lock constraint $c=0.5$"),
               Line2D([], [], color=INK2, marker="o", label="marker: exact simulation (binary outcomes)", **MK)]
    ax.legend(handles=handles, loc="upper right", fontsize=8.3, handlelength=1.8, borderaxespad=0.2)
    fig.subplots_adjust(left=0.10, right=0.84, top=0.90, bottom=0.13)
    fig.savefig(os.path.join(OUT, "fig1_scaling.png"))
    plt.close(fig)
    return dict(lin_sep=dict(zip(ks.tolist(), lin_sep)), lin_ghz=dict(zip(ks.tolist(), lin_ghz)),
                sim_sep=sim_sep, sim_ghz=sim_ghz, k_eq=float(k_eq))


# ---------------------------------------------------------------- figure 2
def fig_window():
    gs = np.linspace(0, 3, 31)
    tes = np.linspace(0, 0.15, 31)
    fig, axes = plt.subplots(1, 2, figsize=(7.4, 3.7), dpi=200, sharey=True)
    out = {"deph": {}, "gen": {}}
    for ax, xs, kind in ((axes[0], gs, "deph"), (axes[1], tes, "gen")):
        for k, col in zip((2, 3, 4), RAMP):
            if kind == "deph":
                ys = [best(ghz(k), 0.5, gamma=g)[1] / best(sep(k), 0.5, gamma=g)[1] for g in xs]
            else:
                s0 = best(sep(k), 0.5)[1]
                ys = [best(ghz(k), 0.5, T_dead=t)[1] / s0 for t in xs]
            out[kind][k] = dict(x=xs.tolist(), ratio=ys)
            ax.plot(xs, ys, color=col, lw=1.8)
            if kind == "deph":
                ax.text(xs[0] - 0.07, ys[0], "$k=%d$" % k, ha="right", va="center", fontsize=9)
            else:
                ax.text(xs[0] - 0.0035, ys[0], "$k=%d$" % k, ha="right", va="center", fontsize=9)
        ax.axhline(1.0, color=INK2, lw=0.9, ls=(0, (4, 3)))
        ax.grid(True, axis="y", color=GRID, lw=0.7); ax.set_axisbelow(True)
    axes[0].text(3.0, 1.012, "break-even", ha="right", va="bottom", fontsize=8.5, color=INK2)
    axes[0].set_xlim(-0.45, 3.05); axes[0].set_xticks([0, 1, 2, 3])
    axes[1].set_xlim(-0.0225, 0.1525); axes[1].set_xticks([0, 0.05, 0.10, 0.15])
    axes[0].set_ylim(0.7, 1.3)
    axes[0].set_ylabel("MSE ratio   GHZ / no entanglement")
    axes[0].set_xlabel("dephasing rate  $\\gamma\\,\\tau_q$   ($=\\tau_q/T_2$)")
    axes[1].set_xlabel("GHZ generation time  $T_e/\\tau_q$   (sensors idle)")
    axes[0].set_title("(a) local dephasing", loc="left", fontsize=10)
    axes[1].set_title("(b) time spent generating entanglement", loc="left", fontsize=10)
    handles = [Line2D([], [], color=c, lw=1.8, label="$k=%d$ sensors" % k) for k, c in zip((2, 3, 4), RAMP)]
    axes[1].legend(handles=handles, loc="lower right", fontsize=8.3, handlelength=1.8)
    fig.subplots_adjust(left=0.09, right=0.95, top=0.90, bottom=0.15, wspace=0.10)
    fig.savefig(os.path.join(OUT, "fig2_window.png"))
    plt.close(fig)
    return out


# ---------------------------------------------------------------- figure 3
def fig_gradient():
    rows = load("res6.json") + load("res8.json")
    r4 = load("res4.json")
    ent = sim_value(r4, "ghz1", 0.5) * 2 ** (-2 / 3)      # effective qubit with coupling 2
    data = {"A": {}, "B": {}}
    for r in rows:
        if abs(r["c"] - 0.5) > 1e-9 or r["rho"] == 0:
            continue
        data[r["policy"]].setdefault(r["rho"], []).extend(r["mse"])
    rhos = sorted(data["A"])
    # a run with a phase slip shows up as a seed far above the others; such seeds are excluded from
    # the plotted mean and the point is drawn with an open marker
    val, slipped = {}, {}
    for p in "AB":
        val[p], slipped[p] = [], []
        for r in rhos:
            m = np.array(data[p][r]); keep = m < 1.5 * m.min()
            val[p].append(float(m[keep].mean())); slipped[p].append(int((~keep).sum()))
    med = val
    fig, ax = plt.subplots(figsize=(7.4, 4.3), dpi=200)
    ax.set_xscale("log")
    ax.plot([rhos[0], rhos[-1]], [ent, ent], color=ORANGE, lw=1.8)
    for p, col in (("A", BLUE), ("B", AQUA)):
        ax.plot(rhos, val[p], color=col, lw=1.8, zorder=2)
        for r, v, sl in zip(rhos, val[p], slipped[p]):
            ax.plot([r], [v], marker="o", markersize=7, zorder=3, linestyle="none",
                    markerfacecolor=(SURF if sl else col), markeredgecolor=(col if sl else SURF), markeredgewidth=1.4)
    x_lab = rhos[-1] * 1.35
    ax.text(x_lab, med["A"][-1], "unentangled,\nboth phases tracked", va="center", fontsize=9)
    ax.text(x_lab, med["B"][-1], "unentangled,\ncorrelation spectroscopy", va="center", fontsize=9)
    ax.text(x_lab, ent, "entangled pair", va="center", fontsize=9)
    ax.set_xlim(rhos[0] * 0.8, rhos[-1] * 1.15); ax.set_ylim(0, 6)
    ax.set_xticks(rhos); ax.set_xticklabels(["0.1", "1", "10", "$10^2$", "$10^3$", "$10^4$"]); ax.minorticks_off()
    ax.grid(True, axis="y", color=GRID, lw=0.7); ax.set_axisbelow(True)
    ax.set_xlabel("common-mode noise strength  $\\rho = q_b/q_g$")
    ax.set_ylabel("tracking MSE of the gradient $g$   (units of $q_g^{2/3}$)")
    ax.set_title("Two sensors tracking a gradient under common-mode noise", loc="left", fontsize=10.5, pad=10)
    handles = [Line2D([], [], color=ORANGE, lw=1.8, label="entangled pair  $(|01\\rangle+|10\\rangle)/\\sqrt{2}$"),
               Line2D([], [], color=BLUE, lw=1.8, marker="o", markersize=6, markeredgecolor=SURF, label="unentangled, both phases tracked"),
               Line2D([], [], color=AQUA, lw=1.8, marker="o", markersize=6, markeredgecolor=SURF, label="unentangled, correlation spectroscopy"),
               Line2D([], [], color=INK2, marker="o", markersize=6, markerfacecolor=SURF, markeredgecolor=INK2, markeredgewidth=1.2,
                      linestyle="none", label="open marker: seeds with a phase slip excluded")]
    ax.legend(handles=handles, loc="upper left", fontsize=8.3, handlelength=2.2)
    fig.subplots_adjust(left=0.09, right=0.74, top=0.90, bottom=0.13)
    fig.savefig(os.path.join(OUT, "fig3_gradient.png"))
    plt.close(fig)
    return dict(rho=rhos, A=med["A"], B=med["B"], entangled=ent, slipped_seeds=slipped,
                seeds={p: {str(r): data[p][r] for r in rhos} for p in "AB"})


if __name__ == "__main__":
    summary = dict(scaling=fig_scaling(), window=fig_window(), gradient=fig_gradient())
    json.dump(summary, open(os.path.join(HERE, "figure_data.json"), "w"), indent=1)
    print("done")
