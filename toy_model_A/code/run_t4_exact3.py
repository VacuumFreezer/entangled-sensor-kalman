"""Exact simulation of the one-pair configurations of toy 4 (k = 4): one Bell pair on the outer link, the two inner
sensors unentangled.  Case A: antisymmetric pair (blind on its own) + two-sensor correlation.  Case B: symmetric pair,
three-unit correlation."""
import json, time, numpy as np
from multiprocessing import Pool
from toy4_modes import *

def build(case):
    if case == "A":
        t, n = make_units(4, [([0, 3], [-1, 1]), ([1], [1]), ([2], [1])], "g", "b")
        cfg = Config(t, n, name="outer pair"); cfg.optimize_delta(n_start=12)
        dl = cfg.delta.copy(); dl[0] = 0.0; cfg.set_delta(dl); kref = 2.0
    else:
        t, n = make_units(4, [([0, 3], [1, 1]), ([1], [1]), ([2], [1])], "c", "bg")
        cfg = Config(t, n, name="outer pair"); cfg.optimize_delta(n_start=12); kref = cfg.a_max
    return cfg, kref

def work(job):
    case, c, seed = job
    cfg, kref = build(case)
    r = simulate(cfg, c=c, kappa_ref=kref, seed=seed, n_burn=300, n_meas=2000)
    r.update(case=case, k=4, name="outer pair", c=c, seed=seed, kref=kref, K=cfg.fisher()); return r

if __name__ == "__main__":
    jobs = [(case, c, s) for case in "AB" for c in (0.35, 0.5, 0.7, 1.0) for s in (0, 1)]
    out = []
    with Pool(4) as pool:
        for r in pool.imap_unordered(work, jobs):
            out.append(r); print(r, flush=True)
            json.dump(out, open("res_t4_exact3.json", "w"), indent=1)
