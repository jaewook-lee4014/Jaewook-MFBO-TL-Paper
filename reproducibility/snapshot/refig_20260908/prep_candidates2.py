# -*- coding: utf-8 -*-
"""Publication-style candidate figures, round 2 (2026-09-11 03:40), after the user's figure decisions:
13 benchmarks (9 original + ExptGap-PBE, Elastic-CHGNet/SevenNet/MatterSim treated as ordinary benchmarks), 40 seeds where available,
no NARGP, no reference policies, no HF-only GP, Curriculum/KD/PL merged as 'Feature-extraction transfer' (FET),
Fig. 2 cut at 30 for Park x2 / FreeSolv / Polarizability. Metrics: M1 budget to exact optimum, M2 budget to top-1 %, M3 regret at B / range,
M4 normalised anytime AUC to B, M5 success rate. Runs on the VM; writes OUT/*.png + cand2.json.
"""
import glob, os, re, json, sys
import numpy as np, pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch

R = "/mnt/data/jaewook_mfbo/MFBO-TL-Paper/experiments"
REFIG = f"{R}/refig_20260908"; EXT = f"{R}/ext_chem_20260909"
OUT = os.environ.get("OUT", f"{REFIG}/figcand2_20260911"); os.makedirs(OUT, exist_ok=True)

POOLS = ["Branin-Fav", "Branin-Unfav", "Park-Fav", "Park-Unfav", "COFs", "FreeSolv", "Polarizability", "HOPV15", "Matbench-Gap",
         "ExptGap-PBE", "Elastic-CHGNet", "Elastic-SevenNet", "Elastic-MatterSim"]
NEW = POOLS[9:]
B_ORIG = {"Branin-Fav": 50, "Branin-Unfav": 50, "Park-Fav": 50, "Park-Unfav": 50, "COFs": 30, "FreeSolv": 50, "Polarizability": 30, "HOPV15": 30, "Matbench-Gap": 20,
          "ExptGap-PBE": 30, "Elastic-CHGNet": 30, "Elastic-SevenNet": 30, "Elastic-MatterSim": 30}   # 2026-09-13: four large pools evaluated at 30
B_MAX = dict(B_ORIG); B_MAX.update({"FreeSolv": 100, "Polarizability": 60, "HOPV15": 45, "Matbench-Gap": 100})
XCUT = dict(B_MAX); XCUT.update({"Park-Fav": 30, "Park-Unfav": 30, "FreeSolv": 30, "Polarizability": 30})   # Fig. 2 window (user: cut at 30)
TOP1 = {"Branin-Fav": 0.4947, "Branin-Unfav": 0.4947, "Park-Fav": 4.082e-09, "Park-Unfav": 4.082e-09, "COFs": 3.542, "FreeSolv": 0.5, "Polarizability": 0.2529,
        "HOPV15": 2.13, "Matbench-Gap": 0.04, "ExptGap-PBE": 0.050, "Elastic-CHGNet": 338.0, "Elastic-SevenNet": 199.0, "Elastic-MatterSim": 338.0}
CSV = {"COFs": "cofs.csv", "FreeSolv": "freesolv.csv", "Polarizability": "polarizability.csv", "HOPV15": "hopv15.csv", "Matbench-Gap": "matbench_gap.csv",
       "Branin-Fav": "synthetic_branin_fav.csv", "Branin-Unfav": "synthetic_branin_unfav.csv", "Park-Fav": "synthetic_park_fav.csv", "Park-Unfav": "synthetic_park_unfav.csv",
       "ExptGap-PBE": "expt_gap_pbe.csv", "Elastic-CHGNet": "elastic_chgnet_shear.csv", "Elastic-SevenNet": "elastic_sevennet_shear.csv", "Elastic-MatterSim": "elastic_mattersim_shear.csv"}
RANGE = {}
for b, f in CSV.items():
    d = pd.read_csv(f"{REFIG}/figrepo/data/{f}", usecols=["HF"]); RANGE[b] = float(d.HF.max() - d.HF.min())
SEEDS = list(range(42, 82))
SHORT = {"Branin-Fav": "Branin-Fav", "Branin-Unfav": "Branin-Unfav", "Park-Fav": "Park-Fav", "Park-Unfav": "Park-Unfav", "COFs": "COFs", "FreeSolv": "FreeSolv",
         "Polarizability": "Polarizability", "HOPV15": "HOPV15", "Matbench-Gap": "Matbench-gap", "ExptGap-PBE": "ExptGap-PBE", "Elastic-CHGNet": "Elastic-CHGNet",
         "Elastic-SevenNet": "Elastic-SevenNet", "Elastic-MatterSim": "Elastic-MatterSim"}

MERGED = "Feature-extraction transfer"
RENAME = {"DNGOGradient": "End-to-End Joint", "DNGO-Gradient": "End-to-End Joint", "DNGOJoint": "Stop-Gradient Joint", "DNGO-Joint": "Stop-Gradient Joint",
          "TwoStageJoint": "Pretrain-then-Joint", "Two-Stage Joint": "Pretrain-then-Joint", "DomainAdaptationMMD": "Domain Adaptation (MMD)", "Domain Adaptation (MMD)": "Domain Adaptation (MMD)",
          "SoftParameterSharing": "Soft Parameter Sharing", "Soft Parameter Sharing": "Soft Parameter Sharing",
          "KnowledgeDistillation": MERGED, "Knowledge Distillation": MERGED, "PseudoLabeling": MERGED, "Pseudo-Labeling": MERGED, "Pseudo-Labelling": MERGED, "Curriculum": MERGED,
          "Sequential": "Sequential", "Progressive": "Progressive", "Adapter": "Adapter",
          "MFGP": "MFGP", "SparseMFGP": "Sparse MFGP", "Sparse MFGP": "Sparse MFGP", "DKL": "DKL", "DKL Multi-Fidelity": "DKL"}
GP = ["MFGP", "Sparse MFGP", "DKL"]
TL = ["Sequential", MERGED, "End-to-End Joint", "Progressive", "Pretrain-then-Joint", "Stop-Gradient Joint", "Domain Adaptation (MMD)", "Soft Parameter Sharing", "Adapter"]
ORDER = GP + TL
ABBR = {"MFGP": "MFGP", "Sparse MFGP": "SV-MFGP", "DKL": "DKL", "Sequential": "Seq", MERGED: "FET", "End-to-End Joint": "E2E", "Progressive": "Prog", "Pretrain-then-Joint": "PtJ",
        "Stop-Gradient Joint": "SGJ", "Domain Adaptation (MMD)": "MMD", "Soft Parameter Sharing": "SPS", "Adapter": "Adpt"}
LINECOL = {"MFGP": "#1f3a93", "Sparse MFGP": "#1b9e77", "DKL": "#5aa9e6", "Sequential": "#7fb3e6", MERGED: "#e6a23c", "End-to-End Joint": "#5cb85c", "Progressive": "#f28e8e",
           "Pretrain-then-Joint": "#8e7cc3", "Stop-Gradient Joint": "#b5651d", "Domain Adaptation (MMD)": "#9e9e9e", "Soft Parameter Sharing": "#c9b037", "Adapter": "#d62728"}
GP_FILL, GP_EDGE, GP_BEST = "#F5B49A", "#C0654A", "#D9734F"
TL_FILL, TL_EDGE, TL_BEST = "#A9CBEE", "#3B6FB6", "#4C86D6"

def canon(m): return RENAME.get(m, None)

def gather(files):
    out = []
    for f in files:
        try: d = pd.read_csv(f)
        except Exception: continue
        if not {"benchmark", "model", "seed", "budget", "regret"} <= set(d.columns): continue
        d["model"] = d["model"].map(canon); d = d[d.model.notna()]
        out.append(d[["benchmark", "model", "seed", "budget", "regret"]])
    return pd.concat(out, ignore_index=True) if out else pd.DataFrame(columns=["benchmark", "model", "seed", "budget", "regret"])

SRC = {
    "orig42": [f"{REFIG}/figrepo/results/{s}/results_trajectory.csv" for s in ["main_9bench", "extra_baselines", "gpfamily_newbench"]],
    "conf62_tl": glob.glob(f"{REFIG}/results_conf/blr_replace__hf_argmin/cells/traj_*.csv"),
    "conf62_gp": glob.glob(f"{REFIG}/results_gp_conf/gp_ei/cells/traj_*.csv"),
    "ext": glob.glob(f"{EXT}/results/*/cells/traj_*.csv") + glob.glob(f"{EXT}/results_slurm/*/cells/traj_*.csv"),
    "ext100": glob.glob(f"{EXT}/results_ext100/*/cells/traj_*.csv"),
    "confirm": glob.glob(f"{REFIG}/results_confirm/**/traj_*.csv", recursive=True) + glob.glob(f"{REFIG}/results_confirm_gp/**/traj_*.csv", recursive=True),
    "confirm_ext": glob.glob(f"{EXT}/results_confirm_ext/*/cells/traj_*.csv"),   # 2026-09-13 re-runs of the four large pools (TL to 60, GP to >= 31); largest horizon wins over the B = 20 runs
}
cells = {}
for src, files in SRC.items():
    d = gather([f for f in files if os.path.exists(f)])
    print(src, len(files), "files", len(d), "rows", file=sys.stderr)
    for (b, m, s), g in d.groupby(["benchmark", "model", "seed"]):
        if b not in POOLS or s not in SEEDS: continue
        g = g.sort_values("budget"); hz = float(g.budget.max())
        cur = cells.get((b, m, s))
        if cur is None or hz > cur[0] + 1e-9: cells[(b, m, s)] = (hz, g.budget.values.astype(float), g.regret.values.astype(float))

def bsf(bu, re_, grid):
    idx = np.searchsorted(bu, grid, side="right") - 1
    return np.where(idx >= 0, re_[np.clip(idx, 0, len(re_) - 1)], re_[0])

def reach_cost(bu, re_, thr, cap):
    ok = np.where(re_ <= thr + 1e-12)[0]
    if len(ok) == 0 or bu[ok[0]] > cap: return cap, False
    return float(bu[ok[0]]), True

S = {"meta": dict(B_orig=B_ORIG, B_max=B_MAX, top1=TOP1, range=RANGE, merged=MERGED, abbr=ABBR), "pools": {}}
for b in POOLS:
    Bm, B0 = B_MAX[b], B_ORIG[b]; grid = np.round(np.arange(0.0, Bm + 1e-9, 0.25), 3)
    P = {"grid": grid.tolist(), "models": {}}
    for m in ORDER:
        seeds = [s for s in SEEDS if (b, m, s) in cells]
        if not seeds: continue
        A = []; hzs = []; rows = []
        for s in seeds:
            hz, bu, re_ = cells[(b, m, s)]; hzs.append(hz)
            c = bsf(bu, re_, grid); c = np.where(grid > hz + 0.26, np.nan, c); A.append(c)
            r = dict(seed=s, hz=hz, regB=float(bsf(bu, re_, np.array([B0]))[0]), regBm=float(c[-1]) if not np.isnan(c[-1]) else None)
            # nAUC to B (original): mean over grid points <= B0 of regret / range
            cB = c[grid <= B0 + 1e-9]; r["nauc"] = float(np.nanmean(cB) / RANGE[b]) if not np.isnan(cB).any() else None
            for tgt, thr in [("opt", 1e-9), ("top1", TOP1[b])]:
                cost, ok = reach_cost(bu, re_, thr, Bm); short = (hz + 0.26 < Bm) and not ok
                r[f"{tgt}_cost"] = cost; r[f"{tgt}_ok"] = ok; r[f"{tgt}_short"] = short
                cost0, ok0 = reach_cost(bu, re_, thr, B0); r[f"{tgt}_cost0"] = cost0; r[f"{tgt}_ok0"] = ok0
            rows.append(r)
        A = np.array(A); n_at = np.sum(~np.isnan(A), axis=0)
        with np.errstate(all="ignore"):
            mean = np.where(n_at > 0, np.nanmean(A, axis=0), np.nan); se = np.where(n_at > 1, np.nanstd(A, axis=0, ddof=1) / np.sqrt(np.maximum(n_at, 1)), np.nan)
            valid = ~np.isnan(A)
            fr_opt = np.where(n_at > 0, np.sum((A <= 1e-9) & valid, axis=0) / np.maximum(n_at, 1), np.nan)
            fr_top1 = np.where(n_at > 0, np.sum((A <= TOP1[b] + 1e-12) & valid, axis=0) / np.maximum(n_at, 1), np.nan)
        df = pd.DataFrame(rows)
        def stat(col, mask=None):
            x = df[col] if mask is None else df.loc[mask, col]; x = x.dropna().astype(float)
            return dict(mean=float(x.mean()) if len(x) else None, se=float(x.std(ddof=1) / np.sqrt(len(x))) if len(x) > 1 else 0.0, n=int(len(x)))
        M = dict(n=len(seeds), horizon_min=float(min(hzs)), horizon_max=float(max(hzs)),
                 mean=[None if np.isnan(v) else float(v) for v in mean], se=[None if np.isnan(v) else float(v) for v in se], n_at=n_at.tolist(),
                 fr_opt=[None if np.isnan(v) else float(v) for v in fr_opt], fr_top1=[None if np.isnan(v) else float(v) for v in fr_top1],
                 regB=stat("regB"), nauc=stat("nauc"))
        M["regB"]["norm"] = M["regB"]["mean"] / RANGE[b] if M["regB"]["mean"] is not None else None
        for tgt in ["opt", "top1"]:
            full = ~df[f"{tgt}_short"] if df[f"{tgt}_short"].any() else pd.Series(True, index=df.index)
            if df[f"{tgt}_short"].any(): full = df.hz + 0.26 >= Bm      # any seed ended early unreached -> use only full-horizon seeds
            st = stat(f"{tgt}_cost", full); st["reach"] = float(df.loc[full, f"{tgt}_ok"].mean()) if full.any() else None
            st0 = stat(f"{tgt}_cost0"); st0["reach"] = float(df[f"{tgt}_ok0"].mean())
            M[f"{tgt}_max"] = st; M[f"{tgt}_orig"] = st0
        P["models"][m] = M
    S["pools"][b] = P
json.dump(S, open(f"{OUT}/cand2.json", "w"))

# coverage
cov = [(b, ABBR[m], S["pools"][b]["models"][m]["n"], S["pools"][b]["models"][m]["horizon_min"], S["pools"][b]["models"][m]["horizon_max"]) for b in POOLS for m in ORDER if m in S["pools"][b]["models"]]
pd.DataFrame(cov, columns=["pool", "model", "n", "hz_min", "hz_max"]).to_csv(f"{OUT}/coverage2.csv", index=False)

# ---------------------------------------------------------------- helpers for figures
LET = "bcdefghijklmnop"
def fam(m): return "GP" if m in GP else "TL"

def panel_bars(ax, b, key, value_fn, err_fn, label_fn=None, xmax=None, best_low=True, title=None, xlabel=None):
    """horizontal bars sorted with the largest value on top; best-of-family highlighted."""
    P = S["pools"][b]["models"]
    items = [(m, value_fn(P[m]), err_fn(P[m])) for m in ORDER if m in P and value_fn(P[m]) is not None]
    if not items: ax.text(0.5, 0.5, "n/a", ha="center", transform=ax.transAxes); return
    items.sort(key=lambda x: x[1])                       # smallest first (drawn at the bottom) -> largest on top
    bestTL = min([x for x in items if fam(x[0]) == "TL"], key=lambda x: x[1])[0] if any(fam(x[0]) == "TL" for x in items) else None
    bestGP = min([x for x in items if fam(x[0]) == "GP"], key=lambda x: x[1])[0] if any(fam(x[0]) == "GP" for x in items) else None
    for j, (m, v, e) in enumerate(items):
        f = fam(m); best = (m == bestTL) or (m == bestGP)
        fill = (TL_BEST if best else TL_FILL) if f == "TL" else (GP_BEST if best else GP_FILL)
        edge = TL_EDGE if f == "TL" else GP_EDGE
        ax.barh(j, v, xerr=e if e else None, color=fill, edgecolor=edge, linewidth=0.6, height=0.74, error_kw=dict(lw=0.7, ecolor="#333"))
        if label_fn:
            lab = label_fn(P[m])
            if lab: ax.text(v + (e or 0) + (xmax or max(x[1] for x in items)) * 0.02, j, lab, va="center", fontsize=6.2, color="#333")
    ax.set_yticks(range(len(items))); ax.set_yticklabels([ABBR[x[0]] for x in items], fontsize=7)
    ax.tick_params(axis="x", labelsize=7); ax.grid(axis="x", alpha=.25); ax.set_axisbelow(True)
    if xmax: ax.set_xlim(0, xmax)
    for sp in ["top", "right"]: ax.spines[sp].set_visible(False)
    if title: ax.set_title(title, loc="left", fontsize=8.5, fontweight="bold")
    if xlabel: ax.set_xlabel(xlabel, fontsize=7.5)

def rank_panel(ax, key_fn, title, lower_better=True):
    """average rank over the 13 pools (descriptive; ties -> average rank)."""
    from scipy.stats import rankdata
    ranks = {m: [] for m in ORDER}
    for b in POOLS:
        P = S["pools"][b]["models"]; ms = [m for m in ORDER if m in P and key_fn(P[m]) is not None]
        vals = np.array([key_fn(P[m]) for m in ms]); rk = rankdata(vals if lower_better else -vals)
        for m, r in zip(ms, rk): ranks[m].append(r)
    items = [(m, float(np.mean(v)), float(np.std(v, ddof=1) / np.sqrt(len(v))) if len(v) > 1 else 0.0) for m, v in ranks.items() if v]
    items.sort(key=lambda x: x[1])
    for j, (m, v, e) in enumerate(items):
        f = fam(m); fill = TL_FILL if f == "TL" else GP_FILL; edge = TL_EDGE if f == "TL" else GP_EDGE
        ax.barh(j, v, xerr=e, color=fill, edgecolor=edge, linewidth=0.6, height=0.74, error_kw=dict(lw=0.7, ecolor="#333"))
    ax.set_yticks(range(len(items))); ax.set_yticklabels([ABBR[x[0]] for x in items], fontsize=7); ax.tick_params(axis="x", labelsize=7)
    ax.grid(axis="x", alpha=.25); ax.set_axisbelow(True); ax.set_title(title, loc="left", fontsize=8.5, fontweight="bold"); ax.set_xlabel("average rank (13 benchmarks)", fontsize=7.5)
    for sp in ["top", "right"]: ax.spines[sp].set_visible(False)
    return items

def legend_ax(ax, extra=""):
    ax.axis("off")
    h = [Patch(facecolor=TL_BEST, edgecolor=TL_EDGE, label="best TL surrogate"), Patch(facecolor=TL_FILL, edgecolor=TL_EDGE, label="TL surrogates"),
         Patch(facecolor=GP_BEST, edgecolor=GP_EDGE, label="best GP"), Patch(facecolor=GP_FILL, edgecolor=GP_EDGE, label="GP family")]
    ax.legend(handles=h, loc="upper left", fontsize=7.5, frameon=False, title=extra, title_fontsize=7)
    ax.text(0, 0.35, "TL: Seq = Sequential · FET = Feature-extraction transfer · E2E = End-to-End Joint\nProg = Progressive · PtJ = Pretrain-then-Joint · SGJ = Stop-Gradient Joint\nMMD = Domain Adaptation (MMD) · SPS = Soft Parameter Sharing · Adpt = Adapter\nGP: MFGP = baseline MFGP · SV-MFGP = sparse variational MFGP · DKL = deep-kernel GP",
            fontsize=6.3, va="top", transform=ax.transAxes, color="#333")

def grid_fig(nrows=3, ncols=5, w=15, h=9.4):
    fig, axes = plt.subplots(nrows, ncols, figsize=(w, h)); return fig, axes.ravel()

# ---------------------------------------------------------------- G1: budget to exact optimum (9 pools) + rank + legend
def fig_G1():
    fig, ax = grid_fig(2, 5, 15, 6.4)
    p9 = POOLS[:9]
    for i, b in enumerate(p9):
        panel_bars(ax[i], b, "opt_max", lambda M: M["opt_max"]["mean"], lambda M: M["opt_max"]["se"],
                   label_fn=lambda M: (f'{M["opt_max"]["reach"]:.2f}' if M["opt_max"]["reach"] is not None and M["opt_max"]["reach"] < 0.995 else "") + (f' n={M["opt_max"]["n"]}' if M["opt_max"]["n"] < 36 else ""),
                   xmax=B_MAX[b] * 1.25, title=f"{LET[i]}  {SHORT[b]} (B = {B_MAX[b]})", xlabel="HF budget to optimum" if i >= 4 else None)
        ax[i].axvline(B_MAX[b], color="k", lw=.6, ls="--", alpha=.6)
    # note on the 4 large pools
    ax[9].axis("off"); ax[9].text(0, 0.95, "Budget to the exact optimum is not defined\non the four large pools (ExptGap-PBE,\nElastic-CHGNet/SevenNet/MatterSim):\nno surrogate reaches it within B = 20.\nSee the top-1 % version (G2).", fontsize=7.5, va="top", transform=ax[9].transAxes)
    legend_ax(ax[9]) if False else None
    fig.suptitle("G1 · HF budget to the exact optimum (mean ± s.e. over seeds; label = fraction of seeds that reach it; bars censored at B)", fontsize=9)
    fig.tight_layout(rect=(0, 0, 1, 0.96)); fig.savefig(f"{OUT}/G1_budget_to_optimum.png", dpi=130); plt.close(fig)

# ---------------------------------------------------------------- G2: budget to top-1 % (13 pools) + rank + legend
def fig_G2():
    fig, ax = grid_fig()
    for i, b in enumerate(POOLS):
        panel_bars(ax[i], b, "top1_max", lambda M: M["top1_max"]["mean"], lambda M: M["top1_max"]["se"],
                   label_fn=lambda M: (f'{M["top1_max"]["reach"]:.2f}' if M["top1_max"]["reach"] is not None and M["top1_max"]["reach"] < 0.995 else ""),
                   xmax=B_MAX[b] * 1.25, title=f"{LET[i]}  {SHORT[b]} (B = {B_MAX[b]})", xlabel="HF budget to pool top 1 %" if i >= 10 else None)
        ax[i].axvline(B_MAX[b], color="k", lw=.6, ls="--", alpha=.6)
    rank_panel(ax[13], lambda M: M["top1_max"]["mean"], f"{LET[13]}  Average rank")
    legend_ax(ax[14])
    fig.suptitle("G2 · HF budget to enter the pool top 1 % (mean ± s.e.; label = fraction of seeds that reach it; censored at B)", fontsize=9)
    fig.tight_layout(rect=(0, 0, 1, 0.96)); fig.savefig(f"{OUT}/G2_budget_to_top1.png", dpi=130); plt.close(fig)

# ---------------------------------------------------------------- G3: normalised anytime AUC to B (13 pools)
def fig_G3():
    fig, ax = grid_fig()
    for i, b in enumerate(POOLS):
        panel_bars(ax[i], b, "nauc", lambda M: M["nauc"]["mean"], lambda M: M["nauc"]["se"], title=f"{LET[i]}  {SHORT[b]} (B = {B_ORIG[b]})",
                   xlabel="normalised anytime regret (AUC / B)" if i >= 10 else None)
    rank_panel(ax[13], lambda M: M["nauc"]["mean"], f"{LET[13]}  Average rank")
    legend_ax(ax[14])
    fig.suptitle("G3 · Anytime performance: mean regret over the budget window, normalised by the pool range (lower is better; mean ± s.e.)", fontsize=9)
    fig.tight_layout(rect=(0, 0, 1, 0.96)); fig.savefig(f"{OUT}/G3_anytime_auc.png", dpi=130); plt.close(fig)

# ---------------------------------------------------------------- G4: regret at B / range (13 pools) - the old Fig 1 look
def fig_G4():
    fig, ax = grid_fig()
    for i, b in enumerate(POOLS):
        panel_bars(ax[i], b, "regB", lambda M: M["regB"]["norm"], lambda M: M["regB"]["se"] / RANGE[b], title=f"{LET[i]}  {SHORT[b]} (B = {B_ORIG[b]})",
                   xlabel="regret at B / pool range" if i >= 10 else None)
    rank_panel(ax[13], lambda M: M["regB"]["norm"], f"{LET[13]}  Average rank")
    legend_ax(ax[14])
    fig.suptitle("G4 · Simple regret at the original budget B, normalised by the pool range (mean ± s.e.)", fontsize=9)
    fig.tight_layout(rect=(0, 0, 1, 0.96)); fig.savefig(f"{OUT}/G4_regret_at_B.png", dpi=130); plt.close(fig)

# ---------------------------------------------------------------- G5: success rate at B_max (exact optimum for 9, top-1 % for the 4 large pools)
def fig_G5():
    fig, ax = grid_fig()
    for i, b in enumerate(POOLS):
        key = "top1_max" if b in NEW else "opt_max"
        panel_bars(ax[i], b, key, lambda M, k=key: (M[k]["reach"] if M[k]["reach"] is not None else None), lambda M: 0.0,
                   xmax=1.15, title=f"{LET[i]}  {SHORT[b]} ({'top 1 %' if b in NEW else 'optimum'}, B = {B_MAX[b]})", xlabel="fraction of seeds" if i >= 10 else None, best_low=False)
    ax[13].axis("off"); ax[13].text(0, 0.95, "Success rate = share of seeds that reach the target\nwithin the budget. Target = exact optimum on the nine\noriginal pools; pool top 1 % on the four large pools\n(no surrogate reaches their optimum within B = 20).\nBars sorted with the largest on top: here larger is better.", fontsize=7.5, va="top", transform=ax[13].transAxes)
    legend_ax(ax[14])
    fig.suptitle("G5 · Success rate within the budget (larger is better)", fontsize=9)
    fig.tight_layout(rect=(0, 0, 1, 0.96)); fig.savefig(f"{OUT}/G5_success_rate.png", dpi=130); plt.close(fig)

# ---------------------------------------------------------------- G6: reach-fraction curves (exact optimum; top-1 % on the 4 large pools), no refs
def fig_G6():
    fig, ax = grid_fig()
    for i, b in enumerate(POOLS):
        P = S["pools"][b]["models"]; grid = np.array(S["pools"][b]["grid"]); key = "fr_top1" if b in NEW else "fr_opt"
        for m in ORDER:
            if m not in P: continue
            y = np.array([np.nan if v is None else v for v in P[m][key]]); y[np.array(P[m]["n_at"]) < 10] = np.nan
            ax[i].plot(grid, y, "-" if fam(m) == "GP" else "--", lw=1.8 if fam(m) == "GP" else 1.2, color=LINECOL[m], label=ABBR[m])
        ax[i].set_ylim(-0.02, 1.02); ax[i].set_title(f"{LET[i]}  {SHORT[b]} ({'top 1 %' if b in NEW else 'optimum'})", loc="left", fontsize=8.5, fontweight="bold")
        ax[i].axvline(B_ORIG[b], color="k", lw=.6, ls=":", alpha=.5); ax[i].grid(alpha=.25); ax[i].tick_params(labelsize=7)
        if i >= 10: ax[i].set_xlabel("budget (HF-equivalent cost)", fontsize=7.5)
        if i % 5 == 0: ax[i].set_ylabel("fraction of seeds at target", fontsize=7.5)
    ax[13].axis("off"); ax[14].axis("off")
    h, l = ax[0].get_legend_handles_labels(); ax[13].legend(h, l, loc="upper left", ncol=2, fontsize=7, frameon=False, title="GP solid · TL dashed", title_fontsize=7)
    fig.suptitle("G6 · Fraction of seeds that have reached the target vs budget (dotted vertical line = original B)", fontsize=9)
    fig.tight_layout(rect=(0, 0, 1, 0.96)); fig.savefig(f"{OUT}/G6_reach_curves.png", dpi=130); plt.close(fig)

# ---------------------------------------------------------------- G7: dumbbell summaries (best TL vs best GP)
def best_pair(b, value_fn):
    P = S["pools"][b]["models"]
    tl = [(m, value_fn(P[m])) for m in TL if m in P and value_fn(P[m]) is not None]; gp = [(m, value_fn(P[m])) for m in GP if m in P and value_fn(P[m]) is not None]
    if not tl or not gp: return None
    return min(tl, key=lambda x: x[1]), min(gp, key=lambda x: x[1])

def fig_G7():
    fig, axes = plt.subplots(1, 3, figsize=(15, 4.6))
    specs = [("HF budget to optimum (9 pools, censored at B)", lambda M: M["opt_max"]["mean"], POOLS[:9], "ratio"),
             ("HF budget to pool top 1 % (13 pools)", lambda M: M["top1_max"]["mean"], POOLS, "ratio"),
             ("Anytime regret / range (13 pools)", lambda M: M["nauc"]["mean"], POOLS, "ratio")]
    for ax, (title, fn, pools, mode) in zip(axes, specs):
        rows = []
        for b in pools:
            bp = best_pair(b, fn)
            if bp is None: continue
            (mt, vt), (mg, vg) = bp; rows.append((b, mt, vt, mg, vg, vg / vt if vt > 0 else np.nan))
        rows.sort(key=lambda r: -np.log(r[5]) if np.isfinite(r[5]) else 0)
        for j, (b, mt, vt, mg, vg, ratio) in enumerate(rows):
            lo, hi = min(vt, vg), max(vt, vg)
            ax.plot([lo, hi], [j, j], color="#bbb", lw=2.2, zorder=1)
            ax.scatter([vg], [j], s=46, color=GP_BEST, edgecolor=GP_EDGE, zorder=3); ax.scatter([vt], [j], s=46, color=TL_BEST, edgecolor=TL_EDGE, zorder=3)
            txt = ("TL %.1f× faster" % ratio) if ratio > 1.02 else (("GP %.1f× faster" % (1 / ratio)) if ratio < 0.98 else "tie")
            if mode == "ratio" and "regret" in title: txt = ("TL %.0f %% lower" % (100 * (1 - vt / vg))) if ratio > 1.02 else (("GP %.0f %% lower" % (100 * (1 - vg / vt))) if ratio < 0.98 else "tie")
            ax.text(hi * 1.04 if hi > 0 else 0.01, j, f"{txt}  ({ABBR[mt]} vs {ABBR[mg]})", va="center", fontsize=6.6, color="#333")
        ax.set_yticks(range(len(rows))); ax.set_yticklabels([SHORT[r[0]] for r in rows], fontsize=7.5); ax.set_xscale("log")
        ax.set_title(title, loc="left", fontsize=8.5, fontweight="bold"); ax.grid(axis="x", alpha=.25); ax.tick_params(axis="x", labelsize=7)
        for sp in ["top", "right"]: ax.spines[sp].set_visible(False)
        ax.set_xlim(right=ax.get_xlim()[1] * 4)
    axes[0].scatter([], [], color=TL_BEST, edgecolor=TL_EDGE, label="best TL surrogate"); axes[0].scatter([], [], color=GP_BEST, edgecolor=GP_EDGE, label="best GP")
    axes[0].legend(loc="lower right", fontsize=7, frameon=False)
    fig.suptitle("G7 · Best TL surrogate vs best GP per benchmark (dumbbells; sorted by TL advantage; log axes)", fontsize=9)
    fig.tight_layout(rect=(0, 0, 1, 0.94)); fig.savefig(f"{OUT}/G7_dumbbells.png", dpi=130); plt.close(fig)

# ---------------------------------------------------------------- G8: heatmaps benchmark x TL model, log2(best GP / TL model)
def fig_G8():
    fig, axes = plt.subplots(1, 3, figsize=(15, 5.2))
    specs = [("HF budget to optimum (9 pools)", lambda M: M["opt_max"]["mean"], POOLS[:9]),
             ("HF budget to pool top 1 % (13 pools)", lambda M: M["top1_max"]["mean"], POOLS),
             ("Anytime regret / range (13 pools)", lambda M: M["nauc"]["mean"], POOLS)]
    for ax, (title, fn, pools) in zip(axes, specs):
        Z = np.full((len(pools), len(TL)), np.nan)
        for i, b in enumerate(pools):
            P = S["pools"][b]["models"]; gp = [fn(P[m]) for m in GP if m in P and fn(P[m]) is not None]
            if not gp: continue
            g = min(gp)
            for j, m in enumerate(TL):
                if m in P and fn(P[m]) not in (None, 0): Z[i, j] = np.log2(g / fn(P[m])) if fn(P[m]) > 0 else np.nan
        v = np.nanmax(np.abs(Z)) if np.isfinite(Z).any() else 1
        im = ax.imshow(Z, cmap="RdBu", vmin=-v, vmax=v, aspect="auto")
        ax.set_xticks(range(len(TL))); ax.set_xticklabels([ABBR[m] for m in TL], fontsize=7, rotation=45, ha="right"); ax.set_yticks(range(len(pools))); ax.set_yticklabels([SHORT[b] for b in pools], fontsize=7)
        for i in range(len(pools)):
            for j in range(len(TL)):
                if np.isfinite(Z[i, j]): ax.text(j, i, f"{2**Z[i,j]:.1f}×" if abs(Z[i, j]) >= 0.07 else "≈1", ha="center", va="center", fontsize=6, color="white" if abs(Z[i, j]) > v * 0.55 else "#222")
        ax.set_title(title, loc="left", fontsize=8.5, fontweight="bold")
        cb = fig.colorbar(im, ax=ax, fraction=0.04, pad=0.02); cb.set_label("log2(best GP / TL)   blue = TL better", fontsize=7); cb.ax.tick_params(labelsize=6.5)
    fig.suptitle("G8 · Each TL surrogate against the strongest GP on that benchmark (cell = GP value / TL value; >1 means the TL surrogate needs less budget / lower regret)", fontsize=9)
    fig.tight_layout(rect=(0, 0, 1, 0.94)); fig.savefig(f"{OUT}/G8_heatmaps.png", dpi=130); plt.close(fig)

# ---------------------------------------------------------------- G9: Fig. 2 trajectories, 13 panels, cut rules, no refs
def fig_G9():
    fig, ax = grid_fig(3, 5, 15, 9.6)
    for i, b in enumerate(POOLS):
        P = S["pools"][b]["models"]; grid = np.array(S["pools"][b]["grid"]); xmax = XCUT[b]; sel = grid <= xmax + 1e-9
        for m in ORDER:
            if m not in P: continue
            y = np.array([np.nan if v is None else v for v in P[m]["mean"]]); se = np.array([np.nan if v is None else v for v in P[m]["se"]]); nat = np.array(P[m]["n_at"])
            y = y.copy(); y[nat < 10] = np.nan; se[nat < 10] = np.nan
            ax[i].plot(grid[sel], y[sel], "-" if fam(m) == "GP" else "--", lw=1.9 if fam(m) == "GP" else 1.2, color=LINECOL[m], label=ABBR[m])
            ax[i].fill_between(grid[sel], np.maximum(y[sel] - se[sel], 0), y[sel] + se[sel], color=LINECOL[m], alpha=.07, lw=0)
        if b in NEW:
            ax[i].set_yscale("log")   # these pools never reach 0 within B: plain log with data-driven limits
            ys = [np.nanmin(np.array([v for v in P[m]["mean"] if v is not None])[np.array(S["pools"][b]["grid"]) <= xmax + 1e-9]) for m in ORDER if m in P]
            ax[i].set_ylim(min(ys) * 0.8, None)
        else:
            lt = 1e-9 if b.startswith("Park") else 1e-3
            ax[i].set_yscale("symlog", linthresh=lt, linscale=0.35); ax[i].set_ylim(bottom=0)
        ax[i].set_title(f"{'abcdefghijklm'[i]}  {SHORT[b]}", loc="left", fontsize=9, fontweight="bold"); ax[i].grid(alpha=.25); ax[i].tick_params(labelsize=7)
        if B_ORIG[b] < xmax: ax[i].axvline(B_ORIG[b], color="k", lw=.6, ls=":", alpha=.6)
        if i >= 10: ax[i].set_xlabel("budget (HF-equivalent cost)", fontsize=7.5)
        if i % 5 == 0: ax[i].set_ylabel("simple regret", fontsize=7.5)
    ax[13].axis("off"); ax[14].axis("off")
    h, l = ax[0].get_legend_handles_labels(); ax[13].legend(h, l, loc="upper left", ncol=2, fontsize=7.5, frameon=False, title="GP family (solid) · TL surrogates (dashed)", title_fontsize=7.5)
    fig.suptitle("G9 · Regret trajectories (mean ± s.e.; Park and the chemistry pools shown to 30; HOPV15 to 45; Matbench-gap to 100; dotted line = original B where the window extends past it)", fontsize=9)
    fig.tight_layout(rect=(0, 0, 1, 0.96)); fig.savefig(f"{OUT}/G9_trajectories.png", dpi=130); plt.close(fig)

for fn in [fig_G1, fig_G2, fig_G3, fig_G4, fig_G5, fig_G6, fig_G7, fig_G8, fig_G9]:
    try: fn(); print("ok", fn.__name__, file=sys.stderr)
    except Exception as e:
        import traceback; traceback.print_exc()

# family table
rows = []
for b in POOLS:
    for key, fn in [("opt_max", lambda M: M["opt_max"]["mean"]), ("top1_max", lambda M: M["top1_max"]["mean"]), ("nauc", lambda M: M["nauc"]["mean"]), ("regB", lambda M: M["regB"]["norm"])]:
        bp = best_pair(b, fn)
        if bp is None: continue
        (mt, vt), (mg, vg) = bp
        P = S["pools"][b]["models"]
        rows.append(dict(pool=b, key=key, best_TL=ABBR[mt], TL=vt, TL_reach=P[mt].get(key, {}).get("reach") if key in ("opt_max", "top1_max") else None,
                         best_GP=ABBR[mg], GP=vg, GP_reach=P[mg].get(key, {}).get("reach") if key in ("opt_max", "top1_max") else None, ratio_GP_over_TL=(vg / vt) if vt else None))
pd.DataFrame(rows).to_csv(f"{OUT}/family2.csv", index=False)
print(pd.DataFrame(rows).round(3).to_string(), file=sys.stderr)
print("DONE", OUT)
