"""Exact-simulation checks: (i) separable networks with 5-10 sensors at their own optimal lock
parameter (for the resource comparison), (ii) GHZ(3) with imperfect contrast v0."""
import time, json, numpy as np
from multiprocessing import Pool
from toy_model import simulate, lin_constrained
jobs = []
for k, c in ((5, 0.474), (6, 0.432), (8, 0.374), (9, 0.353), (10, 0.335)):
    jobs.append((f"sep{k}", [(1, 0.0, 1.0)] * k, c))
for v0 in (0.9, 0.8):
    jobs.append((f"ghz3_v{v0}", [(3, 0.0, v0)], 0.5))
def work(j):
    name, groups, c = j
    res = [simulate(groups, c=c, R=128, Np=768, n_burn=150, n_meas=900, seed=s) for s in (51, 52)]
    return dict(name=name, c=c, mse=[r['mse'] for r in res], T=float(np.mean([r['T'] for r in res])),
                oor=float(np.mean([r['out_of_range'] for r in res])))
if __name__ == "__main__":
    t0 = time.time()
    with Pool(4) as p:
        out = p.map(work, jobs, chunksize=1)
    json.dump(out, open("res9.json", "w"), indent=1)
    for o in out:
        print(f"{o['name']:10s} c={o['c']:.3f} MSE={np.mean(o['mse']):.3f} (seeds {o['mse'][0]:.3f},{o['mse'][1]:.3f}) T={o['T']:.3f} oor={o['oor']:.4f}")
    print("time", time.time() - t0)
