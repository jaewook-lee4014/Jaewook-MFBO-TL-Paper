# -*- coding: utf-8 -*-
"""Fig. 4 e-q variant: LF ECE vs ATTAINMENT (the paper's Fig. 1 metric), 13 pools, seeds 42-81, 8 models (NARGP out, five TL surrogates, DKL in).
y = mean attainment per model from figcand2_20260914_5tl/fig1_attainment_values.csv (fig1_attainment.py, budgets 50/30/20, four targets).
x = LF ECE per model: ECE_X=mean -> ece_lf_mean (mean over every refit of the loop; matches an anytime metric), ECE_X=final -> ece_lf_final.
Higher attainment = better, so the sign convention is the OPPOSITE of the regret plot (well-calibrated & good optimiser -> r > 0).
Outputs figrepo/figures/out/A1_calibration_13_attain_{mean,final}.{pdf,png} + _values.csv.
Style (2026-09-14): the Fig. 1/2 rule set (7.2 in, 3 x 5 grid, regular letters, family hues + one marker per model)."""
import glob, os, sys
from pathlib import Path
import numpy as np, pandas as pd
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
R = Path('/mnt/data/jaewook_mfbo/MFBO-TL-Paper/experiments/refig_20260908')
sys.path.insert(0, str(R / 'figrepo' / 'figures'))
from matplotlib.ticker import MaxNLocator
OUT = R / 'figcand2_20260914_5tl'
XCOL = {'mean': 'ece_lf_mean', 'final': 'ece_lf_final'}[os.environ.get('ECE_X', 'mean')]
POOLS = ['Branin-Fav', 'Branin-Unfav', 'Park-Fav', 'Park-Unfav', 'COFs', 'FreeSolv', 'Polarizability', 'HOPV15', 'Matbench-Gap',
         'ExptGap-PBE', 'Elastic-CHGNet', 'Elastic-SevenNet', 'Elastic-MatterSim']
BUDGET = {p: 50 for p in POOLS[:4]}; BUDGET.update({p: 30 for p in POOLS[4:9]}); BUDGET.update({p: 30 for p in POOLS[9:]})
# 2026-09-14: five TL surrogates (DNGOJoint relabelled Frozen-representation transfer); Sequential, Progressive, Adapter,
# Curriculum, KnowledgeDistillation and PseudoLabeling are dropped. Eight display surrogates in total.
DROP = {'NARGP', 'KnowledgeDistillation', 'PseudoLabeling', 'Curriculum', 'Sequential', 'Progressive', 'Adapter'}
NAMES = {'SparseMFGP': 'Sparse MFGP', 'DNGOGradient': 'End-to-End Joint', 'DNGOJoint': 'Frozen-representation transfer',
         'TwoStageJoint': 'Pretrain-then-Joint', 'DomainAdaptationMMD': 'Domain Adaptation (MMD)', 'SoftParameterSharing': 'Soft Parameter Sharing'}
GP = ['MFGP', 'Sparse MFGP', 'DKL']
TL = ['Frozen-representation transfer', 'Pretrain-then-Joint', 'End-to-End Joint', 'Soft Parameter Sharing', 'Domain Adaptation (MMD)']
MODELS = GP + TL
SRC = ['results/blr_replace__hf_argmin', 'results_conf/blr_replace__hf_argmin', '../ext_chem_20260909/results_confirm_ext/blr_replace__hf_argmin',
       'results_gp/gp_ei', 'results_gp_vm/gp_ei', 'results_gp_conf/gp_ei', '../ext_chem_20260909/results_confirm_ext/gp_ei']   # 2026-09-13: four large pools from the B = 30 re-runs
summ = pd.concat([pd.read_csv(f) for d in SRC for f in glob.glob(str(R / d / 'cells' / 'summary_*.csv'))], ignore_index=True)
summ = summ[summ.benchmark.isin(POOLS) & summ.seed.between(42, 81) & ~summ.model.isin(DROP)].drop_duplicates(['benchmark', 'model', 'seed'])
summ['model'] = summ.model.replace(NAMES)
ece = summ.groupby(['benchmark', 'model'])[['ece_lf_mean', 'ece_lf_final']].mean().reset_index()
att = pd.read_csv(R / 'figcand2_20260914_5tl' / 'fig1_attainment_values.csv').rename(columns={'pool': 'benchmark', 'mean': 'attainment', 'n': 'n_att'})
assert set(att.model) == set(MODELS), set(att.model) ^ set(MODELS)
T = ece.merge(att[['benchmark', 'model', 'attainment', 'n_att', 'se']], on=['benchmark', 'model'])
# ---------------------------------------------------------------- figure (Fig. 1/2 rule set, 2026-09-14)
LABEL = {'Matbench-Gap': 'Matbench-gap'}
ABBR = {'MFGP': 'MFGP', 'Sparse MFGP': 'SV-MFGP', 'DKL': 'DKL', 'Frozen-representation transfer': 'Frozen',
        'Pretrain-then-Joint': 'PtJ', 'End-to-End Joint': 'E2E', 'Domain Adaptation (MMD)': 'MMD',
        'Soft Parameter Sharing': 'SPS'}
# colour = family hue (GP oranges / TL blues of Fig. 2), marker = model; Frozen keeps the colour and marker of the former Stop-Gradient Joint
STYLE = {'MFGP': ('#b5532e', 'o'), 'Sparse MFGP': ('#f2aa84', 's'), 'DKL': ('#e07b4f', 'D'),
         'Frozen-representation transfer': ('#4e95d9', 'P'), 'Pretrain-then-Joint': ('#0b3d7a', 'D'),
         'End-to-End Joint': ('#2467b3', '^'),
         'Domain Adaptation (MMD)': ('#8fc0ec', 'X'), 'Soft Parameter Sharing': ('#8fc0ec', 'h')}
MS = {'o': 13, 's': 11, 'D': 9.5, '^': 14, 'v': 14, '*': 24, 'P': 15, 'X': 15, 'h': 14}     # scatter areas (pt^2), visually matched
plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 6.5, 'axes.linewidth': 0.5, 'xtick.major.width': 0.5, 'ytick.major.width': 0.5,
                     'xtick.major.size': 2, 'ytick.major.size': 2, 'pdf.fonttype': 42, 'ps.fonttype': 42})
TITLE, TICK, LAB = 6.8, 6, 6.5
XLAB = 'LF calibration error\n(held-out, loop mean)' if XCOL == 'ece_lf_mean' else 'LF calibration error\n(held-out, final refit)'
LETTERS = list(os.environ.get('CAL_LETTERS', 'efghijklmnopq'))
fig, axes = plt.subplots(3, 5, figsize=(7.2, 5.0)); axes = axes.ravel(); rows = []
for i, b in enumerate(POOLS):
    ax = axes[i]; t = T[T.benchmark == b].set_index('model').reindex(MODELS).dropna(subset=[XCOL, 'attainment'])
    for m, r in t.iterrows():
        col, mk = STYLE[m]
        ax.errorbar(r[XCOL], r.attainment, yerr=r.se, fmt='none', ecolor='#9a9a9a', elinewidth=0.45, capsize=0, zorder=2)
        ax.scatter(r[XCOL], r.attainment, s=MS[mk], marker=mk, color=col, edgecolor='#222222', linewidth=0.3, zorder=3)
    rr = t[[XCOL, 'attainment']].corr().iloc[0, 1] if t.attainment.std() > 0 else np.nan
    rs = t[[XCOL, 'attainment']].corr(method='spearman').iloc[0, 1] if t.attainment.std() > 0 else np.nan
    rows.append(dict(benchmark=b, pearson_r=rr, spearman_rho=rs, n_models=len(t)))
    ax.text(0.97, 0.05, f'Pearson $r$ = {rr:+.2f}', transform=ax.transAxes, fontsize=5.3, va='bottom', ha='right', color='#333333',
            bbox=dict(boxstyle='round,pad=0.25', facecolor='white', edgecolor='#bbbbbb', linewidth=0.4, alpha=0.9))
    ax.set_ylim(-0.03, 1.03); ax.set_yticks([0, 0.5, 1.0]); ax.set_yticklabels(['0', '0.5', '1'], fontsize=TICK)
    ax.xaxis.set_major_locator(MaxNLocator(3)); ax.tick_params(axis='x', labelsize=TICK, pad=1.5); ax.tick_params(axis='y', labelsize=TICK, pad=1.5)
    ax.text(0.0, 1.13, f'{LETTERS[i]}  {LABEL.get(b, b)}', transform=ax.transAxes, ha='left', va='bottom', fontsize=TITLE)
    ax.text(0.0, 1.02, f'B = {BUDGET[b]}', transform=ax.transAxes, ha='left', va='bottom', fontsize=5.3, color='#555555')
    ax.grid(lw=0.4, alpha=0.35); ax.set_axisbelow(True)
    for sp in ('top', 'right'): ax.spines[sp].set_visible(False)
    if i >= 8: ax.set_xlabel(XLAB, fontsize=6.0, labelpad=1.5)          # lowest panel of each column
    if i % 5 == 0: ax.set_ylabel('Attainment', fontsize=LAB, labelpad=1.5)
for a in (axes[13], axes[14]): a.axis('off')
def _h(m):
    col, mk = STYLE[m]
    return Line2D([0], [0], marker=mk, ls='', markersize=np.sqrt(MS[mk]) * 1.05, markerfacecolor=col, markeredgecolor='#222222', markeredgewidth=0.3, label=ABBR[m])
axes[13].legend(handles=[_h(m) for m in GP], loc='upper left', fontsize=5.8, frameon=False, title='GP family', title_fontsize=6.0, labelspacing=0.45, borderaxespad=0, handletextpad=0.5)
axes[14].legend(handles=[_h(m) for m in TL], loc='upper left', fontsize=5.8, frameon=False, title='TL surrogates', title_fontsize=6.0, labelspacing=0.45, borderaxespad=0, handletextpad=0.5)
fig.subplots_adjust(left=0.065, right=0.982, top=0.94, bottom=0.13, wspace=0.55, hspace=0.62)
fig.text(0.5, 0.032, 'Each point is one surrogate: mean attainment ± s.e. over seeds (Fig. 1) against its held-out LF calibration error averaged over the refits of the loop.', ha='center', va='bottom', fontsize=5.0, color='#333333')
fig.text(0.5, 0.016, 'TL: Frozen = Frozen-representation transfer · PtJ = Pretrain-then-Joint · E2E = End-to-End Joint · SPS = Soft Parameter Sharing · MMD = Domain Adaptation (MMD)', ha='center', va='bottom', fontsize=5.0, color='#333333')
fig.text(0.5, 0.000, 'GP: MFGP = baseline MFGP · SV-MFGP = sparse variational MFGP · DKL = deep-kernel GP', ha='center', va='bottom', fontsize=5.0, color='#333333')
tag = 'mean' if XCOL == 'ece_lf_mean' else 'final'
STEM = os.environ.get('CAL_STEM', f'A1_calibration_13_attain_{tag}')
fig.savefig(OUT / f'{STEM}.pdf'); fig.savefig(OUT / f'{STEM}.png', dpi=110)
T.to_csv(OUT / f'{STEM}_values.csv', index=False)
print(f'x = {XCOL}'); print(pd.DataFrame(rows).round(2).to_string(index=False))
