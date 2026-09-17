"""Fig. 1a fixes (user request 2026-09-17): (1) panel letter "a" drawn with the same DejaVu Sans Bold glyph and size as the
b-p letters of fig1_attainment.pdf (matplotlib PDF, included at the same scale), (2) the "TL-base >= GP-base on all 9
molecular & materials pools" line removed from the overview schematic, (3) overview included at \textwidth like b-p."""
import os
os.chdir('/cephfs/volumes/hpc_data_prj/eng_waste_to_protein/ae035a41-20d2-44f3-aa46-14424ab0f6bf/repositories/Jaewook-MFBO-TL-Paper/.claude/worktrees/final-check-20260917')

def rep(s, a, b, n=1):
    assert s.count(a) == n, (s.count(a), a[:90]); return s.replace(a, b)

# ---- (1) the letter PDF: DejaVu Sans Bold, 8.4 pt = the letter_fs of the 7.2 in figures (prints at 8 pt after x 0.955)
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
plt.rcParams.update({'pdf.fonttype': 42, 'font.family': 'DejaVu Sans'})
fig = plt.figure(figsize=(0.3, 0.3))
fig.text(0.0, 0.0, 'a', fontsize=8.4, fontweight='bold', ha='left', va='baseline')
fig.savefig('paper_figures/fig1_letter_a.pdf', bbox_inches='tight', pad_inches=0.0, transparent=True)
plt.close(fig)

# ---- (2) fig1_overview.tex: drop the TL-base >= GP-base line, update the header comment
p = 'paper_figures/fig1_overview.tex'; s = open(p).read()
s = rep(s, "\\node[text=sub, font=\\footnotesize, anchor=north] at (\\Cc,2.62) {TL-base $\\geq$ GP-base on all 9 molecular \\& materials pools};\n", "")
s = rep(s, "%% Frozen-representation transfer, Pretrain-then-Joint, End-to-End Joint, Soft Parameter Sharing and Domain Adaptation\n%% (MMD)) and to the Fig. 1b-p attainment result (TL-base at or above GP-base on all 9 molecular & materials pools).\n",
        "%% Frozen-representation transfer, Pretrain-then-Joint, End-to-End Joint, Soft Parameter Sharing and Domain Adaptation\n%% (MMD)). 2026-09-17: the \"TL-base >= GP-base on all 9 molecular & materials pools\" line under the regret sketch was removed\n%% (author decision); the panel letter is no longer overlaid in LaTeX text but included as paper_figures/fig1_letter_a.pdf\n%% (DejaVu Sans Bold, the glyph of the b-p letters).\n")
open(p, 'w').write(s)

# ---- (3) main.tex: overlay the DejaVu letter at the b-p scale, overview at \textwidth
p = 'main.tex'; s = open(p).read()
s = rep(s, "%% Display item 1 of 6: (a) overview (paper_figures/fig1_overview.tex; the letter is overlaid in LaTeX below) and\n%% (b--p) attainment on the 13 benchmarks (fig1_attainment.pdf, letters baked in); overview at 0.9\\textwidth so the composite fits the page.\n\\makebox[0.9\\textwidth][l]{\\fontsize{8}{9}\\selectfont\\textsf{\\textbf{a}}}\\\\[1pt]\n\\includegraphics[width=0.9\\textwidth]{paper_figures/fig1_overview.pdf}\\\\[1pt]\n",
        "%% Display item 1 of 6: (a) overview (paper_figures/fig1_overview.tex; the letter a is paper_figures/fig1_letter_a.pdf, the DejaVu Sans Bold\n%% glyph of the b--p letters, included at the scale of fig1_attainment.pdf = \\textwidth / 518.4 pt = 0.955) and\n%% (b--p) attainment on the 13 benchmarks (fig1_attainment.pdf, letters baked in); both at \\textwidth (2026-09-17).\n\\makebox[\\textwidth][l]{\\includegraphics[scale=0.955]{paper_figures/fig1_letter_a.pdf}}\\\\[2pt]\n\\includegraphics[width=\\textwidth]{paper_figures/fig1_overview.pdf}\\\\[1pt]\n")
open(p, 'w').write(s)
print('fig1a patch ok')
