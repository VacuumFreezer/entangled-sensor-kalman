"""Network side with several GHZ units per cycle (network cascade): every unit is a network GHZ that is immune to the
disturbance, with weight w_u (in units of the single-qubit-node pattern), phase w_u * a * d.  Modelled as one pseudo-node."""
import numpy as np, sys, json, time
from toy5_nodes import *; from toy5_sim import *
from scipy.optimize import minimize
a = float(sys.argv[1]); ws = [int(x) for x in sys.argv[2].split(',')]; cs = [float(x) for x in sys.argv[3].split(',')]
seeds = [int(x) for x in sys.argv[4].split(',')]; tag = sys.argv[5]
n = sum(ws)
net = MixNet(np.array([0.0]), np.array([a]), np.zeros((1, 1)), [ws], [1.0])
# references: maximize Fisher information averaged over the prior of d (lock: n a sigma = 0.5), starting from 0
xg, wg = np.polynomial.hermite_e.hermegauss(15); wg = wg / wg.sum(); sig = 0.5 / (n * a)
favg = lambda x: sum(w * net.fisher_exact([x], d=sig * xx) for xx, w in zip(xg, wg))
r = minimize(lambda x: -favg(x), np.zeros(len(ws)), method='Nelder-Mead')
dl = [r.x]; K = net.fisher_exact(dl)
print("refs", np.round(r.x, 3), "K(d=0)", K, "K_avg", -r.fun, flush=True)
out = []
for c in cs:
    for s in seeds:
        J = simulate_mix(net, dl, c, n * a, R=64, Np=1024, n_burn=300, n_meas=2000, seed=s)
        out.append(dict(ws=ws, a=a, K=K, c=c, seed=s, J=J, J_times_n23=J * n ** (2 / 3)))
        print(tag, ws, "K/n^2", round(K / n ** 2 / a ** 2, 3), "c", c, "seed", s, "J", round(J, 3), "J*n^(2/3)", round(J * n ** (2 / 3), 3), flush=True)
        json.dump(out, open(f"res_t5_net_{tag}.json", "w"), indent=1)
