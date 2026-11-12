"""Toy 4, linear Kalman filter: steady-state cost of each nuisance-blind configuration (information from
res_t4_fisher.json, lock c = 0.5 on the largest phase gain) and of unentangled sensors that track every mode (S),
as a function of the nuisance intensity rho."""
import json, numpy as np
from multiprocessing import Pool
from toy4_modes import *

RHOS = [0.0] + [float(x) for x in np.round(10 ** np.arange(0, 6.01, 0.5), 6)]
NUIS = {"A": "b", "A2": "bc", "B": "bg"}

def work(row):
    case, k = row["case"], row["k"]
    target = "g" if case.startswith("A") else "c"; nuis = NUIS[case]
    r = dict(case=case, k=k, S={})
    for name in ("separable", "Bell pairs", "GHZ"):
        J, al, T = lin_cost(row[name]["K"], row[name]["a_max"])
        r[name] = dict(J=float(J), alpha=float(al), T=float(T))
    for rho in RHOS:
        d = {m: rho for m in nuis}; d[target] = 1.0
        tracked = "".join(sorted(nuis + target, key=MODES.index)) if rho > 0 else target
        J, al, T = lin_cost_S(k, d, target=target, tracked=tracked)
        r["S"][str(rho)] = dict(J=J, alpha=al, T=T)
    return r

if __name__ == "__main__":
    fi = json.load(open("res_t4_fisher.json"))
    with Pool(3) as pool:
        out = pool.map(work, fi)
    for r in out:
        print(r["case"], r["k"], {n: round(r[n]["J"], 3) for n in ("separable", "Bell pairs", "GHZ")}, "S:", {a: round(b["J"], 3) for a, b in r["S"].items()}, flush=True)
    json.dump(out, open("res_t4_lin.json", "w"), indent=1)
