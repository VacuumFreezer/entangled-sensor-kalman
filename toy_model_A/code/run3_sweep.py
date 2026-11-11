"""Toy 3 sweep (linear Kalman filter): cost versus pair supply rate R for
no entanglement / eager use / best open-loop timer / best covariance threshold / DP optimum."""
import json, sys, time
import numpy as np
from multiprocessing import Pool
from toy3_dp import *

TAUS = (0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.4, 0.6, 1.0)
THETAS = (0.6, 0.9, 1.2, 1.4, 1.6, 1.8, 2.0, 2.4, 3.0)
PROBS = (0.02, 0.05, 0.1, 0.15, 0.2, 0.3, 0.5, 1.0)

def work(job):
    rho, lam, R = job
    t0 = time.time()
    out = dict(rho=rho, lam=lam, R=(R if np.isfinite(R) else "inf"))
    out["S_only"] = simulate(pol_S(), rho, lam, R)["J"]
    for mode in ("G", "alt"):
        out["eager_" + mode] = simulate(pol_eager(mode), rho, lam, R)["J"]
    bases = (0,) if lam >= 1 else (0, 1)
    best = (np.inf, None)
    for base in bases:
        for tau in TAUS:
            J = simulate(pol_timer(tau, base=base), rho, lam, R)["J"]
            if J < best[0]: best = (J, dict(tau_g=tau, base="SX"[base]))
    out["timer"], out["timer_par"] = best
    best = (np.inf, None)
    for base in bases:
        for th in THETAS:
            J = simulate(pol_threshold(th, base=base), rho, lam, R)["J"]
            if J < best[0]: best = (J, dict(theta_g=th, base="SX"[base]))
    out["threshold"], out["threshold_par"] = best
    best = (np.inf, None)
    for base in bases:
        for pr in PROBS:
            J = simulate(pol_thin(pr, base=base), rho, lam, R)["J"]
            if J < best[0]: best = (J, dict(prob=pr, base="SX"[base]))
    out["thin"], out["thin_par"] = best
    J, pol = optimal_policy(rho, lam, R, J0=min(out["timer"], out["S_only"]))
    r = simulate(lambda m, pb, pg, st: table_policy(pol, m, pb, pg), rho, lam, R, seed=1)
    out["dp"] = r["J"]; out["dp_detail"] = {k: (float(v) if not isinstance(v, dict) else {a: float(b) for a, b in v.items()}) for k, v in r.items()}
    out["time"] = time.time() - t0
    return out

if __name__ == "__main__":
    jobs = []
    for rho, lam in ((1000.0, 1.0), (1000.0, 0.1), (100.0, 1.0)):
        jobs.append((rho, lam, 0.0))
        for R in (0.5, 1.0, 2.0, 4.0, 8.0, 16.0, np.inf):
            jobs.append((rho, lam, R))
    with Pool(4) as p:
        res = []
        for o in p.imap(work, jobs, chunksize=1):
            res.append(o)
            print(f"rho={o['rho']:6.0f} lam={o['lam']:.1f} R={str(o['R']):>4s}: S={o['S_only']:.3f} eagerG={o['eager_G']:.3f} eagerAlt={o['eager_alt']:.3f} "
                  f"thin={o['thin']:.3f} {o['thin_par']} timer={o['timer']:.3f} {o['timer_par']} thr={o['threshold']:.3f} {o['threshold_par']} DP={o['dp']:.3f} "
                  f"use={o['dp_detail']['frac']} pair_rate={o['dp_detail']['pair_rate']:.2f} ({o['time']:.0f}s)", flush=True)
            json.dump(res, open("res3_sweep.json", "w"), indent=1)
