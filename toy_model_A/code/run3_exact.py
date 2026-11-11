"""Exact-simulation checks for toy 3 at rho = 1000 (cost = MSE_b / rho^(2/3) + MSE_g)."""
import json, time
import numpy as np
from multiprocessing import Pool
from toy3_exact import simulate3

jobs = [("S", np.inf, None), ("eager_alt", np.inf, None)]
jobs += [("timer", np.inf, t) for t in (0.15, 0.2, 0.3)]
jobs += [("threshold", np.inf, t) for t in (1.4, 1.8, 2.4)]
jobs += [("timer", 2.0, t) for t in (0.0, 0.1, 0.15, 0.25)]
jobs += [("threshold", 2.0, t) for t in (1.6, 2.0, 2.6)]

def work(j):
    pol, R, par = j
    r = [simulate3(1000.0, pol, R_arr=R, par=par, seed=s) for s in (71, 72)]
    return dict(policy=pol, R=(R if np.isfinite(R) else "inf"), par=par, mse_b=[x["mse_b"] for x in r], mse_g=[x["mse_g"] for x in r],
                frac_G=float(np.mean([x["frac_G"] for x in r])), frac_B=float(np.mean([x["frac_B"] for x in r])),
                pair_rate=float(np.mean([x["pair_rate"] for x in r])))

if __name__ == "__main__":
    t0 = time.time()
    with Pool(4) as p:
        res = []
        for o in p.imap(work, jobs, chunksize=1):
            res.append(o)
            J = [a + b for a, b in zip(o["mse_b"], o["mse_g"])]
            print(f"{o['policy']:10s} R={str(o['R']):>4s} par={o['par']}: J={np.mean(J):.3f} (seeds {J[0]:.3f},{J[1]:.3f}) "
                  f"mse_b={np.mean(o['mse_b']):.3f} mse_g={np.mean(o['mse_g']):.3f} fracG={o['frac_G']:.3f} fracB={o['frac_B']:.3f} pair_rate={o['pair_rate']:.2f}", flush=True)
            json.dump(res, open("res3_exact.json", "w"), indent=1)
    print("time", time.time() - t0)
