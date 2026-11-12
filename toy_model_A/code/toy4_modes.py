"""Toy 4: k single-qubit sensors on a line, one target spatial mode, strong fast nuisance modes.

Sensor j sits at z_j (equally spaced on [-1, 1]) and accumulates the phase
    phi_j = sum_m f_m(z_j) * Phi_m,      Phi_m = integral of x_m(t) over the interrogation window,
with modes f = 1 (uniform, "b"), z (gradient, "g"), z^2 - mean(z^2) (curvature, "c").

A measurement configuration is a list of UNITS.  A unit is a group of sensors in a GHZ-type state
(|s> + |s_bar>)/sqrt(2) with sign pattern sigma; it behaves like one qubit whose phase is
    theta_u = t_u * d + (nuisance phases) + delta_u,     t_u = sum_j sigma_j f_target(z_j),
with d = (target phase) - (feedback phase), and gives one outcome m_u = +/-1 with P = (1 + m_u sin theta_u)/2.
A single unentangled sensor is a unit of size one.

Nuisance modes are NOT tracked: their phases are uniformly random.  Averaging the joint outcome distribution
over them leaves only the nuisance-blind combinations (exact marginal likelihood):
    P(m | d) = 2^-U [ 1 + sum_{eps != 0, sum_u eps_u n_u = 0} chi_S(m) Re( (2i)^-|S| prod(eps) e^{i (A d + D)} ) ],
    eps in {-1,0,1}^U,  S = support(eps),  A = sum eps_u t_u,  D = sum eps_u delta_u,  n_u = nuisance coefficients.

fisher()      classical Fisher information of the configuration about the target phase at d = 0
simulate()    exact outcomes + particle filter for tracking the target (1D), any configuration
lin_cost()    steady-state linear Kalman filter cost for a measurement with information K and lock scale a_max
"""
import itertools
import numpy as np
from toy_model import _solve_T, _resample

MODES = "bgc"


def positions(k):
    return np.linspace(-1.0, 1.0, k)


def mode_matrix(k):
    z = positions(k)
    return np.stack([np.ones(k), z, z * z - np.mean(z * z)], axis=1)       # columns b, g, c


def make_units(k, groups, target, nuisance):
    """groups: list of (sensor indices, signs).  Returns arrays t[U], n[U, J]."""
    F = mode_matrix(k)
    it = MODES.index(target); inu = [MODES.index(m) for m in nuisance]
    t = np.array([sum(s * F[j, it] for j, s in zip(idx, sg)) for idx, sg in groups])
    n = np.array([[sum(s * F[j, m] for j, s in zip(idx, sg)) for m in inu] for idx, sg in groups]).reshape(len(groups), len(inu))
    return t, n


class Config:
    def __init__(self, t, n, delta=None, name=""):
        self.t = np.asarray(t, float); self.n = np.asarray(n, float); self.U = len(self.t); self.name = name
        eps = np.array([e for e in itertools.product((-1, 0, 1), repeat=self.U) if any(e)])
        ok = np.all(np.abs(eps @ self.n) < 1e-9, axis=1) if self.n.shape[1] else np.ones(len(eps), bool)
        self.eps = eps[ok]
        size = np.abs(self.eps).sum(axis=1)
        self.coef = (2j) ** (-size.astype(float)) * np.prod(np.where(self.eps == 0, 1, self.eps), axis=1)
        self.A = self.eps @ self.t
        outs = np.array(list(itertools.product((1, -1), repeat=self.U)))                       # 2^U outcomes
        self.outs = outs
        self.chi = np.prod(np.where(self.eps[None, :, :] != 0, outs[:, None, :], 1), axis=2).astype(float)  # [outcome, term]
        self.Avals, self.Ainv = np.unique(np.round(self.A, 9), return_inverse=True)
        self.a_max = float(np.abs(self.A).max()) if len(self.A) else 0.0
        self.set_delta(np.zeros(self.U) if delta is None else delta)

    def set_delta(self, delta):
        self.delta = np.asarray(delta, float)
        self.cD = self.coef * np.exp(1j * (self.eps @ self.delta))                              # coef * e^{iD}

    def probs(self, d):
        """P[r, outcome] for an array d[r] of phase deviations."""
        v = np.real(self.cD[None, :] * np.exp(1j * np.outer(d, self.A)))                        # [r, term]
        return (1.0 + v @ self.chi.T) / 2 ** self.U

    def dprobs(self, d):
        v = np.real(1j * self.A[None, :] * self.cD[None, :] * np.exp(1j * np.outer(d, self.A)))
        return (v @ self.chi.T) / 2 ** self.U

    def fisher(self, d=0.0):
        p = self.probs(np.atleast_1d(d)); dp = self.dprobs(np.atleast_1d(d))
        return float(np.sum(dp ** 2 / np.maximum(p, 1e-15)))

    def fisher_avg(self, sigma, npts=41):
        """Fisher information averaged over d ~ N(0, sigma^2)."""
        x, w = np.polynomial.hermite_e.hermegauss(npts)
        d = sigma * x; p = self.probs(d); dp = self.dprobs(d)
        return float(np.sum(w / w.sum() * np.sum(dp ** 2 / np.maximum(p, 1e-15), axis=1)))

    def optimize_delta(self, sigma=0.0, n_start=24, seed=0):
        from scipy.optimize import minimize
        rng = np.random.default_rng(seed)
        def f(dl):
            self.set_delta(dl)
            return -(self.fisher() if sigma == 0 else self.fisher_avg(sigma))
        best = (np.inf, None)
        starts = [np.where(np.arange(self.U) < self.U / 2, -np.pi / 4, np.pi / 4)] + [rng.uniform(-np.pi, np.pi, self.U) for _ in range(n_start)]
        for s in starts:
            r = minimize(f, s, method="BFGS")
            if r.fun < best[0]: best = (r.fun, r.x)
        self.set_delta(best[1])
        return -best[0]

    def weights(self, iout, dp):
        """Particle likelihoods: iout[r] observed outcome index, dp[r, p] particle phase deviations.
        Terms with -A are folded onto +A; if all |A| are multiples of one step u, cos/sin(n u d) come from a recurrence."""
        absA = np.round(np.abs(self.A), 9)
        cc = np.where(self.A >= 0, self.cD, np.conj(self.cD))
        vals, inv = np.unique(absA, return_inverse=True)
        Z = np.zeros((len(vals), len(iout)), complex)
        np.add.at(Z, inv, (self.chi[iout, :] * cc[None, :]).T)
        pos = vals[vals > 1e-9]
        u = pos.min() if len(pos) else 1.0
        nn = vals / u
        w = np.ones(dp.shape)
        if np.all(np.abs(nn - np.rint(nn)) < 1e-6) and nn.max() < 200:
            nn = np.rint(nn).astype(int); look = {n: i for i, n in enumerate(nn)}
            c1 = np.cos(u * dp); s1 = np.sin(u * dp)
            cp, sp = np.ones_like(dp), np.zeros_like(dp)          # n = 0
            cn, sn = c1, s1                                        # n = 1
            if 0 in look: w += Z[look[0]].real[:, None]
            for n in range(1, nn.max() + 1):
                if n in look:
                    w += Z[look[n]].real[:, None] * cn - Z[look[n]].imag[:, None] * sn
                cn, cp = 2 * c1 * cn - cp, cn
                sn, sp = 2 * c1 * sn - sp, sn
        else:
            for i, a in enumerate(vals):
                w += Z[i].real[:, None] * np.cos(a * dp) - Z[i].imag[:, None] * np.sin(a * dp)
        return np.maximum(w, 0.0)


def simulate(cfg, c=0.5, kappa_ref=None, q=1.0, R=64, Np=1024, n_burn=200, n_meas=1500, seed=0):
    """Exact outcomes + particle filter on the target mode.  T is set each cycle from the particle variance so that
    kappa_ref * std(target phase - feedback phase) = c."""
    rng = np.random.default_rng(seed)
    kr = cfg.a_max if kappa_ref is None else kappa_ref
    x = np.zeros(R); xp = 0.05 * rng.standard_normal((R, Np))
    num = den = Tsum = 0.0; cnt = 0; err2 = None; worst = 0.0
    for it in range(n_burn + n_meas):
        m = xp.mean(axis=1); P = xp.var(axis=1)
        T = _solve_T(P, q, c / kr)
        if err2 is not None and it >= n_burn:
            num += np.sum(err2 * T + q * T ** 2 / 2); den += np.sum(T); Tsum += T.sum(); cnt += R
            worst = max(worst, float(err2.max()))
        xi = np.sqrt(q * T) * rng.standard_normal(R)
        eta = 0.5 * T * xi + np.sqrt(q * T ** 3 / 12) * rng.standard_normal(R)
        d = x * T + eta - m * T
        x = x + xi
        Tc = T[:, None]
        xip = np.sqrt(q * Tc) * rng.standard_normal((R, Np))
        etap = 0.5 * Tc * xip + np.sqrt(q * Tc ** 3 / 12) * rng.standard_normal((R, Np))
        dpp = xp * Tc + etap - (m * T)[:, None]
        xp = xp + xip
        pr = cfg.probs(d); pr = np.maximum(pr, 0); pr /= pr.sum(axis=1, keepdims=True)
        iout = (rng.random(R)[:, None] > np.cumsum(pr, axis=1)).sum(axis=1).clip(0, pr.shape[1] - 1)
        w = cfg.weights(iout, dpp) + 1e-300
        w /= w.sum(axis=1, keepdims=True)
        err2 = (x - np.sum(w * xp, axis=1)) ** 2
        xp = _resample(rng, w, xp)
    return dict(mse=float(num / den), T=float(Tsum / cnt), worst=worst)


# ------------------------------------------------------------------ linear Kalman filter (integrated-phase model)
def upd(p, q, T, k2):
    var = T * T * p + q * T ** 3 / 3
    cov = T * p + q * T * T / 2
    return p + q * T - k2 * cov ** 2 / (k2 * var + 1)


def lin_cost(K, a_max, c=0.5, q=1.0, alphas=np.linspace(0.3, 1.0, 15), iters=3000):
    """Single tracked mode, measurement information K (per unit phase^2), lock a_max * std(phase) <= c."""
    best = (np.inf, None, None)
    for al in alphas:
        p = q ** (2 / 3)
        for _ in range(iters):
            T = al * _solve_T(np.array([p]), q, c / a_max)[0]
            pn = upd(p, q, T, K)
            if abs(pn - p) < 1e-13: p = pn; break
            p = pn
        J = p + q * T / 2
        if J < best[0]: best = (J, al, T)
    return best


def lin_cost_S(k, rho, target="g", tracked="bg", c=0.5, alphas=np.linspace(0.3, 1.0, 15), iters=40000):
    """Unentangled sensors that track every mode in `tracked`.  The mode functions are orthogonal on the array, so
    each mode has its own scalar recursion with information K_m = sum_j f_m(z_j)^2; the lock constraint is the phase
    variance of the edge sensor.  rho: dict mode -> process-noise intensity (target has 1)."""
    F = mode_matrix(k); idx = [MODES.index(m) for m in tracked]
    Km = (F[:, idx] ** 2).sum(axis=0); fe = F[-1, idx] ** 2
    qs = np.array([rho[m] for m in tracked], float)
    it = tracked.index(target)
    al = np.asarray(alphas)[:, None]
    p = np.tile(qs ** (2 / 3), (len(alphas), 1))
    for _ in range(iters):
        T = al * _solve_T((fe * p).sum(axis=1), np.sum(fe * qs), c, iters=12)[:, None]     # edge-sensor lock
        pn = upd(p, qs, T, Km)
        done = np.max(np.abs(pn - p) / p) < 1e-12
        p = pn
        if done: break
    J = p[:, it] + qs[it] * T[:, 0] / 2
    i = int(np.argmin(J))
    return float(J[i]), float(alphas[i]), float(T[i, 0])


# ------------------------------------------------------------------ configurations
def cfg_separable(k, target, nuisance):
    t, n = make_units(k, [([j], [1]) for j in range(k)], target, nuisance)
    return Config(t, n, name="separable")


def antisym(k):
    return [-1] * (k // 2) + [1] * (k // 2)


def curv_pattern(k):
    """Signs with sum sigma = 0 and sum sigma z = 0 (k multiple of 4): outer half +, inner half -."""
    z = np.abs(positions(k)); order = np.argsort(-z)
    s = np.zeros(k, int); s[order[: k // 2]] = 1; s[order[k // 2:]] = -1
    return list(s)


def cfg_ghz(k, target, nuisance):
    sg = antisym(k) if target == "g" else curv_pattern(k)
    t, n = make_units(k, [(list(range(k)), sg)], target, nuisance)
    assert np.all(np.abs(n) < 1e-9), "GHZ pattern is not nuisance-blind"
    return Config(t, n, name="GHZ")


def cfg_pairs(k, target, nuisance):
    """Mirror Bell pairs (j, k-1-j): antisymmetric for a gradient target, symmetric for a curvature target."""
    sg = [-1, 1] if target == "g" else [1, 1]
    t, n = make_units(k, [([j, k - 1 - j], sg) for j in range(k // 2)], target, nuisance)
    return Config(t, n, name="Bell pairs")


# ------------------------------------------------------------------ exact simulation, unentangled sensors tracking all modes
def simulate_S(k, rho, target="g", tracked="bg", c=0.5, R=64, Np=2048, n_burn=300, n_meas=1500, seed=0):
    """k unentangled sensors; every mode in `tracked` is followed by a particle filter (state dimension len(tracked)).
    rho: dict mode -> process-noise intensity.  T is set from the phase variance of the worst sensor."""
    rng = np.random.default_rng(seed)
    F = mode_matrix(k)[:, [MODES.index(m) for m in tracked]]                    # [sensor, mode]
    qs = np.array([rho[m] for m in tracked], float); it = tracked.index(target); M = len(tracked)
    x = np.zeros((R, M)); xp = 0.05 * rng.standard_normal((R, Np, M))
    num = den = Tsum = 0.0; cnt = 0; err2 = None
    qe = float(np.max(F ** 2 @ qs))
    for n in range(n_burn + n_meas):
        mean = xp.mean(axis=1)                                                    # [R, M]
        loc = np.einsum("rpm,jm->rpj", xp, F)                                     # field at each sensor
        P = loc.var(axis=1).max(axis=1)
        T = _solve_T(P, qe, c)
        if err2 is not None and n >= n_burn:
            num += np.sum(err2 * T + qs[it] * T ** 2 / 2); den += np.sum(T); Tsum += T.sum(); cnt += R
        Tc = T[:, None]
        xi = np.sqrt(qs[None, :] * Tc) * rng.standard_normal((R, M))
        eta = 0.5 * Tc * xi + np.sqrt(qs[None, :] * Tc ** 3 / 12) * rng.standard_normal((R, M))
        d = (x - mean) * Tc + eta                                                 # phase deviation per mode
        x = x + xi
        Tp = T[:, None, None]
        xip = np.sqrt(qs[None, None, :] * Tp) * rng.standard_normal((R, Np, M))
        etap = 0.5 * Tp * xip + np.sqrt(qs[None, None, :] * Tp ** 3 / 12) * rng.standard_normal((R, Np, M))
        dp = (xp - mean[:, None, :]) * Tp + etap
        xp = xp + xip
        th = d @ F.T                                                              # [R, sensor]
        out = np.where(rng.random((R, k)) < 0.5 * (1 + np.sin(th)), 1.0, -1.0)
        thp = np.einsum("rpm,jm->rpj", dp, F)
        w = np.prod(0.5 * (1 + out[:, None, :] * np.sin(thp)), axis=2) + 1e-300
        w /= w.sum(axis=1, keepdims=True)
        err2 = (x[:, it] - np.sum(w * xp[:, :, it], axis=1)) ** 2
        # systematic resampling (same indices for all modes)
        cs = np.cumsum(w, axis=1); cs /= cs[:, -1:]; cs[:, -1] = 1.0
        u = (rng.random((R, 1)) + np.arange(Np)[None, :]) / Np
        off = np.arange(R)[:, None]
        idx = np.minimum(np.searchsorted((cs + off).ravel(), (u + off).ravel()), R * Np - 1)
        xp = xp.reshape(R * Np, M)[idx].reshape(R, Np, M)
    return dict(mse=float(num / den), T=float(Tsum / cnt))
