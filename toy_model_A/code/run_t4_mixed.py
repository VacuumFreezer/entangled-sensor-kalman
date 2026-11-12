"""Toy 4, finite nuisance intensity and limited pairs (k = 4, linear Kalman filter): unentangled sensors track every
mode and insert one nuisance-blind GHZ cycle whenever three pairs are stored."""
import json, numpy as np
from toy4_supply import *
from run_t4_supply import configs_for

if __name__ == "__main__":
    out = []
    for case, target, tracked in (("A", "g", "bg"), ("B", "c", "bgc")):
        cf, Jex = configs_for(case); g = cf[3]; ghz = (g[1], g[2], g[3])
        for rho in (100.0, 1000.0, 10000.0):
            d = {m: rho for m in tracked}; d[target] = 1.0
            for R in (0.0, 0.25, 0.5, 1.0, 2.0, 4.0, 8.0, 16.0, 32.0, np.inf):
                r = simulate_mixed(4, d, target, tracked, ghz, R, M=200, n_burn=1500, n_meas=6000)
                r.update(case=case, rho=rho, R=(R if np.isfinite(R) else "inf")); out.append(r)
            print(case, rho, [round(r["J"], 3) for r in out[-10:]], flush=True)
    json.dump(out, open("res_t4_mixed.json", "w"), indent=1)
