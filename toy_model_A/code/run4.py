import time, json, numpy as np
from multiprocessing import Pool
from toy_model import *
pi=np.pi
jobs=[]
def add(name, groups, cs, **kw):
    for c in cs:
        jobs.append((name, groups, c, kw))
add("ghz1", ghz(1), (0.5,0.55,0.6,0.65))
add("ghz2", ghz(2), (0.5,0.55,0.6,0.65))
add("ghz4", ghz(4), (0.55,0.6))
add("sep2", sep(2), (0.45,0.5,0.55))
add("sep3", sep(3), (0.45,0.5,0.55))
add("sep4", sep(4), (0.45,0.5,0.55))
add("mix(2,1)", [(2,0,1.0),(1,0,1.0)], (0.5,0.6,0.7,0.8,1.0))
add("mix(3,1)", [(3,0,1.0),(1,0,1.0)], (0.5,0.6,0.7,0.8,1.0))
add("mix(2,2)", [(2,0,1.0),(2,0,1.0)], (0.5,0.6,0.7,0.8))
add("mix(2,1,1)", [(2,0,1.0),(1,0,1.0),(1,0,1.0)], (0.5,0.6,0.7,0.8,1.0))
def work(j):
    name, groups, c, kw = j
    res=[]
    for seed in (11,12):
        r = simulate(groups, c=c, R=128, Np=768, n_burn=150, n_meas=900, seed=seed, **kw)
        res.append(r)
    return dict(name=name, c=c, mse=[r['mse'] for r in res], T=float(np.mean([r['T'] for r in res])), oor=float(np.mean([r['out_of_range'] for r in res])))
if __name__=="__main__":
    t0=time.time()
    with Pool(4) as p:
        out = p.map(work, jobs, chunksize=1)
    json.dump(out, open("res4.json","w"), indent=1)
    for o in out:
        print(f"{o['name']:12s} c={o['c']:.2f} MSE={np.mean(o['mse']):.3f} (seeds {o['mse'][0]:.3f},{o['mse'][1]:.3f}) T={o['T']:.3f} oor={o['oor']:.4f}")
    print("time", time.time()-t0)
