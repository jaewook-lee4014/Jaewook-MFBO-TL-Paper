# Re-render of 2026-09-17: bold panel letters, print-size Fig. 4 and SI Fig. 4, Fig. 3 d-f

Pre-submission layout pass (author decision of 2026-09-17, item 1 of the final check). No value changes: every value
csv behind the eight figures has the same md5 before and after (checked on the VM, `md5_BEFORE.txt` / `md5_AFTER.txt`
in `$R/_backup_boldletters_20260917/`, which also holds the pre-edit scripts and PDFs).

## 1. What changed

| Figure | File | md5 before -> after | Change |
|---|---|---|---|
| Fig. 1 b-p | paper_figures/fig1_attainment.pdf | f964ecc4 -> acc16c02 | panel letters bold, 8 pt in print (label unchanged, regular 7.5 pt) |
| Fig. 2 a-m | paper_figures/fig2_trajectories.pdf | b897ac76 -> f3d7c92e | same |
| Fig. 3 a-f | paper_figures/fig3_grid_final_regret.pdf | 52d301e7 -> ebcda350 | a-c bold; new letters d-f on the marginal-profile row (caption and Results 2.3 now cite Fig. 3d-f) |
| Fig. 4 a,b | paper_figures/B2_topk_13.pdf | 80c6d7dd -> b0746678 | drawn at print width (7.2 in, was 12.6 in): 6.5/7/7.5 pt text, bold letters; colour-blind-safe encoding of the 13 curves (Okabe-Ito hues + distinct line styles for the six single pools; the Branin/Park pairs and the elastic ladder keep one hue in shades); legend in four columns |
| SI Fig. 1 a-i | paper_figures/supp_acq_matrix.pdf | 61a0a1f4 -> 351c92d3 | bold letters (rendered locally by reproducibility/render_acquisition_controls.py) |
| SI Fig. 2 a-k | paper_figures/supp_acq_portfolio.pdf | ee4ec342 -> dd0d020f | bold letters |
| SI Fig. 3 a-m | paper_figures/fig4_calibration_attain.pdf | 831bec45 -> 4d19f11a | bold letters |
| SI Fig. 4 a-j | paper_figures/computing_time_blr.pdf | 78fc654d -> a15d5824 | drawn at print width (7.2 x 3.9 in, was 15 x 7 in): 6/6.5/7.5 pt text, 5.5 pt bar values, bold letters |

Fig. 5 (compute_scaling_law_blr.pdf, single panel, no letter) and Fig. 1a (fig1_overview.pdf, letter overlaid in main.tex)
were not re-rendered.

## 2. Mechanism

All scripts that wrote the letter and the panel label as one string (`f"{letter}  {label}"`, regular weight) now call a
small helper `_panel_title(ax, letter, label, x, y, fs, letter_fs)`: it draws the letter in bold at `letter_fs`
(8.4 pt in the 7.2 in figures, which print at 0.955 x -> 8.0 pt; 9.1 pt in Fig. 4, which prints at 0.88 x), measures its
rendered width and places the label after it in regular weight at the panel-title size. Fig. 3 draws its letters
separately and only gained `fontweight='bold'` plus the d-f letters (`FIG1LN_LETTERS=a,b,c,d,e,f`).

## 3. Scripts and commands (VM `l40s`, `R=/mnt/data/jaewook_mfbo/MFBO-TL-Paper/experiments/refig_20260908`,
`PY=/mnt/data/jaewook_mfbo/bo_env/bin/python`; the patch script `vm_patch_letters.py`, the new
`make_b2_topk_13.py` and the driver `vm_render.sh` are in `$R/_backup_boldletters_20260917/` and in
`reproducibility/snapshot/refig_20260908/boldletters_20260917/`)

```
bash $R/_backup_boldletters_20260917/vm_render.sh      # backs up, patches, renders, compares md5
# which runs, in order:
cd $R && $PY figcand2_20260914_5tl/scripts/fig1_attainment_exact.py
cd $R && $PY figcand2_20260914_5tl/scripts/fig2_trajectories_exact.py
cd $R/figrepo/figures && ECE_X=mean CAL_LETTERS=abcdefghijklm CAL_STEM=fig4_calibration_attain \
    $PY ../../figcand2_20260914_5tl/scripts/make_a1_calibration_13_attain_exact.py
cd $R && $PY supp_attain_5tl.py S2
cd $R/figrepo/figures && FIG_OUT=fig5tl_20260914 FIG_OUT_DIR=$R/figrepo/figures/out/fig5tl_20260914 \
    FIG1LN_LETTERS=a,b,c,d,e,f FIG_STEM=fig_grid_final $PY make_fig1ln_final_5tl.py   # FIG_OUT_DIR must be absolute
cd $R/figrepo/figures && MPLBACKEND=Agg FIG_OUT=fig5_13 $PY make_b2_topk_13.py
cd $R/figrepo/figures && FIG_OUT=fig5tl_20260914 GP_VARIANTS=DKL $PY plot_computing_flops_blr_5tl.py
# SI Fig. 1, locally in the manuscript repository:
python reproducibility/render_acquisition_controls.py
```

Note: `vm_render.sh` passed a relative `FIG_OUT_DIR` to `make_fig1ln_final_5tl.py`, so its output first landed in
`$R/figrepo/figures/figrepo/figures/out/fig5tl_20260914/`; it was copied to the proper `out/fig5tl_20260914/` by hand
(md5 ebcda350; the cells csv there is identical, 7e324af1).

## 4. Checks

- Value csv md5 unchanged: fig1_attainment_values, fig1_attainment_summary_deficit(_chem), fig2_trajectories_values,
  fig4_calibration_attain_values, supp_acq_portfolio_{values,winshare,meandelta}, fig1ln_final_cells,
  computing_flops_values_blr, B2_topk_13_values (VM) and supp_acq_matrix_values (local).
- `pdffonts`: DejaVuSans-Bold embedded (Type 42) in all eight PDFs; page sizes 518 x 410 / 403 / 360 / 454 / 389 pt
  (Fig. 1, 2, SI 3, SI 2, SI 1), 471 x 286 (Fig. 3), 515 x 291 (Fig. 4), 545 x 282 (SI Fig. 4).
- 130 dpi renders inspected: letters bold and aligned with the labels; Fig. 3 d-f sit at the top-left of the profile
  panels; Fig. 4 legend (14 entries, 4 columns) clears the curves; SI Fig. 4 bar values legible.

## 5. Fig. 1a (same day, second author request)

- The "TL-base >= GP-base on all 9 molecular & materials pools" line under the regret sketch was removed from
  `paper_figures/fig1_overview.tex` and the schematic rebuilt with `pdflatex fig1_overview.tex`
  (md5 005c2a48 -> 8f8dbc97; 636 x 177 pt).
- The panel letter "a" was a LaTeX-overlaid Helvetica Bold 8 pt and printed visibly smaller than the DejaVu Sans Bold
  letters of b-p. It is now `paper_figures/fig1_letter_a.pdf` (md5 7ad43138), the DejaVu Sans Bold glyph at 8.4 pt drawn
  by matplotlib (`patch_fig1a.py` in the boldletters_20260917 snapshot), included in main.tex at scale 0.955, i.e. the
  scale of fig1_attainment.pdf, so a and b-p print with the same glyph at 8.0 pt.
- The overview is now included at \textwidth (was 0.9\textwidth), so its edges align with the attainment panels; page 2
  still holds Fig. 1 and its caption (checked in the rebuilt main_clean.pdf, 15 pages).

## 6. Fig. 3 letters and Figs. 4/5 placement (same day, third author request)

- Fig. 3 profile row carries ONE letter, d (the row is cited once, as Fig. 3d); re-rendered with
  `FIG1LN_LETTERS=a,b,c,d` (md5 ebcda350 -> e72e36e2; cells csv unchanged, 7e324af1). Caption: "d, Per-condition
  advantage for the three comparisons (left to right as in a-c) ...".
- Figs. 4 and 5 had been packed onto one float page after Fig. 4 became shorter; Fig. 5 is now `figure*[t]` (top of
  page only), so Fig. 4 sits on page 7 and Fig. 5 on page 8 with text below each (author preference).
