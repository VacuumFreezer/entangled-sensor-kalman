"""Fast steady-state linear Kalman filter for the integrated-phase model (uses a DARE solver).
Same model as toy_model.lin_steady; used for the curves in the figures."""
import numpy as np
from scipy.linalg import solve_discrete_are
from scipy.optimize import minimize_scalar, brentq


def steady(T, groups, q=1.0, gamma=0.0, T_dead=0.0):
    """groups: list of (kappa, delta, v0). Returns (time-avg MSE of x, posterior var of x, phase variance)."""
    A = np.array([[1.0, 0.0], [T, 0.0]])
    Td = T_dead
    Q = q * np.array([[Td + T, Td * T + T**2 / 2], [Td * T + T**2 / 2, Td * T**2 + T**3 / 3]])
    C = np.array([[0.0, k * v0 * np.exp(-k * gamma * T) * np.cos(d)] for k, d, v0 in groups])
    Rm = np.diag([1.0 - (v0 * np.exp(-k * gamma * T) * np.sin(d)) ** 2 for k, d, v0 in groups])
    Pp = solve_discrete_are(A.T, C.T, Q, Rm)
    P = Pp - Pp @ C.T @ np.linalg.solve(C @ Pp @ C.T + Rm, C @ Pp)
    Pxx = P[0, 0]
    return Pxx + q * (T + Td) / 2, Pxx, T**2 * (Pxx + q * Td) + q * T**3 / 3


def T_lock(groups, c, **kw):
    """Interrogation time at which kappa_max * std(phi - phi_hat) = c (first crossing from small T)."""
    kmax = max(g[0] for g in groups)
    f = lambda lt: kmax**2 * steady(np.exp(lt), groups, **kw)[2] - c**2
    lo = np.log(1e-4)
    hi = lo
    while f(hi) < 0:
        lo, hi = hi, hi + 0.25
        if hi > np.log(8.0):
            return 8.0
    return np.exp(brentq(f, lo, hi, xtol=1e-10))


def best(groups, c=None, **kw):
    """Minimum time-averaged MSE over T, subject to the lock constraint if c is given. Returns (T, MSE)."""
    hi = np.log(T_lock(groups, c, **kw)) if c is not None else np.log(8.0)
    r = minimize_scalar(lambda lt: steady(np.exp(lt), groups, **kw)[0], bounds=(np.log(1e-3), hi),
                        method="bounded", options=dict(xatol=1e-7))
    T = np.exp(r.x)
    # the objective is unimodal in T here; also test the constraint boundary
    cand = [(T, r.fun)]
    if c is not None:
        cand.append((np.exp(hi), steady(np.exp(hi), groups, **kw)[0]))
    return min(cand, key=lambda t: t[1])


def sep(k, v0=1.0):
    return [(1, 0.0, v0)] * k


def ghz(k, v0=1.0):
    return [(k, 0.0, v0)]


if __name__ == "__main__":
    print("unconstrained single:", best(ghz(1)))
    for k in (1, 2, 3, 4, 8, 16):
        s = best(sep(k), 0.5); g = best(ghz(k), 0.5)
        print(k, "sep T=%.3f MSE=%.4f | ghz T=%.3f MSE=%.4f | ratio %.4f" % (*s, *g, g[1] / s[1]))
    print("deph k=3 g=1:", best(sep(3), 0.5, gamma=1.0), best(ghz(3), 0.5, gamma=1.0))
    print("dead k=3 Te=0.1:", best(ghz(3), 0.5, T_dead=0.1))
