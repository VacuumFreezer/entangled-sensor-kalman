import time, json, numpy as np
from multiprocessing import Pool
from toy_gradient import simulate_sep2
jobs=[]
for rho in (0.0, 1.0, 10.0, 100.0, 1000.0, 10000.0):
    jobs.append((rho, 0.5, "A"))
    jobs.append((rho, 0.5, "B"))
def work(j):
    rho, c, pol = j
    r = [simulate_sep2(rho, c, pol, seed=s) for s in (31,32)]
    return dict(rho=rho, c=c, policy=pol, mse=[x['mse'] for x in r], T=float(np.mean([x['T'] for x in r])))
if __name__=="__main__":
    t0=time.time()
    with Pool(4) as p:
        out = p.map(work, jobs, chunksize=1)
    json.dump(out, open("res6.json","w"), indent=1)
    for o in out:
        print(f"rho={o['rho']:8.1f} policy {o['policy']} c={o['c']}: MSE_g={np.mean(o['mse']):.3f} (seeds {o['mse'][0]:.3f},{o['mse'][1]:.3f}) T={o['T']:.3f}")
    print("time", time.time()-t0)
