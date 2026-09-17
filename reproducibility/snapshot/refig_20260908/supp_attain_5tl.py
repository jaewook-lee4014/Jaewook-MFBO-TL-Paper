# -*- coding: utf-8 -*-
"""Supplementary / Extended-Data figures under the paper's unified attainment metric (2026-09-11 evening).  [2026-09-14 5-TL variant: supp_attain_5tl.py, three GP + five TL surrogates, new output dir]

Attainment (Fig. 1 rule, fig1_attainment.py): per seed, for each target tau in {pool top 5, 2, 1, 0.5 %} the share of the
budget window [t0, b] spent with best-so-far regret <= tau (0 if never reached); mean over the four targets. Higher is better.
Thresholds come from explorer_data.json (same as Fig. 1). Budgets: Branin/Park 50, COFs/FreeSolv/Polarizability/HOPV15 30,
Matbench-Gap 20 for the acquisition / ablation / init arms (those runs were never extended past their original B = 20);
the metric-sensitivity panel (S3) uses the Fig. 1 budgets (Matbench-Gap 30 from the extended runs) because it re-reads
explorer_data.json.

Figures (paper style: 7.2 in wide, DejaVu Sans 6-7 pt, two hues TL #4e95d9 / GP #f2aa84, no bold):
  S1  supp_acq_matrix      surrogate x acquisition (GP-base EI/greedy, TL-E2E greedy/EI; 40 seeds) + heat-map of EI - greedy per surrogate
  S2  supp_acq_portfolio   acquisition portfolio (greedy, EI, PI, GP-UCB, MES, Thompson; 5 TL rows; 20 seeds)
  S3  supp_metric_sens     attainment sensitivity to the target set and to the budget (13 pools, 40 seeds)
  S4  supp_tl_design       TL design ablation: cold vs warm start, tanh vs ReLU, BLR head vs small MLP head (20 seeds)
  S5  supp_init_design     initial design: farthest-point (paper) vs random initial design, 12 surrogates (20 seeds)
  S6  supp_grid_attain     grid advantage maps under attainment (from map13_data.json; 10 seeds per cell)
Outputs to OUTDIR (default figcand2_20260914_5tl/supp): png (300 dpi) + pdf + values csv + supp_summary.json.
"""
import glob, json, os, sys
import numpy as np, pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from matplotlib.colors import LinearSegmentedColormap, TwoSlopeNorm

REFIG = "/mnt/data/jaewook_mfbo/MFBO-TL-Paper/experiments/refig_20260908"
sys.path.insert(0, REFIG)
import collect as C

OUTDIR = os.environ.get("OUTDIR", f"{REFIG}/figcand2_20260914_5tl/supp"); os.makedirs(OUTDIR, exist_ok=True)
EXPL = json.load(open(f"{REFIG}/figcand2_20260914_5tl/explorer_data.json"))
B9 = ["Branin-Fav", "Branin-Unfav", "Park-Fav", "Park-Unfav", "COFs", "FreeSolv", "Polarizability", "HOPV15", "Matbench-Gap"]
B13 = EXPL and list(EXPL["pools"].keys())
BUD9 = {"Branin-Fav": 50, "Branin-Unfav": 50, "Park-Fav": 50, "Park-Unfav": 50, "COFs": 30, "FreeSolv": 30, "Polarizability": 30, "HOPV15": 30, "Matbench-Gap": 20}
BUD13 = {"Branin-Fav": 50, "Branin-Unfav": 50, "Park-Fav": 50, "Park-Unfav": 50, "COFs": 30, "FreeSolv": 30, "Polarizability": 30, "HOPV15": 30, "Matbench-Gap": 30,
         "ExptGap-PBE": 20, "Elastic-CHGNet": 20, "Elastic-SevenNet": 20, "Elastic-MatterSim": 20}
TARGETS = ["5", "2", "1", "0.5"]
LABEL = {"Matbench-Gap": "Matbench-gap"}
MODELS = EXPL["models"]; GP = EXPL["gp"]; ABBR = EXPL["abbr"]; TLM = [m for m in MODELS if m not in GP]
# 2026-09-14: five TL surrogates (DNGOJoint relabelled Frozen-representation transfer); Sequential, Progressive, Adapter,
# Curriculum, KnowledgeDistillation and PseudoLabeling dropped. Eight display surrogates in total.
MERGED = None
RAW = {"DNGOJoint": "Frozen-representation transfer", "TwoStageJoint": "Pretrain-then-Joint", "DNGOGradient": "End-to-End Joint",
       "SoftParameterSharing": "Soft Parameter Sharing", "DomainAdaptationMMD": "Domain Adaptation (MMD)",
       "MFGP": "MFGP", "SparseMFGP": "Sparse MFGP", "DKL": "DKL"}
TL_COLOR, GP_COLOR = "#4e95d9", "#f2aa84"
TL_DARK, GP_DARK = "#2f6fb0", "#c9714a"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 6.5, "axes.linewidth": 0.5, "xtick.major.width": 0.5, "ytick.major.width": 0.5,
                     "xtick.major.size": 2, "ytick.major.size": 2, "pdf.fonttype": 42, "ps.fonttype": 42, "hatch.linewidth": 0.4})
TITLE, TICK, LAB = 6.8, 6, 6.5
DIV = LinearSegmentedColormap.from_list("gp_tl", [GP_DARK, "#f7f7f5", TL_DARK])   # negative = GP/first-named better, positive = TL/second better
SUMMARY = {}

# ------------------------------------------------------------------ metric
def attain_pts(pts, b, thrs):
    t0 = pts[0][0]
    if b <= t0 + 1e-9: return None
    acc = 0.0
    for thr in thrs:
        c = None
        for x, y in pts:
            if y <= thr + 1e-12: c = x; break
        if c is not None and c <= b + 1e-9: acc += (b - max(c, t0)) / (b - t0)
    return acc / len(thrs)

def to_pts(bu, re_):
    pts = [[float(bu[0]), float(re_[0])]]
    for x, y in zip(bu[1:], re_[1:]):
        if y < pts[-1][1] - 1e-12: pts.append([float(x), float(y)])
    return pts

def thr_of(pool, keys=TARGETS): return [EXPL["pools"][pool]["thr"][k] for k in keys]

def per_seed_attain(traj, pool, model_raw, b, keys=TARGETS):
    """traj: DataFrame (benchmark, model, seed, budget, regret) with RAW model names. -> {seed: attainment}"""
    d = traj[(traj.benchmark == pool) & (traj.model == model_raw)]
    out = {}
    thrs = thr_of(pool, keys)
    for s, g in d.groupby("seed"):
        g = g.sort_values("budget"); hz = float(g.budget.max())
        if hz + 0.26 < b: continue
        v = attain_pts(to_pts(g.budget.values, g.regret.values), b, thrs)
        if v is not None: out[int(s)] = v
    return out

def mean_se(vals):
    v = np.asarray(list(vals), float)
    if len(v) == 0: return np.nan, np.nan, 0
    return float(v.mean()), float(v.std(ddof=1) / np.sqrt(len(v))) if len(v) > 1 else 0.0, int(len(v))

def load_traj(roots, arm):
    _, t = C.load_arm([__import__("pathlib").Path(r) for r in roots], arm)
    t = t[t.benchmark.isin(B9)].copy(); t["seed"] = t.seed.astype(int)
    return t

def merged_rows(traj, pool, b, seeds=None, tag=""):
    """Attainment per display model (up to 8 rows: 3 GP + 5 TL; 2026-09-14 reduced TL set, no merged row)."""
    rows = {}
    def get(raw):
        ps = per_seed_attain(traj, pool, raw, b)
        return {s: v for s, v in ps.items() if seeds is None or s in seeds}
    for raw, disp in RAW.items():
        ps = get(raw)
        if ps: rows[disp] = ps
    return rows

def save(fig, stem):
    fig.savefig(f"{OUTDIR}/{stem}.png", dpi=300, facecolor="white"); fig.savefig(f"{OUTDIR}/{stem}.pdf", facecolor="white"); plt.close(fig)
    print("wrote", stem, file=sys.stderr)

def style(a, xlabel=None, xmax=1.3):
    a.grid(axis="x", lw=0.4, alpha=0.35); a.set_axisbelow(True)
    for sp in ("top", "right"): a.spines[sp].set_visible(False)
    a.tick_params(axis="y", length=0, pad=1.5); a.tick_params(axis="x", labelsize=TICK, pad=1.5)
    a.set_xlim(0, xmax); a.set_xticks([0, 0.5, 1.0]); a.set_xticklabels(["0", "0.5", "1"], fontsize=TICK)
    if xlabel: a.set_xlabel(xlabel, fontsize=LAB, labelpad=1.5)

def vlabel(a, yi, m, se):
    if np.isfinite(m): a.text(m + (se if np.isfinite(se) else 0) + 0.025, yi, f"{m:.2f}", va="center", ha="left", fontsize=4.8, color="#222222")

def compact(v):
    s = f"{v:+.2f}"; return s.replace("+0.", "+.").replace("-0.", "−.").replace("+.00", "0").replace("−.00", "0")


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

def title(a, letter, name, sub):
    _panel_title(a, letter, name, 0.0, 1.13, TITLE, letter_fs=8.4)
    a.text(0.0, 1.02, sub, transform=a.transAxes, ha="left", va="bottom", fontsize=5.3, color="#555555")

def heat(a, M, rows, cols, vmax=None, fmt="{:+.2f}", cmap=DIV, cb=True, fig=None, cblabel="", fs=4.6, nan_grey=False):
    M = np.asarray(M, float)
    if vmax is None: vmax = np.nanmax(np.abs(M)) if np.isfinite(M).any() else 1
    vmax = max(vmax, 1e-6)
    if nan_grey: a.set_facecolor("#e4e4e2")
    im = a.imshow(M, cmap=cmap, norm=TwoSlopeNorm(0, -vmax, vmax), aspect="auto")
    a.set_xticks(range(len(cols))); a.set_xticklabels(cols, rotation=40, ha="right", fontsize=5.4, rotation_mode="anchor")
    a.set_yticks(range(len(rows))); a.set_yticklabels(rows, fontsize=5.6)
    a.tick_params(length=0, pad=1.5)
    for sp in a.spines.values(): sp.set_visible(False)
    for i in range(M.shape[0]):
        for j in range(M.shape[1]):
            v = M[i, j]
            if np.isfinite(v): a.text(j, i, (compact(v) if fmt == "compact" else fmt.format(v)), ha="center", va="center", fontsize=fs, color="white" if abs(v) > 0.6 * vmax else "#222222")
    if cb and fig is not None:
        c = fig.colorbar(im, ax=a, fraction=0.03, pad=0.015); c.ax.tick_params(labelsize=5, length=2, width=0.4); c.outline.set_linewidth(0.4)
        if cblabel: c.set_label(cblabel, fontsize=5.4, labelpad=2)
    return im

FOOT1 = "TL: TL-base = base transfer-learning surrogate · TL-PtJ = pretrain-then-joint · TL-E2E = end-to-end joint · TL-SPS = soft parameter sharing · TL-MMD = domain adaptation (MMD)"
FOOT2 = "GP: GP-base = autoregressive multi-fidelity GP (MFGP) · GP-SV = sparse variational MFGP · GP-DKL = deep-kernel GP"
def footnote(fig, y1=0.040, y2=0.025):
    fig.text(0.982, y1, FOOT1, ha="right", va="bottom", fontsize=5.0, color="#333333")
    fig.text(0.982, y2, FOOT2, ha="right", va="bottom", fontsize=5.0, color="#333333")

TL_ROOTS = [f"{REFIG}/results", f"{REFIG}/results_slurm"]
GP_ROOTS = [f"{REFIG}/results_gp", f"{REFIG}/results_gp_vm"]
S20 = set(range(42, 62)); S40 = set(range(42, 82))

# ================================================================== S1 acquisition matrix
def fig_S1():
    tl_g = pd.concat([load_traj(TL_ROOTS, "blr_replace__hf_argmin"), load_traj([f"{REFIG}/results_conf"], "blr_replace__hf_argmin")])
    tl_e = pd.concat([load_traj(TL_ROOTS, "blr_replace__hf_ei"), load_traj([f"{REFIG}/results_conf"], "blr_replace__hf_ei")])
    gp_e = pd.concat([load_traj(GP_ROOTS, "gp_ei"), load_traj([f"{REFIG}/results_gp_conf"], "gp_ei")])
    gp_g = pd.concat([load_traj(GP_ROOTS, "gp_greedy"), load_traj([f"{REFIG}/results_gp_conf"], "gp_greedy")])
    COND = [("GP-base EI", gp_e, "MFGP", GP_COLOR, None), ("GP-base greedy", gp_g, "MFGP", GP_COLOR, "////"),
            ("TL-E2E greedy", tl_g, "DNGOGradient", TL_COLOR, None), ("TL-E2E EI", tl_e, "DNGOGradient", TL_COLOR, "////")]
    rows = []; vals = {}
    for p in B9:
        b = BUD9[p]
        for name, t, raw, col, h in COND:
            ps = per_seed_attain(t, p, raw, b); ps = {s: v for s, v in ps.items() if s in S40}
            m, se, n = mean_se(ps.values()); vals[(p, name)] = (m, se, n, ps)
            rows.append(dict(pool=p, condition=name, mean=m, se=se, n=n, budget=b))
    V = pd.DataFrame(rows); V.to_csv(f"{OUTDIR}/supp_acq_matrix_values.csv", index=False)
    # heat-map: EI - greedy per surrogate (TL 5 rows at 20 seeds 42-61; MFGP at 40 seeds), positive = EI better
    H = []; hn = []
    for disp in ["MFGP"] + TLM:
        r = []; rn = []
        for p in B9:
            b = BUD9[p]
            if disp == "MFGP":
                a = per_seed_attain(gp_e, p, "MFGP", b); g = per_seed_attain(gp_g, p, "MFGP", b)
            else:
                raw = [k for k, v in RAW.items() if v == disp][0]
                a = {s: v for s, v in per_seed_attain(tl_e, p, raw, b).items() if s in S20}; g = {s: v for s, v in per_seed_attain(tl_g, p, raw, b).items() if s in S20}
            common = sorted(set(a) & set(g))
            r.append(np.mean([a[s] - g[s] for s in common]) if common else np.nan); rn.append(len(common))
        H.append(r); hn.append(rn)
    H = np.array(H)
    pd.DataFrame(H, index=[ABBR["MFGP"]] + [ABBR[m] for m in TLM], columns=B9).to_csv(f"{OUTDIR}/supp_acq_matrix_delta.csv")
    pd.DataFrame(hn, index=[ABBR["MFGP"]] + [ABBR[m] for m in TLM], columns=B9).to_csv(f"{OUTDIR}/supp_acq_matrix_delta_n.csv")

    fig = plt.figure(figsize=(7.2, 6.0))
    gs = fig.add_gridspec(3, 5, left=0.095, right=0.985, top=0.93, bottom=0.11, wspace=0.80, hspace=0.80, height_ratios=[1, 1, 1.45])   # 2026-09-16: wspace 0.55 -> 0.72 (TL labels) -> 0.80 and left 0.085 -> 0.095, so that the longer GP-base greedy row labels clear both the figure edge and the value labels of the panel on their left
    letters = "abcdefghi"
    for i, p in enumerate(B9):
        a = fig.add_subplot(gs[i // 5, i % 5])
        y = np.arange(4)[::-1]
        for yi, (name, _, _, col, h) in zip(y, COND):
            m, se, n, _ = vals[(p, name)]
            a.barh(yi, m, xerr=se, color=col, height=0.72, edgecolor=("white" if h else "none"), hatch=h, linewidth=0.4,
                   error_kw=dict(lw=0.5, capsize=1.2, capthick=0.5, ecolor="#333333"))
            vlabel(a, yi, m, se)
        a.set_yticks(y); a.set_yticklabels([c[0] for c in COND], fontsize=5.4)
        style(a, "Attainment" if i >= 4 else None); title(a, letters[i], LABEL.get(p, p), f"B = {BUD9[p]} · n = {vals[(p, COND[0][0])][2]}")
    a = fig.add_subplot(gs[1, 4]); a.axis("off")
    h = [Patch(facecolor=GP_COLOR, label="GP-base · EI (default)"), Patch(facecolor=GP_COLOR, hatch="////", edgecolor="white", label="GP-base · greedy"),
         Patch(facecolor=TL_COLOR, label="TL-E2E · greedy (default)"), Patch(facecolor=TL_COLOR, hatch="////", edgecolor="white", label="TL-E2E · EI")]
    a.legend(handles=h, loc="center left", bbox_to_anchor=(-0.35, 0.5), fontsize=5.4, frameon=False, handlelength=1.4, handleheight=1.0, borderaxespad=0)
    a = fig.add_subplot(gs[2, 0:3])
    heat(a, H, [ABBR["MFGP"]] + [ABBR[m] for m in TLM], [LABEL.get(p, p) for p in B9], vmax=None, fig=fig, cblabel="EI − greedy (attainment)")
    title(a, "j", "Attainment with EI minus attainment with greedy, per surrogate", "GP-base row: 40 seeds · TL rows: 20 seeds (42–61) · positive = EI attains more")
    a = fig.add_subplot(gs[2, 3:5]); a.axis("off")
    a.text(0.0, 0.95, "a–i: mean ± s.e. over 40 seeds (42–81); FreeSolv\nGP-base EI n = 39 (one failed fit). Budgets as in\nFig. 1 except Matbench-gap at 20.\n\nj: paired difference per seed, then averaged;\nTL rows 20 seeds (42–61).",
           transform=a.transAxes, fontsize=5.4, va="top", color="#333333", linespacing=1.4)
    footnote(fig, 0.032, 0.017)
    save(fig, "supp_acq_matrix")
    SUMMARY["S1"] = {"conditions": [c[0] for c in COND], "values": {f"{p}|{c[0]}": [round(vals[(p, c[0])][0], 4), round(vals[(p, c[0])][1], 4), vals[(p, c[0])][2]] for p in B9 for c in COND},
                     "delta_rows": [ABBR["MFGP"]] + [ABBR[m] for m in TLM], "delta": [[None if not np.isfinite(x) else round(float(x), 4) for x in r] for r in H], "delta_n": hn}

# ================================================================== S2 acquisition portfolio
def fig_S2():
    ACQS = ["greedy", "ei", "pi", "ucb", "mes", "ts"]; UQ = ACQS[1:]
    ARM = {"greedy": "blr_replace__hf_argmin", "ei": "blr_replace__hf_ei", "pi": "blr_replace__hf_pi", "ucb": "blr_replace__hf_ucb", "mes": "blr_replace__hf_mes", "ts": "blr_replace__hf_ts"}
    AL = {"greedy": "Greedy", "ei": "EI", "pi": "PI", "ucb": "GP-UCB", "mes": "MES", "ts": "Thompson"}
    T = {a: load_traj(TL_ROOTS, ARM[a]) for a in ACQS}
    M = {a: {} for a in ACQS}   # M[a][p][disp] = (mean, se, n)
    PS = {a: {} for a in ACQS}
    for a in ACQS:
        for p in B9:
            rows = merged_rows(T[a], p, BUD9[p], seeds=S20, tag=f"S2-{a}")
            M[a][p] = {d: mean_se(v.values()) for d, v in rows.items()}; PS[a][p] = rows
    recs = [dict(acq=a, pool=p, model=ABBR[d], mean=v[0], se=v[1], n=v[2]) for a in ACQS for p in B9 for d, v in M[a][p].items()]
    pd.DataFrame(recs).to_csv(f"{OUTDIR}/supp_acq_portfolio_values.csv", index=False)
    # a: share of TL surrogates on which the acquisition attains more than greedy; b: mean paired difference over surrogates
    W = np.full((5, 9), np.nan); D = np.full((5, 9), np.nan); N = np.zeros((5, 9), int)
    for i, a in enumerate(UQ):
        for j, p in enumerate(B9):
            diffs = []
            for d in TLM:
                if d in PS[a][p] and d in PS["greedy"][p]:
                    common = sorted(set(PS[a][p][d]) & set(PS["greedy"][p][d]))
                    if len(common) >= 10: diffs.append(np.mean([PS[a][p][d][s] - PS["greedy"][p][d][s] for s in common]))
            if diffs: W[i, j] = np.mean([x > 1e-12 for x in diffs]); D[i, j] = np.mean(diffs); N[i, j] = len(diffs)
    pd.DataFrame(W, index=[AL[a] for a in UQ], columns=B9).to_csv(f"{OUTDIR}/supp_acq_portfolio_winshare.csv")
    pd.DataFrame(D, index=[AL[a] for a in UQ], columns=B9).to_csv(f"{OUTDIR}/supp_acq_portfolio_meandelta.csv")
    pd.DataFrame(N, index=[AL[a] for a in UQ], columns=B9).to_csv(f"{OUTDIR}/supp_acq_portfolio_n_models.csv")

    # ---- layout (2026-09-14 legibility pass; S2 only): printed at \textwidth = 174 mm = 0.951 x 7.2 in, so 7.5 pt here = 7.1 pt in print
    # (panel titles, colour-bar labels) and 6.5 pt here = 6.2 pt in print (tick labels, value labels, colour-bar ticks, footnotes); the heat-map cell values are
    # 6.2 pt (5.9 pt in print), the largest size that fits a 23 pt cell. The two heat maps span the full width with horizontal colour bars
    # below them (their labels used to be clipped at the right edge); the same numbers are drawn as before.
    T2, K2, L2, S2, V2, C2, F2, CB2 = 7.5, 6.5, 7, 6.5, 6.5, 6.2, 6.5, 7.5
    fig = plt.figure(figsize=(7.2, 6.3))
    gs_top = fig.add_gridspec(1, 2, left=0.085, right=0.985, top=0.94, bottom=0.768, wspace=0.21)
    gs = fig.add_gridspec(2, 5, left=0.085, right=0.985, top=0.585, bottom=0.179, wspace=0.55, hspace=0.55)
    a1 = fig.add_subplot(gs_top[0, 0]); a2 = fig.add_subplot(gs_top[0, 1])
    cols = [LABEL.get(p, p) for p in B9]
    SEQ = LinearSegmentedColormap.from_list("w_tl", ["#f7f7f5", TL_DARK])
    def hbar(a, im, label):
        """Horizontal colour bar under the x tick labels of heat map `a`, its label to the right of the bar."""
        p = a.get_position(); cax = fig.add_axes([p.x0, p.y0 - 0.104, 0.42 * p.width, 0.011])
        c = fig.colorbar(im, cax=cax, orientation="horizontal"); c.ax.tick_params(labelsize=K2, length=2, width=0.4, pad=1.5); c.outline.set_linewidth(0.4)
        cax.text(1.04, 0.5, label, transform=cax.transAxes, ha="left", va="center", fontsize=CB2)
        return c
    im = a1.imshow(W, cmap=SEQ, vmin=0, vmax=1, aspect="auto")
    a1.set_xticks(range(9)); a1.set_xticklabels(cols, rotation=40, ha="right", fontsize=K2, rotation_mode="anchor"); a1.set_yticks(range(5)); a1.set_yticklabels([AL[a] for a in UQ], fontsize=K2)
    a1.tick_params(length=0, pad=1.5)
    for sp in a1.spines.values(): sp.set_visible(False)
    for i in range(5):
        for j in range(9):
            if np.isfinite(W[i, j]): a1.text(j, i, f"{W[i, j]:.2f}", ha="center", va="center", fontsize=C2, color="white" if W[i, j] > 0.6 else "#222222")
    hbar(a1, im, "share of TL surrogates")
    _panel_title(a1, "a", "Share of TL surrogates attaining more than greedy", 0.0, 1.15, T2, letter_fs=8.4)
    a1.text(0.0, 1.03, "5 surrogates · 20 seeds each", transform=a1.transAxes, ha="left", va="bottom", fontsize=S2, color="#555555")
    vmaxD = max(np.nanmax(np.abs(D)) if np.isfinite(D).any() else 1, 1e-6)
    im2 = a2.imshow(D, cmap=DIV, norm=TwoSlopeNorm(0, -vmaxD, vmaxD), aspect="auto")
    a2.set_xticks(range(9)); a2.set_xticklabels(cols, rotation=40, ha="right", fontsize=K2, rotation_mode="anchor"); a2.set_yticks(range(5)); a2.set_yticklabels([AL[a] for a in UQ], fontsize=K2)
    a2.tick_params(length=0, pad=1.5)
    for sp in a2.spines.values(): sp.set_visible(False)
    for i in range(5):
        for j in range(9):
            if np.isfinite(D[i, j]): a2.text(j, i, f"{D[i, j]:+.2f}", ha="center", va="center", fontsize=C2, color="white" if abs(D[i, j]) > 0.6 * vmaxD else "#222222")
    hbar(a2, im2, "acquisition − greedy")
    _panel_title(a2, "b", "Mean attainment difference vs greedy", 0.0, 1.15, T2, letter_fs=8.4)
    a2.text(0.0, 1.03, "mean over the 5 surrogates", transform=a2.transAxes, ha="left", va="bottom", fontsize=S2, color="#555555")
    letters = "cdefghijk"
    SH = {"greedy": TL_DARK, "ei": TL_COLOR, "pi": "#7fb3e6", "ucb": "#a9cbee", "mes": "#c9def3", "ts": "#e3eef9"}
    for i, p in enumerate(B9):
        a = fig.add_subplot(gs[i // 5, i % 5])
        mu, se = [], []
        for acq in ACQS:
            v = [M[acq][p][d][0] for d in TLM if d in M[acq][p] and M[acq][p][d][2] >= 10]
            mu.append(np.mean(v) if v else np.nan); se.append(np.std(v, ddof=1) / np.sqrt(len(v)) if len(v) > 1 else 0.0)
        y = np.arange(6)[::-1]
        a.barh(y, mu, xerr=se, color=[SH[acq] for acq in ACQS], height=0.72, edgecolor="none", error_kw=dict(lw=0.5, capsize=1.2, capthick=0.5, ecolor="#333333"))
        for yi, m, s in zip(y, mu, se):
            if np.isfinite(m): a.text(m + (s if np.isfinite(s) else 0) + 0.025, yi, f"{m:.2f}", va="center", ha="left", fontsize=V2, color="#222222")
        a.set_yticks(y); a.set_yticklabels([AL[acq] for acq in ACQS], fontsize=K2)
        a.grid(axis="x", lw=0.4, alpha=0.35); a.set_axisbelow(True)
        for sp in ("top", "right"): a.spines[sp].set_visible(False)
        a.tick_params(axis="y", length=0, pad=1.5); a.tick_params(axis="x", labelsize=K2, pad=1.5)
        a.set_xlim(0, 1.3); a.set_xticks([0, 0.5, 1.0]); a.set_xticklabels(["0", "0.5", "1"], fontsize=K2)
        if i >= 4: a.set_xlabel("Attainment", fontsize=L2, labelpad=1.5)
        _panel_title(a, letters[i], LABEL.get(p, p), 0.0, 1.15, T2, letter_fs=8.4)
        a.text(0.0, 1.03, f"B = {BUD9[p]}", transform=a.transAxes, ha="left", va="bottom", fontsize=S2, color="#555555")
    NOTE2 = ["c–k: mean ± s.e. over the five TL surrogates of each surrogate's 20-seed mean attainment (seeds 42–61).",
             "a, b: paired per surrogate (acquisition − greedy), then the share of positive differences (a) or the mean difference (b).",
             "TL: TL-base = base transfer-learning surrogate · TL-PtJ = pretrain-then-joint · TL-E2E = end-to-end joint",
             "TL-SPS = soft parameter sharing · TL-MMD = domain adaptation (MMD)",
             "GP: GP-base = autoregressive multi-fidelity GP (MFGP) · GP-SV = sparse variational MFGP · GP-DKL = deep-kernel GP"]
    for k, line in enumerate(NOTE2):
        fig.text(0.085, 0.108 - 0.0185 * k - (0.006 if k >= 2 else 0), line, ha="left", va="bottom", fontsize=F2, color="#333333")
    save(fig, "supp_acq_portfolio")
    SUMMARY["S2"] = {"acqs": [AL[a] for a in ACQS], "winshare": [[None if not np.isfinite(x) else round(float(x), 3) for x in r] for r in W],
                     "meandelta": [[None if not np.isfinite(x) else round(float(x), 4) for x in r] for r in D], "n_models": N.tolist(),
                     "pool_means": {p: {AL[acq]: round(float(np.nanmean([M[acq][p][d][0] for d in TLM if d in M[acq][p]])), 4) if any(d in M[acq][p] for d in TLM) else None for acq in ACQS} for p in B9},
                     "coverage": {AL[acq]: {p: {ABBR[d]: M[acq][p][d][2] for d in TLM if d in M[acq][p]} for p in B9} for acq in ACQS}}

# ================================================================== S3 metric sensitivity (explorer data, 13 pools)
def fig_S3():
    P13 = list(BUD13.keys())
    def att(pool, model, b, keys):
        P = EXPL["pools"][pool]; thrs = [P["thr"][k] for k in keys]
        v = [attain_pts(r["pts"], b, thrs) for s, r in P["series"].get(model, {}).items() if r["hz"] + 0.26 >= b]
        v = [x for x in v if x is not None]; return mean_se(v)
    def best_diff(pool, b, keys):
        tl = max(att(pool, m, b, keys)[0] for m in TLM); gp = max(att(pool, m, b, keys)[0] for m in GP); return tl - gp
    tsets = [("5", ["5"]), ("2", ["2"]), ("1", ["1"]), ("0.5", ["0.5"]), ("mean", TARGETS)]
    A = np.array([[best_diff(p, BUD13[p], k) for _, k in tsets] for p in P13])
    fr = [0.5, 0.75, 1.0]
    Bm = np.array([[best_diff(p, f * BUD13[p], TARGETS) for f in fr] for p in P13])
    # c: normalised-score summary (Fig. 1 panel o rule) of the 12 surrogates under each single target
    S = {}
    for tname, keys in tsets:
        T = pd.DataFrame([[att(p, m, BUD13[p], keys)[0] for m in MODELS] for p in P13], index=P13, columns=MODELS)
        lo, hi = T.min(axis=1), T.max(axis=1); Z = (T.sub(lo, axis=0)).div((hi - lo).replace(0, np.nan), axis=0).fillna(0.5)
        S[tname] = Z.mean(axis=0)
    S = pd.DataFrame(S)
    pd.DataFrame(A, index=P13, columns=[t for t, _ in tsets]).to_csv(f"{OUTDIR}/supp_metric_sens_targets.csv")
    pd.DataFrame(Bm, index=P13, columns=[f"{f}B" for f in fr]).to_csv(f"{OUTDIR}/supp_metric_sens_budgets.csv")
    S.to_csv(f"{OUTDIR}/supp_metric_sens_scores.csv")
    fig = plt.figure(figsize=(7.2, 3.6))
    gs = fig.add_gridspec(1, 3, left=0.14, right=0.985, top=0.86, bottom=0.20, wspace=0.55, width_ratios=[1.0, 0.7, 1.35])
    a = fig.add_subplot(gs[0, 0]); rows = [LABEL.get(p, p) for p in P13]
    vmax = float(np.nanmax(np.abs(np.concatenate([A.ravel(), Bm.ravel()]))))
    heat(a, A, rows, ["top 5 %", "top 2 %", "top 1 %", "top 0.5 %", "mean (Fig. 1)"], vmax=vmax, fig=fig, cb=False)
    title(a, "a", "Best TL − best GP by target", "attainment at the Fig. 1 budget · 40 seeds")
    a = fig.add_subplot(gs[0, 1])
    im = heat(a, Bm, rows, ["0.5 B", "0.75 B", "B"], vmax=vmax, fig=fig, cb=True, cblabel="best TL − best GP"); a.set_yticklabels([])
    title(a, "b", "By budget", "four-target mean")
    a = fig.add_subplot(gs[0, 2])
    x = np.arange(len(tsets))
    for m in MODELS:
        col = GP_COLOR if m in GP else TL_COLOR
        a.plot(x, S.loc[m].values, "-o", color=col, lw=0.9 if m in GP else 0.7, ms=2.2, alpha=0.95 if m in GP else 0.8)
    ends = sorted([(float(S.loc[m].values[-1]), m) for m in MODELS]); ys = [e[0] for e in ends]
    for i in range(1, len(ys)):                       # simple repel so the end labels do not overlap (min gap 0.032)
        if ys[i] - ys[i - 1] < 0.032: ys[i] = ys[i - 1] + 0.032
    over = ys[-1] - 1.0
    if over > 0: ys = [v - over for v in ys]
    for (v, m), yl in zip(ends, ys):
        a.annotate(ABBR[m], (x[-1], v), (x[-1] + 0.10, yl), fontsize=4.4, va="center", color=GP_DARK if m in GP else TL_DARK,
                   arrowprops=dict(arrowstyle="-", lw=0.3, color="#aaaaaa", shrinkA=0, shrinkB=1), annotation_clip=False)
    a.set_xticks(x); a.set_xticklabels(["top 5 %", "top 2 %", "top 1 %", "top 0.5 %", "mean"], fontsize=TICK); a.set_xlim(-0.3, len(tsets) - 0.4)
    a.set_ylim(0, 1); a.set_yticks([0, 0.5, 1]); a.set_yticklabels(["0", "0.5", "1"], fontsize=TICK); a.set_ylabel("Normalised score (13 benchmarks)", fontsize=LAB, labelpad=1.5)
    a.grid(axis="y", lw=0.4, alpha=0.35); a.set_axisbelow(True)
    for sp in ("top", "right"): a.spines[sp].set_visible(False)
    a.tick_params(pad=1.5)
    title(a, "c", "Surrogate summary by target", "Fig. 1 panel-o rule per target")
    h = [Patch(facecolor=TL_COLOR, label="TL surrogates"), Patch(facecolor=GP_COLOR, label="GP family")]
    a.legend(handles=h, loc="lower left", fontsize=5.2, frameon=False, handlelength=1.1)
    footnote(fig, 0.040, 0.025)
    save(fig, "supp_metric_sens")
    sign = lambda M: [[("TL" if v > 0.02 else "GP" if v < -0.02 else "tie") for v in r] for r in M]
    SUMMARY["S3"] = {"pools": P13, "targets": [t for t, _ in tsets], "A": np.round(A, 4).tolist(), "A_sign": sign(A), "budgets": [f"{f}B" for f in fr], "B": np.round(Bm, 4).tolist(), "B_sign": sign(Bm),
                     "scores": {t: {ABBR[m]: round(float(S.loc[m, t]), 3) for m in MODELS} for t in S.columns}}

# ================================================================== S4 TL design ablation
def fig_S4():
    prim = load_traj(TL_ROOTS, "blr_replace__hf_argmin")
    ARMS = [("Warm start (vs cold)", "blr_replace__hf_argmin__warm"), ("ReLU (vs tanh)", "blr_replace__hf_argmin__relu"), ("16×1 MLP head (vs BLR head)", "mlp_small__hf_argmin")]
    T = {n: load_traj(TL_ROOTS, arm) for n, arm in ARMS}
    base = {p: merged_rows(prim, p, BUD9[p], seeds=S20, tag="S4-base") for p in B9}
    D = {}; Nn = {}; recs = []
    for n, _ in ARMS:
        Dm = np.full((len(TLM), 9), np.nan); Nm = np.zeros((len(TLM), 9), int)
        for j, p in enumerate(B9):
            alt = merged_rows(T[n], p, BUD9[p], seeds=S20, tag=f"S4-{n}")
            for i, d in enumerate(TLM):
                if d in alt and d in base[p]:
                    common = sorted(set(alt[d]) & set(base[p][d]))
                    if len(common) >= 5:
                        Dm[i, j] = np.mean([alt[d][s] - base[p][d][s] for s in common]); Nm[i, j] = len(common)
                        recs.append(dict(variant=n, pool=p, model=ABBR[d], delta=Dm[i, j], n=len(common), base_mean=np.mean([base[p][d][s] for s in common]), alt_mean=np.mean([alt[d][s] for s in common])))
        D[n] = Dm; Nn[n] = Nm
    pd.DataFrame(recs).to_csv(f"{OUTDIR}/supp_tl_design_values.csv", index=False)
    fig = plt.figure(figsize=(7.2, 3.0))
    gs = fig.add_gridspec(1, 3, left=0.055, right=0.975, top=0.84, bottom=0.25, wspace=0.16, width_ratios=[1, 1, 1.12])
    vmax = float(np.nanmax(np.abs(np.concatenate([D[n].ravel() for n, _ in ARMS]))))
    for k, (n, _) in enumerate(ARMS):
        a = fig.add_subplot(gs[0, k])
        heat(a, D[n], [ABBR[m] for m in TLM], [LABEL.get(p, p) for p in B9], vmax=vmax, fig=fig, cb=(k == 2), cblabel="variant − paper setting", fmt="compact", fs=4.3, nan_grey=True)
        if k: a.set_yticklabels([])
        nmin, nmax = int(Nn[n][Nn[n] > 0].min()) if (Nn[n] > 0).any() else 0, int(Nn[n].max())
        title(a, "abc"[k], n, f"paired seeds per cell n = {nmin}–{nmax}" if nmin != nmax else f"paired seeds per cell n = {nmax}")
    fig.text(0.055, 0.045, "Cells: mean over paired seeds (42–61) of attainment with the variant minus attainment with the paper setting (BLR head, cold restart, tanh); positive = variant attains more.\n"
             "Grey = no runs (MMD and SPS cannot take the MLP head). Values without a leading zero (+.34 = +0.34). In c the FET row is the Curriculum run (with an MLP head KD and PL differ from it).",
             fontsize=5.0, color="#333333", linespacing=1.4)
    save(fig, "supp_tl_design")
    SUMMARY["S4"] = {n: {"delta": [[None if not np.isfinite(x) else round(float(x), 4) for x in r] for r in D[n]], "n": Nn[n].tolist()} for n, _ in ARMS}
    SUMMARY["S4"]["rows"] = [ABBR[m] for m in TLM]

# ================================================================== S5 initial design
def fig_S5():
    prim_tl = load_traj(TL_ROOTS, "blr_replace__hf_argmin"); prim_gp = load_traj(GP_ROOTS, "gp_ei")
    rand_tl = load_traj([f"{REFIG}/results_conf"], "blr_replace__hf_argmin__initrand"); rand_gp = load_traj([f"{REFIG}/results_gp_conf"], "gp_ei__initrand")
    prim = pd.concat([prim_tl, prim_gp]); rand = pd.concat([rand_tl, rand_gp])
    F = {p: merged_rows(prim, p, BUD9[p], seeds=S20, tag="S5-fps") for p in B9}; R = {p: merged_rows(rand, p, BUD9[p], seeds=S20, tag="S5-rand") for p in B9}
    recs = []
    for p in B9:
        for d in MODELS:
            if d in F[p]: m, se, n = mean_se(F[p][d].values()); recs.append(dict(init="FPS", pool=p, model=ABBR[d], family="GP" if d in GP else "TL", mean=m, se=se, n=n))
            if d in R[p]: m, se, n = mean_se(R[p][d].values()); recs.append(dict(init="random", pool=p, model=ABBR[d], family="GP" if d in GP else "TL", mean=m, se=se, n=n))
    V = pd.DataFrame(recs); V.to_csv(f"{OUTDIR}/supp_init_design_values.csv", index=False)
    fig = plt.figure(figsize=(7.2, 4.6))
    gs = fig.add_gridspec(2, 5, left=0.06, right=0.985, top=0.90, bottom=0.15, wspace=0.55, hspace=0.75)
    letters = "abcdefghi"; bd = []
    for i, p in enumerate(B9):
        a = fig.add_subplot(gs[i // 5, i % 5])
        rows = [d for d in MODELS if d in F[p] and d in R[p]]
        fm = np.array([np.mean(list(F[p][d].values())) for d in rows]); rm = np.array([np.mean(list(R[p][d].values())) for d in rows])
        order = np.argsort(fm); rows = [rows[k] for k in order]; fm = fm[order]; rm = rm[order]
        y = np.arange(len(rows))
        for yi, d, f_, r_ in zip(y, rows, fm, rm):
            col = GP_COLOR if d in GP else TL_COLOR; dark = GP_DARK if d in GP else TL_DARK
            a.plot([f_, r_], [yi, yi], "-", color="#bbbbbb", lw=0.7, zorder=1)
            a.plot(f_, yi, "o", color=col, ms=3.0, mec="none", zorder=2); a.plot(r_, yi, "o", color="white", mec=dark, mew=0.7, ms=3.0, zorder=3)
        a.set_yticks(y); a.set_yticklabels([ABBR[d] for d in rows], fontsize=5.2)
        style(a, "Attainment" if i >= 4 else None)
        btl_f = max(fm[k] for k, d in enumerate(rows) if d not in GP); bgp_f = max(fm[k] for k, d in enumerate(rows) if d in GP)
        btl_r = max(rm[k] for k, d in enumerate(rows) if d not in GP); bgp_r = max(rm[k] for k, d in enumerate(rows) if d in GP)
        bd.append(dict(pool=p, fps=btl_f - bgp_f, random=btl_r - bgp_r, n_models=len(rows)))
        title(a, letters[i], LABEL.get(p, p), f"B = {BUD9[p]}")
    a = fig.add_subplot(gs[1, 4]); a.axis("off")
    from matplotlib.lines import Line2D
    h = [Line2D([], [], marker="o", color=TL_COLOR, ls="none", ms=4, label="TL, FPS (paper)"), Line2D([], [], marker="o", color="white", mec=TL_DARK, mew=0.8, ls="none", ms=4, label="TL, random"),
         Line2D([], [], marker="o", color=GP_COLOR, ls="none", ms=4, label="GP, FPS (paper)"), Line2D([], [], marker="o", color="white", mec=GP_DARK, mew=0.8, ls="none", ms=4, label="GP, random")]
    a.legend(handles=h, loc="upper left", bbox_to_anchor=(0.0, 1.0), fontsize=5.4, frameon=False, handlelength=1.0, borderaxespad=0)
    a.text(0.0, 0.02, "Rows: surrogates, 20 seeds\n(42–61). The same seed draws\nthe same random initial design\nfor every surrogate. Rows are\nsorted by the FPS value.", transform=a.transAxes, fontsize=4.9, va="bottom", color="#333333", linespacing=1.35)
    footnote(fig, 0.032, 0.017)
    save(fig, "supp_init_design")
    pd.DataFrame(bd).to_csv(f"{OUTDIR}/supp_init_design_bestdiff.csv", index=False)
    SUMMARY["S5"] = {"bestdiff": bd, "values": {f"{r.init}|{r.pool}|{r.model}": [round(r["mean"], 4), round(r.se, 4), int(r.n)] for _, r in V.iterrows()}}

# ================================================================== S6 grid maps under attainment (map13_data.json)
def fig_S6():
    D = json.load(open(f"{REFIG}/figcand2_20260911/map13_data.json"))
    grid = D["grid"]; TLG = D["meta"]["grid_tl"]; GPG = D["meta"]["grid_gp"]
    fam = {"TL": TLG, "MFGP baseline": ["MFGP"], "MFGP variants": [g for g in GPG if g != "MFGP"]}
    COMP = [("TL", "MFGP baseline"), ("TL", "MFGP variants"), ("MFGP variants", "MFGP baseline")]
    rows = []
    for c in grid:
        best = {f: max(c["models"][m]["attain"]["mean"] for m in mem if m in c["models"]) for f, mem in fam.items()}
        rec = dict(cell=c["id"], r2=c["r2"], top10=c["top10"])
        for f1, f2 in COMP: rec[f"{f1}|{f2}"] = best[f1] - best[f2]      # positive = first-named attains more
        rows.append(rec)
    G = pd.DataFrame(rows); G["ri"] = np.clip(np.round((G.r2 - 0.1) / 0.1).astype(int), 0, 8); G["ti"] = np.round(G.top10 * 10).astype(int)
    G.to_csv(f"{OUTDIR}/supp_grid_attain_cells.csv", index=False)
    R2B = np.round(np.arange(0.1, 0.91, 0.1), 2); T10 = np.round(np.arange(0.0, 1.01, 0.1), 2)
    mats = []
    for f1, f2 in COMP:
        k = f"{f1}|{f2}"; M = np.full((11, 9), np.nan)
        for (ti, ri), g in G.groupby(["ti", "ri"]): M[ti, ri] = g[k].mean()
        mats.append(M)
    vmax = float(np.nanmax([np.nanmax(np.abs(M)) for M in mats]))
    fig, axes = plt.subplots(2, 3, figsize=(7.2, 4.2), gridspec_kw={"height_ratios": [2.4, 1.1], "hspace": 0.55, "wspace": 0.45, "left": 0.075, "right": 0.985, "top": 0.88, "bottom": 0.12})
    C_AGR, C_R2 = "#1baf7a", "#eb6834"
    stats = {}
    for c, ((f1, f2), M) in enumerate(zip(COMP, mats)):
        ax = axes[0, c]; k = f"{f1}|{f2}"
        im = ax.imshow(M, origin="lower", cmap=DIV, norm=TwoSlopeNorm(0, -vmax, vmax), aspect="auto", extent=(0.05, 0.95, -0.05, 1.05), interpolation="nearest")
        ax.set_xticks(R2B); ax.set_xticklabels([f"{v:.1f}" for v in R2B], fontsize=TICK); ax.set_yticks(T10); ax.set_yticklabels([f"{v:.1f}" for v in T10] if c == 0 else [], fontsize=TICK)
        ax.set_xlabel("global LF–HF R²", fontsize=LAB, labelpad=1.5)
        if c == 0: ax.set_ylabel("top-10 optimum agreement", fontsize=LAB, labelpad=1.5)
        ax.tick_params(pad=1.5)
        title(ax, "abc"[c], f"{f1} vs {f2}", f"{f1} attains more in {int((G[k] > 1e-12).sum())}/126 · ties {int((G[k].abs() <= 1e-12).sum())}")
        cb = fig.colorbar(im, ax=ax, fraction=0.05, pad=0.03); cb.ax.tick_params(labelsize=5, length=2, width=0.4); cb.outline.set_linewidth(0.4)
        if c == 2: cb.set_label("attainment advantage", fontsize=5.4, labelpad=2)
        ax2 = axes[1, c]
        for col, vals, colr, lab in [("ti", T10, C_AGR, "vs top-10 agreement (mean over R²)"), ("ri", R2B, C_R2, "vs global R² (mean over agreement)")]:
            P = []
            for i, v in enumerate(vals):
                g = G[G[col] == i][k]; P.append((v, g.mean(), g.std(ddof=1) / np.sqrt(len(g)) if len(g) > 1 else 0.0))
            P = pd.DataFrame(P, columns=["x", "m", "se"])
            ax2.fill_between(P.x, P.m - P.se, P.m + P.se, color=colr, alpha=0.18, lw=0); ax2.plot(P.x, P.m, "-o", color=colr, lw=1.0, ms=2.2, label=lab)
        ax2.axhline(0, color="#999999", lw=0.6); ax2.set_xlim(-0.03, 1.03); ax2.set_xlabel("axis value (agreement or R²)", fontsize=LAB, labelpad=1.5)
        if c == 0: ax2.set_ylabel("advantage\n(mean ± s.e.)", fontsize=LAB, labelpad=1.5)
        ax2.tick_params(labelsize=TICK, pad=1.5)
        for s in ("top", "right"): ax2.spines[s].set_visible(False)
        rho_t = G[k].corr(G.top10, method="spearman"); rho_r = G[k].corr(G.r2, method="spearman")
        ax2.text(0.99, 0.95, f"ρ(agreement) {rho_t:+.2f}\nρ(R²) {rho_r:+.2f}", transform=ax2.transAxes, ha="right", va="top", fontsize=5.2, color="#444444")
        stats[k] = dict(pos=int((G[k] > 1e-12).sum()), tie=int((G[k].abs() <= 1e-12).sum()), neg=int((G[k] < -1e-12).sum()), rho_agr=round(float(rho_t), 3), rho_r2=round(float(rho_r), 3), mean=round(float(G[k].mean()), 4), max=round(float(G[k].max()), 4), min=round(float(G[k].min()), 4))
    axes[1, 0].legend(fontsize=5.2, frameon=False, loc="upper left", bbox_to_anchor=(0, 1.42), ncol=1)
    fig.text(0.075, 0.018, f"Grid: 126 synthetic pools (real HF, synthetic LF in PCA-10), 10 seeds per cell, B = {int(D['meta']['grid_budget'])}; attainment with the Fig. 1 rule (targets = cell top 5/2/1/0.5 %).\n"
             "Best of family per cell: TL = Progressive / Feature-extraction transfer (KD = PL); variants = DKL + sparse variational MFGP; positive = first-named family attains more.", fontsize=5.0, color="#333333", linespacing=1.4)
    save(fig, "supp_grid_attain")
    SUMMARY["S6"] = {"stats": stats, "vmax": round(vmax, 4), "grid_budget": D["meta"]["grid_budget"], "tl": TLG, "gp": GPG}

if __name__ == "__main__":
    which = sys.argv[1:] or ["S1", "S2", "S3", "S4", "S5", "S6"]
    for w in which:
        print("==", w, file=sys.stderr); globals()[f"fig_{w}"]()
    prev = {}
    pth = f"{OUTDIR}/supp_summary.json"
    if os.path.exists(pth):
        try: prev = json.load(open(pth))
        except Exception: prev = {}
    prev.update(SUMMARY); json.dump(prev, open(pth, "w"), indent=1)
    print("DONE", file=sys.stderr)
