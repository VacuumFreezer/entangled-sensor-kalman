"""Toy 3 (linear Kalman filter): two sensors, x1 = b + g, x2 = b - g, both modes tracked.
Entangled pairs arrive as a Poisson process of rate R into a one-pair buffer.

Actions (each with a fraction alpha of its lock-limited interrogation time):
  S  separable, both sensors read out:        information 2 on b and 2 on g;  lock Var(phi_b)+Var(phi_g) <= c^2
  X  correlation spectroscopy (no pair):      information 1 on g only;        lock 4 Var(phi_g) <= c^2
  B  Bell pair |00>+|11> (consumes a pair):   information 4 on b only;        lock 4 Var(phi_b) <= c^2
  G  Bell pair |01>+|10> (consumes a pair):   information 4 on g only;        lock 4 Var(phi_g) <= c^2
Cost rate: lam * MSE_b / rho^(2/3) + MSE_g   (units q_g = 1, q_b = rho).

optimal_policy(): average-cost dynamic programme on a (log p_b, log p_g, buffer) grid (Dinkelbach iteration).
simulate():       Monte Carlo of the covariance recursion under any policy (no grid error in the evaluation).
"""
import numpy as np

C = 0.5
ALPHAS = np.array([0.4, 0.55, 0.7, 0.85, 1.0])
TYPES = "SXBG"
KB = np.array([2.0, 0.0, 4.0, 0.0])
KG = np.array([2.0, 1.0, 0.0, 4.0])


def solve_T(a, bq, c2, iters=10):
    a = np.asarray(a, float)
    T = np.minimum(np.sqrt(c2 / np.maximum(a, 1e-300)), (3 * c2 / bq) ** (1 / 3))
    for _ in range(iters):
        f = a * T * T + bq * T**3 / 3 - c2
        T = np.maximum(T - f / (2 * a * T + bq * T * T), 1e-9)
    return T


def upd(p, q, T, k2):
    var = T * T * p + q * T**3 / 3
    cov = T * p + q * T * T / 2
    return p + q * T - k2 * cov**2 / (k2 * var + 1)


def lock_T(typ, pb, pg, rho):
    """Lock-limited interrogation time for action type index typ (array or scalar)."""
    TS = solve_T(pb + pg, rho + 1.0, C * C)
    Tb = solve_T(pb, rho, C * C / 4)
    Tg = solve_T(pg, 1.0, C * C / 4)
    return np.where(typ == 0, TS, np.where(typ == 2, Tb, Tg))


def step(typ, alpha, pb, pg, rho, lam):
    T = alpha * lock_T(typ, pb, pg, rho)
    wb = lam * rho ** (-2 / 3)
    cost = wb * (pb * T + rho * T * T / 2) + (pg * T + T * T / 2)
    return upd(pb, rho, T, KB[typ]), upd(pg, 1.0, T, KG[typ]), T, cost


class Grid:
    def __init__(self, rho, n=100, b_range=(0.02, 3e3), g_range=(0.02, 3e2)):
        self.rho = rho
        self.ub = np.linspace(np.log(b_range[0] * rho ** (2 / 3)), np.log(b_range[1] * rho ** (2 / 3)), n)
        self.vg = np.linspace(np.log(g_range[0]), np.log(g_range[1]), n)
        self.n = n

    def locate(self, pb, pg):
        n = self.n
        fb = np.clip((np.log(pb) - self.ub[0]) / (self.ub[1] - self.ub[0]), 0, n - 1 - 1e-9)
        fg = np.clip((np.log(pg) - self.vg[0]) / (self.vg[1] - self.vg[0]), 0, n - 1 - 1e-9)
        ib = fb.astype(int); ig = fg.astype(int)
        return ib, ig, fb - ib, fg - ig


def optimal_policy(rho, lam, R, allowed="SXBG", n=100, n_vi=1500, n_outer=6, J0=None, verbose=False, seed=0):
    """Returns (J, policy) with policy = dict(grid, table[m, ib, ig] -> action index a = typ * len(ALPHAS) + ialpha)."""
    G = Grid(rho, n)
    PB, PG = np.meshgrid(np.exp(G.ub), np.exp(G.vg), indexing="ij")
    acts = [(t, ia) for t in range(4) if TYPES[t] in allowed for ia in range(len(ALPHAS))]
    pre = []
    for t, ia in acts:
        pb2, pg2, T, cost = step(t, ALPHAS[ia], PB, PG, rho, lam)
        ib, ig, wb_, wg_ = G.locate(pb2, pg2)
        i00 = ib * n + ig
        pre.append(dict(t=t, ia=ia, T=T, cost=cost, i00=i00, wb=wb_, wg=wg_,
                        parr=(1.0 - np.exp(-R * T)) if np.isfinite(R) else np.ones_like(T)))

    def interp(V, a):
        f = V.ravel()
        i = a["i00"]
        return ((1 - a["wb"]) * (1 - a["wg"]) * f[i] + (1 - a["wb"]) * a["wg"] * f[i + 1]
                + a["wb"] * (1 - a["wg"]) * f[i + n] + a["wb"] * a["wg"] * f[i + n + 1])

    J = J0 if J0 is not None else 5.0
    V0 = np.zeros((n, n)); V1 = np.zeros((n, n))
    for outer in range(n_outer):
        for it in range(n_vi):
            Q0 = []; Q1 = []
            for a in pre:
                e0 = interp(V0, a); e1 = interp(V1, a)
                mix = a["parr"] * e1 + (1 - a["parr"]) * e0
                base = a["cost"] - J * a["T"]
                if a["t"] >= 2:                 # consumes the pair
                    Q1.append(base + mix); Q0.append(np.full_like(base, np.inf))
                else:
                    Q0.append(base + mix); Q1.append(base + e1)
            Q0 = np.array(Q0); Q1 = np.array(Q1)
            N0 = Q0.min(axis=0); N1 = Q1.min(axis=0)
            ref = N1[n // 2, n // 2]
            d = max(np.abs(N0 - ref - V0).max(), np.abs(N1 - ref - V1).max())
            V0 = 0.5 * V0 + 0.5 * (N0 - ref); V1 = 0.5 * V1 + 0.5 * (N1 - ref)
            if d < 1e-7:
                break
        table = np.array([Q0.argmin(axis=0), Q1.argmin(axis=0)])
        table = np.array([[acts[k][0] * len(ALPHAS) + acts[k][1] for k in row.ravel()] for row in table]).reshape(2, n, n)
        pol = dict(grid=G, table=table)
        Jn = simulate(lambda m, pb, pg, st: table_policy(pol, m, pb, pg), rho, lam, R, seed=seed)["J"]
        if verbose:
            print(f"   outer {outer}: J_in={J:.5f} J_policy={Jn:.5f} vi_iters={it+1} resid={d:.2e}", flush=True)
        if abs(Jn - J) < 2e-4 * J:
            J = Jn; break
        J = Jn
    return J, pol


def table_policy(pol, m, pb, pg):
    G = pol["grid"]
    ib, ig, wb_, wg_ = G.locate(pb, pg)
    ib = ib + (wb_ > 0.5); ig = ig + (wg_ > 0.5)
    a = pol["table"][m, ib, ig]
    return a // len(ALPHAS), ALPHAS[a % len(ALPHAS)]


def simulate(policy, rho, lam, R, M=200, n_burn=1000, n_meas=4000, seed=0):
    """policy(m, pb, pg, state) -> (type index array, alpha array).  state: dict with 'tg', 'tb' = time since the
    last G / B cycle, usable by open-loop (timer) policies.  Returns time-averaged cost and diagnostics."""
    rng = np.random.default_rng(seed)
    pb = np.full(M, rho ** (2 / 3)); pg = np.ones(M)
    m = np.zeros(M, int)
    st = dict(tg=np.full(M, 1e9), tb=np.full(M, 1e9))
    cost = time = cb = cg = 0.0
    used = np.zeros(4)
    for it in range(n_burn + n_meas):
        typ, alpha = policy(m, pb, pg, st)
        typ = np.where((typ >= 2) & (m == 0), 0, typ)            # no pair: fall back to S
        T = alpha * lock_T(typ, pb, pg, rho)
        if it >= n_burn:
            cbi = (pb * T + rho * T * T / 2) / rho ** (2 / 3); cgi = pg * T + T * T / 2
            cb += cbi.sum(); cg += cgi.sum(); time += T.sum()
            used += np.bincount(typ, minlength=4)
        pb, pg = upd(pb, rho, T, KB[typ]), upd(pg, 1.0, T, KG[typ])
        st["tg"] = np.where(typ == 3, 0.0, st["tg"] + T); st["tb"] = np.where(typ == 2, 0.0, st["tb"] + T)
        m = np.where(typ >= 2, 0, m)
        arr = (rng.random(M) < (1 - np.exp(-R * T))) if np.isfinite(R) else np.ones(M, bool)
        m = np.where(arr, 1, m)
    return dict(J=(lam * cb + cg) / time, mse_b=cb / time, mse_g=cg / time, frac=dict(zip(TYPES, (used / used.sum()).round(4))),
                pair_rate=float((used[2] + used[3]) / time), cycle_time=float(time / used.sum()))


# ------------------------------------------------------------ simple policies
def pol_S(alpha=1.0):
    return lambda m, pb, pg, st: (np.zeros(len(pb), int), np.full(len(pb), alpha))


def pol_eager(mode):
    """Use every pair the moment it is available.  mode: 'G', 'B' or 'alt' (the mode measured longer ago)."""
    def f(m, pb, pg, st):
        if mode == "G": t = np.full(len(pb), 3)
        elif mode == "B": t = np.full(len(pb), 2)
        else: t = np.where(st["tg"] >= st["tb"], 3, 2)
        return np.where(m == 1, t, 0), np.ones(len(pb))
    return f


def pol_timer(tau_g, tau_b=np.inf, base=0):
    """Open-loop allocation: spend a pair on g if the last G cycle is at least tau_g ago, else on b if the last
    B cycle is at least tau_b ago, else the no-entanglement action `base` (0 = S, 1 = X)."""
    def f(m, pb, pg, st):
        t = np.where((m == 1) & (st["tg"] >= tau_g), 3, np.where((m == 1) & (st["tb"] >= tau_b), 2, base))
        return t, np.ones(len(pb))
    return f


def pol_threshold(theta_g, theta_b=np.inf, base=0):
    """Covariance-driven allocation: spend a pair on g if p_g >= theta_g, else on b if p_b >= theta_b * rho^(2/3)."""
    def f(m, pb, pg, st, rho=[None]):
        t = np.where((m == 1) & (pg >= theta_g), 3, np.where((m == 1) & (pb >= theta_b), 2, base))
        return t, np.ones(len(pb))
    return f


def pol_thin(prob, mode="G", base=0, seed=123):
    """Open-loop randomized allocation: a waiting pair is spent on `mode` with probability `prob` at each cycle start."""
    rng = np.random.default_rng(seed)
    t = 3 if mode == "G" else 2
    def f(m, pb, pg, st):
        return np.where((m == 1) & (rng.random(len(pb)) < prob), t, base), np.ones(len(pb))
    return f
