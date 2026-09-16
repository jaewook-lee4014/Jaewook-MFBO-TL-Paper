# Figure regeneration 2026-09-16 — Gaussian-process surrogate labels renamed to the GP- prefix

Labels only, with one exception that is flagged throughout: **Fig. 1 panels o and p** also change design
(the V7a summary, decided the same day) and are documented in section 6. No run was executed, and no
metric, budget, seed set, colour, panel order or data path was touched. Every value file is bit-identical
to the 2026-09-16 TL-label render once the label strings are mapped; the proof is in section 5.

All work was done on the VM `l40s` with `/mnt/data/jaewook_mfbo/bo_env/bin/python`, root
`R = /mnt/data/jaewook_mfbo/MFBO-TL-Paper/experiments/refig_20260908`. The pre-edit PDFs, value files and
scripts are archived in `$R/_backup_labels_gp_20260916/` (with `md5_BEFORE.txt`); the renders used for the
layout checks are in `$R/_backup_labels_gp_20260916/render/`.

## 1. Rename table

| internal display-name key (unchanged) | abbreviation before | abbreviation after |
| --- | --- | --- |
| `MFGP` | `MFGP` | `GP-base` |
| `Sparse MFGP` | `SV-MFGP` | `GP-SV` |
| `DKL` / `DKL Multi-Fidelity` | `DKL` | `GP-DKL` |
| the five TL surrogates | `TL-base` … `TL-MMD` | unchanged |

Footnote / legend expansion, before:

```
GP: MFGP = baseline MFGP · SV-MFGP = sparse variational MFGP · DKL = deep-kernel GP
```

after:

```
GP: GP-base = autoregressive multi-fidelity GP (MFGP) · GP-SV = sparse variational MFGP · GP-DKL = deep-kernel GP
```

The TL half of every footnote, every family label (`Gaussian-process family`, `Gaussian-process (GP) family`,
`Transfer-learning (TL) surrogates`, `GP cheaper`, `TL cheaper`, the `TL: ` / `GP: ` footnote prefixes) and
every display-name key are unchanged.

## 2. Files edited (all paths relative to `$R` on `l40s`)

### `figcand2_20260914_5tl/scripts/prep_candidates2.py` — line 53 (`ABBR` values only)
- before: `ABBR = {"MFGP": "MFGP", "Sparse MFGP": "SV-MFGP", "DKL": "DKL", "Frozen-representation transfer": "TL-base", …}`
- after: `ABBR = {"MFGP": "GP-base", "Sparse MFGP": "GP-SV", "DKL": "GP-DKL", "Frozen-representation transfer": "TL-base", …}`
- `RENAME`, `GP`, `TL`, `ORDER`, `LINECOL`, `MERGED` untouched. This dict is baked into `explorer_data.json`
  by `export_explorer_exact.py`, which Fig. 1, Fig. 2 and `supp_attain_5tl.py` read.

### `figcand2_20260914_5tl/scripts/fig1_attainment_exact.py` — footnote (lines 147-151) and the o/p csv
- footnote, before (2 lines + the o/p note):
  `"TL-MMD = domain adaptation (MMD)    GP: MFGP = baseline MFGP · SV-MFGP = sparse variational MFGP · DKL = deep-kernel GP"`
- after (3 lines; see the layout note in section 4):
  `"TL-MMD = domain adaptation (MMD)    GP: GP-base = autoregressive multi-fidelity GP (MFGP)"` /
  `"GP-SV = sparse variational MFGP · GP-DKL = deep-kernel GP"` , and under `SUMMARY=deficit` the o/p note
  `"    o, p: mean deficit to the best surrogate of each benchmark (lower is better)"` is appended to that
  third line instead of occupying a fourth one.
- added after the summary print: the combined `fig1_summary_deficit.csv`
  (`scope, surrogate, mean_attainment, mean_deficit, se_over_benchmarks`, 16 rows = 8 surrogates x 2 scopes).
- the V7a panel code itself (panels o, p, the `→ better` / `↓ better` cues) was already in the file when this
  pass started; it is described in section 6.

### `figcand2_20260914_5tl/scripts/fig2_trajectories_exact.py` — line 95 (`FOOTNOTE`, GP line)
### `figcand2_20260914_5tl/scripts/make_a1_calibration_13_attain_exact.py` — line 41 (`ABBR` values) and line 84 (GP footnote)
- `NAMES`, `GP`, `TL`, `STYLE`, `MS` untouched; the point colours and markers are keyed on the display names.

### `supp_attain_5tl.py` — lines 12, 150, 165, 190-191, 194, 207, 211, 212, 214, 219, 311
- line 150 `FOOT2` and line 311 `NOTE2[-1]`: GP key replaced as in section 1.
- line 165 (SI Fig. 1 `COND`, the y-tick labels of panels a-i and the `condition` column of
  `supp_acq_matrix_values.csv`): `("MFGP EI", …), ("MFGP greedy", …)` -> `("GP-base EI", …), ("GP-base greedy", …)`.
  The third element of each tuple (`"MFGP"`, the raw model key) is untouched.
- lines 190, 191, 211, 219 (heat-map row labels and the csv/json row index): the literal `["MFGP"]` becomes
  `[ABBR["MFGP"]]`, so the row label follows `explorer_data.json` exactly as the TL rows already did.
- line 207 (legend): `label="MFGP · EI (default)"` / `label="MFGP · greedy"` -> `label="GP-base · EI (default)"` /
  `label="GP-base · greedy"`.
- line 212 (panel j subtitle) and line 214 (side note): `MFGP row` -> `GP-base row`, `MFGP EI n = 39` -> `GP-base EI n = 39`.
- line 12: docstring wording follows the same rename.
- line 194 — **layout fix**, see section 4.
- the `RAW` map (raw run name -> display name) and the `NAMES` dict are untouched.

### `figrepo/figures/_common.py` — `CODE_NAMES` (three new entries after line 71) and `CODE_KEY_GP` (line 98)
- three entries `'MFGP': 'GP-base'`, `'Sparse MFGP': 'GP-SV'`, `'DKL Multi-Fidelity': 'GP-DKL'` are appended to the
  dict literal and deliberately **shadow** the same keys in the 12-surrogate head (the head lines are left
  textually untouched, and the later entries win) — the same approach used for `TL-SPS` / `TL-MMD` on 2026-09-14.
  This is what gives SI Fig. 3 its `GP-base` / `GP-SV` / `GP-DKL` axis codes.
- `CODE_KEY_GP` before: `'GP family:  MFGP = baseline MFGP · … · SV-MFGP = sparse variational MFGP'`;
  after: `'GP family:  GP-base = autoregressive multi-fidelity GP (MFGP) · … · GP-SV = sparse variational MFGP'`
  (the `DKL` entry of the variant dict becomes `GP-DKL = deep-kernel GP`). The string keeps its existing
  `base · variant · sparse` order; no paper figure uses it (the two live scripts use `CODE_KEY_TL_5` and a
  literal GP line).
- `RENAME_5TL`, `TL5_PROFILE`, `SHORT_NAMES`, `CODE_KEY_TL`, `CODE_KEY_TL2`, `CODE_KEY_TL_5` untouched.

### `figrepo/figures/make_fig1ln_final_5tl.py` — lines 22-24 (family keys) and the docstring
- before: `FAMILIES = {'TL': TL5, 'MFGP baseline': ['MFGP'], 'MFGP variants': ['DKL', 'SparseMFGP']}` /
  `COMPARISONS = [('TL', 'MFGP baseline'), ('TL', 'MFGP variants'), ('MFGP variants', 'MFGP baseline')]`
- after: `FAMILIES = {'TL': TL5, 'GP-base': ['MFGP'], 'GP variants': ['DKL', 'SparseMFGP']}` /
  `COMPARISONS = [('TL', 'GP-base'), ('TL', 'GP variants'), ('GP variants', 'GP-base')]`
- the map titles therefore read `TL vs GP-base`, `TL vs GP variants`, `GP variants vs GP-base`, the per-map
  annotation reads `GP variants better in 81/126 · ties 45`, and the three comparison columns of
  `fig1ln_final_cells.csv` are renamed with them. The member lists (`'MFGP'`, `'DKL'`, `'SparseMFGP'`) are
  raw model keys and are untouched.

### `figrepo/figures/plot_computing_flops_blr_5tl.py` — line 119 (GP footnote)
- the tick labels come from `_common.code`, so they follow `CODE_NAMES` above. The two `print()` diagnostics on
  lines 76-77 (`MFGP {…}`, `Sparse {…}`) write to the console, not to the figure, and were left alone.

### `figrepo/figures/make_scaling_law_blr_5tl.py` — not edited
Fig. 5c carries family labels only (`Gaussian-process family`, `Transfer-learning surrogates`, `GP cheaper`,
`TL cheaper`); it was re-run for completeness and its page content is byte-identical (section 5).

### Deliberately not edited
`figcand2_20260914_5tl/scripts/prep_candidates2.py` line 199 (the legacy 9-model gallery footnote: it still
spells out `Seq`/`FET`/`SGJ`/`Adpt`, is not executed by `export_explorer_exact.py` and is not a paper figure);
`supp_attain_5tl.py` lines 460-461 and 506 (`fig_S6`, which builds its own `MFGP baseline` / `MFGP variants`
family map — S4/S5/S6 are not paper figures and were not regenerated); the stale legacy copies at `$R/*.py`.

## 3. Command sequence (exact, in order)

```
PY=/mnt/data/jaewook_mfbo/bo_env/bin/python
R=/mnt/data/jaewook_mfbo/MFBO-TL-Paper/experiments/refig_20260908
cd $R
$PY figcand2_20260914_5tl/scripts/export_explorer_exact.py
$PY figcand2_20260914_5tl/scripts/fig1_attainment_exact.py                 # SUMMARY defaults to "deficit"
$PY figcand2_20260914_5tl/scripts/fig2_trajectories_exact.py
cd $R/figrepo/figures && ECE_X=mean CAL_LETTERS=abcdefghijklm CAL_STEM=fig4_calibration_attain \
    $PY ../../figcand2_20260914_5tl/scripts/make_a1_calibration_13_attain_exact.py
cd $R && $PY supp_attain_5tl.py S1 S2
cd $R/figrepo/figures && FIG_OUT=fig5tl_20260914 GP_VARIANTS=DKL $PY make_scaling_law_blr_5tl.py
cd $R/figrepo/figures && FIG_OUT=fig5tl_20260914 GP_VARIANTS=DKL $PY plot_computing_flops_blr_5tl.py
cd $R/figrepo/figures && FIG_OUT=fig5tl_20260914 FIG_OUT_DIR=$R/figrepo/figures/out/fig5tl_20260914 \
    FIG1LN_LETTERS=a,b,c FIG_STEM=fig_grid_final $PY make_fig1ln_final_5tl.py
```

Two changes against the 2026-09-16 TL note: Fig. 1 is no longer run with `SUMMARY=score` (the default
`deficit` is the published panel set; `SUMMARY=score` now writes the superseded variant to
`fig1_attainment_score.*`), and `make_fig1ln_final_5tl.py` (Fig. 3) is run because its map titles carry the
family labels. `merge_grid5tl.py` and `make_b2_topk_13.py` were **not** run (Fig. 5a,b carries pool labels only,
and the grid cells themselves are unchanged).

## 4. Layout fixes (two, both in SI Fig. 1)

`supp_attain_5tl.py` line 194, `fig_S1` gridspec: `left=0.085 -> 0.095` and `wspace=0.72 -> 0.80`.

Reason (measured on the PDF word boxes with `pdftotext -bbox`, page 518.4 x 432 pt):
- the row label `GP-base greedy` is 42.2 pt wide at 5.4 pt against the 44.1 pt left margin, so in the first
  column it started at x = 0.00 pt, flush against the figure edge. With `left = 0.095` it starts at 5.20 pt.
- the narrower columns that follow from that left margin pushed the value label of each panel to within
  1.41 pt (0.50 mm) of the `GP-base` row label of the panel to its right (worst pair: Polarizability `0.95`
  -> HOPV15 `GP-base`). `wspace = 0.80` restores the clearance to 3.72 pt (1.31 mm), wider than the 2.3 pt
  that the TL pass accepted for `TL-E2E greedy`. The rightmost ink is at 516.0 pt, inside the 518.4 pt page.

Font sizes, colours, hatches, panel order, letters and data are unchanged.

No other figure needed a fix:
- Fig. 1: the new row labels are no wider than the old ones (`GP-base` 0.368 in = `TL-base`; `GP-SV` 0.226 in is
  narrower than the old `SV-MFGP` 0.395 in), and the three footnote lines end at x = 0.928 / 0.655 / 0.936 of
  the figure width. The GP key no longer fits on the second line, which is why it runs on to a third; putting
  the o/p note on that third line keeps the block at the three lines of the V7a layout (fourth line would have
  fallen off the canvas at y = -0.0145).
- Fig. 2, Fig. 4, SI Fig. 2: the GP key is a single centred / right-aligned line — 5.28 in at 6.5 pt (Fig. 2)
  and 4.06 in at 5.0 pt (Fig. 4, SI Fig. 1/2) inside the 7.2 in width.
- Fig. 3 grid maps: the new titles are *shorter* (`GP variants vs GP-base` 1.197 in vs `MFGP variants vs MFGP
  baseline` 1.678 in at 7.5 pt).
- SI Fig. 3: the axis codes grow from `MFGP`/`DKL` to `GP-base`/`GP-DKL`, and the figure is saved with
  `bbox_inches='tight'`, so the canvas absorbs them; the GP key line is 8.53 in inside a 15 in width.

Every regenerated PDF was rendered to PNG at 110 dpi (SI Fig. 1 also at 400 dpi) and inspected;
the renders are in `$R/_backup_labels_gp_20260916/render/`.

## 5. Proof that no number changed

### md5, PDFs (VM = repo `paper_figures/`, verified identical after transfer)

| figure | file | md5 before | md5 after |
| --- | --- | --- | --- |
| Fig. 1 b-p | `fig1_attainment.pdf` | `81ac57708d4513b4e02882eb8ecfa7f2` | `75ca3067830c23b521ade854686cb8a9` |
| Fig. 2 a-m | `fig2_trajectories.pdf` | `914afad694233ff3c78e638ab8fccc8f` | `22509c7e1bd118621406d63e6eff20c4` |
| Fig. 3 a-c | `fig_grid_final.pdf` -> `fig3_grid_final_regret.pdf` | `8bba695e…` | `52d301e71ceae67fb1a1abe81e8df2a9` |
| Fig. 4 a-m | `fig4_calibration_attain.pdf` | `c0d0503801cb11eaefc428d3a203b907` | `831bec45877c7d9cfabab9bf4bc6646d` |
| Fig. 5 c | `compute_scaling_law_blr.pdf` | `800357368ffc5b63acb7900aa2b61cc9` | `5f36b4cbe7bbbf7b96a7a26f20e06a8e` |
| SI Fig. 1 | `supp_acq_matrix.pdf` | `10e715890dced4a4ad887ed09249a6fc` | `09367e914b5bb73861ca4354f387a2f7` |
| SI Fig. 2 | `supp_acq_portfolio.pdf` | `2b8c75497a9bda751fe42d81a3756c2f` | `ee4ec3423b6f9dbdf50a48a9321deaf0` |
| SI Fig. 3 | `computing_time_blr.pdf` | `6b9aa0ac1e176fc95516bd0d92ce0908` | `78fc654d482df927852c15767fdd618f` |

`compute_scaling_law_blr` carries no surrogate label at all: its **PNG** md5 is unchanged
(`c3a22891135a2f61ead2364f1bf3c06e` before and after), so the page content is byte-identical and only the PDF
`CreationDate` differs. The Fig. 3 file shipped in the repository (`8bba695e`) and the pre-rename VM render are
byte-identical, and a 150 dpi raster of the two pre-rename PDFs differs in 0 pixels.

### Value files, md5 unchanged (bit-identical)

```
52293229fbc2fe7a9941e58bfb5f9b2b  fig1_attainment_summary_score.csv
0b94382ca43ca5a188d726c7bfd81298  fig1_attainment_summary_score_chem.csv
97d733d9e1dfd4ac2a5029b3f2802af7  fig2_trajectories_values.csv
c0fe13798d4eb704dbb09a020ba3d359  fig4_calibration_attain_values.csv
9a12e190241b964dd18fdf713e9c46cd  supp_acq_portfolio_values.csv
b485ec2a5a9c240ac082f321b3cc5bf4  supp_acq_portfolio_meandelta.csv
d35a752b846c384251d8c9e930bb7985  supp_acq_portfolio_n_models.csv
3eb2c13e56ef06b025b93eadd7cbfeeb  supp_acq_portfolio_winshare.csv
d9ba24476d384e30f952464adcad52ea  computing_flops_values_blr.csv
24bb0a42352af2d8b7b015df5716f967  scaling_law_blr.json
```

### Value files whose md5 changed — label strings only

| file | md5 before -> after | what differs |
| --- | --- | --- |
| `explorer_data.json` | `7030f472…` -> `815eedc7…` | only the three GP values of the `abbr` dict. The `abbr` keys, `models`, `gp`, `tl` and the whole `pools` payload (per-seed change points, thresholds, budgets, ranges, pool sizes) compare byte-identical under `json.dumps(sort_keys=True)`. |
| `fig1_attainment_values.csv` | `55cdae42…` -> `648be30c…` | only the `abbr` column, which equals the old column under the three renames; `pool`, `model`, `family`, `n`, `mean`, `se` bit-identical; 104 rows both. |
| `supp_acq_matrix_values.csv` | `e64c5f57…` -> `a47ede37…` | only the `condition` column (`MFGP EI`/`MFGP greedy` -> `GP-base EI`/`GP-base greedy`); `mean`, `se`, `n`, `budget` bit-identical. |
| `supp_acq_matrix_delta.csv` | `494c180c…` -> `8d8b12cf…` | only the first row index (`MFGP` -> `GP-base`); the 6 x 9 value array is `np.array_equal` before/after, columns identical. |
| `supp_acq_matrix_delta_n.csv` | `afaeedd7…` -> `8ef146fe…` | as above. |
| `supp_summary.json` | `bbd34390…` -> `c1227827…` | a recursive walk finds exactly three string differences (`S1/conditions[0,1]`, `S1/delta_rows[0]`) plus the `S1/values` composite keys `"<pool>\|MFGP EI"` / `"<pool>\|MFGP greedy"` -> `"<pool>\|GP-base …"`; no numeric value anywhere differs and no list changes length. |
| `fig1ln_final_cells.csv` | `9c335649…` -> `7e324af1…` | only the three comparison column names (`TL\|MFGP baseline`, `TL\|MFGP variants`, `MFGP variants\|MFGP baseline` -> `TL\|GP-base`, `TL\|GP variants`, `GP variants\|GP-base`); the 126 x 8 value array is `np.array_equal` before/after, and the printed map statistics (81/126 · 45, 66/126 · 60, 81/126 · 45; rho -0.81 / -0.78 / -0.72; vmax 0.2593) are unchanged. |

Every remaining difference in each table above was checked to be exactly one of the three documented renames.

## 6. Fig. 1 panels o and p — the V7a design (the one non-label change)

Panels o and p no longer show the per-benchmark min-max **normalised score**; they show the **mean deficit to
the best surrogate of each benchmark** (the highest mean attainment in that benchmark minus the surrogate's
mean attainment, averaged over the benchmarks; bars from 0 upward, sorted smallest = best on the left, mean
± s.e. over benchmarks, no dots, y-label `Deficit to best`, `↓ better` cue, titles `o  All benchmarks` and
`p  Chem & Mat`, y range 0-0.20 for the 13 benchmarks and 0-0.12 for the nine chemistry/materials ones).
Panels b-n are unchanged attainment bars and now carry a `→ better` cue at the right end of the subtitle line.
The design was prototyped as **V7a** in `$R/threshold_sweep_20260916/op_fix/full/full_fig1_v7.py`
(`V7a.pdf/.png`, `v7_numbers.json`); the panel code was ported into the exact script
`figcand2_20260914_5tl/scripts/fig1_attainment_exact.py`, which remains the single source of the paper figure.

Script differences against the 2026-09-16 TL-label version, in summary:
`SUMMARY` now defaults to `deficit` (values `deficit | score | mean`); `summary_panel()` gained the deficit
branch (`A.max(axis=1) - A`, `mean`, `se = std(ddof=1)/sqrt(n_benchmarks)`, ascending sort, `YMAX_D`,
`↓ better` in place of the "13 benchmarks" subtitle); the b-n loop gained the `→ better` cue
(`CUE_FS = 5.3`, `SUB_GREY = "#555555"`); `STEM` is `fig1_attainment` for `deficit` (so `SUMMARY=score` now
writes `fig1_attainment_score.*` instead of overwriting the paper file); the summary csv is written as
`fig1_attainment_summary_deficit{,_chem}.csv` indexed by abbreviation, and this pass added the combined
`fig1_summary_deficit.csv`.

Cross-check of the regenerated panels against `v7_numbers.json` (16 rows = 8 surrogates x 2 scopes):
**maximum absolute deviation 0** at a 1e-12 tolerance for both `mean` and `se`, and the left-to-right bar
order matches V7a in both panels.

| 13 benchmarks (o) | deficit | | 9 chemistry / materials (p) | deficit |
| --- | --- | --- | --- | --- |
| GP-DKL | 0.069 | | TL-base | 0.013 |
| TL-E2E | 0.081 | | TL-MMD | 0.023 |
| TL-base | 0.084 | | TL-E2E | 0.033 |
| GP-base | 0.096 | | TL-PtJ | 0.053 |
| TL-SPS | 0.124 | | TL-SPS | 0.055 |
| TL-MMD | 0.126 | | GP-DKL | 0.070 |
| TL-PtJ | 0.130 | | GP-SV | 0.083 |
| GP-SV | 0.131 | | GP-base | 0.089 |

The b-n bars are untouched: `fig1_attainment_values.csv` is bit-identical outside its `abbr` column
(section 5), and the 110 dpi render was compared panel by panel with `V7a.png` — identical apart from the
three GP labels and the footnote rewrap.

## 7. Files written in this repository

```
paper_figures/fig1_attainment.pdf
paper_figures/fig2_trajectories.pdf
paper_figures/fig3_grid_final_regret.pdf          (from fig_grid_final.pdf)
paper_figures/fig4_calibration_attain.pdf
paper_figures/supp_acq_matrix.pdf
paper_figures/supp_acq_portfolio.pdf
paper_figures/compute_scaling_law_blr.pdf
paper_figures/computing_time_blr.pdf
reproducibility/values/figcand2_20260914_exact/explorer_data.json
reproducibility/values/figcand2_20260914_exact/fig1_attainment_values.csv
reproducibility/values/figcand2_20260914_exact/fig1_summary_deficit.csv        (new: panels o and p)
reproducibility/values/figcand2_20260914_exact/md5_outputs.txt
reproducibility/values/figrepo_out/fig1ln_final_cells.csv
reproducibility/values/supp/supp_acq_matrix_values.csv
reproducibility/values/supp/supp_acq_matrix_delta.csv
reproducibility/values/supp/supp_acq_matrix_delta_n.csv
reproducibility/values/supp/supp_summary.json
reproducibility/figure_manifest.csv          (8 rows: md5 prefix, command, generated 2026-09-16, note)
reproducibility/values/REGEN_LABELS_GPBASE_20260916.md   (this file)
```

`paper_figures/` holds only `.pdf` for these eight figures (the only sibling `.png` there belongs to
`B2_topk_13`, which was not regenerated), so no other extension needed copying. The Fig. 3 row of the
manifest also had its stale `41ad037d` prefix corrected to the `8bba695e` that was actually shipped.

`main.tex`, `si-content.tex` and `paper_figures/fig1_overview.tex` were not touched: the caption and body text
that spell out the abbreviations, and the Fig. 1a schematic, are handled separately.
