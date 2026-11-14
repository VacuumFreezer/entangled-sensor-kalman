import numpy as np, sys, json, time
from toy5_nodes import *
from scipy.optimize import minimize
cases = {
  "A2": (np.array([-1., 1.]), "g", "b", [1.]),
  "B4": (np.linspace(-1, 1, 4), "c", "bg", [1., 1/3]),
  "B3": (np.array([-1., 0., 1.]), "c", "bg", [1., 1.]),
  "A4": (np.linspace(-1, 1, 4), "g", "b", [1.]),
}
which = sys.argv[1:] or list(cases)
res = {}
for name in which:
    z, t, nu, unit = cases[name]; k = len(z); M = modes(z)
    Fn = np.stack([M[x] for x in nu], 1); res[name] = {}
    for m in range(1, 9):
        gs = [[1] * m] * k
        net = MixNet(z, M[t], Fn, gs, unit); t0 = time.time(); row = dict(nterms=len(net.Q))
        if k * m <= 12:
            f = lambda x: -net.fisher_exact([spread_refs(g, x[j]) for j, g in enumerate(gs)])
            best = min((minimize(f, np.random.default_rng(s).uniform(-3, 3, k), method='Nelder-Mead', options=dict(maxiter=300)) for s in range(4)), key=lambda r: r.fun)
            row["K"] = -best.fun; row["src"] = "exact"; offs = best.x
        else:
            K, e = net.fisher_mc([spread_refs(g, 0.3 * j) for j, g in enumerate(gs)], N=60000)
            row["K"] = K; row["err"] = e; row["src"] = "mc"
        res[name][m] = row
        print(name, m, row, f"{time.time()-t0:.1f}s", flush=True)
    json.dump(res, open(f"res_t5_KU_{'_'.join(which)}.json", "w"), indent=1)
