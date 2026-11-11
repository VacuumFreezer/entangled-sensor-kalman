"""Toy 3, exact simulation: binary outcomes + particle filter on (b, g).
Two sensors, x1 = b + g, x2 = b - g; q_b = rho, q_g = 1; both modes tracked.
Cycle types: 0 = S (both sensors read out separately), 2 = B (Bell pair |00>+|11>, measures 2*phi_b),
3 = G (Bell pair |01>+|10>, measures 2*phi_g).  Pairs arrive as a Poisson process (rate R_arr) into a one-pair buffer.
The interrogation time is always set from the particle variance (lock parameter c)."""
import numpy as np
from toy_model import _solve_T
from toy_gradient import _resample2, _noise


def simulate3(rho, policy, R_arr=np.inf, par=None, c=0.5, R=64, Np=2048, n_burn=300, n_meas=2500, seed=0):
    rng = np.random.default_rng(seed)
    qb, qg = float(rho), 1.0
    b = np.zeros(R); g = np.zeros(R)
    bp = 0.05 * rng.standard_normal((R, Np)); gp = 0.05 * rng.standard_normal((R, Np))
    m = np.zeros(R, int); tg = np.full(R, 1e9); tb = np.full(R, 1e9)
    cb = cg = time = 0.0
    used = np.zeros(4)
    eb2 = eg2 = None
    for n in range(n_burn + n_meas):
        mb = bp.mean(axis=1); mg = gp.mean(axis=1)
        vb = bp.var(axis=1); vg = gp.var(axis=1)
        vs = np.maximum((bp + gp).var(axis=1), (bp - gp).var(axis=1))
        if policy == "S":
            typ = np.zeros(R, int)
        elif policy == "timer":
            typ = np.where((m == 1) & (tg >= par), 3, 0)
        elif policy == "threshold":
            typ = np.where((m == 1) & (vg >= par), 3, 0)
        elif policy == "eager_alt":
            typ = np.where(m == 1, np.where(tg >= tb, 3, 2), 0)
        elif policy == "dp":                      # table from the linear-model DP, fed with the particle variances
            from toy3_dp import table_policy
            typ, alpha = table_policy(par, m, vb, vg)
            typ = np.where(typ == 1, 0, typ)
        else:
            raise ValueError(policy)
        T = np.where(typ == 0, _solve_T(vs, qb + qg, c), np.where(typ == 2, _solve_T(vb, qb, c / 2), _solve_T(vg, qg, c / 2)))
        if policy == "dp":
            T = alpha * T
        if eb2 is not None and n >= n_burn:
            cb += np.sum(eb2 * T + qb * T**2 / 2); cg += np.sum(eg2 * T + qg * T**2 / 2); time += np.sum(T)
            used += np.bincount(typ, minlength=4)
        xib, etab = _noise(rng, qb, T, R); xig, etag = _noise(rng, qg, T, R)
        db = b * T + etab - mb * T; dg = g * T + etag - mg * T
        b = b + xib; g = g + xig
        Tc = T[:, None]
        xibp, etabp = _noise(rng, qb, Tc, (R, Np)); xigp, etagp = _noise(rng, qg, Tc, (R, Np))
        dbp = bp * Tc + etabp - (mb * T)[:, None]; dgp = gp * Tc + etagp - (mg * T)[:, None]
        bp = bp + xibp; gp = gp + xigp
        isS = typ == 0; isB = typ == 2
        th1 = np.where(isS, db + dg, np.where(isB, 2 * db, 2 * dg))
        o1 = np.where(rng.random(R) < 0.5 * (1 + np.sin(th1)), 1.0, -1.0)
        th1p = np.where(isS[:, None], dbp + dgp, np.where(isB[:, None], 2 * dbp, 2 * dgp))
        w = 0.5 * (1 + o1[:, None] * np.sin(th1p))
        o2 = np.where(rng.random(R) < 0.5 * (1 + np.sin(db - dg)), 1.0, -1.0)
        w = w * np.where(isS[:, None], 0.5 * (1 + o2[:, None] * np.sin(dbp - dgp)), 1.0)
        w += 1e-300
        w /= w.sum(axis=1, keepdims=True)
        eb2 = (b - np.sum(w * bp, axis=1)) ** 2; eg2 = (g - np.sum(w * gp, axis=1)) ** 2
        bp, gp = _resample2(rng, w, bp, gp)
        tg = np.where(typ == 3, 0.0, tg + T); tb = np.where(typ == 2, 0.0, tb + T)
        m = np.where(typ >= 2, 0, m)
        arr = (rng.random(R) < 1 - np.exp(-R_arr * T)) if np.isfinite(R_arr) else np.ones(R, bool)
        m = np.where(arr, 1, m)
    mse_b = cb / time / rho ** (2 / 3); mse_g = cg / time
    return dict(mse_b=float(mse_b), mse_g=float(mse_g), frac_G=float(used[3] / used.sum()), frac_B=float(used[2] / used.sum()),
                pair_rate=float((used[2] + used[3]) / time))


if __name__ == "__main__":
    import time as _t
    t0 = _t.time()
    print(simulate3(1000.0, "S", R=16, Np=1024, n_burn=100, n_meas=300), _t.time() - t0)
    print(simulate3(1000.0, "timer", par=0.2, R=16, Np=1024, n_burn=100, n_meas=300), _t.time() - t0)
