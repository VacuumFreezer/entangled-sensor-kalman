"""Toy model 2: two unentangled sensors, fields B1 = b + g, B2 = b - g.
b (common mode) and g (gradient) are independent Wiener processes with
diffusion q_b = rho and q_g = 1.  Goal: track g.

Exact Bernoulli outcomes + particle filter on the 2D state (b, g).
policy "A": interrogation time set by the single-qubit phase (b and g both tracked)
policy "B": interrogation time set by the differential phase 2g (correlation
            spectroscopy; the common-mode phase is allowed to randomize)
"""
import numpy as np
from toy_model import _solve_T


def _resample2(rng, w, a, b):
    R, Np = w.shape
    cs = np.cumsum(w, axis=1)
    cs /= cs[:, -1:]
    cs[:, -1] = 1.0
    u = (rng.random((R, 1)) + np.arange(Np)[None, :]) / Np
    off = np.arange(R)[:, None]
    idx = np.searchsorted((cs + off).ravel(), (u + off).ravel())
    idx = np.minimum(idx, R * Np - 1)
    return a.ravel()[idx].reshape(R, Np), b.ravel()[idx].reshape(R, Np)


def _noise(rng, q, T, shape):
    z1 = rng.standard_normal(shape)
    z2 = rng.standard_normal(shape)
    xi = np.sqrt(q * T) * z1
    eta = 0.5 * T * xi + np.sqrt(q * T**3 / 12) * z2
    return xi, eta


def simulate_sep2(rho, c, policy, R=64, Np=2048, n_burn=150, n_meas=800, seed=0):
    rng = np.random.default_rng(seed)
    qb, qg = float(rho), 1.0
    deltas = (0.0, 0.0) if policy == "A" else (np.pi / 4, -np.pi / 4)
    b = np.zeros(R); g = np.zeros(R)
    bp = 0.05 * rng.standard_normal((R, Np)); gp = 0.05 * rng.standard_normal((R, Np))
    num = den = 0.0
    err2 = None
    Tsum = 0.0; cnt = 0
    for n in range(n_burn + n_meas):
        mb = bp.mean(axis=1); mg = gp.mean(axis=1)
        if policy == "A":
            P = np.maximum((bp + gp).var(axis=1), (bp - gp).var(axis=1))
            T = _solve_T(P, qb + qg, c)
        else:
            T = _solve_T(gp.var(axis=1), qg, c / 2)
        if err2 is not None and n >= n_burn:
            num += np.sum(err2 * T + qg * T**2 / 2); den += np.sum(T)
            Tsum += np.sum(T); cnt += R
        xib, etab = _noise(rng, qb, T, R) if qb > 0 else (np.zeros(R), np.zeros(R))
        xig, etag = _noise(rng, qg, T, R)
        phib = b * T + etab; phig = g * T + etag
        b = b + xib; g = g + xig
        Tc = T[:, None]
        xibp, etabp = _noise(rng, qb, Tc, (R, Np)) if qb > 0 else (0.0, 0.0)
        xigp, etagp = _noise(rng, qg, Tc, (R, Np))
        phibp = bp * Tc + etabp; phigp = gp * Tc + etagp
        bp = bp + xibp; gp = gp + xigp
        w = np.ones((R, Np))
        for sgn, dl in ((1.0, deltas[0]), (-1.0, deltas[1])):
            d = (phib - mb * T) + sgn * (phig - mg * T)
            p = 0.5 * (1 + np.sin(d + dl))
            out = np.where(rng.random(R) < p, 1.0, -1.0)
            dp = (phibp - (mb * T)[:, None]) + sgn * (phigp - (mg * T)[:, None])
            w *= 0.5 * (1 + out[:, None] * np.sin(dp + dl))
        w += 1e-300
        w /= w.sum(axis=1, keepdims=True)
        est = np.sum(w * gp, axis=1)
        err2 = (g - est) ** 2
        bp, gp = _resample2(rng, w, bp, gp)
    return dict(mse=num / den, T=Tsum / cnt)
