# -*- coding: utf-8 -*-
"""Figure-style harmonisation patch (2026-09-14): Figs. 3, 4, 5 a-c and SI Figs. 1-3 follow the Fig. 1/2 rule set
(regular-weight panel letters, Table-1 benchmark names, model abbreviations, family hues). Data code is untouched.
Run on the VM from refig_20260908/:  python style_patch_20260914.py
Each patched script is backed up once as <script>.bak_style_20260914."""
import re, shutil, sys
from pathlib import Path
R = Path('/mnt/data/jaewook_mfbo/MFBO-TL-Paper/experiments/refig_20260908')
F = R / 'figrepo' / 'figures'

def backup(p):
    b = p.with_name(p.name + '.bak_style_20260914')
    if not b.exists(): shutil.copy2(p, b); print('backup', b.name)
    return b

def sub1(s, old, new, label):
    n = s.count(old)
    assert n == 1, f'{label}: expected 1 occurrence, found {n}: {old[:60]!r}'
    return s.replace(old, new)

# ---------------------------------------------------------------- Fig. 4: make_a1_calibration_13_attain.py (plot block rewritten)
p = F / 'make_a1_calibration_13_attain.py'; b = backup(p); s = b.read_text()
head, sep, _ = s.partition("PAL = ['#2ca02c'")
assert sep, 'Fig. 4: PAL anchor not found'
head = head.replace("from _common import add_panel_letter, letter_pt\n", "from matplotlib.ticker import MaxNLocator\n")
head = head.replace('Outputs figrepo/figures/out/A1_calibration_13_attain_{mean,final}.{pdf,png} + _values.csv."""',
                    'Outputs figrepo/figures/out/A1_calibration_13_attain_{mean,final}.{pdf,png} + _values.csv.\n'
                    'Style (2026-09-14): the Fig. 1/2 rule set (7.2 in, 3 x 5 grid, regular letters, family hues + one marker per model)."""')
block = r'''# ---------------------------------------------------------------- figure (Fig. 1/2 rule set, 2026-09-14)
LABEL = {'Matbench-Gap': 'Matbench-gap'}
ABBR = {'MFGP': 'MFGP', 'Sparse MFGP': 'SV-MFGP', 'DKL': 'DKL', 'Sequential': 'Seq', 'Feature-extraction transfer': 'FET', 'Progressive': 'Prog',
        'Pretrain-then-Joint': 'PtJ', 'Stop-Gradient Joint': 'SGJ', 'End-to-End Joint': 'E2E', 'Domain Adaptation (MMD)': 'MMD',
        'Soft Parameter Sharing': 'SPS', 'Adapter': 'Adpt'}
# colour = family hue (GP oranges / TL blues of Fig. 2), marker = model
STYLE = {'MFGP': ('#b5532e', 'o'), 'Sparse MFGP': ('#f2aa84', 's'), 'DKL': ('#e07b4f', 'D'),
         'Sequential': ('#0b3d7a', 'o'), 'Feature-extraction transfer': ('#0b3d7a', 's'),
         'End-to-End Joint': ('#2467b3', '^'), 'Progressive': ('#2467b3', 'v'), 'Adapter': ('#2467b3', '*'),
         'Pretrain-then-Joint': ('#4e95d9', 'D'), 'Stop-Gradient Joint': ('#4e95d9', 'P'),
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
fig.text(0.5, 0.036, 'Each point is one surrogate: mean attainment ± s.e. over seeds (Fig. 1) against its held-out LF calibration error averaged over the refits of the loop.', ha='center', va='bottom', fontsize=5.0, color='#333333')
fig.text(0.5, 0.020, 'TL: Seq = Sequential · FET = Feature-extraction transfer · E2E = End-to-End Joint · Prog = Progressive · PtJ = Pretrain-then-Joint · SGJ = Stop-Gradient Joint', ha='center', va='bottom', fontsize=5.0, color='#333333')
fig.text(0.5, 0.004, 'MMD = Domain Adaptation (MMD) · SPS = Soft Parameter Sharing · Adpt = Adapter    GP: MFGP = baseline MFGP · SV-MFGP = sparse variational MFGP · DKL = deep-kernel GP', ha='center', va='bottom', fontsize=5.0, color='#333333')
tag = 'mean' if XCOL == 'ece_lf_mean' else 'final'
STEM = os.environ.get('CAL_STEM', f'A1_calibration_13_attain_{tag}')
fig.savefig(OUT / f'{STEM}.pdf'); fig.savefig(OUT / f'{STEM}.png', dpi=110)
T.to_csv(OUT / f'{STEM}_values.csv', index=False)
print(f'x = {XCOL}'); print(pd.DataFrame(rows).round(2).to_string(index=False))
'''
p.write_text(head + block); print('patched', p.name)

# ---------------------------------------------------------------- Fig. 3: make_fig1ln_final.py
p = F / 'make_fig1ln_final.py'; b = backup(p); s = b.read_text()
s = sub1(s, "(second-named minus first-named family; red = first-named better)", "(second-named minus first-named family; blue = first-named better, orange = second-named better)", 'fig3 doc')
s = sub1(s, "import matplotlib.pyplot as plt\nfrom pathlib import Path\n", "import matplotlib.pyplot as plt\nfrom matplotlib.colors import LinearSegmentedColormap\nfrom pathlib import Path\n", 'fig3 import')
s = sub1(s, "plt.rcParams.update({'font.family': 'sans-serif', 'font.size': 9, 'axes.linewidth': 0.8, 'savefig.dpi': 200})\nC_AGR, C_R2 = '#1baf7a', '#eb6834'\n",
         "plt.rcParams.update({'font.family': 'sans-serif', 'font.size': 9, 'axes.linewidth': 0.8, 'savefig.dpi': 200, 'pdf.fonttype': 42, 'ps.fonttype': 42})\n"
         "C_AGR, C_R2 = '#2a9d8f', '#4b5563'                       # marginal profiles: teal (agreement), slate (R2); neither is a family hue\n"
         "CMAP = LinearSegmentedColormap.from_list('gp_tl', ['#b5532e', '#f7f7f5', '#0b3d7a'])   # orange = second-named better, blue = first-named better (paper hues)\n", 'fig3 style')
s = sub1(s, "cmap='RdBu_r'", "cmap=CMAP", 'fig3 cmap')
s = sub1(s, "transform=ax.transAxes, fontsize=13, fontweight='bold', va='bottom')", "transform=ax.transAxes, fontsize=13, va='bottom')", 'fig3 letter')
p.write_text(s); print('patched', p.name)

# ---------------------------------------------------------------- Fig. 5 a,b: make_b2_topk_13.py
p = F / 'make_b2_topk_13.py'; b = backup(p); s = b.read_text()
s = sub1(s, "from _common import NEWFIGS, add_panel_letter, letter_pt, save_dual\n", "from _common import NEWFIGS, letter_pt, save_dual\nplt.rcParams.update({'pdf.fonttype': 42, 'ps.fonttype': 42})\n", 'b2 import')
s = sub1(s, """HIGHLIGHT_COLOR, MFGP_COLOR = '#4e95d9', '#f2aa84'
PALETTE = {'Branin-Fav': '#4e95d9', 'Branin-Unfav': '#1f4e89', 'Park-Fav': '#9467bd', 'Park-Unfav': '#5b2c83',
           'COFs': '#f2aa84', 'FreeSolv': '#2ca02c', 'Polarizability': '#17becf', 'HOPV15': '#d62728',
           'Matbench-Gap': '#bcbd22', 'ExptGap-PBE': '#8c564b',
           'Elastic-CHGNet': '#ffbf47', 'Elastic-SevenNet': '#ff8c00', 'Elastic-MatterSim': '#b34700'}
""", """REGIME_A, REGIME_B = '#9fb8ad', '#5b6770'          # neutral regime colours (sage / slate), not the family hues
LABEL = {'Matbench-Gap': 'Matbench-gap'}
# 2026-09-14 palette: the Branin and Park pairs share one hue in two shades, the elastic ladder one hue in three shades
# (lighter = weaker LF source), the remaining pools one distinct hue each
PALETTE = {'Branin-Fav': '#1f4e89', 'Branin-Unfav': '#7fb3e6', 'Park-Fav': '#5b2c83', 'Park-Unfav': '#b48ad8',
           'COFs': '#e07b4f', 'FreeSolv': '#2f8f4e', 'Polarizability': '#1aa6b7', 'HOPV15': '#c2302f',
           'Matbench-Gap': '#a08a12', 'ExptGap-PBE': '#8c564b',
           'Elastic-CHGNet': '#f0a6d2', 'Elastic-SevenNet': '#c9559e', 'Elastic-MatterSim': '#7d1f5f'}
""", 'b2 palette')
s = sub1(s, "SCREENING_TOL = 0.3\n", "SCREENING_TOL = 0.3\n\n\ndef panel_letter(ax, letter, x, y, size):\n    \"\"\"Regular-weight panel letter (Fig. 1/2 rule set).\"\"\"\n    ax.text(x, y, letter, transform=ax.transAxes, fontsize=size, fontfamily='sans-serif', ha='left', va='bottom')\n", 'b2 helper')
s = sub1(s, "label=f'{bench} (n={n:,})')", "label=f'{LABEL.get(bench, bench)} (n={n:,})')", 'b2 legend label')
s = sub1(s, "add_panel_letter(ax_curve, 'a', x=-0.10, y=1.02, size=LETTER_PT)", "panel_letter(ax_curve, 'a', x=-0.10, y=1.02, size=LETTER_PT)", 'b2 letter a')
s = sub1(s, "add_panel_letter(ax_bar, 'b', x=-0.27, y=1.02, size=LETTER_PT)", "panel_letter(ax_bar, 'b', x=-0.27, y=1.02, size=LETTER_PT)", 'b2 letter b')
s = sub1(s, "colors = [HIGHLIGHT_COLOR if b in regime_a else MFGP_COLOR for b in order]", "colors = [REGIME_A if b in regime_a else REGIME_B for b in order]", 'b2 colors')
s = sub1(s, "ax_bar.set_yticks(y_pos); ax_bar.set_yticklabels(order, fontsize=TICK_SIZE - 1)", "ax_bar.set_yticks(y_pos); ax_bar.set_yticklabels([LABEL.get(b, b) for b in order], fontsize=TICK_SIZE - 1)", 'b2 yticks')
s = sub1(s, "handles = [Patch(facecolor=HIGHLIGHT_COLOR, label='Regime A (regret ≤ 0.3)'),\n               Patch(facecolor=MFGP_COLOR, label='Regime B (regret > 0.3)')]",
         "handles = [Patch(facecolor=REGIME_A, label='Regime A (regret ≤ 0.3)'),\n               Patch(facecolor=REGIME_B, label='Regime B (regret > 0.3)')]", 'b2 legend')
p.write_text(s); print('patched', p.name)

# ---------------------------------------------------------------- Fig. 5c: make_scaling_law_blr.py
p = F / 'make_scaling_law_blr.py'; b = backup(p); s = b.read_text()
s = sub1(s, "from _common import NEWFIGS, RESULTS, add_panel_letter, letter_pt, save_dual\n", "from _common import NEWFIGS, RESULTS, letter_pt, save_dual\nplt.rcParams.update({'pdf.fonttype': 42, 'ps.fonttype': 42})\n", '5c import')
s = sub1(s, "add_panel_letter(ax, 'c', x=-0.075, y=1.01, size=letter_pt(230.3, 148))",
         "ax.text(-0.075, 1.01, 'c', transform=ax.transAxes, fontsize=letter_pt(230.3, 148), fontfamily='sans-serif', ha='left', va='bottom')   # regular weight (2026-09-14)", '5c letter')
p.write_text(s); print('patched', p.name)

# ---------------------------------------------------------------- SI Fig. 3: plot_computing_flops_blr.py
p = F / 'plot_computing_flops_blr.py'; b = backup(p); s = b.read_text()
s = sub1(s, "from _common import short\n", "from _common import short, code\n", 'flops import')
s = sub1(s, "ABC = [f'({c})' for c in 'abcdefghijk']\n", "ABC = list('abcdefghijk')            # regular-weight letters, no parentheses (2026-09-14)\nLABEL = {'Matbench-Gap': 'Matbench-gap'}\nplt.rcParams.update({'pdf.fonttype': 42, 'ps.fonttype': 42})\n", 'flops letters')
s = sub1(s, "    ax.set_yticks(y); ax.set_yticklabels([short(m) for m in g.disp], fontsize=TICK)\n    ax.set_title(f'{ABC[i]} {b}', fontsize=TITLE, loc='left')\n",
         "    ax.set_yticks(y); ax.set_yticklabels([code(m) for m in g.disp], fontsize=TICK)\n    ax.set_title(f'{ABC[i]}  {LABEL.get(b, b)}', fontsize=TITLE, loc='left')\n", 'flops panel labels')
s = sub1(s, "ax.set_yticks(y); ax.set_yticklabels([short(m) for m in avg.disp], fontsize=TICK)\nax.set_title(f'{ABC[len(BENCHES)]} Average Rank', fontsize=TITLE, loc='left')\n",
         "ax.set_yticks(y); ax.set_yticklabels([code(m) for m in avg.disp], fontsize=TICK)\nax.set_title(f'{ABC[len(BENCHES)]}  Average compute rank', fontsize=TITLE, loc='left')\n"
         "unmapped = sorted(set(allt.disp) - set(__import__('_common').CODE_NAMES)); assert not unmapped, f'no abbreviation for {unmapped}'\n", 'flops rank panel')
s = sub1(s, "           edgecolor='gray', handlelength=2.4, labelspacing=1.0, bbox_to_anchor=(0.5, -0.005))\nplt.tight_layout(w_pad=1.4, h_pad=1.4, rect=(0, 0.045, 1, 1))\n",
         "           edgecolor='gray', handlelength=2.4, labelspacing=1.0, bbox_to_anchor=(0.5, 0.040))\n"
         "fig.text(0.5, 0.024, 'TL: Seq = Sequential · Curr = Curriculum · KD = Knowledge Distillation · PL = Pseudo-Labelling · E2E = End-to-End Joint · Prog = Progressive · PtJ = Pretrain-then-Joint · SGJ = Stop-Gradient Joint',\n"
         "         ha='center', va='bottom', fontsize=10.5, color='#333333')\n"
         "fig.text(0.5, 0.006, 'MMD = Domain Adaptation (MMD) · SPS = Soft Parameter Sharing · Adpt = Adapter    GP: MFGP = baseline MFGP · SV-MFGP = sparse variational MFGP · DKL = deep-kernel GP',\n"
         "         ha='center', va='bottom', fontsize=10.5, color='#333333')\n"
         "plt.tight_layout(w_pad=1.4, h_pad=1.4, rect=(0, 0.085, 1, 1))\n", 'flops footnote')
p.write_text(s); print('patched', p.name)

# ---------------------------------------------------------------- SI Fig. 1: supp_attain.py (S1 strings only)
p = R / 'supp_attain.py'; b = backup(p); s = b.read_text()
s = sub1(s, 'label="MFGP · EI (paper)"', 'label="MFGP · EI (default)"', 's1 label 1')
s = sub1(s, 'label="E2E · greedy (paper)"', 'label="E2E · greedy (default)"', 's1 label 2')
s = sub1(s, 'a.text(0.0, 0.95, "a–i: mean ± s.e. over 40 seeds (42–81); FreeSolv MFGP EI n = 39\\n(one PSD-failed seed). Budgets as in Fig. 1 except Matbench-gap,\\nwhose acquisition runs stop at their original B = 20.\\n\\nj: paired difference per seed, then averaged; TL rows use the\\n11-surrogate EI arm of the 42–61 set (FET = Curriculum row;\\nKD and PL identical).",',
         'a.text(0.0, 0.95, "a–i: mean ± s.e. over 40 seeds (42–81); FreeSolv MFGP EI n = 39\\n(one failed fit). Budgets as in Fig. 1 except Matbench-gap at 20.\\n\\nj: paired difference per seed, then averaged; TL rows 20 seeds\\n(42–61); FET = Curriculum run, KD and PL identical.",', 's1 annotation')
p.write_text(s); print('patched', p.name)
print('ALL PATCHED')
