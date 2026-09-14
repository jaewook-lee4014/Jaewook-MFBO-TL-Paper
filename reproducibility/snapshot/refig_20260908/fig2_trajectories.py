# -*- coding: utf-8 -*-
"""Paper Fig. 2 a-m: regret trajectories (mean +/- s.e. over seeds) for the 13 benchmarks under the fixed rules
(40 seeds where available, no NARGP, no reference policies, Curriculum/KD/PL merged as FET, two hues: TL blues / GP oranges,
no bold). Windows: Branin 50; Park x2, COFs, FreeSolv, Polarizability 30; HOPV15 45; Matbench-gap 100; the four large pools 20.
No reference lines (user rule).
Input: figcand2_20260911/explorer_data.json (per-seed best-so-far change points). Output: fig2_trajectories.{pdf,png,svg} + values csv."""
import json, os, sys, numpy as np, pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.ticker
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

OUT = "/mnt/data/jaewook_mfbo/MFBO-TL-Paper/experiments/refig_20260908/figcand2_20260911"
D = json.load(open(f"{OUT}/explorer_data.json"))
POOLS = ["Branin-Fav", "Branin-Unfav", "Park-Fav", "Park-Unfav", "COFs", "FreeSolv", "Polarizability", "HOPV15", "Matbench-Gap",
         "ExptGap-PBE", "Elastic-CHGNet", "Elastic-SevenNet", "Elastic-MatterSim"]
XMAX = {"Branin-Fav": 50, "Branin-Unfav": 50, "Park-Fav": 50, "Park-Unfav": 50, "COFs": 30, "FreeSolv": 30, "Polarizability": 30, "HOPV15": 30, "Matbench-Gap": 30,   # 2026-09-13: synthetic 50, chemistry/materials 30
        "ExptGap-PBE": 30, "Elastic-CHGNet": 30, "Elastic-SevenNet": 30, "Elastic-MatterSim": 30}
BFIG1 = {"Branin-Fav": 50, "Branin-Unfav": 50, "Park-Fav": 50, "Park-Unfav": 50, "COFs": 30, "FreeSolv": 30, "Polarizability": 30, "HOPV15": 30, "Matbench-Gap": 30,
         "ExptGap-PBE": 30, "Elastic-CHGNet": 30, "Elastic-SevenNet": 30, "Elastic-MatterSim": 30}
LABEL = {"Matbench-Gap": "Matbench-gap"}
MODELS = D["models"]; GP = [m for m in MODELS if m in set(D["gp"])]; TL = [m for m in MODELS if m not in set(D["gp"])]; ABBR = D["abbr"]
LARGE = POOLS[9:]
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 6.5, "axes.linewidth": 0.5, "xtick.major.width": 0.5, "ytick.major.width": 0.5,
                     "xtick.major.size": 2, "ytick.major.size": 2, "pdf.fonttype": 42, "ps.fonttype": 42, "svg.fonttype": "none"})
TICK, LAB = 6, 6.5
# two hues: GP oranges (solid), TL blues (dashed variants)
STYLE = {
    "MFGP": ("#b5532e", "-", 1.35), "Sparse MFGP": ("#f2aa84", "-", 1.35), "DKL": ("#e07b4f", "-", 1.35),
    "Sequential": ("#0b3d7a", (0, (4, 1.5)), 1.0), "Feature-extraction transfer": ("#0b3d7a", (0, (1.2, 1.2)), 1.0),
    "End-to-End Joint": ("#2467b3", (0, (4, 1.5)), 1.0), "Progressive": ("#2467b3", (0, (1.2, 1.2)), 1.0),
    "Pretrain-then-Joint": ("#4e95d9", (0, (4, 1.5)), 1.0), "Stop-Gradient Joint": ("#4e95d9", (0, (1.2, 1.2)), 1.0),
    "Domain Adaptation (MMD)": ("#8fc0ec", (0, (4, 1.5)), 1.0), "Soft Parameter Sharing": ("#8fc0ec", (0, (1.2, 1.2)), 1.0),
    "Adapter": ("#2467b3", (0, (4, 1.5, 1.2, 1.5)), 1.0),
}

def reg_at(pts, grid):
    xs = np.array([p[0] for p in pts]); ys = np.array([p[1] for p in pts])
    idx = np.searchsorted(xs, grid, side="right") - 1
    return np.where(idx >= 0, ys[np.clip(idx, 0, len(ys) - 1)], ys[0])

rows = []
fig, axes = plt.subplots(3, 5, figsize=(7.2, 5.0)); ax = axes.ravel()
letters = "abcdefghijklm"
for i, p in enumerate(POOLS):
    a = ax[i]; P = D["pools"][p]; xmax = XMAX[p]; grid = np.round(np.arange(0.0, xmax + 1e-9, 0.25), 3)
    for m in MODELS:
        ser = P["series"].get(m, {})
        curves = []
        for s, r in ser.items():
            c = reg_at(r["pts"], grid); c = np.where(grid > r["hz"] + 0.26, np.nan, c); curves.append(c)
        if not curves: continue
        A = np.array(curves); n_at = np.sum(~np.isnan(A), axis=0)
        with np.errstate(all="ignore"):
            mean = np.where(n_at > 0, np.nanmean(A, axis=0), np.nan); se = np.where(n_at > 1, np.nanstd(A, axis=0, ddof=1) / np.sqrt(np.maximum(n_at, 1)), np.nan)
        mean[n_at < 10] = np.nan; se[n_at < 10] = np.nan
        col, ls, lw = STYLE[m]
        a.plot(grid, mean, color=col, ls=ls, lw=lw, label=ABBR[m], solid_capstyle="butt")
        a.fill_between(grid, np.maximum(mean - se, 0), mean + se, color=col, alpha=0.07, lw=0)
        rows.append(dict(pool=p, model=m, n_min=int(n_at[n_at > 0].min()) if (n_at > 0).any() else 0, n_max=int(n_at.max()), mean_end=float(mean[~np.isnan(mean)][-1]) if (~np.isnan(mean)).any() else None))
    if p in LARGE:
        ys = [r["mean_end"] for r in rows if r["pool"] == p and r["mean_end"]]
        ymin = min(ys); ymax = a.get_ylim()[1]; a.set_ylim(ymin - 0.12 * (ymax - ymin), ymax)   # linear: these pools span less than one decade
    elif p.startswith("Park"):
        a.set_yscale("symlog", linthresh=1e-9, linscale=0.35); a.set_ylim(bottom=0); a.set_yticks([0, 1e-8, 1e-6, 1e-4, 1e-2, 1e0])
    else:
        a.set_yscale("symlog", linthresh=1e-3, linscale=0.35); a.set_ylim(bottom=0)
    a.yaxis.set_minor_formatter(matplotlib.ticker.NullFormatter())
    a.set_xlim(0, xmax)
    a.text(0.0, 1.13, f"{letters[i]}  {LABEL.get(p, p)}", transform=a.transAxes, ha="left", va="bottom", fontsize=6.8)
    a.text(0.0, 1.02, f"B = {xmax}", transform=a.transAxes, ha="left", va="bottom", fontsize=5.3, color="#555555")
    a.grid(lw=0.4, alpha=0.3); a.set_axisbelow(True); a.tick_params(labelsize=TICK, pad=1.5)
    for sp in ("top", "right"): a.spines[sp].set_visible(False)
    if i >= 10 or i == 8 or i == 9: a.set_xlabel("Budget", fontsize=LAB, labelpad=1.5)
    if i % 5 == 0: a.set_ylabel("Simple regret", fontsize=LAB, labelpad=1.5)
# legends in the two spare slots
for k in (13, 14): ax[k].axis("off")
hg = [Line2D([0], [0], color=STYLE[m][0], ls=STYLE[m][1], lw=STYLE[m][2], label=ABBR[m]) for m in GP]
ht = [Line2D([0], [0], color=STYLE[m][0], ls=STYLE[m][1], lw=STYLE[m][2], label=ABBR[m]) for m in TL]
ax[13].legend(handles=hg, loc="upper left", fontsize=5.8, frameon=False, title="GP family (solid)", title_fontsize=6.0, handlelength=2.4, labelspacing=0.45, borderaxespad=0)
ax[14].legend(handles=ht, loc="upper left", fontsize=5.8, frameon=False, title="TL surrogates", title_fontsize=6.0, handlelength=2.4, labelspacing=0.45, borderaxespad=0, ncol=1)
fig.subplots_adjust(left=0.065, right=0.982, top=0.94, bottom=0.125, wspace=0.55, hspace=0.62)
fig.text(0.5, 0.036, "Mean ± s.e. over seeds; budget in HF-equivalent cost.", ha="center", va="bottom", fontsize=5.0, color="#333333")
fig.text(0.5, 0.020, "TL: Seq = Sequential · FET = Feature-extraction transfer · E2E = End-to-End Joint · Prog = Progressive · PtJ = Pretrain-then-Joint · SGJ = Stop-Gradient Joint", ha="center", va="bottom", fontsize=5.0, color="#333333")
fig.text(0.5, 0.004, "MMD = Domain Adaptation (MMD) · SPS = Soft Parameter Sharing · Adpt = Adapter    GP: MFGP = baseline MFGP · SV-MFGP = sparse variational MFGP · DKL = deep-kernel GP", ha="center", va="bottom", fontsize=5.0, color="#333333")
for ext in ("pdf", "png", "svg"): fig.savefig(f"{OUT}/fig2_trajectories.{ext}", dpi=400 if ext == "png" else None)
plt.close(fig)
pd.DataFrame(rows).to_csv(f"{OUT}/fig2_trajectories_values.csv", index=False)
print(pd.DataFrame(rows).groupby("pool")[["n_min", "n_max"]].agg(["min", "max"]).to_string(), file=sys.stderr)
print("DONE", file=sys.stderr)
