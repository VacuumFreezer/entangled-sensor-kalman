"""Exact check of the unentangled all-modes-tracked strategy against the linear model."""
import json, sys, time, numpy as np
from multiprocessing import Pool
from toy4_modes import *

def work(job):
    case, k, rho, seed = job
    target, nuis = {"A": ("g", "b"), "B": ("c", "bg")}[case]
    d = {m: rho for m in nuis}; d[target] = 1.0
    tracked = "".join(sorted(nuis + target, key=MODES.index))
    t0 = time.time()
    r = simulate_S(k, d, target=target, tracked=tracked, seed=seed, Np=(2048 if len(tracked) == 2 else 6000))
    r.update(case=case, k=k, rho=rho, seed=seed, lin=lin_cost_S(k, d, target=target, tracked=tracked)[0], lin_a1=lin_cost_S(k, d, target=target, tracked=tracked, alphas=np.array([1.0]))[0], time=time.time() - t0)
    return r

if __name__ == "__main__":
    jobs = [(case, k, rho, seed) for case, k in (("A", 2), ("A", 4), ("B", 4)) for rho in (10.0, 100.0, 1000.0) for seed in (0, 1)]
    out = []
    with Pool(4) as pool:
        for r in pool.imap_unordered(work, jobs):
            out.append(r); print(r, flush=True)
            json.dump(out, open("res_t4_S.json", "w"), indent=1)
