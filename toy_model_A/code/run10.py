"""Toy 2, resource view at strong common-mode noise: n unentangled pairs doing correlation
spectroscopy. Each pair is an effective binary measurement with coupling 2 and visibility 1/2."""
import time, json, numpy as np
from multiprocessing import Pool
from toy_model import simulate
jobs = [(n, c) for n in (2, 3, 4, 5, 6) for c in (0.3, 0.4, 0.5)]
def work(j):
    n, c = j
    res = [simulate([(2, 0.0, 0.5)] * n, c=c, R=128, Np=768, n_burn=150, n_meas=900, seed=s) for s in (61, 62)]
    return dict(n=n, c=c, mse=[r['mse'] for r in res], T=float(np.mean([r['T'] for r in res])),
                oor=float(np.mean([r['out_of_range'] for r in res])))
if __name__ == "__main__":
    t0 = time.time()
    with Pool(4) as p:
        out = p.map(work, jobs, chunksize=1)
    json.dump(out, open("res10.json", "w"), indent=1)
    for o in out:
        # x in simulate() is 2g-coupled field g itself (coupling 2), so the MSE is that of g in units q_g^(2/3)
        print(f"n={o['n']} pairs c={o['c']:.2f} MSE_g={np.mean(o['mse']):.3f} (seeds {o['mse'][0]:.3f},{o['mse'][1]:.3f}) T={o['T']:.3f} oor={o['oor']:.4f}")
    print("time", time.time() - t0)
