"""Toy model: tracking a random-walk field with k qubit sensors,
with and without entanglement, using a centralized filter.

Units: coupling constant = 1 (phase rate = field). Field x(t) is a Wiener
process with E[dx^2] = q dt.  A group of size kappa in a GHZ state has a parity
outcome m = +/-1 with
    P(m) = 1/2 [1 + m V sin(kappa (phi - phi_hat) + delta)],
phi = integral of x over the interrogation window of length T,
phi_hat = T * (filter estimate of x) is the feedback phase,
V = v0 * exp(-kappa * gamma * T) is the fringe visibility.

Two tools:
  lin_steady(...)  : steady state of the linear(ized) Kalman filter
  simulate(...)    : exact Bernoulli outcomes + particle filter (no linearization)
"""
import numpy as np


# ---------------------------------------------------------------- linear KF
def lin_steady(T, groups, q=1.0, gamma=0.0, T_dead=0.0, iters=4000):
    """Steady-state linear Kalman filter for the integrated-phase model.

    groups: list of (kappa, delta, v0).
    Returns (time-averaged MSE of x, posterior var of x, predicted phase var).
    """
    A = np.array([[1.0, 0.0], [T, 0.0]])
    Td = T_dead
    Q = q * np.array([[Td + T, Td * T + T**2 / 2],
                      [Td * T + T**2 / 2, Td * T**2 + T**3 / 3]])
    C = []
    Rm = []
    for kappa, delta, v0 in groups:
        V = v0 * np.exp(-kappa * gamma * T)
        C.append([0.0, kappa * V * np.cos(delta)])
        Rm.append(1.0 - (V * np.sin(delta))**2)
    C = np.array(C)
    Rm = np.diag(Rm)
    P = np.eye(2)
    for _ in range(iters):
        Pp = A @ P @ A.T + Q
        S = C @ Pp @ C.T + Rm
        K = Pp @ C.T @ np.linalg.inv(S)
        Pn = Pp - K @ C @ Pp
        if np.max(np.abs(Pn - P)) < 1e-14:
            P = Pn
            break
        P = Pn
    Pxx = P[0, 0]
    mse = Pxx + q * (T + Td) / 2
    phase_var = T**2 * (Pxx + q * Td) + q * T**3 / 3
    return mse, Pxx, phase_var


def lin_opt(groups, q=1.0, gamma=0.0, T_dead=0.0, Tgrid=None):
    """Minimize the linear-KF time-averaged MSE over T (no phase constraint)."""
    if Tgrid is None:
        Tgrid = np.geomspace(0.02, 6, 400)
    vals = np.array([lin_steady(T, groups, q, gamma, T_dead)[0] for T in Tgrid])
    i = int(np.argmin(vals))
    return Tgrid[i], vals[i]


def lin_constrained(groups, c, q=1.0, gamma=0.0, T_dead=0.0):
    """Linear-KF MSE when T is set so that kappa_max * (phase std) = c."""
    kmax = max(g[0] for g in groups)
    lo, hi = 1e-4, 20.0
    for _ in range(80):
        mid = np.sqrt(lo * hi)
        _, _, pv = lin_steady(mid, groups, q, gamma, T_dead)
        if kmax**2 * pv > c**2:
            hi = mid
        else:
            lo = mid
    T = np.sqrt(lo * hi)
    return T, lin_steady(T, groups, q, gamma, T_dead)[0]


# ------------------------------------------------------- exact simulation
def _solve_T(P, q, a, iters=30):
    """Solve T^2 P + q T^3 / 3 = a^2 for T > 0 (vectorized Newton)."""
    T = np.minimum(a / np.sqrt(P + 1e-300), (3 * a**2 / q) ** (1 / 3))
    for _ in range(iters):
        f = T**2 * P + q * T**3 / 3 - a**2
        fp = 2 * T * P + q * T**2
        T = np.maximum(T - f / fp, 1e-6)
    return T


def _resample(rng, w, xp):
    """Systematic resampling, vectorized over replicas (rows)."""
    R, Np = w.shape
    cs = np.cumsum(w, axis=1)
    cs /= cs[:, -1:]
    cs[:, -1] = 1.0
    u = (rng.random((R, 1)) + np.arange(Np)[None, :]) / Np
    off = np.arange(R)[:, None]
    idx = np.searchsorted((cs + off).ravel(), (u + off).ravel())
    idx = np.minimum(idx, R * Np - 1)
    return xp.ravel()[idx].reshape(R, Np)


def simulate(groups, c=None, T_fixed=None, q=1.0, gamma=0.0, T_dead=0.0,
             R=128, Np=512, n_burn=150, n_meas=600, seed=0, kc=None):
    """Exact Bernoulli outcomes + bootstrap particle filter.

    groups : list of (kappa, delta, v0)
    c      : adaptive policy. Each cycle T is chosen from the filter variance so
             that kc * std(phi - phi_hat) = c  (kc defaults to max kappa).
    T_fixed: use a fixed interrogation time instead.
    Returns dict with time-averaged MSE of x, mean T, slip indicator.
    """
    rng = np.random.default_rng(seed)
    if kc is None:
        kc = max(g[0] for g in groups)
    x = np.zeros(R)
    xp = 0.05 * rng.standard_normal((R, Np))
    num = 0.0
    den = 0.0
    Tsum = 0.0
    big = 0
    cnt = 0
    err2 = None
    for n in range(n_burn + n_meas):
        m = xp.mean(axis=1)
        if T_dead > 0:
            x = x + np.sqrt(q * T_dead) * rng.standard_normal(R)
            xp = xp + np.sqrt(q * T_dead) * rng.standard_normal((R, Np))
        P = xp.var(axis=1)
        if T_fixed is not None:
            T = np.full(R, float(T_fixed))
        else:
            T = _solve_T(P, q, c / kc)
        L = T + T_dead
        if err2 is not None and n >= n_burn:
            num += np.sum(err2 * L + q * L**2 / 2)
            den += np.sum(L)
            Tsum += np.sum(T)
            cnt += R
        # true system over the window
        z1 = rng.standard_normal(R)
        z2 = rng.standard_normal(R)
        xi = np.sqrt(q * T) * z1
        eta = 0.5 * T * xi + np.sqrt(q * T**3 / 12) * z2
        phi = x * T + eta
        phi_hat = m * T
        x = x + xi
        # particles
        Tc = T[:, None]
        z1 = rng.standard_normal((R, Np))
        z2 = rng.standard_normal((R, Np))
        xip = np.sqrt(q * Tc) * z1
        etap = 0.5 * Tc * xip + np.sqrt(q * Tc**3 / 12) * z2
        dphip = xp * Tc + etap - phi_hat[:, None]
        xp = xp + xip
        w = np.ones((R, Np))
        dphi = phi - phi_hat
        for kappa, delta, v0 in groups:
            V = v0 * np.exp(-kappa * gamma * T)
            p = 0.5 * (1 + V * np.sin(kappa * dphi + delta))
            out = np.where(rng.random(R) < p, 1.0, -1.0)
            w *= 0.5 * (1 + out[:, None] * V[:, None] * np.sin(kappa * dphip + delta))
        w += 1e-300
        w /= w.sum(axis=1, keepdims=True)
        est = np.sum(w * xp, axis=1)
        err2 = (x - est) ** 2
        if n >= n_burn:
            big += np.sum(np.abs(kc * dphi) > np.pi / 2)
        xp = _resample(rng, w, xp)
    return dict(mse=num / den, T=Tsum / cnt, out_of_range=big / (n_meas * R))


def sep(k, deltas=None, v0=1.0):
    if deltas is None:
        deltas = [0.0] * k
    return [(1, d, v0) for d in deltas]


def ghz(k, v0=1.0):
    return [(k, 0.0, v0)]


if __name__ == "__main__":
    # sanity: sampled-model constant 1.091 vs integrated-model constant
    for k in (1, 2, 4, 16, 64):
        T, m = lin_opt(sep(k))
        print(f"sep k={k:3d}: T*={T:.3f}  MSE*={m:.4f}  MSE*k^(1/3)={m*k**(1/3):.4f}")
    for k in (1, 2, 4):
        T, m = lin_opt(ghz(k))
        print(f"ghz k={k:3d}: T*={T:.3f}  MSE*={m:.4f}  MSE*k^(2/3)={m*k**(2/3):.4f}")
