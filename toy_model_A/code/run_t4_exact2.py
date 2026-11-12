"""Second round of exact simulations for toy 4:
 - units that are nuisance-blind on their own (GHZ, antisymmetric Bell pairs) are operated at mid-fringe (delta = 0);
 - wider lock parameters where the first round had its minimum at the edge of the scan;
 - separable correlations with reference phases optimized for a wide prior (Fisher information averaged over d)."""
import json, sys, time, numpy as np
from multiprocessing import Pool
from toy4_modes import *
from run_t4_exact import FI, CASES, MK

def work(job):
    case, k, name, c, seed, mode = job
    target, nuis = CASES[case]
    cfg = MK[name](k, target, nuis)
    standalone = np.all(np.abs(cfg.n) < 1e-9)
    if standalone:
        cfg.set_delta(np.zeros(cfg.U))
    elif mode == "avg":
        cfg.optimize_delta(sigma=1.0 / cfg.a_max, n_start=(3 if cfg.U >= 8 else 10), seed=1)
    else:
        cfg.set_delta(FI[(case, k)][name]["delta"])
    kref = float(np.abs(cfg.t).max()) if standalone else cfg.a_max
    t0 = time.time()
    r = simulate(cfg, c=c, kappa_ref=kref, seed=seed, n_burn=300, n_meas=2000)
    r.update(case=case, k=k, name=name, c=c, seed=seed, kref=kref, mode=mode, time=time.time() - t0)
    return r

if __name__ == "__main__":
    jobs = []
    for seed in (0, 1):
        for c in (0.4, 0.5, 0.6): jobs.append(("A", 4, "GHZ", c, seed, "mid"))
        for c in (0.4, 0.5, 0.6): jobs.append(("B", 8, "GHZ", c, seed, "mid"))
        for k in (4, 8):
            for c in (0.35, 0.5, 0.7, 1.0): jobs.append(("A", k, "Bell pairs", c, seed, "mid"))
        for c in (2.8, 4.0): jobs.append(("A", 8, "separable", c, seed, "fi0"))
        for case, k, cs in (("A", 4, (1.0, 1.4)), ("A", 8, (1.4, 2.0, 2.8)), ("A2", 4, (0.7, 1.0)), ("A2", 8, (1.0, 1.4)), ("B", 4, (0.5, 0.7)), ("B", 8, (1.0, 1.4))):
            for c in cs: jobs.append((case, k, "separable", c, seed, "avg"))
    out = []
    with Pool(4) as pool:
        for r in pool.imap_unordered(work, jobs):
            out.append(r)
            print(r["case"], r["k"], r["name"], r["mode"], "c=%.2f seed=%d mse=%.3f T=%.3f  (%.0fs)" % (r["c"], r["seed"], r["mse"], r["T"], r["time"]), flush=True)
            json.dump(out, open("res_t4_exact2.json", "w"), indent=1)
