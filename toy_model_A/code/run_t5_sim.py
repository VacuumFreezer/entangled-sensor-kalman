import numpy as np, sys, json, time
from toy5_nodes import *; from toy5_sim import *
from scipy.optimize import minimize
geo = {"B4": (np.linspace(-1, 1, 4), [1., 1/3]), "B3": (np.array([-1., 0., 1.]), [1., 1.]), "A2": (np.array([-1., 1.]), [1.])}
cfgs = {
  "B4_1x1": ("B4", "c", "bg", [[1]] * 4, 16 / 9),
  "B4_1x2": ("B4", "c", "bg", [[1, 1]] * 4, 16 / 9),
  "B4_1x3": ("B4", "c", "bg", [[1, 1, 1]] * 4, 16 / 9),
  "B4_1x4": ("B4", "c", "bg", [[1, 1, 1, 1]] * 4, 16 / 9),
  "B4_1x6": ("B4", "c", "bg", [[1] * 6] * 4, 16 / 9),
  "B4_1x8": ("B4", "c", "bg", [[1] * 8] * 4, 16 / 9),
  "B3_121": ("B3", "c", "bg", [[1], [2], [1]], 2.0),
  "B3_121x2": ("B3", "c", "bg", [[1, 1], [2, 2], [1, 1]], 2.0),
  "A2_1x2": ("A2", "g", "b", [[1, 1]] * 2, 2.0),
}
name = sys.argv[1]; cs = [float(x) for x in sys.argv[2].split(',')]; seeds = [int(x) for x in sys.argv[3].split(',')]
g, t, nu, gs, kref = cfgs[name]; z, unit = geo[g]; M = modes(z); Fn = np.stack([M[x] for x in nu], 1)
net = MixNet(z, M[t], Fn, gs, unit)
k = len(z)
if net.nbits <= 12:
    f = lambda x: -net.fisher_exact([spread_refs(gg, x[j]) for j, gg in enumerate(gs)])
    r = min((minimize(f, np.random.default_rng(s).uniform(-3, 3, k), method='Nelder-Mead') for s in range(4)), key=lambda r: r.fun)
    offs = r.x; K = -r.fun
else:
    offs = 0.3 * np.arange(k); K = net.fisher_mc([spread_refs(gg, offs[j]) for j, gg in enumerate(gs)], N=40000)[0]
dl = [spread_refs(gg, offs[j]) for j, gg in enumerate(gs)]
out = []
for c in cs:
    for s in seeds:
        t0 = time.time()
        J = simulate_mix(net, dl, c, kref, R=64, Np=1024, n_burn=300, n_meas=2000, seed=s)
        out.append(dict(cfg=name, K=K, c=c, seed=s, J=J))
        print(name, "K", round(K, 4), "c", c, "seed", s, "J", round(J, 3), f"{time.time()-t0:.0f}s", flush=True)
        json.dump(out, open(f"res_t5_sim_{name}.json", "w"), indent=1)
