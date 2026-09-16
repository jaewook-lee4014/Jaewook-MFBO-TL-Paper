# Figure regeneration 2026-09-16 — transfer-learning surrogate labels renamed to the TL- prefix

Labels only. No run was executed, no metric, budget, seed set, colour, panel order or data path
was touched. Every value file is bit-identical to the 2026-09-14 5-TL render once the label strings
are mapped; the proof is in section 5.

All work was done on the VM `l40s` with `/mnt/data/jaewook_mfbo/bo_env/bin/python`, root
`R = /mnt/data/jaewook_mfbo/MFBO-TL-Paper/experiments/refig_20260908`. The pre-edit PDFs, value
files and scripts are archived in `$R/_backup_labels_20260916/` (with `md5_BEFORE.txt`).

## 1. Rename table

| internal display-name key (unchanged) | abbreviation before | abbreviation after |
| --- | --- | --- |
| `Frozen-representation transfer` | `Frozen` | `TL-base` |
| `Pretrain-then-Joint` | `PtJ` | `TL-PtJ` |
| `End-to-End Joint` | `E2E` | `TL-E2E` |
| `Soft Parameter Sharing` | `SPS` | `TL-SPS` |
| `Domain Adaptation (MMD)` | `MMD` | `TL-MMD` |
| `MFGP` / `Sparse MFGP` / `DKL` | `MFGP` / `SV-MFGP` / `DKL` | unchanged |

Footnote / legend expansion, before:

```
TL: Frozen = Frozen-representation transfer · PtJ = Pretrain-then-Joint · E2E = End-to-End Joint · SPS = Soft Parameter Sharing · MMD = Domain Adaptation (MMD)
```

after:

```
TL: TL-base = base transfer-learning surrogate · TL-PtJ = pretrain-then-joint · TL-E2E = end-to-end joint · TL-SPS = soft parameter sharing · TL-MMD = domain adaptation (MMD)
```

The GP half (`GP: MFGP = baseline MFGP · SV-MFGP = sparse variational MFGP · DKL = deep-kernel GP`)
and every family label (`Transfer-learning (TL) surrogates`, `Gaussian-process family`,
`TL surrogates`, `TL cheaper`, the `TL: ` footnote prefix) are unchanged.

## 2. Files edited (all paths relative to `$R` on `l40s`)

### `figcand2_20260914_5tl/scripts/prep_candidates2.py` — lines 53-54 (`ABBR` values only)
- before: `ABBR = {... "Frozen-representation transfer": "Frozen", "Pretrain-then-Joint": "PtJ",` / `"End-to-End Joint": "E2E", "Soft Parameter Sharing": "SPS", "Domain Adaptation (MMD)": "MMD"}`
- after: `ABBR = {... "Frozen-representation transfer": "TL-base", "Pretrain-then-Joint": "TL-PtJ",` / `"End-to-End Joint": "TL-E2E", "Soft Parameter Sharing": "TL-SPS", "Domain Adaptation (MMD)": "TL-MMD"}`
- `RENAME`, `TL`, `GP`, `ORDER`, `LINECOL`, `MERGED` untouched. This dict is baked into
  `explorer_data.json` by `export_explorer_exact.py`, which Fig. 1, Fig. 2 and `supp_attain_5tl.py` read.

### `figcand2_20260914_5tl/scripts/fig1_attainment_exact.py` — lines 117-118 (`FOOTNOTE`)
- before: `"TL: Frozen = Frozen-representation transfer · PtJ = Pretrain-then-Joint · E2E = End-to-End Joint · SPS = Soft Parameter Sharing"` / `"MMD = Domain Adaptation (MMD)    GP: …"`
- after: `"TL: TL-base = base transfer-learning surrogate · TL-PtJ = pretrain-then-joint · TL-E2E = end-to-end joint · TL-SPS = soft parameter sharing"` / `"TL-MMD = domain adaptation (MMD)    GP: …"`

### `figcand2_20260914_5tl/scripts/fig2_trajectories_exact.py` — lines 93-94 (`FOOTNOTE`)
- before: `"TL: Frozen = Frozen-representation transfer · PtJ = Pretrain-then-Joint · E2E = End-to-End Joint"` / `"SPS = Soft Parameter Sharing · MMD = Domain Adaptation (MMD)"`
- after: `"TL: TL-base = base transfer-learning surrogate · TL-PtJ = pretrain-then-joint · TL-E2E = end-to-end joint"` / `"TL-SPS = soft parameter sharing · TL-MMD = domain adaptation (MMD)"`
- the `STYLE` dict keys (colour / dash per model) are untouched.

### `figcand2_20260914_5tl/scripts/make_a1_calibration_13_attain_exact.py` — lines 41-43 (`ABBR` values) and line 83 (footnote)
- before line 41-43: `'Frozen-representation transfer': 'Frozen', 'Pretrain-then-Joint': 'PtJ', 'End-to-End Joint': 'E2E', 'Domain Adaptation (MMD)': 'MMD', 'Soft Parameter Sharing': 'SPS'`
- after line 41-43: `'Frozen-representation transfer': 'TL-base', 'Pretrain-then-Joint': 'TL-PtJ', 'End-to-End Joint': 'TL-E2E', 'Domain Adaptation (MMD)': 'TL-MMD', 'Soft Parameter Sharing': 'TL-SPS'`
- line 83: the `TL: …` footnote replaced as in section 1.
- `NAMES`, `TL`, `GP`, `STYLE`, `MS` untouched.

### `supp_attain_5tl.py` — lines 12, 149, 166, 194, 208, 309-310
- line 149 `FOOT1`: `TL: …` footnote replaced as in section 1.
- lines 309-310 `NOTE2`: `"TL: TL-base = base transfer-learning surrogate · TL-PtJ = pretrain-then-joint · TL-E2E = end-to-end joint"` / `"TL-SPS = soft parameter sharing · TL-MMD = domain adaptation (MMD)"`.
- line 166 (SI Fig. 1 `COND`, y-tick labels of panels a-i, also the `condition` column of
  `supp_acq_matrix_values.csv`): `("E2E greedy", …), ("E2E EI", …)` -> `("TL-E2E greedy", …), ("TL-E2E EI", …)`.
- line 208 (SI Fig. 1 legend): `label="E2E · greedy (default)"` / `label="E2E · EI"` ->
  `label="TL-E2E · greedy (default)"` / `label="TL-E2E · EI"`.
- line 12: docstring wording follows the same rename.
- line 194 — **layout fix**, see section 4.
- the `RAW` map (raw run name -> display name) is untouched; `ABBR` is read from `explorer_data.json`.

### `figrepo/figures/_common.py` — lines 65-71 (`CODE_NAMES` 5-TL block) and 82-84 (`CODE_KEY_TL_5`)
- before (5-TL block): `'Frozen-representation transfer': 'Frozen', 'Pretrain-then-Joint': 'PtJ', 'End-to-End Joint': 'E2E'`
- after (5-TL block): `'Frozen-representation transfer': 'TL-base', 'Pretrain-then-Joint': 'TL-PtJ', 'End-to-End Joint': 'TL-E2E', 'Soft Parameter Sharing': 'TL-SPS', 'Domain Adaptation (MMD)': 'TL-MMD'`
- the two new `Soft Parameter Sharing` / `Domain Adaptation (MMD)` entries deliberately **shadow**
  the same keys in the 12-surrogate head of the dict literal (the head lines are left textually
  untouched, and the later entries win). This is what gives SI Fig. 3 its `TL-SPS` / `TL-MMD` axis
  codes. Consequence to know about: if a legacy 12-surrogate figure is ever regenerated it will now
  also print `TL-SPS` / `TL-MMD` while `CODE_KEY_TL2` still spells out `SPS` / `MMD`. No such figure
  is in the paper.
- `CODE_KEY_TL_5` replaced as in section 1. `RENAME_5TL`, `TL5_PROFILE`, `SHORT_NAMES`,
  `CODE_KEY_TL`, `CODE_KEY_TL2`, `CODE_KEY_GP` untouched.

### Deliberately not edited
`$R/prep_candidates2.py`, `$R/fig1_attainment.py`, `$R/style_patch_20260914.py`, `$R/supp_attain.py`,
`$R/compute_multimetric.py`, `$R/collect.py` (stale legacy copies);
`figcand2_20260914_5tl/scripts/prep_candidates2.py` line 199 (legacy 9-model gallery footnote, not
executed by `export_explorer_exact.py` and not a paper figure); `supp_attain_5tl.py` line 408
(fig_S4 note — S4/S5/S6 are not paper figures and were not regenerated).

## 3. Command sequence (exact, in order)

```
PY=/mnt/data/jaewook_mfbo/bo_env/bin/python
R=/mnt/data/jaewook_mfbo/MFBO-TL-Paper/experiments/refig_20260908
cd $R
$PY figcand2_20260914_5tl/scripts/export_explorer_exact.py
SUMMARY=score $PY figcand2_20260914_5tl/scripts/fig1_attainment_exact.py
$PY figcand2_20260914_5tl/scripts/fig2_trajectories_exact.py
cd $R/figrepo/figures && ECE_X=mean CAL_LETTERS=abcdefghijklm CAL_STEM=fig4_calibration_attain \
    $PY ../../figcand2_20260914_5tl/scripts/make_a1_calibration_13_attain_exact.py
cd $R && $PY supp_attain_5tl.py S1 S2
cd $R/figrepo/figures && FIG_OUT=fig5tl_20260914 GP_VARIANTS=DKL $PY make_scaling_law_blr_5tl.py
cd $R/figrepo/figures && FIG_OUT=fig5tl_20260914 GP_VARIANTS=DKL $PY plot_computing_flops_blr_5tl.py
```

`make_fig1ln_final_5tl.py` (Fig. 3) and `make_b2_topk_13.py` (Fig. 6 top-k) were **not** run: they
carry family and pool labels only.

## 4. Layout fix (one, in SI Fig. 1 only)

`supp_attain_5tl.py` line 194, `fig_S1` gridspec: `wspace=0.55` -> `wspace=0.72`.
Reason: the row label `TL-E2E greedy` is 0.477 in wide at 5.4 pt against a 0.495 in column gap, so on
FreeSolv -> Polarizability and Polarizability -> HOPV15 (bars at 0.94 / 0.96) it collided with the
value label of the panel to its left. The new gap is 0.592 in. Font sizes, colours, panel order,
letters and data are unchanged. No other figure needed a fix: every new tick label
(`TL-base` 0.368 in, `TL-SPS` 0.308 in, `TL-MMD` 0.368 in, `TL-PtJ` 0.258 in, `TL-E2E` 0.318 in at
6.5 pt) is narrower than the pre-existing `SV-MFGP` (0.395 in), and the longest new footnote line of
Fig. 1 ends at x = 0.979 of the figure width (was 0.901), inside the 1.0 edge.

## 5. Proof that no number changed

### md5, PDFs (VM = repo `paper_figures/`, verified identical after transfer)

| figure | file | md5 before | md5 after |
| --- | --- | --- | --- |
| Fig. 1 b-p | `fig1_attainment.pdf` | `be9dd051846d6536ef477e686a44df3b` | `81ac57708d4513b4e02882eb8ecfa7f2` |
| Fig. 2 a-m | `fig2_trajectories.pdf` | `fa6dd4c4ddb6a8a7f1330571733fa2e3` | `914afad694233ff3c78e638ab8fccc8f` |
| Fig. 4 a-m | `fig4_calibration_attain.pdf` | `b4646d277246f22498f1027f971130cb` | `c0d0503801cb11eaefc428d3a203b907` |
| Fig. 5 c | `compute_scaling_law_blr.pdf` | `d0642f1e90c69fc42cfcadfdc8bf7bb8` | `800357368ffc5b63acb7900aa2b61cc9` |
| SI Fig. 1 | `supp_acq_matrix.pdf` | `f53e0df1cbecfd9bf11709be67489686` | `10e715890dced4a4ad887ed09249a6fc` |
| SI Fig. 2 | `supp_acq_portfolio.pdf` | `064332d8fade3427c1025dc46eb7d689` | `2b8c75497a9bda751fe42d81a3756c2f` |
| SI Fig. 3 | `computing_time_blr.pdf` | `fa97d908806deb9fbc301a5fd9923446` | `6b9aa0ac1e176fc95516bd0d92ce0908` |

`compute_scaling_law_blr` carries no surrogate labels at all: its **PNG** md5 is unchanged
(`c3a22891135a2f61ead2364f1bf3c06e` before and after), so the page content is byte-identical and only
the PDF `CreationDate` differs.

### Value files, md5 unchanged (bit-identical)

```
52293229fbc2fe7a9941e58bfb5f9b2b  fig1_attainment_summary_score.csv
0b94382ca43ca5a188d726c7bfd81298  fig1_attainment_summary_score_chem.csv
97d733d9e1dfd4ac2a5029b3f2802af7  fig2_trajectories_values.csv
c0fe13798d4eb704dbb09a020ba3d359  fig4_calibration_attain_values.csv
b485ec2a5a9c240ac082f321b3cc5bf4  supp_acq_portfolio_meandelta.csv
d35a752b846c384251d8c9e930bb7985  supp_acq_portfolio_n_models.csv
3eb2c13e56ef06b025b93eadd7cbfeeb  supp_acq_portfolio_winshare.csv
d9ba24476d384e30f952464adcad52ea  computing_flops_values_blr.csv
24bb0a42352af2d8b7b015df5716f967  scaling_law_blr.json
```

### Value files whose md5 changed — label strings only

| file | md5 before -> after | what differs |
| --- | --- | --- |
| `explorer_data.json` | `78531838…` -> `7030f472…` | only the `abbr` dict values. `models`, `gp`, `tl` and the whole `pools` payload (per-seed change points, thresholds, budgets, ranges, pool sizes) compare byte-identical under `json.dumps(sort_keys=True)`; the `abbr` **keys** are identical. |
| `fig1_attainment_values.csv` | `3b5eb436…` -> `55cdae42…` | only the `abbr` column; `n`, `mean`, `se` bit-identical; 104 rows both. |
| `supp_acq_matrix_values.csv` | `2d01907e…` -> `e64c5f57…` | only the `condition` column (`E2E EI`/`E2E greedy` -> `TL-E2E EI`/`TL-E2E greedy`); `mean`, `se`, `n`, `budget` bit-identical. |
| `supp_acq_matrix_delta.csv` | `aade5450…` -> `494c180c…` | only the row index; the 6 x 9 value array is `np.array_equal` before/after. |
| `supp_acq_matrix_delta_n.csv` | `8ad38789…` -> `afaeedd7…` | only the row index; the 6 x 9 value array is `np.array_equal` before/after. |
| `supp_acq_portfolio_values.csv` | `1053c9ee…` -> `9a12e190…` | only the `model` column; `mean`, `se`, `n` bit-identical. |
| `supp_summary.json` | `ce13c7e5…` -> `bbd34390…` | a recursive walk finds no value difference anywhere; the only difference is the S1 `values` composite keys `"<pool>|E2E EI"` / `"<pool>|E2E greedy"` -> `"<pool>|TL-E2E EI"` / `"<pool>|TL-E2E greedy"` and the S2 `coverage` model keys. |

Every remaining difference in each table above was checked to be exactly one of the five documented
renames (plus the two derived `E2E greedy` / `E2E EI` condition strings); no other string changed.

## 6. Files written in this repository

```
paper_figures/fig1_attainment.pdf
paper_figures/fig2_trajectories.pdf
paper_figures/fig4_calibration_attain.pdf
paper_figures/supp_acq_matrix.pdf
paper_figures/supp_acq_portfolio.pdf
paper_figures/compute_scaling_law_blr.pdf
paper_figures/computing_time_blr.pdf
reproducibility/values/figcand2_20260914_exact/explorer_data.json
reproducibility/values/figcand2_20260914_exact/fig1_attainment_values.csv
reproducibility/values/figcand2_20260914_exact/md5_outputs.txt
reproducibility/values/supp/supp_acq_matrix_values.csv
reproducibility/values/supp/supp_acq_matrix_delta.csv
reproducibility/values/supp/supp_acq_matrix_delta_n.csv
reproducibility/values/supp/supp_acq_portfolio_values.csv
reproducibility/values/supp/supp_summary.json
reproducibility/figure_manifest.csv          (7 rows: md5 prefix, producing command, generated, status)
reproducibility/values/REGEN_LABELS_TLBASE_20260916.md   (this file)
```

`paper_figures/` holds only `.pdf` for these seven figures (the only sibling `.png` there belongs to
`B2_topk_13`, which was not regenerated), so no other extension needed copying.

`main.tex`, `si-content.tex` and `paper_figures/fig1_overview.tex` were not touched: the caption and
body text that spell out the abbreviations are handled separately.
