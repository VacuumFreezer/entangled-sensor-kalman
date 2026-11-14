"""Best local-only partition of n qubits per node into local GHZ units (same partition at every node)."""
import numpy as np, sys, json, time
from toy5_nodes import *
from scipy.optimize import minimize
cases = {
  "A2": (np.array([-1., 1.]), "g", "b", [1.], None),
  "B4": (np.linspace(-1, 1, 4), "c", "bg", [1., 1/3], None),
  "B3w": (np.array([-1., 0., 1.]), "c", "bg", [1., 1.], [1, 2, 1]),   # node j holds w_j * n qubits
}
def partitions(n, maxlen=6):
    def rec(n, mx):
        if n == 0: yield []; return
        for p in range(min(n, mx), 0, -1):
            for rest in rec(n - p, p): yield [p] + rest
    return [p for p in rec(n, n) if len(p) <= maxlen]

def refs(gs, x):
    # x: per node offset + relative offsets of the size classes (shared across nodes)
    sizes = sorted(set(gs), reverse=True)
    out = np.zeros(len(gs)); gs_a = np.array(gs)
    for ci, g in enumerate(sizes):
        idx = np.where(gs_a == g)[0]
        out[idx] = x[ci] + np.pi * np.arange(len(idx)) / len(idx)
    return out

name = sys.argv[1]; ns = [int(a) for a in sys.argv[2:]]
z, t, nu, unit, w = cases[name]; k = len(z); M = modes(z); Fn = np.stack([M[x] for x in nu], 1)
w = [1] * k if w is None else w
out = {}
for n in ns:
    out[n] = []
    for p in partitions(n):
        gsn = [[g for g in p for _ in range(1)] for _ in range(k)]
        # node j with weight w_j: repeat the partition w_j times (w_j * n qubits)
        gsn = [p * w[j] for j in range(k)]
        net = MixNet(z, M[t], Fn, gsn, unit); t0 = time.time()
        ncls = len(set(p))
        def deltas(x):
            return [refs(gsn[j], x[ncls * 0:ncls] + x[ncls + j]) for j in range(k)]
        if net.nbits <= 12:
            f = lambda x: -net.fisher_exact(deltas(x))
            best = min((minimize(f, np.random.default_rng(s).uniform(-3, 3, ncls + k), method='Nelder-Mead', options=dict(maxiter=400)) for s in range(3)), key=lambda r: r.fun)
            K = -best.fun; src = "exact"
        else:
            # coarse search of class offsets with small MC, then a final MC
            rng = np.random.default_rng(1); cands = [np.zeros(ncls + k)] + [np.concatenate([rng.uniform(0, np.pi, ncls), 0.3 * np.arange(k)]) for _ in range(5)]
            sc = [net.fisher_mc(deltas(x), N=8000, seed=3)[0] for x in cands]
            xb = cands[int(np.argmax(sc))]
            K, e = net.fisher_mc(deltas(xb), N=40000, seed=5); src = f"mc±{e:.3f}"
        out[n].append(dict(p=p, K=float(K), src=src, K_over_n2=float(K) / n ** 2))
        print(name, n, p, round(K, 4), round(K / n ** 2, 4), src, f"{time.time()-t0:.1f}s", flush=True)
json.dump(out, open(f"res_t5_part_{name}_{'_'.join(map(str, ns))}.json", "w"), indent=1)
