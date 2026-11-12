import json, numpy as np
from toy4_modes import *
out = []
for case, target, nuis in (("A", "g", "b"), ("A2", "g", "bc"), ("B", "c", "bg")):
    for k in (2, 4, 8):
        if case == "B" and k < 4: continue
        if case == "A2" and k < 4: continue
        row = dict(case=case, k=k)
        for mk in (cfg_separable, cfg_pairs, cfg_ghz):
            cfg = mk(k, target, nuis)
            K0 = cfg.optimize_delta(n_start=(8 if cfg.U >= 8 else 24))
            row[cfg.name] = dict(K=K0, a_max=cfg.a_max, nterms=len(cfg.A), delta=[float(x) for x in cfg.delta])
        F = mode_matrix(k); it = MODES.index(target)
        row["S_all_tracked"] = float((F[:, it] ** 2).sum())
        out.append(row)
        print(case, k, {n: (round(v["K"], 4), round(v["a_max"], 3), v["nterms"]) if isinstance(v, dict) else round(v, 4) for n, v in row.items() if n not in ("case", "k")}, flush=True)
json.dump(out, open("res_t4_fisher.json", "w"), indent=1)
