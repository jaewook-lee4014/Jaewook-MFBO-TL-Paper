#!/usr/bin/env python
"""Build figrepo/results/grid5tl/ = the public GP grid rows (MFGP/SparseMFGP/DKL, taken
verbatim from figrepo/results/grid/cells) + the five retained TL classes from
results_grid_5tl/blr_replace__hf_argmin/cells.  Mirrors collect.py:185-203."""
import glob, os, sys
from pathlib import Path
import pandas as pd

R = Path("/mnt/data/jaewook_mfbo/MFBO-TL-Paper/experiments/refig_20260908")
SRC = R / "figrepo" / "results" / "grid"
OUT = R / "figrepo" / "results" / os.environ.get("GRID5TL_OUT", "grid5tl")
TL = os.environ.get("TL5", "DNGOJoint,TwoStageJoint,DNGOGradient,SoftParameterSharing,DomainAdaptationMMD").split(",")
GP = ["MFGP", "SparseMFGP", "DKL"]
COLS = ["benchmark", "model", "seed", "final_regret", "auc"]

(OUT / "cells").mkdir(parents=True, exist_ok=True)
man = pd.read_csv(SRC / "grid_manifest.csv"); man.to_csv(OUT / "grid_manifest.csv", index=False)
new = pd.concat([pd.read_csv(f) for f in glob.glob(str(R / "results_grid_5tl" / "blr_replace__hf_argmin" / "cells" / "summary_*.csv"))],
                ignore_index=True)[COLS].drop_duplicates(["benchmark", "model", "seed"])
short = []
for cid in man.cell_id:
    g = pd.read_csv(SRC / "cells" / f"summary_{cid}.csv")
    g = g[g.model.isin(GP)][COLS]
    t = new[(new.benchmark == cid) & (new.model.isin(TL))][COLS]
    for m in TL:
        k = int(t[t.model == m].seed.nunique())
        if k < 10: short.append(f"{cid}/{m}:{k}")
    pd.concat([g, t], ignore_index=True).to_csv(OUT / "cells" / f"summary_{cid}.csv", index=False)
print(f"[grid5tl] cells {len(man)}; TL rows {len(new)}; models {sorted(new.model.unique())}")
print(f"[grid5tl] cell/model below 10 seeds: {len(short)}", " ".join(short[:40]))
