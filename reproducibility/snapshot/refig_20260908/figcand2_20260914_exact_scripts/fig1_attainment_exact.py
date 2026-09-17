# -*- coding: utf-8 -*-
"""Paper Fig. 1 b-p: multi-target attainment per benchmark (user decision 2026-09-11 13:30).
Metric per seed: for each target tau in {pool top 5 %, 2 %, 1 %, 0.5 %} the fraction of the budget window [t_init, B] during which the
best-so-far regret is <= tau (0 if never); attainment = mean over the four targets. Bars = mean +/- s.e. over seeds; higher is better.
Budgets: synthetic 50, chemistry/materials 30, the four large pools 20. Two colours only (paper scheme): TL blue #4e95d9, GP salmon #f2aa84.
Panels: b-n = 13 benchmarks (largest on top), o = summary over the 13 benchmarks (vertical bars), p = summary over the nine chemistry and
materials benchmarks. Every b-n panel carries a grey direction cue at the right end of its subtitle line.
SUMMARY selects the o/p summary; the default is 'deficit', the published panels since 2026-09-16:
  deficit -> mean deficit to the best surrogate of each benchmark (highest mean attainment in that benchmark minus the surrogate's mean
             attainment), averaged over benchmarks, bars from 0 upward sorted ascending, mean +/- s.e. over the paired per-benchmark
             deficits; stem fig1_attainment, values fig1_attainment_summary_deficit{,_chem}.csv
  score   -> per-benchmark min-max normalised score (0 = worst, 1 = best surrogate in that benchmark), averaged over benchmarks
             (superseded reference); stem fig1_attainment_score, values fig1_attainment_summary_score{,_chem}.csv
  mean    -> mean attainment over benchmarks; stem fig1_attainment_mean, values fig1_attainment_summary_mean{,_chem}.csv
Input: explorer_data.json (per-seed best-so-far change points + top-k thresholds). Output: <stem>.{pdf,png,svg} + fig1_attainment_values.csv"""
import json, os, sys, numpy as np, pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

OUT = "/mnt/data/jaewook_mfbo/MFBO-TL-Paper/experiments/refig_20260908/figcand2_20260914_5tl"
D = json.load(open(f"{OUT}/explorer_data.json"))
POOLS = ["Branin-Fav", "Branin-Unfav", "Park-Fav", "Park-Unfav", "COFs", "FreeSolv", "Polarizability", "HOPV15", "Matbench-Gap",
         "ExptGap-PBE", "Elastic-CHGNet", "Elastic-SevenNet", "Elastic-MatterSim"]
BUDGET = {"Branin-Fav": 50, "Branin-Unfav": 50, "Park-Fav": 50, "Park-Unfav": 50, "COFs": 30, "FreeSolv": 30, "Polarizability": 30, "HOPV15": 30, "Matbench-Gap": 30,
          "ExptGap-PBE": 30, "Elastic-CHGNet": 30, "Elastic-SevenNet": 30, "Elastic-MatterSim": 30}
TARGETS = ["5", "2", "1", "0.5"]
LABEL = {"Matbench-Gap": "Matbench-gap"}
MODELS = D["models"]; GP = set(D["gp"]); ABBR = D["abbr"]
TL_COLOR, GP_COLOR = "#4e95d9", "#f2aa84"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 7, "axes.linewidth": 0.5, "xtick.major.width": 0.5, "ytick.major.width": 0.5,
                     "xtick.major.size": 2, "ytick.major.size": 2, "pdf.fonttype": 42, "ps.fonttype": 42, "svg.fonttype": "none"})
# Type sizes (2026-09-14 legibility pass): the figure is printed at \textwidth = 174 mm, i.e. 0.951 x its 7.2 in width, so 7.5 pt here
# = 7.1 pt in print (legend, panel titles) and 6.5 pt here = 6.2 pt in print (tick labels, subtitles, footnotes); the 8 vertical
# labels of panels o and p are 6.8 pt (6.5 pt in print), the largest size that clears their bar pitch (8 bars, 2026-09-14 5-TL set).
TITLE, TICK, LAB = 7.5, 6.5, 7
SUB, LEG, FOOT, SUMTICK = 6.5, 7.5, 6.5, 6.8
CUE_FS, SUB_GREY = 5.3, "#555555"          # direction cues ("-> better" in b-n, "v better" in o/p), in the subtitle grey
YMAX_D = {"13pools": 0.20, "9chem": 0.12}  # y range of the deficit summary panels o / p (ticks every 0.05)

def cost_to(pts, thr, b):
    for x, y in pts:
        if y <= thr + 1e-12: return (x, True) if x <= b + 1e-9 else (b, False)
    return b, False

def attain(pts, b, thrs):
    t0 = pts[0][0]
    if b <= t0 + 1e-9: return None
    acc = 0.0
    for thr in thrs:
        c, ok = cost_to(pts, thr, b)
        acc += (b - max(c, t0)) / (b - t0) if ok else 0.0
    return acc / len(thrs)

rows = []
for p in POOLS:
    P = D["pools"][p]; b = BUDGET[p]; thrs = [P["thr"][k] for k in TARGETS]
    for m in MODELS:
        ser = P["series"].get(m, {})
        vals = [attain(r["pts"], b, thrs) for s, r in ser.items() if r["hz"] + 0.26 >= b]
        vals = [v for v in vals if v is not None]
        if not vals: continue
        v = np.array(vals)
        rows.append(dict(pool=p, model=m, abbr=ABBR[m], family="GP" if m in GP else "TL", n=len(v), mean=v.mean(), se=v.std(ddof=1) / np.sqrt(len(v)) if len(v) > 1 else 0.0))
T = pd.DataFrame(rows); T.to_csv(f"{OUT}/fig1_attainment_values.csv", index=False)
print(T.pivot(index="model", columns="pool", values="n").loc[MODELS, POOLS].to_string(), file=sys.stderr)

# ---------------------------------------------------------------- figure
fig, axes = plt.subplots(3, 5, figsize=(7.2, 5.7))          # 5.7 in tall (was 5.0): room for the 6.5 pt row labels, the legend line and the footnote
ax = axes.ravel()

def _panel_title(a, letter, label, x, y, fs, letter_fs=None, **kw):
    """Nature Portfolio panel title (2026-09-17): bold lowercase letter, then the label in regular weight."""
    lfs = letter_fs if letter_fs is not None else fs + 0.9
    t = a.text(x, y, letter, transform=a.transAxes, ha="left", va="baseline", fontsize=lfs, fontweight="bold", **kw)
    fig = a.figure
    bb = t.get_window_extent(renderer=fig.canvas.get_renderer())
    w_pt = bb.width * 72.0 / fig.dpi
    if label:
        a.annotate(label, xy=(x, y), xycoords="axes fraction", xytext=(w_pt + 0.5 * fs, 0), textcoords="offset points",
                   ha="left", va="baseline", fontsize=fs, annotation_clip=False, **kw)
    return t

letters = "bcdefghijklmnop"
for i, p in enumerate(POOLS):
    a = ax[i]; t = T[T.pool == p].sort_values("mean")          # smallest first -> drawn at the bottom; largest ends on top
    bestTL = t[t.family == "TL"].iloc[-1].model; bestGP = t[t.family == "GP"].iloc[-1].model
    y = np.arange(len(t))
    a.barh(y, t["mean"], xerr=t["se"], color=[TL_COLOR if f == "TL" else GP_COLOR for f in t.family], height=0.72, edgecolor="none",
           error_kw=dict(lw=0.5, capsize=1.2, capthick=0.5, ecolor="#333333"))
    a.set_yticks(y); a.set_yticklabels(t.abbr, fontsize=TICK)
    a.set_xlim(0, 1.0); a.set_xticks([0, 0.5, 1.0]); a.set_xticklabels(["0", "0.5", "1"], fontsize=TICK)
    _panel_title(a, letters[i], LABEL.get(p, p), 0.0, 1.15, TITLE, letter_fs=8.4)
    a.text(0.0, 1.02, f"B = {BUDGET[p]}", transform=a.transAxes, ha="left", va="bottom", fontsize=SUB, color=SUB_GREY)
    a.text(1.0, 1.02, "→ better", transform=a.transAxes, ha="right", va="bottom", fontsize=CUE_FS, color=SUB_GREY)
    a.grid(axis="x", lw=0.4, alpha=0.35); a.set_axisbelow(True)
    for sp in ("top", "right"): a.spines[sp].set_visible(False)
    a.tick_params(axis="y", length=0, pad=1.5); a.tick_params(axis="x", labelsize=TICK, pad=1.5)
    if i >= 10: a.set_xlabel("Attainment", fontsize=LAB, labelpad=1.5)

# panels o and p: summaries (o = all 13 benchmarks, p = the nine chemistry and materials benchmarks). SUMMARY=deficit (default, the
# published panels) -> mean deficit to the best surrogate of each benchmark; SUMMARY=mean -> mean attainment; SUMMARY=score ->
# per-benchmark min-max normalised score (0 = worst model, 1 = best model in that benchmark), averaged (superseded reference)
SUMMARY = os.environ.get("SUMMARY", "deficit")
CHEM = POOLS[4:]
def summary_panel(a, letter, pools, title, scope, ylabel, bold=False):
    deficit = SUMMARY == "deficit"
    Tsub = T[T.pool.isin(pools)].copy()
    if deficit:
        A_ = Tsub.pivot(index="pool", columns="model", values="mean").loc[pools, MODELS]
        assert not A_.isna().any().any(), "deficit summary needs all eight surrogates in every benchmark"
        Dd = pd.DataFrame(A_.max(axis=1).values[:, None] - A_.values, index=pools, columns=MODELS)   # deficit to the benchmark best
        M = pd.DataFrame(dict(mean=Dd.mean(), se=Dd.std(ddof=1) / np.sqrt(len(pools)), n=len(pools), raw_mean=A_.mean()))
        M = M.sort_values("mean", ascending=True)               # smallest deficit (best) on the left
    else:
        if SUMMARY == "score":
            for p_ in pools:
                m_ = Tsub.pool == p_; lo, hi = Tsub.loc[m_, "mean"].min(), Tsub.loc[m_, "mean"].max()
                Tsub.loc[m_, "mean"] = (Tsub.loc[m_, "mean"] - lo) / (hi - lo) if hi > lo else 0.5
        M = Tsub.groupby("model").agg(mean=("mean", "mean"), n=("mean", "size")).reindex(MODELS)
        sd = Tsub.groupby("model")["mean"].std(ddof=1).reindex(MODELS); M["se"] = sd / np.sqrt(M["n"])
        M = M.sort_values("mean", ascending=False)
    x = np.arange(len(M))
    a.bar(x, M["mean"], yerr=M["se"], color=[GP_COLOR if m in GP else TL_COLOR for m in M.index], width=0.72, edgecolor="none",
          error_kw=dict(lw=0.5, capsize=1.2, capthick=0.5, ecolor="#333333"))
    a.set_xticks(x); a.set_xticklabels([ABBR[m] for m in M.index], fontsize=SUMTICK, rotation=90)   # vertical labels: 6.8 pt is the largest size that clears the 8-bar pitch
    if bold:
        bestTL = next(m for m in M.index if m not in GP); bestGP = next(m for m in M.index if m in GP)
        for lab, m in zip(a.get_xticklabels(), M.index):
            if m in (bestTL, bestGP): lab.set_fontweight("bold")
    if deficit:
        ymax = YMAX_D[scope]; a.set_ylim(0, ymax)
        yt = list(np.round(np.arange(0, ymax + 1e-9, 0.05), 2))
        a.set_yticks(yt); a.set_yticklabels(["0" if abs(z) < 1e-12 else f"{round(z, 3):g}" for z in yt], fontsize=TICK)
        subtitle, subfs = "↓ better", CUE_FS
    else:
        a.set_ylim(0, 1.0); a.set_yticks([0, 0.5, 1.0]); a.set_yticklabels(["0", "0.5", "1"], fontsize=TICK)
        subtitle, subfs = f"{len(pools)} benchmarks", SUB
    a.set_ylabel(ylabel, fontsize=LAB, labelpad=1.5)
    _panel_title(a, letter, title, 0.0, 1.15, TITLE, letter_fs=8.4)
    a.text(0.0, 1.02, subtitle, transform=a.transAxes, ha="left", va="bottom", fontsize=subfs, color=SUB_GREY)
    a.grid(axis="y", lw=0.4, alpha=0.35); a.set_axisbelow(True)
    for sp in ("top", "right"): a.spines[sp].set_visible(False)
    a.tick_params(axis="x", length=0, pad=1.5); a.tick_params(axis="y", pad=1.5)
    return M
ylab = {"mean": "Mean attainment", "score": "Normalised score", "deficit": "Deficit to best"}[SUMMARY]
Mo = summary_panel(ax[13], letters[13], POOLS, "All benchmarks", "13pools", ylab)
Mp = summary_panel(ax[14], letters[14], CHEM, "Mol & Mat", "9chem", ylab, bold=False)
def sumcsv(M):                                             # deficit summaries are indexed by the abbreviation used in the figure
    if SUMMARY != "deficit": return M
    Mc = M.copy(); Mc.index = [ABBR[m] for m in Mc.index]; Mc.index.name = "abbr"; return Mc
sumcsv(Mo).to_csv(f"{OUT}/fig1_attainment_summary_{SUMMARY}.csv"); sumcsv(Mp).to_csv(f"{OUT}/fig1_attainment_summary_{SUMMARY}_chem.csv")
print(f"== panel o ({SUMMARY})\n" + sumcsv(Mo).to_string() + f"\n== panel p ({SUMMARY})\n" + sumcsv(Mp).to_string(), file=sys.stderr)
if SUMMARY == "deficit":                                   # combined o/p table for the manuscript record (both scopes in one file)
    pd.concat([pd.DataFrame(dict(scope=sc, surrogate=[ABBR[m] for m in M.index], mean_attainment=M["raw_mean"].values,
                                 mean_deficit=M["mean"].values, se_over_benchmarks=M["se"].values))
               for sc, M in (("13pools", Mo), ("9chem", Mp))], ignore_index=True).to_csv(f"{OUT}/fig1_summary_deficit.csv", index=False)
# colour legend (7.5 pt = 7.1 pt in print) on its own line below the panels, above the abbreviation footnote
h = [Patch(facecolor=TL_COLOR, label="Transfer-learning (TL) surrogates"), Patch(facecolor=GP_COLOR, label="Gaussian-process (GP) family")]
fig.legend(handles=h, loc="lower left", bbox_to_anchor=(0.065, 0.066), fontsize=LEG, frameon=False, handlelength=1.1, handleheight=0.8, borderaxespad=0, ncol=2, columnspacing=1.5)

fig.subplots_adjust(left=0.065, right=0.982, top=0.935, bottom=0.160, wspace=0.5, hspace=0.45)
# abbreviation footnote (as in the manuscript's Fig. 1), 6.5 pt, wrapped over three lines so that it fits the 7.2 in width
# (2026-09-16: the GP key no longer fits on the second line, so it runs on to a third one, which also carries the o/p note)
FOOTNOTE = ["TL: TL-base = base transfer-learning surrogate · TL-PtJ = pretrain-then-joint · TL-E2E = end-to-end joint · TL-SPS = soft parameter sharing",
            "TL-MMD = domain adaptation (MMD)    GP: GP-base = autoregressive multi-fidelity GP (MFGP)",
            "GP-SV = sparse variational MFGP · GP-DKL = deep-kernel GP"]
if SUMMARY == "deficit":
    FOOTNOTE[-1] += "    o, p: mean deficit to the best surrogate of each benchmark (lower is better)"
for k, line in enumerate(FOOTNOTE):
    fig.text(0.065, 0.044 - 0.0195 * k, line, ha="left", va="bottom", fontsize=FOOT, color="#333333")
STEM = "fig1_attainment" if SUMMARY == "deficit" else f"fig1_attainment_{SUMMARY}"
for ext in ("pdf", "png", "svg"):
    fig.savefig(f"{OUT}/{STEM}.{ext}", dpi=400 if ext == "png" else None)
plt.close(fig)
print("DONE", file=sys.stderr)
