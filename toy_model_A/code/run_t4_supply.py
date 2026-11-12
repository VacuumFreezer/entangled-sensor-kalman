"""Toy 4 with a limited supply of Bell pairs (k = 4): cost versus supply rate for simple policies and the DP optimum.
Each configuration's information is calibrated so that the linear model reproduces its exact-simulation cost."""
import json, sys, numpy as np
from multiprocessing import Pool
from toy4_supply import *

def best(rows, **kw):
    """(cost, c) at the best lock parameter, averaged over seeds."""
    t = {}
    for r in rows:
        if all(r.get(a) == b for a, b in kw.items()): t.setdefault(r["c"], []).append(r["mse"])
    c = min(t, key=lambda c: np.mean(t[c]))
    return float(np.mean(t[c])), c

def configs_for(case):
    e1 = json.load(open("res_t4_exact.json")); e2 = json.load(open("res_t4_exact2.json")); e3 = json.load(open("res_t4_exact3.json"))
    fr = json.load(open("res_t4_fringe.json"))
    cs = sorted({r["c"] for r in fr}); CF = min(cs, key=lambda c: np.mean([r["mse"] for r in fr if r["c"] == c]))   # slips included
    J1 = float(np.mean([r["mse"] for r in fr if r["c"] == CF]))
    if case == "A":
        a = 8 / 3
        raw = [(0, best(e1 + [r for r in e2 if r["mode"] == "avg"], case="A", k=4, name="separable"), a),
               (1, best(e3, case="A"), 2.0),
               (2, best([r for r in e2 if r["mode"] == "mid"], case="A", k=4, name="Bell pairs"), 2.0),
               (3, (J1 * a ** (-2 / 3), CF), a)]
    else:
        a = 16 / 9
        raw = [(0, best(e1 + [r for r in e2 if r["mode"] == "avg"], case="B", k=4, name="separable"), a),
               (1, best(e3, case="B"), a),
               (2, best(e1, case="B", k=4, name="Bell pairs"), a),
               (3, (J1 * a ** (-2 / 3), CF), a)]
    return [(need, calibrate(J, kref, c), kref, c) for need, (J, c), kref in raw], [J for _, (J, c), _ in raw]

def work(job):
    case, R = job
    configs, Jex = configs_for(case)
    out = dict(case=case, R=(R if np.isfinite(R) else "inf"), configs=configs, J_exact=Jex)
    out["none"] = simulate(pol_fixed(0), configs, R, 3)["J"]
    for name, pol in (("greedy", pol_greedy(configs)), ("one_pair", pol_one(configs, 1)), ("two_pairs", pol_one(configs, 2)), ("save_ghz", pol_save(configs))):
        r = simulate(pol, configs, R, 3); out[name] = r["J"]; out[name + "_detail"] = r
    J, pol = optimal_policy(configs, R, 3, J0=min(out["greedy"], out["save_ghz"], out["one_pair"]),
                            p_range=((0.03, 30.0) if case == "A" else (0.2, 400.0)))
    r = simulate(lambda m, p: table_policy(pol, m, p), configs, R, 3, seed=1)
    out["dp"] = r["J"]; out["dp_detail"] = r
    return out

if __name__ == "__main__":
    cases = sys.argv[1] if len(sys.argv) > 1 else "AB"
    jobs = [(case, R) for case in cases for R in (0.25, 0.5, 1.0, 2.0, 4.0, 8.0, 16.0, 32.0, np.inf)]
    res = [r for r in json.load(open("res_t4_supply.json")) if r["case"] not in cases] if cases != "AB" else []
    with Pool(4) as pool:
        for r in pool.imap(work, jobs):
            res.append(r)
            print(r["case"], r["R"], {n: round(r[n], 3) for n in ("none", "greedy", "one_pair", "two_pairs", "save_ghz", "dp")}, r["dp_detail"]["frac"], round(r["dp_detail"]["pair_rate"], 2), flush=True)
            json.dump(res, open("res_t4_supply.json", "w"), indent=1)
