import numpy as np, sys
from toy5_nodes import *
from scipy.optimize import minimize
z = np.array([-1., 0., 1.]); M = modes(z); Fn = np.stack([M['b'], M['g']], 1)
for gs in ([[1], [2], [1]], [[1, 1], [2, 2], [1, 1]], [[1, 1], [2, 1, 1], [1, 1]], [[1, 1, 1], [2, 2, 2], [1, 1, 1]]):
    net = MixNet(z, M['c'], Fn, gs, [1, 1])
    f = lambda x: -net.fisher_exact([spread_refs(g, x[j]) for j, g in enumerate(gs)])
    r = min((minimize(f, np.random.default_rng(s).uniform(-3, 3, 3), method='Nelder-Mead') for s in range(4)), key=lambda r: r.fun)
    nq = sum(gs[0]); print(gs, "K", round(-r.fun, 4), "per n^2 (n=edge qubits)", round(-r.fun / nq ** 2, 4), "terms", len(net.Q), flush=True)
