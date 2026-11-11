"""Toy 2, more seeds: two unentangled sensors tracking the gradient g under common-mode noise b."""
import time, json, numpy as np
from multiprocessing import Pool
from toy_gradient import simulate_sep2
jobs = []
for rho in (0.1, 1.0, 10.0, 100.0, 1000.0, 10000.0):
    for pol in ("A", "B"):
        seeds = (31, 32, 33, 34) if rho == 0.1 else (33, 34)
        jobs.append((rho, 0.5, pol, seeds))
jobs.append((1.0, 0.4, "B", (31, 32, 33, 34)))
def work(j):
    rho, c, pol, seeds = j
    r = [simulate_sep2(rho, c, pol, seed=s) for s in seeds]
    return dict(rho=rho, c=c, policy=pol, seeds=list(seeds), mse=[x['mse'] for x in r], T=float(np.mean([x['T'] for x in r])))
if __name__ == "__main__":
    t0 = time.time()
    with Pool(4) as p:
        out = p.map(work, jobs, chunksize=1)
    json.dump(out, open("res8.json", "w"), indent=1)
    for o in out:
        print(f"rho={o['rho']:8.1f} policy {o['policy']} c={o['c']}: MSE_g={np.mean(o['mse']):.3f} median={np.median(o['mse']):.3f} seeds {['%.3f'%m for m in o['mse']]} T={o['T']:.3f}")
    print("time", time.time() - t0)
