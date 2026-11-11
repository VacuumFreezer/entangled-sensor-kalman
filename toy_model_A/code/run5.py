import time, json, numpy as np
from multiprocessing import Pool
from toy_model import *
jobs=[]
for c in (0.4,0.5,0.6,0.7,0.8,1.0,1.2):
    jobs.append(("q1_V0.5", [(1,0.0,0.5)], c))
for c in (0.45,):
    jobs.append(("ghz1", ghz(1), c))
def work(j):
    name, groups, c = j
    res=[simulate(groups, c=c, R=128, Np=768, n_burn=150, n_meas=900, seed=s) for s in (21,22)]
    Tl, ml = lin_constrained(groups, c)
    return dict(name=name, c=c, mse=[r['mse'] for r in res], T=float(np.mean([r['T'] for r in res])), oor=float(np.mean([r['out_of_range'] for r in res])), lin=ml)
if __name__=="__main__":
    t0=time.time()
    with Pool(3) as p:
        out = p.map(work, jobs, chunksize=1)
    json.dump(out, open("res5.json","w"), indent=1)
    for o in out:
        print(f"{o['name']:10s} c={o['c']:.2f} MSE={np.mean(o['mse']):.3f} (seeds {o['mse'][0]:.3f},{o['mse'][1]:.3f}) T={o['T']:.3f} oor={o['oor']:.4f} lin={o['lin']:.3f}")
    print("lin unconstrained V=0.5:", lin_opt([(1,0.0,0.5)]))
    print("time", time.time()-t0)
