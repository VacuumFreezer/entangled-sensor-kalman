"""Summarize toy 5: information ratios network / local-only, with and without a GHZ-size cap."""
import json, numpy as np
KU = {}
for f, n in (("res_t5_KU_A2.json", "A2"), ("res_t5_KU_B4.json", "B4"), ("res_t5_KU_B3.json", "B3"), ("res_t5_KU_A4.json", "A4")):
    d = json.load(open(f))[n]; KU[n] = [d[str(m)]["K"] for m in range(1, 9)]
track = {"A2": 2.0, "A4": 20 / 9, "B4": 64 / 81, "B3": 2 / 3}       # per-qubit information when every mode is tracked
net = {"A2": 4.0, "A4": 64 / 9, "B4": 256 / 81}                       # network GHZ information per n^2
out = {"KU": KU, "track": track}
print("fraction of tracked-all information kept by m unentangled qubits per node (random disturbance)")
for c in KU: print(c, [round(KU[c][m - 1] / (m * track[c]), 3) for m in range(1, 9)])
# no cap: local best = max_m (n/m)^2 K_U(m)  (n divisible by m)
print("\nno GHZ-size cap, large n: local best per n^2, network per n^2, ratio")
for c in net:
    best = max((KU[c][m - 1] / m ** 2, m) for m in range(1, 9))
    print(c, round(best[0], 4), "m*", best[1], round(net[c], 3), "ratio", round(net[c] / best[0], 1))
# cap G*: n = r G*; local: groups of size G*/s, s=1,2,3,4, m = r*s units per node -> (1/s^2) K_U(r s) G*^2
#          network: rails of G* qubits with weights proportional to |f_j| (optimal rails) -> total = r * track * G*^2
#          (for A2 and B4 equal-split rails already reach this; for A4 rails on the outer and on the inner pair)
print("\nGHZ size capped at G*, node holds n = r G* qubits: ratio network/local")
cap = {}
for c in net:
    row = {}
    for r in (1, 2, 4, 8):
        loc = max(KU[c][r * s - 1] / s ** 2 for s in (1, 2, 3, 4) if r * s <= 8)
        nw = r * track[c]
        row[r] = nw / loc
    cap[c] = row; print(c, {r: round(v, 2) for r, v in row.items()})
out["cap_ratio"] = cap
json.dump(out, open("res_t5_summary.json", "w"), indent=1)
