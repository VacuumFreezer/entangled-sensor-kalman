"""Toy 4, limited entanglement supply (linear Kalman filter).  One target mode, nuisance-immune measurements only.
Bell pairs arrive as a Poisson process (rate R per tau_g) into a buffer of capacity MCAP; pairs can be delivered to any
link and fused, so a configuration that merges the k sensors into G groups consumes k - G pairs.
Configurations: list of (pairs consumed, information K, lock scale kref, lock parameter c).
State of the decision problem: (posterior variance p of the target, number of stored pairs m)."""
import numpy as np
from scipy.stats import poisson
from toy_model import _solve_T
from toy4_modes import upd

C = 0.5
ALPHAS = np.array([0.4, 0.55, 0.7, 0.85, 1.0])


def cycle(p, K, kref, alpha, c=C):
    T = alpha * _solve_T(np.asarray(p, float), 1.0, np.asarray(c) / kref, iters=12)
    return upd(p, 1.0, T, K), T, p * T + T * T / 2


def simulate(policy, configs, R, mcap, M=400, n_burn=1500, n_meas=6000, seed=0):
    """policy(m, p) -> (config index array, alpha array)."""
    rng = np.random.default_rng(seed)
    need = np.array([cf[0] for cf in configs]); Ks = np.array([cf[1] for cf in configs]); kr = np.array([cf[2] for cf in configs])
    cs = np.array([cf[3] for cf in configs])
    p = np.ones(M); m = np.zeros(M, int); cost = time = 0.0; used = np.zeros(len(configs)); pairs = 0.0
    for it in range(n_burn + n_meas):
        j, al = policy(m, p)
        j = np.where(need[j] > m, 0, j)
        pn, T, cst = cycle(p, Ks[j], kr[j], al, cs[j])
        if it >= n_burn:
            cost += cst.sum(); time += T.sum(); used += np.bincount(j, minlength=len(configs)); pairs += need[j].sum()
        p = pn
        arr = rng.poisson(R * T) if np.isfinite(R) else np.full(M, mcap)
        m = np.minimum(m - need[j] + arr, mcap)
    return dict(J=float(cost / time), frac=(used / used.sum()).round(4).tolist(), pair_rate=float(pairs / time), cycle_time=float(time / used.sum()))


def optimal_policy(configs, R, mcap, n=240, p_range=(0.03, 30.0), n_vi=4000, n_outer=8, J0=1.5, verbose=False):
    grid = np.linspace(np.log(p_range[0]), np.log(p_range[1]), n); pg = np.exp(grid)
    acts = [(j, ia) for j in range(len(configs)) for ia in range(len(ALPHAS))]
    pre = []
    for j, ia in acts:
        need, K, kref, cj = configs[j]
        pn, T, cst = cycle(pg, K, kref, ALPHAS[ia], cj)
        f = np.clip((np.log(pn) - grid[0]) / (grid[1] - grid[0]), 0, n - 1 - 1e-9); i0 = f.astype(int); w = f - i0
        if np.isfinite(R):
            pa = np.array([poisson.pmf(a, R * T) for a in range(mcap)]); pa = np.vstack([pa, 1 - pa.sum(axis=0)])   # arrivals 0..mcap-1, >=mcap
        else:
            pa = np.zeros((mcap + 1, n)); pa[mcap] = 1.0
        pre.append(dict(j=j, ia=ia, need=need, T=T, cost=cst, i0=i0, w=w, pa=pa))
    J = J0; V = np.zeros((mcap + 1, n))
    for outer in range(n_outer):
        for it in range(n_vi):
            Q = np.full((len(acts), mcap + 1, n), np.inf)
            for ai, a in enumerate(pre):
                Vn = (1 - a["w"]) * V[:, a["i0"]] + a["w"] * V[:, a["i0"] + 1]            # [m', p]
                for m in range(a["need"], mcap + 1):
                    ev = sum(a["pa"][arr] * Vn[min(m - a["need"] + arr, mcap)] for arr in range(mcap + 1))
                    Q[ai, m] = a["cost"] - J * a["T"] + ev
            N = Q.min(axis=0); ref = N[0, n // 2]
            d = np.abs(N - ref - V).max()
            V = 0.5 * V + 0.5 * (N - ref)
            if d < 1e-8: break
        table = Q.argmin(axis=0)
        pol = dict(grid=grid, table=table, acts=acts)
        Jn = simulate(lambda m, p: table_policy(pol, m, p), configs, R, mcap)["J"]
        if verbose: print(f"   outer {outer}: J_in={J:.5f} J_policy={Jn:.5f} it={it+1} resid={d:.1e}", flush=True)
        if abs(Jn - J) < 1e-4 * J: J = Jn; break
        J = Jn
    return J, pol


def table_policy(pol, m, p):
    g = pol["grid"]; n = len(g)
    i = np.clip(np.rint((np.log(p) - g[0]) / (g[1] - g[0])).astype(int), 0, n - 1)
    a = pol["table"][m, i]
    acts = np.array(pol["acts"])
    return acts[a, 0], ALPHAS[acts[a, 1]]


def pol_fixed(j):
    return lambda m, p: (np.full(len(p), j), np.ones(len(p)))


def pol_greedy(configs):
    """Use the configuration with the most pairs that the buffer allows."""
    need = np.array([cf[0] for cf in configs])
    def f(m, p):
        j = np.array([np.max(np.where(need <= mm)[0]) for mm in m])
        return j, np.ones(len(p))
    return f


def pol_save(configs):
    """Wait until the largest configuration is affordable; otherwise no entanglement."""
    need = np.array([cf[0] for cf in configs]); top = len(configs) - 1
    return lambda m, p: (np.where(m >= need[top], top, 0), np.ones(len(p)))


def pol_one(configs, j=1):
    """Use at most configuration j (e.g. one pair on the longest baseline) whenever affordable."""
    need = np.array([cf[0] for cf in configs])
    return lambda m, p: (np.where(m >= need[j], j, 0), np.ones(len(p)))


def calibrate(J_exact, kref, c):
    """Information K for which the linear model (T at the lock limit) reproduces the exact-simulation cost."""
    from toy4_modes import lin_cost
    lo, hi = 1e-4, 1e3
    for _ in range(60):
        mid = np.sqrt(lo * hi)
        if lin_cost(mid, kref, c=c, alphas=np.array([1.0]))[0] > J_exact: lo = mid
        else: hi = mid
    return float(np.sqrt(lo * hi))


def simulate_mixed(k, rho, target, tracked, ghz, R, mcap=3, need=3, c=C, M=400, n_burn=3000, n_meas=12000, seed=0):
    """Finite nuisance intensity: unentangled sensors track every mode (S cycles) and, whenever `need` pairs are stored,
    one nuisance-blind GHZ cycle is inserted.  During the GHZ cycle the nuisance modes are not measured, so the
    following S cycles are shorter until the lock on the nuisance modes is recovered.
    ghz = (information K, lock scale kref, lock parameter c).  Linear Kalman filter; cost = MSE of the target."""
    from toy4_modes import mode_matrix, MODES
    rng = np.random.default_rng(seed)
    F = mode_matrix(k); idx = [MODES.index(m) for m in tracked]
    Km = (F[:, idx] ** 2).sum(axis=0); fe = F[-1, idx] ** 2
    qs = np.array([rho[m] for m in tracked], float); it = tracked.index(target)
    p = np.tile(qs ** (2 / 3), (M, 1)); m = np.zeros(M, int)
    cost = time = 0.0; ng = 0; ncyc = 0
    Kg = np.zeros(len(tracked)); Kg[it] = ghz[0]
    for n in range(n_burn + n_meas):
        use = m >= need
        TS = _solve_T((fe * p).sum(axis=1), np.sum(fe * qs), c, iters=12)
        TG = _solve_T(p[:, it], qs[it], ghz[2] / ghz[1], iters=12)
        T = np.where(use, TG, TS)[:, None]
        K = np.where(use[:, None], Kg[None, :], Km[None, :])
        if n >= n_burn:
            cost += np.sum(p[:, it] * T[:, 0] + qs[it] * T[:, 0] ** 2 / 2); time += T.sum(); ng += use.sum(); ncyc += M
        p = upd(p, qs[None, :], T, K)
        arr = rng.poisson(R * T[:, 0]) if np.isfinite(R) else np.full(M, mcap)
        m = np.minimum(m - need * use + arr, mcap)
    return dict(J=float(cost / time), frac_ghz=float(ng / ncyc), pair_rate=float(need * ng / time))
