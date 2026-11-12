"""Single-fringe measurement (GHZ with phase gain a): cost J1(c) for a = 1, slips included.  J(a) = J1 * a^(-2/3)."""
import json, numpy as np
from multiprocessing import Pool
from toy4_modes import *

def work(job):
    c, seed = job
    cfg = Config([1.0], np.zeros((1, 0)))
    r = simulate(cfg, c=c, kappa_ref=1.0, seed=seed, R=128, Np=1024, n_burn=300, n_meas=4000)
    r.update(c=c, seed=seed); return r

if __name__ == "__main__":
    jobs = [(c, s) for c in (0.35, 0.4, 0.45, 0.5) for s in range(4)]
    out = []
    with Pool(2) as pool:
        for r in pool.imap_unordered(work, jobs):
            out.append(r); print(r, flush=True)
            json.dump(out, open("res_t4_fringe.json", "w"), indent=1)
