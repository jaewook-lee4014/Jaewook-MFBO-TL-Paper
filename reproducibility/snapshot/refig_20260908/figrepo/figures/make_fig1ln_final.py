"""Fig. 1 l-n, CONFIRMED form (user, 2026-09-11): final-regret advantage of the best model per family
(second-named minus first-named family; blue = first-named better, orange = second-named better), 126-cell grid binned by (R2, top-10 agreement),
shared symmetric colour scale, NO significance stars, and under each map the marginal profile of the per-cell
advantage against top-10 agreement (mean over R2) and against global R2 (mean over agreement), mean +- s.e.
TL = Progressive / KnowledgeDistillation / PseudoLabeling (BLR head); variants = DKL + SparseMFGP (NARGP excluded).
Run on the VM: cd refig_20260908/figrepo/figures && python make_fig1ln_final.py  (reads results/grid summaries only).
"""
import glob, os, numpy as np, pandas as pd, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
GRID = REPO / 'results' / 'grid'
OUT = Path(os.environ.get('FIG_OUT_DIR', REPO / 'figures' / 'out'))
OUT.mkdir(parents=True, exist_ok=True)
FAMILIES = {'TL': ['Progressive', 'KnowledgeDistillation', 'PseudoLabeling'],
            'MFGP baseline': ['MFGP'], 'MFGP variants': ['DKL', 'SparseMFGP']}
COMPARISONS = [('TL', 'MFGP baseline'), ('TL', 'MFGP variants'), ('MFGP variants', 'MFGP baseline')]
METRIC = 'final_regret'
R2B = np.round(np.arange(0.1, 0.91, 0.1), 2)
T10 = np.round(np.arange(0.0, 1.01, 0.1), 2)
plt.rcParams.update({'font.family': 'sans-serif', 'font.size': 9, 'axes.linewidth': 0.8, 'savefig.dpi': 200, 'pdf.fonttype': 42, 'ps.fonttype': 42})
C_AGR, C_R2 = '#2a9d8f', '#4b5563'                       # marginal profiles: teal (agreement), slate (R2); neither is a family hue
CMAP = LinearSegmentedColormap.from_list('gp_tl', ['#b5532e', '#f7f7f5', '#0b3d7a'])   # orange = second-named better, blue = first-named better (paper hues)

man = pd.read_csv(GRID / 'grid_manifest.csv').set_index('cell_id')
rows = []
for f in sorted(glob.glob(str(GRID / 'cells' / 'summary_cell_*.csv'))):
    d = pd.read_csv(f)
    cid = d.benchmark.iloc[0]
    vals = {m: dict(zip(g.seed, g[METRIC])) for m, g in d.groupby('model')}
    best = {}
    for fam, mem in FAMILIES.items():
        have = [m for m in mem if m in vals]
        means = {m: np.mean(list(vals[m].values())) for m in have}
        b = min(means, key=means.get)
        best[fam] = means[b]
    rec = dict(cell=cid, r2=man.loc[cid, 'r2'], top10=man.loc[cid, 'top10'])
    for f1, f2 in COMPARISONS:
        rec[f'{f1}|{f2}'] = best[f2] - best[f1]
    rows.append(rec)
G = pd.DataFrame(rows)
G['ri'] = np.clip(np.round((G.r2 - 0.1) / 0.1).astype(int), 0, 8)
G['ti'] = np.round(G.top10 * 10).astype(int)
print('cells', len(G))

mats = []
for f1, f2 in COMPARISONS:
    k = f'{f1}|{f2}'
    M = np.full((11, 9), np.nan)
    for (ti, ri), g in G.groupby(['ti', 'ri']):
        M[ti, ri] = g[k].mean()
    mats.append(M)
vmax = float(np.nanmax([np.nanmax(np.abs(M)) for M in mats]))


def prof(k, col, vals):
    out = []
    for i, v in enumerate(vals):
        g = G[G[col] == i][k]
        out.append((v, g.mean(), g.std(ddof=1) / np.sqrt(len(g)) if len(g) > 1 else 0.0, len(g)))
    return pd.DataFrame(out, columns=['x', 'm', 'se', 'n'])


fig, axes = plt.subplots(2, 3, figsize=(11.5, 5.8),
                         gridspec_kw={'height_ratios': [2.6, 1.15], 'hspace': 0.45, 'wspace': 0.40})
letters = os.environ.get('FIG1LN_LETTERS', 'l,m,n').split(',')
for c, ((f1, f2), M) in enumerate(zip(COMPARISONS, mats)):
    ax = axes[0, c]
    k = f'{f1}|{f2}'
    im = ax.imshow(M, origin='lower', cmap=CMAP, vmin=-vmax, vmax=vmax, aspect='auto',
                   extent=(0.05, 0.95, -0.05, 1.05), interpolation='nearest')
    ax.set_xticks(R2B); ax.set_xticklabels([f'{v:.1f}' for v in R2B])
    ax.set_yticks(T10); ax.set_yticklabels([f'{v:.1f}' for v in T10] if c == 0 else [])
    ax.set_xlabel('global LF–HF $R^2$')
    if c == 0:
        ax.set_ylabel('top-10 optimum agreement')
    ax.set_title(f'{f1} vs {f2}', fontsize=9.5, pad=14)
    ax.text(-0.22 if c == 0 else -0.14, 1.12, letters[c], transform=ax.transAxes, fontsize=13, va='bottom')
    cb = fig.colorbar(im, ax=ax, fraction=0.05, pad=0.03)
    if c == 2:
        cb.set_label('final-regret advantage', fontsize=8)
    cb.ax.tick_params(labelsize=7.5)
    pos = int((G[k] > 1e-12).sum()); tie = int((G[k].abs() <= 1e-12).sum())
    ax.text(0.99, 1.01, f'{f1} better in {pos}/126 · ties {tie}', transform=ax.transAxes,
            ha='right', va='bottom', fontsize=7.5, color='#444')
    ax2 = axes[1, c]
    for col, vals, colr, lab in [('ti', T10, C_AGR, 'vs top-10 agreement (mean over $R^2$)'),
                                 ('ri', R2B, C_R2, 'vs global $R^2$ (mean over agreement)')]:
        P = prof(k, col, vals)
        ax2.fill_between(P.x, P.m - P.se, P.m + P.se, color=colr, alpha=0.18, lw=0)
        ax2.plot(P.x, P.m, '-o', color=colr, lw=1.6, ms=3.2, label=lab)
    ax2.axhline(0, color='#999', lw=0.8)
    ax2.set_xlim(-0.03, 1.03)
    ax2.set_xlabel('axis value (agreement or $R^2$)', fontsize=8)
    if c == 0:
        ax2.set_ylabel('advantage\n(mean ± s.e.)', fontsize=8)
    ax2.tick_params(labelsize=7.5)
    for s in ('top', 'right'):
        ax2.spines[s].set_visible(False)
    rho_t = G[k].corr(G.top10, method='spearman'); rho_r = G[k].corr(G.r2, method='spearman')
    ax2.text(0.99, 0.95, f'ρ(agreement) {rho_t:+.2f}\nρ($R^2$) {rho_r:+.2f}', transform=ax2.transAxes,
             ha='right', va='top', fontsize=7.2, color='#444')
axes[1, 0].legend(fontsize=7, frameon=False, loc='upper left', bbox_to_anchor=(0, 1.34), ncol=1)
for ext in ('pdf', 'png'):
    fig.savefig(OUT / f'{os.environ.get("FIG_STEM", "fig1ln_final")}.{ext}', bbox_inches='tight')
print('wrote', OUT / 'fig1ln_final.pdf', OUT / 'fig1ln_final.png', 'vmax', round(vmax, 4))
for f1, f2 in COMPARISONS:
    k = f'{f1}|{f2}'
    print(k, 'pos', int((G[k] > 1e-12).sum()), 'tie', int((G[k].abs() <= 1e-12).sum()), 'neg', int((G[k] < -1e-12).sum()),
          'rho_agr %.2f rho_r2 %.2f' % (G[k].corr(G.top10, method='spearman'), G[k].corr(G.r2, method='spearman')),
          'mean %.4f' % G[k].mean())
G.to_csv(OUT / 'fig1ln_final_cells.csv', index=False)
