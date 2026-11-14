"""Exact tracking simulation (particle filter on the target mode) for local-only multi-qubit-node strategies.
Nuisance modes are strong and untracked: each cycle their phases are uniformly random.  Same conventions as
toy4_modes.simulate: integrated-phase random walk, T set from the particle variance by kappa_ref*std = c."""
import numpy as np
from toy_model import _solve_T, _resample
from toy5_nodes import node_coeffs


def prepare(net):
    A = net.A
    pos = np.abs(A[np.abs(A) > 1e-9]); u = pos.min()
    nn = np.rint(A / u).astype(int)
    assert np.allclose(nn * u, A, atol=1e-7)
    return u, nn


def simulate_mix(net, deltas, c, kappa_ref, q=1.0, R=64, Np=1024, n_burn=200, n_meas=1500, seed=0):
    rng = np.random.default_rng(seed)
    u, nn = prepare(net); nmax = np.abs(nn).max()
    x = np.zeros(R); xp = 0.05 * rng.standard_normal((R, Np))
    num = den = 0.0; err2 = None; slips = 0
    for it in range(n_burn + n_meas):
        m = xp.mean(axis=1); P = xp.var(axis=1)
        T = _solve_T(P, q, c / kappa_ref)
        if err2 is not None and it >= n_burn:
            num += np.sum(err2 * T + q * T ** 2 / 2); den += np.sum(T)
        xi = np.sqrt(q * T) * rng.standard_normal(R)
        eta = 0.5 * T * xi + np.sqrt(q * T ** 3 / 12) * rng.standard_normal(R)
        d = x * T + eta - m * T
        x = x + xi
        Tc = T[:, None]
        xip = np.sqrt(q * Tc) * rng.standard_normal((R, Np))
        etap = 0.5 * Tc * xip + np.sqrt(q * Tc ** 3 / 12) * rng.standard_normal((R, Np))
        dpp = xp * Tc + etap - (m * T)[:, None]
        xp = xp + xip
        # outcomes
        nu = rng.uniform(0, 2 * np.pi, (R, net.Fn.shape[1]))
        phin = nu @ (net.Fn / net.unit).T
        prod = np.ones((R, len(net.Q)), complex)
        for j in range(net.k):
            phi = d * net.ft[j] + phin[:, j]
            g = np.array(net.gs[j]); dl = np.asarray(deltas[j])
            p = (1 + np.sin(g[None, :] * phi[:, None] - dl[None, :])) / 2
            b = np.where(rng.random(p.shape) < p, 1, -1)
            C = node_coeffs(b, net.gs[j], dl)
            prod *= C[:, net.Q[:, j] + net.G[j]]
        # Z_n = sum over terms with nn = n ; weight = Re sum_n Z_n e^{i n u d}
        Z = np.zeros((R, 2 * nmax + 1), complex)
        np.add.at(Z.T, nn + nmax, prod.T)
        Zp = Z[:, nmax + 1:] + np.conj(Z[:, nmax - 1::-1])        # fold -n onto +n (real result)
        w = np.real(Z[:, nmax])[:, None] * np.ones_like(dpp)
        c1 = np.cos(u * dpp); s1 = np.sin(u * dpp); cn, sn = c1.copy(), s1.copy(); cp, sp = np.ones_like(dpp), np.zeros_like(dpp)
        for n in range(1, nmax + 1):
            zr = Zp[:, n - 1].real[:, None]; zi = Zp[:, n - 1].imag[:, None]
            # Re(Z_n e^{ind}) + Re(Z_-n e^{-ind}) = Re((Z_n + conj Z_-n) e^{ind})
            w += zr * cn - zi * sn
            cn, cp = 2 * c1 * cn - cp, cn
            sn, sp = 2 * c1 * sn - sp, sn
        w = np.maximum(w, 0) + 1e-300
        w /= w.sum(axis=1, keepdims=True)
        est = np.sum(w * xp, axis=1)
        err2 = (x - est) ** 2
        xp = _resample(rng, w, xp)
    return float(num / den)
