"""Exact-simulation checks of the linear-KF sweeps: GHZ(3), GHZ(4) at c=0.5,
dephasing g=0.3 and 1.0, and GHZ generation dead time (k=3)."""
import time, json, numpy as np
from multiprocessing import Pool
from toy_model import *
jobs = []
for k in (3, 4):
    jobs.append((f"ghz{k}", ghz(k), 0.5, dict()))
for k in (2, 3, 4):
    for g in (0.3, 1.0):
        jobs.append((f"sep{k}", sep(k), 0.5, dict(gamma=g)))
        jobs.append((f"ghz{k}", ghz(k), 0.5, dict(gamma=g)))
for Te in (0.05, 0.10):
    jobs.append(("ghz3", ghz(3), 0.5, dict(T_dead=Te)))
def work(j):
    name, groups, c, kw = j
    res = [simulate(groups, c=c, R=128, Np=768, n_burn=150, n_meas=900, seed=s, **kw) for s in (41, 42)]
    lin = lin_constrained(groups, c, **kw)[1]
    return dict(name=name, c=c, kw=kw, mse=[r['mse'] for r in res], T=float(np.mean([r['T'] for r in res])),
                oor=float(np.mean([r['out_of_range'] for r in res])), lin=lin)
if __name__ == "__main__":
    t0 = time.time()
    with Pool(4) as p:
        out = p.map(work, jobs, chunksize=1)
    json.dump(out, open("res7.json", "w"), indent=1)
    for o in out:
        print(f"{o['name']:6s} {str(o['kw']):18s} c={o['c']:.2f} MSE={np.mean(o['mse']):.3f} (seeds {o['mse'][0]:.3f},{o['mse'][1]:.3f}) T={o['T']:.3f} oor={o['oor']:.4f} lin={o['lin']:.3f}")
    print("time", time.time() - t0)
