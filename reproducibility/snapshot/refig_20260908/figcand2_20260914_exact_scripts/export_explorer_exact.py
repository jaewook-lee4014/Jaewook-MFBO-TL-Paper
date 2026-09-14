# -*- coding: utf-8 -*-
"""Export per-seed best-so-far change points for the interactive figure explorer (13 pools x 12 models x seeds 42-81).
Reuses the loading rules of prep_candidates2.py (largest horizon wins; no NARGP; merged FET). Output: explorer_data.json"""
import json, os, sys, numpy as np, pandas as pd
sys.argv = ["x"]
os.environ["OUT"] = "/tmp/explorer_tmp"
src = open("/mnt/data/jaewook_mfbo/MFBO-TL-Paper/experiments/refig_20260908/prep_candidates2.py").read()
# execute only the loading part (everything before the metrics section)
head = src.split("S = {\"meta\"")[0]
ns = {}
exec(compile(head, "prep_head", "exec"), ns)
cells, POOLS, ORDER, ABBR, B_ORIG, B_MAX, RANGE, CSV, REFIG, TOP1 = (ns[k] for k in ["cells", "POOLS", "ORDER", "ABBR", "B_ORIG", "B_MAX", "RANGE", "CSV", "REFIG", "TOP1"])
GP, TL = ns["GP"], ns["TL"]

# top-k % thresholds per pool from the HF column (regret = f_best - f, in the minimisation convention used by the runs)
def thresholds(b):
    d = pd.read_csv(f"{REFIG}/figrepo/data/{CSV[b]}", usecols=["HF"]).HF.values.astype(float)
    # regret of every candidate: we do not know the sign convention here, so use the top-1 % threshold from the runs to orient
    r1 = np.sort(np.max(d) - d); r2 = np.sort(d - np.min(d))      # maximise / minimise conventions
    k1 = max(1, int(np.ceil(0.01 * len(d)))) - 1
    cand = r1 if abs(r1[k1] - TOP1[b]) <= abs(r2[k1] - TOP1[b]) else r2
    out = {}
    for k in [0.1, 0.2, 0.5, 1, 2, 5, 10, 20]:
        idx = max(1, int(np.ceil(k / 100 * len(d)))) - 1; out[str(k)] = float(cand[idx])
    return out, int(len(d))

data = {"pools": {}, "models": ORDER, "abbr": ABBR, "gp": GP, "tl": TL}
for b in POOLS:
    thr, n = thresholds(b)
    P = {"B": B_ORIG[b], "Bmax": B_MAX[b], "range": RANGE[b], "n_pool": n, "thr": thr, "series": {}}
    for m in ORDER:
        rows = {}
        for s in range(42, 82):
            if (b, m, s) not in cells: continue
            hz, bu, re_ = cells[(b, m, s)]
            # best-so-far change points: (budget, regret) where the regret drops
            pts = [[float(bu[0]), float(re_[0])]]
            for x, y in zip(bu[1:], re_[1:]):
                if y < pts[-1][1] - 1e-12: pts.append([float(x), float(y)])
            rows[str(s)] = {"hz": float(hz), "pts": [[float(x), float(y)] for x, y in pts]}
        if rows: P["series"][m] = rows
    data["pools"][b] = P
out = "/mnt/data/jaewook_mfbo/MFBO-TL-Paper/experiments/refig_20260908/figcand2_20260914_exact/explorer_data.json"
json.dump(data, open(out, "w"), separators=(",", ":"))
print("wrote", out, os.path.getsize(out) // 1024, "KB")
