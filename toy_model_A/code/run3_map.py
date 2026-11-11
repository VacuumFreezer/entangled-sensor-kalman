"""Toy 3: gain from optimally scheduled entanglement (unlimited supply) versus the best no-entanglement policy,
for different noise ratios rho and weights lam (DP in the linear Kalman filter model)."""
import json, time
import numpy as np
from multiprocessing import Pool
from toy3_dp import *

def work(job):
    rho, lam, label = job
    Jn, poln = optimal_policy(rho, lam, 0.0, allowed="SX")
    rn = simulate(lambda m, pb, pg, st: table_policy(poln, m, pb, pg), rho, lam, 0.0, seed=1)
    Je, pole = optimal_policy(rho, lam, np.inf, J0=Jn)
    re = simulate(lambda m, pb, pg, st: table_policy(pole, m, pb, pg), rho, lam, np.inf, seed=1)
    f = lambda r: dict(J=float(r["J"]), mse_b=float(r["mse_b"]), mse_g=float(r["mse_g"]), frac={k: float(v) for k, v in r["frac"].items()}, pair_rate=r["pair_rate"])
    return dict(rho=rho, lam=lam, label=label, none=f(rn), ent=f(re))

if __name__ == "__main__":
    jobs = []
    for rho in (10.0, 100.0, 1000.0):
        jobs.append((rho, rho ** (2 / 3), "equal"))
        for lam in (1.0, 0.1, 0.01):
            jobs.append((rho, lam, f"lam={lam}"))
    with Pool(4) as p:
        res = []
        for o in p.imap(work, jobs, chunksize=1):
            res.append(o)
            print(f"rho={o['rho']:6.0f} {o['label']:9s}: none J={o['none']['J']:.3f} (b {o['none']['mse_b']:.3f}, g {o['none']['mse_g']:.3f}, use {o['none']['frac']}) | "
                  f"ent J={o['ent']['J']:.3f} (b {o['ent']['mse_b']:.3f}, g {o['ent']['mse_g']:.3f}, use {o['ent']['frac']}, pairs {o['ent']['pair_rate']:.1f}) ratio={o['ent']['J']/o['none']['J']:.3f}", flush=True)
            json.dump(res, open("res3_map.json", "w"), indent=1)
