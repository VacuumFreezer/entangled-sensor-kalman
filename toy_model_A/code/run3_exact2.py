"""Second round of exact-simulation checks (rho = 1000, lam = 1): lock parameter of the no-entanglement
baseline, finer covariance thresholds, and the DP table policy driven by the particle variances."""
import json, time
import numpy as np
from multiprocessing import Pool
from toy3_exact import simulate3

jobs = []
for c in (0.35, 0.4, 0.45):
    jobs += [("S", np.inf, None, c, (71, 72)), ("S", np.inf, None, c, (73, 74))]
jobs += [("S", np.inf, None, 0.5, (73, 74))]
jobs += [("dp", np.inf, None, 0.5, (71, 72)), ("dp", 2.0, None, 0.5, (71, 72))]
jobs += [("threshold", np.inf, 1.6, 0.5, (71, 72)), ("threshold", np.inf, 2.0, 0.5, (71, 72))]
jobs += [("timer", np.inf, 0.25, 0.5, (71, 72))]

def work(j):
    pol, R, par, c, seeds = j
    if pol == "dp":
        from toy3_dp import optimal_policy
        par = optimal_policy(1000.0, 1.0, R, J0=3.8)[1]
    r = [simulate3(1000.0, pol, R_arr=R, par=par, c=c, seed=s) for s in seeds]
    return dict(policy=pol, R=(R if np.isfinite(R) else "inf"), par=(par if not isinstance(par, dict) else "dp table"), c=c, seeds=list(seeds),
                mse_b=[x["mse_b"] for x in r], mse_g=[x["mse_g"] for x in r],
                frac_G=float(np.mean([x["frac_G"] for x in r])), frac_B=float(np.mean([x["frac_B"] for x in r])),
                pair_rate=float(np.mean([x["pair_rate"] for x in r])))

if __name__ == "__main__":
    t0 = time.time()
    with Pool(4) as p:
        res = []
        for o in p.imap(work, jobs, chunksize=1):
            res.append(o)
            J = [a + b for a, b in zip(o["mse_b"], o["mse_g"])]
            print(f"{o['policy']:10s} R={str(o['R']):>4s} par={o['par']} c={o['c']}: J={np.mean(J):.3f} (seeds {J[0]:.3f},{J[1]:.3f}) "
                  f"mse_b={[round(x,3) for x in o['mse_b']]} mse_g={[round(x,3) for x in o['mse_g']]} fracG={o['frac_G']:.3f} fracB={o['frac_B']:.3f} pair_rate={o['pair_rate']:.2f}", flush=True)
            json.dump(res, open("res3_exact2.json", "w"), indent=1)
    print("time", time.time() - t0)
