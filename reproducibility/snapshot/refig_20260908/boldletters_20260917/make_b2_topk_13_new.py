"""B2_topk_13 -- Fig. 4 a,b (top-k overlap + LF-only screening regret) extended from the nine original benchmarks to the
13 benchmarks of the 2026-09-11 paper data set (+ ExptGap-PBE and the CHGNet / SevenNet / MatterSim elastic-modulus ladder).

Data: every pool's (y_hf, y_lf) is taken from pools.make_bench (the SAME loader as the regenerated runs: csv column HF/LF,
negate flags of pools.PAPER / pools.CONFIRM, minimisation), so the synthetic pools are the candidate lattices the runs
used (synthetic_*.csv) rather than a re-generated grid. Definitions are those of the original make_b2_topk.py /
plot_b2_topk.py:  overlap(k) = |top-k(HF) & top-k(LF)| / k with k = max(1, int(frac * n)) (argsort order, stable);
screening regret = y_hf[argmin y_lf] - min(y_hf) (first index among LF ties); top-1 hit = argmin y_lf == argmin y_hf.
Regime split at 0.3 (raw HF units, unchanged). Values -> B2_topk_13_values.csv (also the nine originals for checking).
Run on the VM from figrepo/figures/:  MPLBACKEND=Agg FIG_OUT=fig5_13 python make_b2_topk_13.py

2026-09-17 print-size re-layout: drawn at 7.2 in (printed at 0.92 x \\textwidth = 161 mm, scale 0.88) with the Fig. 1/2
rule set (DejaVu Sans; 6.5 pt ticks, 7 pt labels, 7.5 pt titles, 6.2 pt legends), bold lowercase panel letters, and a
colour-blind-safe encoding for the 13 curves: paired / laddered pools keep one hue in two or three shades, the six single
pools use Okabe-Ito hues AND distinct line styles, so no curve is separated by hue alone. The values are unchanged.
"""
import os, sys
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
import numpy as np, pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from _common import NEWFIGS, save_dual
plt.rcParams.update({'pdf.fonttype': 42, 'ps.fonttype': 42, 'font.family': 'DejaVu Sans', 'font.size': 6.5,
                     'axes.linewidth': 0.5, 'xtick.major.width': 0.5, 'ytick.major.width': 0.5,
                     'xtick.major.size': 2, 'ytick.major.size': 2})
PKG = HERE.parent.parent                      # refig_20260908/
sys.path.insert(0, str(PKG))
import pools as POOLS
from run_tl import REPO

ORDER = ['Branin-Fav', 'Branin-Unfav', 'Park-Fav', 'Park-Unfav', 'COFs', 'FreeSolv', 'Polarizability',
         'HOPV15', 'Matbench-Gap', 'ExptGap-PBE', 'Elastic-CHGNet', 'Elastic-SevenNet', 'Elastic-MatterSim']
REGIME_A, REGIME_B = '#9fb8ad', '#5b6770'          # neutral regime colours (sage / slate), not the family hues
LABEL = {'Matbench-Gap': 'Matbench-gap'}
# 2026-09-17 palette (colour-blind safe): the Branin and Park pairs share one hue in two shades, the elastic ladder one
# hue in three shades (lighter = weaker LF source); the six single pools use Okabe-Ito hues with distinct line styles
PALETTE = {'Branin-Fav': '#1f4e89', 'Branin-Unfav': '#7fb3e6', 'Park-Fav': '#5b2c83', 'Park-Unfav': '#b48ad8',
           'COFs': '#e69f00', 'FreeSolv': '#009e73', 'Polarizability': '#56b4e9', 'HOPV15': '#d55e00',
           'Matbench-Gap': '#8a6d00', 'ExptGap-PBE': '#6e6e6e',
           'Elastic-CHGNet': '#f0a6d2', 'Elastic-SevenNet': '#c9559e', 'Elastic-MatterSim': '#7d1f5f'}
STYLE = {'Branin-Fav': '-', 'Branin-Unfav': (0, (4, 2)), 'Park-Fav': '-', 'Park-Unfav': (0, (4, 2)),
         'COFs': '-', 'FreeSolv': (0, (4, 2)), 'Polarizability': (0, (5, 1.5, 1, 1.5)), 'HOPV15': '-',
         'Matbench-Gap': (0, (1, 1.2)), 'ExptGap-PBE': (0, (2, 1.5)),
         'Elastic-CHGNet': (0, (4, 2)), 'Elastic-SevenNet': (0, (4, 2)), 'Elastic-MatterSim': (0, (4, 2))}
TITLE_SIZE, LABEL_SIZE, TICK_SIZE, LEGEND_SIZE, NOTE_SIZE = 7.5, 7, 6.5, 6.2, 5.6
LETTER_PT = 9.1                                   # prints at 8 pt after the 0.88 scaling to 0.92 x \textwidth
SCREENING_TOL = 0.3


def panel_letter(ax, letter, x, y, size):
    """Bold lowercase panel letter (Nature Portfolio style, 2026-09-17)."""
    ax.text(x, y, letter, transform=ax.transAxes, fontsize=size, fontweight='bold', fontfamily='sans-serif', ha='left', va='bottom')


def load_y():
    ys = {}
    for name in ORDER:
        b, cfg = POOLS.make_bench(name, REPO / 'data')
        ys[name] = (np.asarray(b.y_hf, float), np.asarray(b.y_lf, float))
    return ys


def main():
    ys = load_y()
    rows = []
    k_fractions = np.linspace(0.005, 0.30, 60)
    curves = {}
    for bench in ORDER:
        y_hf, y_lf = ys[bench]; n = len(y_hf)
        o_hf, o_lf = np.argsort(y_hf, kind='stable'), np.argsort(y_lf, kind='stable')
        ov = []
        for frac in k_fractions:
            k = max(1, int(frac * n))
            ov.append(len(set(o_hf[:k]) & set(o_lf[:k])) / k)
        curves[bench] = np.array(ov)
        lf_best, hf_best = int(np.argmin(y_lf)), int(np.argmin(y_hf))
        sr = float(y_hf[lf_best] - y_hf.min())
        n_lf_ties = int(np.sum(y_lf == y_lf.min()))
        sr_ties = y_hf[y_lf == y_lf.min()] - y_hf.min()
        r2 = float(np.corrcoef(y_hf, y_lf)[0, 1]) ** 2
        top10 = len(set(o_hf[:10]) & set(o_lf[:10])) / 10
        k1 = max(1, int(0.01 * n))
        rows.append(dict(benchmark=bench, n=n, r2=r2, top10_overlap=top10,
                         top1pct_overlap=len(set(o_hf[:k1]) & set(o_lf[:k1])) / k1,
                         screening_regret=sr, screening_regret_over_range=sr / float(y_hf.max() - y_hf.min()),
                         top1_hit=int(lf_best == hf_best), hf_best_idx=hf_best, lf_best_idx=lf_best,
                         lf_rank_of_hf_best=int(np.where(o_lf == hf_best)[0][0]) + 1,
                         n_lf_ties_at_min=n_lf_ties, screening_regret_ties_min=float(sr_ties.min()),
                         screening_regret_ties_max=float(sr_ties.max()),
                         regime='A' if sr <= SCREENING_TOL else 'B'))
    met = pd.DataFrame(rows)
    met.to_csv(NEWFIGS / 'B2_topk_13_values.csv', index=False)
    print(met.to_string())

    fig, axes = plt.subplots(1, 2, figsize=(7.2, 4.0), gridspec_kw={'width_ratios': [1.15, 1]})
    ax_curve, ax_bar = axes
    for bench in ORDER:
        n = len(ys[bench][0])
        ax_curve.plot(k_fractions * 100, curves[bench], color=PALETTE[bench], lw=1.1, ls=STYLE[bench],
                      label=f'{LABEL.get(bench, bench)} (n={n:,})')
    ax_curve.plot(k_fractions * 100, k_fractions, color='black', ls=(0, (1, 3)), alpha=0.6, lw=0.8, label='Random (E[overlap]=k/n)')
    ax_curve.set_xlabel('Top-k fraction (%)', fontsize=LABEL_SIZE, labelpad=2)
    ax_curve.set_ylabel('Overlap (|LF top-k ∩ HF top-k|)/k', fontsize=LABEL_SIZE, labelpad=2)
    ax_curve.set_title('Fidelity ranking alignment', fontsize=TITLE_SIZE, pad=6)
    panel_letter(ax_curve, 'a', x=-0.12, y=1.02, size=LETTER_PT)
    ax_curve.set_xlim(0.5, 30); ax_curve.set_ylim(0, 1.05)
    ax_curve.grid(True, alpha=0.3, lw=0.4); ax_curve.set_axisbelow(True)
    ax_curve.tick_params(axis='both', labelsize=TICK_SIZE, pad=1.5)
    for sp in ('top', 'right'): ax_curve.spines[sp].set_visible(False)
    # 13 curves: the legend sits below the axes so that it hides none of the low-overlap curves (HOPV15, Matbench-Gap, ExptGap, elastic)
    fig.legend(*ax_curve.get_legend_handles_labels(), fontsize=LEGEND_SIZE, loc='lower center',
               bbox_to_anchor=(0.5, 0.0), frameon=True, edgecolor='gray', ncol=4, columnspacing=1.2, handlelength=2.4,
               labelspacing=0.45, borderpad=0.6)

    sr_full = met.set_index('benchmark')['screening_regret']
    regime_a = [b for b in ORDER if sr_full[b] <= SCREENING_TOL]
    regime_b = [b for b in ORDER if sr_full[b] > SCREENING_TOL]
    order = sorted(regime_a, key=lambda b: float(sr_full[b])) + sorted(regime_b, key=lambda b: float(sr_full[b]))
    sr = sr_full.loc[order]; top1 = met.set_index('benchmark').loc[order, 'top1_hit']
    colors = [REGIME_A if b in regime_a else REGIME_B for b in order]
    y_pos = np.arange(len(order))
    xmax = float(np.abs(sr.values).max())
    # raw HF units span 0 (Park) to ~4e2 GPa (elastic ladder): symlog axis, linear below 0.1
    ax_bar.set_xscale('symlog', linthresh=0.1, linscale=0.5)
    ax_bar.barh(y_pos, sr.values, color=colors, edgecolor='none', height=0.7, alpha=0.9)
    ax_bar.axvline(SCREENING_TOL, color='0.35', ls=(0, (4, 3)), lw=0.8, zorder=0)
    ax_bar.set_yticks(y_pos); ax_bar.set_yticklabels([LABEL.get(b, b) for b in order], fontsize=TICK_SIZE)
    ax_bar.invert_yaxis()
    ax_bar.set_xlabel(r'Screening regret $f_\mathrm{HF}[\arg\min f_\mathrm{LF}] - f^*_\mathrm{HF}$ (HF units)',
                      fontsize=LABEL_SIZE, labelpad=2)
    ax_bar.set_title('LF-only screening regret', fontsize=TITLE_SIZE, pad=6)
    panel_letter(ax_bar, 'b', x=-0.30, y=1.02, size=LETTER_PT)
    ax_bar.grid(axis='x', alpha=0.3, lw=0.4); ax_bar.set_axisbelow(True)
    ax_bar.tick_params(axis='both', labelsize=TICK_SIZE, pad=1.5)
    ax_bar.tick_params(axis='y', length=0)
    for sp in ('top', 'right'): ax_bar.spines[sp].set_visible(False)
    for i, (b, val) in enumerate(zip(order, sr.values)):
        marker = ('✓ top-1 hit' if int(top1[b]) == 1 else '✗ top-1 miss') + f'  ({val:.3g})'
        ax_bar.text(val * 1.25 + 0.02, i, marker, va='center', fontsize=NOTE_SIZE, color='#333')
    ax_bar.set_xlim(0, xmax * 30)
    ax_bar.set_xticks([0, 0.1, 1, 10, 100, 1000]); ax_bar.set_xticklabels(['0', '0.1', '1', '10', '100', '1000'], fontsize=TICK_SIZE)
    handles = [Patch(facecolor=REGIME_A, label='Regime A (regret ≤ 0.3)'),
               Patch(facecolor=REGIME_B, label='Regime B (regret > 0.3)')]
    ax_bar.legend(handles=handles, fontsize=LEGEND_SIZE, loc='upper right', frameon=True, edgecolor='gray', borderpad=0.5)
    plt.tight_layout(w_pad=2.0, rect=(0, 0.20, 1, 1))
    save_dual(fig, NEWFIGS / 'B2_topk_13')
    plt.close(fig)


if __name__ == '__main__':
    main()
