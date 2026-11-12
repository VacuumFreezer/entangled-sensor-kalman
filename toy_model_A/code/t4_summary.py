"""Collect the toy-4 results into one table (res_t4_summary.json).
Exact costs are taken at the best lock parameter c of each configuration, averaged over seeds, slips included."""
import json, numpy as np

def load(f): return json.load(open(f))

def best(rows, **kw):
    """Best (reference-phase choice, lock parameter c), cost averaged over seeds."""
    t = {}
    for r in rows:
        if all(r.get(a) == b for a, b in kw.items()): t.setdefault((r.get("mode", "fi0"), r["c"]), []).append(r["mse"])
    key = min(t, key=lambda q: np.mean(t[q]))
    return dict(J=float(np.mean(t[key])), c=key[1], seeds=[round(x, 3) for x in t[key]])

if __name__ == "__main__":
    e1, e2, e3, fr = load("res_t4_exact.json"), load("res_t4_exact2.json"), load("res_t4_exact3.json"), load("res_t4_fringe.json")
    fi = {(r["case"], r["k"]): r for r in load("res_t4_fisher.json")}
    lin = {(r["case"], r["k"]): r for r in load("res_t4_lin.json")}
    f1 = best(fr); J1 = f1["J"]
    out = dict(J1=J1, c_fringe=f1["c"], J1_c05_noslip=float(np.mean(sorted(r["mse"] for r in fr if r["c"] == 0.5)[:3])), rows=[])
    for (case, k), row in fi.items():
        r = dict(case=case, k=k, info={n: row[n]["K"] for n in ("separable", "Bell pairs", "GHZ")}, info_S=row["S_all_tracked"], a_ghz=row["GHZ"]["a_max"])
        r["sep"] = best(e1 + [x for x in e2 if x["mode"] == "avg"], case=case, k=k, name="separable")
        if k > 2:
            src_case = "A" if case == "A2" else case                       # antisymmetric pairs are blind to the curvature too
            rows = [x for x in e2 if x["mode"] == "mid"] if src_case == "A" else e1
            r["pairs"] = best(rows, case=src_case, k=k, name="Bell pairs")
        r["ghz"] = dict(J=J1 * row["GHZ"]["a_max"] ** (-2 / 3), c=f1["c"])
        r["S_lin"] = {rho: v["J"] for rho, v in lin[(case, k)]["S"].items()}
        r["gain_inf"] = r["sep"]["J"] / r["ghz"]["J"]
        r["gain_none"] = r["S_lin"]["0.0"] / lin[(case, k)]["GHZ"]["J"]
        r["gain_rho"] = {rho: min(v, r["sep"]["J"]) / r["ghz"]["J"] for rho, v in r["S_lin"].items()}
        out["rows"].append(r)
        print(case, k, "sep %.2f (c=%.2f)" % (r["sep"]["J"], r["sep"]["c"]), ("pairs %.2f (c=%.2f)" % (r["pairs"]["J"], r["pairs"]["c"])) if "pairs" in r else "",
              "ghz %.3f" % r["ghz"]["J"], "| gain: none %.2f, rho=100 %.2f, 1e3 %.2f, 1e4 %.2f, inf %.2f" % (r["gain_none"], r["gain_rho"]["100.0"], r["gain_rho"]["1000.0"], r["gain_rho"]["10000.0"], r["gain_inf"]))
    out["one_pair"] = {case: best(e3, case=case) for case in "AB"}
    print("J1", J1, "at c", f1["c"], "| c=0.5 without the slipped seed:", out["J1_c05_noslip"], "| one pair:", out["one_pair"])
    json.dump(out, open("res_t4_summary.json", "w"), indent=1)
