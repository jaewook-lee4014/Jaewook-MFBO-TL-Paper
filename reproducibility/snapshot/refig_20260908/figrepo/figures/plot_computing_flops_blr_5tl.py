"""Computational-cost figure using FLOPs (hardware-independent), reconstructed
over the BO loop: total = sum_{n=n_init..n_final} [fit_FLOPs(n) + predict_FLOPs(n)].
FLOPs counted with torch FlopCounterMode (+ custom GP-linalg formulas), all 9
benchmarks x 8 surrogates (3 GP + 5 TL, 2026-09-14) on one node. Also prints the empirical FLOP scaling
exponent (fit_FLOPs ~ N^k) to confirm the O(.) complexity.
"""
import warnings; warnings.filterwarnings('ignore')
from pathlib import Path
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
import sys
sys.path.insert(0, str(HERE))
from _common import short, code
from _common import NEWFIGS as _NF
OUT = _NF
OUT.mkdir(exist_ok=True)
PROF = REPO / 'results' / 'flop_profile_blr' / 'flop_profile.csv'
BENCHES = ['Branin-Fav', 'Branin-Unfav', 'Park-Fav', 'Park-Unfav', 'COFs',
           'FreeSolv', 'Polarizability', 'HOPV15', 'Matbench-Gap']
SCHED = {'Branin-Fav': (27, 283), 'Branin-Unfav': (7, 76), 'Park-Fav': (27, 280), 'Park-Unfav': (7, 76), 'COFs': (25, 245), 'FreeSolv': (27, 283),
         'Polarizability': (10, 99), 'HOPV15': (17, 164), 'Matbench-Gap': (22, 209)}   # (n_init_lf+n_init_hf, n_lf+n_hf) of the regenerated runs
from _common import GP_PAPER as _GPP, EXCLUDED_PAPER as _EXC, TL5_PROFILE as _TL5, RENAME_5TL, CODE_KEY_TL_5
GP_FAMILY = set(_GPP)
KEEP = set(_GPP) | set(_TL5)          # 2026-09-14: 3 GP + the five retained TL configurations only
RENAME = dict(RENAME_5TL)
SALMON, BLUE = '#f2aa84', '#4e95d9'
ABC = list('abcdefghijk')            # bold lowercase letters, no parentheses (2026-09-17)
BLABEL = {'Matbench-Gap': 'Matbench-gap'}   # benchmark display names
plt.rcParams.update({'pdf.fonttype': 42, 'ps.fonttype': 42})
# 2026-08-18 print-size re-export: 30x11 in -> 15x7 in (~2.2x print width),
# compact tick names from _common.short
TITLE, LABEL, TICK = 7.5, 6.5, 6.0   # 2026-09-17: drawn at print width (7.2 in), Fig. 1/2 rule set
TFLOP = 1e12

d = pd.read_csv(PROF); d = d[d.ok == 1]; d = d[~d['model'].isin(_EXC)]   # excluded MFGP variants (env GP_VARIANTS)
_missing = sorted(KEEP - set(d.model.unique()))
assert not _missing, f'FLOP profile is missing {_missing}'
d = d[d.model.isin(KEEP)]
med = d.groupby(['benchmark', 'model', 'fraction']).agg(
    N=('n_train', 'median'), fit=('fit_flops', 'median'), pred=('predict_flops', 'median')).reset_index()

# empirical FLOP scaling exponent fit_FLOPs ~ N^k (pooled across benchmarks)
print('Empirical FLOP scaling exponent (fit_FLOPs ~ N^k); theory: exact GP O(N^3), DNN O(N):')
for m in list(_TL5) + list(_GPP):
    g = med[med.model == m]
    k, b = np.polyfit(np.log(g.N), np.log(np.maximum(g.fit, 1)), 1)
    print(f'   {m:24s} k = {k:.2f}')


def recon(model, bench, col):
    g = med[(med.benchmark == bench) & (med.model == model)].sort_values('N')
    if len(g) < 2: return np.nan
    a, b = SCHED[bench]; grid = np.arange(a, b + 1)
    return float(np.interp(grid, g.N.values, g[col].values).sum())

models = sorted(med.model.unique())
rows = [{'benchmark': b, 'model': m, 'flops': recon(m, b, 'fit') + recon(m, b, 'pred')}
        for b in BENCHES for m in models]
allt = pd.DataFrame(rows); allt['disp'] = allt.model.replace(RENAME)
allt.to_csv(OUT / 'computing_flops_values_blr.csv', index=False)

print('\nTotal BO-loop FLOPs (TFLOPs), Sparse vs cheapest TL surrogate:')
for b in BENCHES:
    g = allt[allt.benchmark == b]
    # cheapest over the TL family only -- the manuscript's "fastest
    # transfer-learning surrogate" (a global min would pick NARGP on the
    # smallest pools and inflate the ratio)
    sp = g[g.model == 'Sparse MFGP'].flops.values[0]
    ch = g[~g.model.isin(GP_FAMILY)].flops.min()
    print(f'   {b:14s} cheapest {ch/TFLOP:5.2f}  MFGP {g[g.model=="MFGP"].flops.values[0]/TFLOP:5.2f}  '
          f'Sparse {sp/TFLOP:5.2f} TFLOP ({sp/ch:4.0f}x cheapest)')


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

plt.rcParams.update({'font.family': 'DejaVu Sans', 'axes.linewidth': 0.5, 'xtick.major.width': 0.5, 'ytick.major.width': 0.5, 'xtick.major.size': 2, 'ytick.major.size': 2})
fig, axes = plt.subplots(2, 5, figsize=(7.2, 3.9))
for i, b in enumerate(BENCHES):
    ax = axes[i // 5, i % 5]; g = allt[allt.benchmark == b].sort_values('flops')
    y = np.arange(len(g))
    ax.barh(y, g.flops / TFLOP, color=[SALMON if m in GP_FAMILY else BLUE for m in g.model],
            alpha=0.9, height=0.72, edgecolor='none')
    for yi, (_, r) in zip(y, g.iterrows()):
        ax.text(r.flops / TFLOP, yi, f' {r.flops/TFLOP:.2f}', va='center', ha='left', fontsize=5.5, color='#333')
    ax.set_yticks(y); ax.set_yticklabels([code(m) for m in g.disp], fontsize=TICK)
    _panel_title(ax, ABC[i], BLABEL.get(b, b), 0.0, 1.03, TITLE, letter_fs=8.4)
    ax.set_xlabel('Total compute (TFLOPs)', fontsize=LABEL)
    ax.set_xlim(0, g.flops.max() / TFLOP * 1.45); ax.tick_params(labelsize=TICK)
    ax.grid(axis='x', alpha=0.3, lw=0.5)
# average-rank panel (panel j): rank surrogates by total compute within each
# benchmark (lower = cheaper), then average across all nine. All 8 surrogates
# are present on every benchmark, so the raw average rank is directly comparable.
rr = []
for b in BENCHES:
    g = allt[allt.benchmark == b][['model', 'flops']].copy()
    g['rank'] = g['flops'].rank()
    rr.append(g[['model', 'rank']])
avg = pd.concat(rr).groupby('model')['rank'].mean().reset_index().sort_values('rank')
avg['disp'] = avg.model.replace(RENAME)
ax = axes[1, 4]
y = np.arange(len(avg))
ax.barh(y, avg['rank'], color=[SALMON if m in GP_FAMILY else BLUE for m in avg.model],
        alpha=0.9, height=0.72, edgecolor='none')
for yi, r in zip(y, avg['rank']):
    ax.text(r, yi, f' {r:.1f}', va='center', ha='left', fontsize=5.5, color='#333')
ax.set_yticks(y); ax.set_yticklabels([code(m) for m in avg.disp], fontsize=TICK)
_panel_title(ax, ABC[len(BENCHES)], 'Average compute rank', 0.0, 1.03, TITLE, letter_fs=8.4)
unmapped = sorted(set(allt.disp) - set(__import__('_common').CODE_NAMES)); assert not unmapped, f'no abbreviation for {unmapped}'
ax.set_xlabel('Average compute rank', fontsize=LABEL)
ax.set_xlim(0, avg['rank'].max() * 1.45); ax.tick_params(labelsize=TICK)
ax.grid(axis='x', alpha=0.3, lw=0.5)
fig.legend(handles=[Patch(fc=SALMON, label='Gaussian-process family'),
                    Patch(fc=BLUE, label='Transfer-learning surrogates')],
           loc='lower center', ncol=2, fontsize=6.5, frameon=True, fancybox=False,
           edgecolor='gray', handlelength=2.0, labelspacing=0.6, bbox_to_anchor=(0.5, 0.062))
fig.text(0.5, 0.030, CODE_KEY_TL_5, ha='center', va='bottom', fontsize=6.0, color='#333333')
fig.text(0.5, 0.004, 'GP: GP-base = autoregressive multi-fidelity GP (MFGP) · GP-SV = sparse variational MFGP · GP-DKL = deep-kernel GP',
         ha='center', va='bottom', fontsize=6.0, color='#333333')
plt.tight_layout(w_pad=1.0, h_pad=1.2, rect=(0, 0.125, 1, 1))
# regenerated figure lands in figures/out; compare against paper/paper_figures
for stem in (OUT / 'computing_time_blr',):
    fig.savefig(f'{stem}.pdf', bbox_inches='tight', facecolor='white')
    fig.savefig(f'{stem}.png', dpi=200, bbox_inches='tight', facecolor='white')
    print('wrote', f'{stem}.pdf + .png')
plt.close()
