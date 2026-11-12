"""Exact simulation (outcomes + particle filter) of the nuisance-immune configurations of toy 4."""
import json, sys, time, numpy as np
from multiprocessing import Pool
from toy4_modes import *

FI = {(r["case"], r["k"]): r for r in json.load(open("res_t4_fisher.json"))}
CASES = {"A": ("g", "b"), "A2": ("g", "bc"), "B": ("c", "bg")}
MK = {"separable": cfg_separable, "Bell pairs": cfg_pairs, "GHZ": cfg_ghz}

def work(job):
    case, k, name, c, seed = job
    target, nuis = CASES[case]
    cfg = MK[name](k, target, nuis)
    cfg.set_delta(FI[(case, k)][name]["delta"])
    standalone = np.all(np.abs(cfg.n) < 1e-9)
    kref = float(np.abs(cfg.t).max()) if standalone else cfg.a_max
    t0 = time.time()
    r = simulate(cfg, c=c, kappa_ref=kref, seed=seed, n_burn=300, n_meas=2000)
    r.update(case=case, k=k, name=name, c=c, seed=seed, kref=kref, time=time.time() - t0)
    return r

if __name__ == "__main__":
    jobs = []
    for case, k in (("A", 2), ("A", 4), ("A", 8), ("A2", 4), ("A2", 8), ("B", 4), ("B", 8)):
        for name in ("separable", "Bell pairs", "GHZ"):
            if name == "GHZ" and not (case == "A" and k == 4): continue        # single fringe: follows from toy 1 by scaling
            if name == "Bell pairs" and (k == 2 or case == "A2"): continue     # k=2: same as GHZ; A2: same as A
            cs = (0.4, 0.5, 0.6) if name == "GHZ" else (0.35, 0.5, 0.7, 1.0, 1.4, 2.0)
            for c in cs:
                for seed in (0, 1):
                    jobs.append((case, k, name, c, seed))
    jobs.sort(key=lambda j: -j[1])
    out = []
    with Pool(4) as pool:
        for r in pool.imap_unordered(work, jobs):
            out.append(r)
            print(r["case"], r["k"], r["name"], "c=%.2f seed=%d mse=%.3f T=%.3f worst=%.1f  (%.0fs)" % (r["c"], r["seed"], r["mse"], r["T"], r["worst"], r["time"]), flush=True)
            json.dump(out, open("res_t4_exact.json", "w"), indent=1)
