# Figure regeneration 2026-09-16 — Fig. 1 panels o and p become the mean deficit to the per-benchmark best

Panels **o** and **p** only. The per-benchmark panels **b**--**n** are unchanged (same metric, budgets, seed
set, colours, sorting and values); the only addition to them is a grey `→ better` cue at the right end of the
subtitle line. No run was executed and no data path was touched: `fig1_attainment_values.csv` is bit-identical
before and after (section 4).

All work was done on the VM `l40s` with `/mnt/data/jaewook_mfbo/bo_env/bin/python`, root
`R = /mnt/data/jaewook_mfbo/MFBO-TL-Paper/experiments/refig_20260908`. The pre-edit script, PDF/PNG/SVG and
value files are archived in `$R/_backup_op_deficit_20260916/` (with `md5_BEFORE.txt`); the superseded figure is
kept there as `fig1_attainment.pdf.score`.

## 1. What the panels show now

Within each benchmark, the highest mean attainment among the eight surrogates minus the surrogate's own mean
attainment (its deficit to the best surrogate of that benchmark); the deficits are averaged over benchmarks
(o: the thirteen benchmarks, p: the nine chemistry and materials benchmarks). Bars start at 0 and are sorted
ascending, so the leftmost bar is the smallest deficit; the error bar is the s.e.\ over the paired
per-benchmark deficits. Axis 0--0.20 (o) and 0--0.12 (p) with ticks every 0.05, y label `Deficit to best`,
grey subtitle `↓ better`, titles `o  All benchmarks` and `p  Chem & Mat`, no per-benchmark dots and no
triangles. Because the per-benchmark best is a constant within a benchmark, the mean deficit equals a constant
minus the mean attainment: differences between surrogates are identical in the two summaries and the ordering
is the same (Supplementary Table 10 prints both).

The approved rendering is `$R/threshold_sweep_20260916/op_fix/full/full_fig1_v7.py`, variant **V7a**. The o/p
code, the cue placement and the extra footnote line were taken from it verbatim; the pipeline keeps its own
(current) abbreviation footnote, which is the only difference between the two PDFs (section 5).

## 2. Files edited (paths relative to `$R` on `l40s`)

### `figcand2_20260914_5tl/scripts/fig1_attainment_exact.py`

1. Docstring: the panel description and the three `SUMMARY` modes are documented; `deficit` is the default.
2. New constants after `SUB, LEG, FOOT, SUMTICK = 6.5, 7.5, 6.5, 6.8`:
   - after: `CUE_FS, SUB_GREY = 5.3, "#555555"` and `YMAX_D = {"13pools": 0.20, "9chem": 0.12}`
3. b--n loop, direction cue added after the `B = …` subtitle:
   - after: `a.text(1.0, 1.02, "→ better", transform=a.transAxes, ha="right", va="bottom", fontsize=CUE_FS, color=SUB_GREY)`
   - the `B = …` line now takes `color=SUB_GREY` (same `#555555` as before).
4. Summary mode:
   - before: `SUMMARY = os.environ.get("SUMMARY", "score")`
   - after: `SUMMARY = os.environ.get("SUMMARY", "deficit")`
5. `summary_panel(a, letter, pools, title, subtitle, ylabel, bold=False)` -> `summary_panel(a, letter, pools, title, scope, ylabel, bold=False)`; in deficit mode it computes
   ```
   A_ = Tsub.pivot(index="pool", columns="model", values="mean").loc[pools, MODELS]
   Dd = pd.DataFrame(A_.max(axis=1).values[:, None] - A_.values, index=pools, columns=MODELS)
   M  = pd.DataFrame(dict(mean=Dd.mean(), se=Dd.std(ddof=1) / np.sqrt(len(pools)), n=len(pools), raw_mean=A_.mean()))
   M  = M.sort_values("mean", ascending=True)
   ```
   and draws `a.set_ylim(0, YMAX_D[scope])` with ticks `np.arange(0, ymax + 1e-9, 0.05)`, the subtitle
   `↓ better` at `CUE_FS`, and the y label `Deficit to best`. The `score` and `mean` branches are unchanged.
6. y label:
   - before: `ylab = "Mean attainment" if SUMMARY == "mean" else "Normalised score"`
   - after: `ylab = {"mean": "Mean attainment", "score": "Normalised score", "deficit": "Deficit to best"}[SUMMARY]`
7. Summary CSVs: in deficit mode the index is the abbreviation printed in the figure (`sumcsv()`), and the
   columns are `mean, se, n, raw_mean` (`raw_mean` = mean attainment over benchmarks, for reference).
8. Footnote: in deficit mode one line is appended,
   `"o, p: mean deficit to the best surrogate of each benchmark (lower is better)"`. The two abbreviation
   lines are unchanged.
9. Output stem:
   - before: `STEM = "fig1_attainment" if SUMMARY == "score" else f"fig1_attainment_{SUMMARY}"`
   - after: `STEM = "fig1_attainment" if SUMMARY == "deficit" else f"fig1_attainment_{SUMMARY}"`
   (`SUMMARY=score` now writes `fig1_attainment_score.*` and no longer overwrites the paper figure; its
   `fig1_attainment_summary_score{,_chem}.csv` are still written and are bit-identical to the 2026-09-14 files.)

md5 of the script: `eadd205d6b38ddeaeb3a429f501d04ae` -> `6a728161de4f4caa92c7cddb4afb6c50`.

### `reproducibility/verify/verify_paper_numbers_5tl.py` (this repository)

A deficit block was added after the normalised-score block (which is kept and marked
`superseded reference`): `deficit_summary()` recomputes, from the raw run cells, the per-benchmark best minus
each surrogate's mean attainment, averages over benchmarks and takes the s.e.\ over benchmarks; it is compared
against the two new summary CSVs (mean, s.e.\ and raw mean; the check is `< 1e-9`) and it records in REPORT
both orderings, the check that on the nine chemistry and materials benchmarks all five TL deficits are below
all three GP deficits, and the check that on the thirteen benchmarks the raw-mean range is at most 0.07 with
DKL at the smallest deficit.

## 3. Commands run (exact, in order)

```
PY=/mnt/data/jaewook_mfbo/bo_env/bin/python
R=/mnt/data/jaewook_mfbo/MFBO-TL-Paper/experiments/refig_20260908
cd $R/figcand2_20260914_5tl/scripts && SUMMARY=deficit $PY fig1_attainment_exact.py
# verification, from a scratch mirror of this repository's reproducibility/ tree:
cd /mnt/data/jaewook_mfbo/verify_scratch_op_deficit_20260916/reproducibility/verify
OUT=/mnt/data/jaewook_mfbo/verify_out_op_deficit_20260916 $PY verify_paper_numbers_5tl.py
```

`export_explorer_exact.py` was **not** re-run: `explorer_data.json` is unchanged
(`7030f472b3399c2ba03f270a97f0996e`).

## 4. md5 before / after

| file | before | after |
| --- | --- | --- |
| `fig1_attainment.pdf` | `81ac57708d4513b4e02882eb8ecfa7f2` | `bc9e60341f1635d0e8f6561a8adb6762` |
| `fig1_attainment.png` | `599a8cd71f320f4c7ebfdb37fcebbb5d` | `e953e47aac319802825896de658cd1f9` |
| `fig1_attainment.svg` | `9d3e4f870a387d0df59a8b050a7e1e95` | `8b1ba7d93fc9ea28e25082d83463fd4d` |
| `fig1_attainment_values.csv` | `55cdae422a9778388ec8b39acd489dfe` | `55cdae422a9778388ec8b39acd489dfe` (unchanged) |
| `explorer_data.json` | `7030f472b3399c2ba03f270a97f0996e` | `7030f472b3399c2ba03f270a97f0996e` (unchanged) |
| `fig1_attainment_summary_score.csv` | `52293229fbc2fe7a9941e58bfb5f9b2b` | `52293229fbc2fe7a9941e58bfb5f9b2b` (unchanged) |
| `fig1_attainment_summary_score_chem.csv` | `0b94382ca43ca5a188d726c7bfd81298` | `0b94382ca43ca5a188d726c7bfd81298` (unchanged) |
| `fig1_attainment_summary_deficit.csv` | — | `aaac21ba9441b97ea14849c8766d8dd7` (new) |
| `fig1_attainment_summary_deficit_chem.csv` | — | `5e54bc82fde5049e89f1966fa91bacea` (new) |

## 5. The two summaries

Panel o, thirteen benchmarks (bar order, left to right):

| surrogate | mean deficit | s.e. | mean attainment |
| --- | --- | --- | --- |
| DKL | 0.069 | 0.016 | 0.686 |
| TL-E2E | 0.081 | 0.032 | 0.673 |
| TL-base | 0.084 | 0.038 | 0.671 |
| MFGP | 0.096 | 0.027 | 0.659 |
| TL-SPS | 0.124 | 0.058 | 0.631 |
| TL-MMD | 0.126 | 0.060 | 0.629 |
| TL-PtJ | 0.130 | 0.061 | 0.625 |
| SV-MFGP | 0.131 | 0.044 | 0.623 |

Panel p, nine chemistry and materials benchmarks (bar order, left to right):

| surrogate | mean deficit | s.e. | mean attainment |
| --- | --- | --- | --- |
| TL-base | 0.013 | 0.007 | 0.688 |
| TL-MMD | 0.023 | 0.009 | 0.678 |
| TL-E2E | 0.033 | 0.012 | 0.668 |
| TL-PtJ | 0.053 | 0.025 | 0.649 |
| TL-SPS | 0.055 | 0.032 | 0.647 |
| DKL | 0.070 | 0.021 | 0.631 |
| SV-MFGP | 0.083 | 0.030 | 0.619 |
| MFGP | 0.089 | 0.024 | 0.612 |

Full precision in `reproducibility/values/figcand2_20260914_exact/fig1_attainment_summary_deficit{,_chem}.csv`.
Against the reference run `$R/threshold_sweep_20260916/op_fix/full/v7_numbers.json` (variant V7a) the bar
order is identical in both panels and the largest absolute difference in mean or s.e.\ is `8.3e-17`.

Rendered at 200 dpi, the new `fig1_attainment.pdf` and `V7a.pdf` differ in 1.07 % of their pixels, all of them
inside the two abbreviation footnote lines (rows 1071--1110 of 1140): V7a spells the abbreviations out with
the pre-2026-09-16 model names, the pipeline uses the current footnote. All fifteen panels, the cues, the
titles, the legend and the `o, p: …` footnote line are pixel-identical. The longest footnote line ends at
0.93 of the figure width.

## 6. Verification

`OUT=/mnt/data/jaewook_mfbo/verify_out_op_deficit_20260916`, section 2 of `report.md`:

```
  panel o/p max |diff| vs the deficit summary csvs (mean, s.e., raw mean): 1.11e-16 / 1.11e-16; both < 1e-9: True
  panel o bar order (smallest deficit first): DKL < TL-E2E < TL-base < MFGP < TL-SPS < TL-MMD < TL-PtJ < SV-MFGP
  panel p bar order (smallest deficit first): TL-base < TL-MMD < TL-E2E < TL-PtJ < TL-SPS < DKL < SV-MFGP < MFGP
  p (9 chem/mat): all five TL deficits below all three GP deficits: True (TL 0.013-0.055, GP 0.070-0.089)
  o (13 benchmarks): raw mean attainment range 0.0625 (<= 0.07: True); smallest deficit DKL 0.069; deficit range 0.069-0.131
  cells: 104 (ref 104); n identical: True; max |mean diff| vs fig1_attainment_values.csv = 4.44e-16
  panel o/p max |diff| vs summary csvs: 8.88e-16 / 1.22e-15        (superseded normalised-score reference)
```

The recomputation starts from the raw run cells, not from the value CSVs.

## 7. Files written in this repository

```
paper_figures/fig1_attainment.pdf
reproducibility/values/figcand2_20260914_exact/fig1_attainment_summary_deficit.csv
reproducibility/values/figcand2_20260914_exact/fig1_attainment_summary_deficit_chem.csv
reproducibility/values/figcand2_20260914_exact/md5_outputs.txt
reproducibility/verify/verify_paper_numbers_5tl.py
reproducibility/figure_manifest.csv                  (Fig. 1 b-p row)
reproducibility/claim_manifest.csv                   (C17, C21)
reproducibility/values/REGEN_OP_DEFICIT_20260916.md  (this file)
main.tex          (Fig. 1 caption o/p; Results 2.2 and 2.3; Methods summary definition; header comment)
si-content.tex    (new Supplementary Table 10, supptab:op_summary)
si.tex            (Supplementary Tables 1--11 in the SI abstract)
```
