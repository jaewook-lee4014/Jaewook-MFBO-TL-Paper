# Figure regeneration 2026-09-17 — composite Fig. 4 split into Fig. 4 (a,b) and Fig. 5; compute panel re-rendered without its letter

Display-item change only. No run was executed, and no metric, fit, data path, colour, axis or label was touched. The only
visual difference in the re-rendered PDF is the removal of the baked-in panel letter "c" at the top left, because the
compute-scaling plot is now a single-panel figure of its own (Fig. 5). The top-k / screening-regret PDF
(`B2_topk_13.pdf`, letters a,b baked in) is unchanged and becomes Fig. 4 on its own.

Work was done on the VM `l40s` with `/mnt/data/jaewook_mfbo/bo_env/bin/python`, root
`R = /mnt/data/jaewook_mfbo/MFBO-TL-Paper/experiments/refig_20260908`. The pre-edit script, PDF, PNG and fit-constants
JSON are archived in `$R/_backup_fig5_noletter_20260917/` (`md5_BEFORE.txt`).

## 1. Script edit

### VM `$R/figrepo/figures/make_scaling_law_blr_5tl.py` (snapshot refreshed in
`reproducibility/snapshot/refig_20260908/figrepo/figures/make_scaling_law_blr_5tl.py`)
- `import os` added.
- The unconditional `ax.text(-0.075, 1.01, 'c', ...)` call is now guarded by `PANEL_LETTER = os.environ.get('PANEL_LETTER', '')`;
  the letter is drawn only when the variable is set. `PANEL_LETTER=c` reproduces the old composite panel exactly.

## 2. Command

```
cd $R/figrepo/figures && FIG_OUT=fig5tl_20260914 GP_VARIANTS=DKL $PY make_scaling_law_blr_5tl.py
```
Console output, identical to the 2026-09-16 run: `GP: k_N=2.29 (R2=0.93)`, `TL: k_N=0.94 (R2=1.00)`, `break-even N = 45.9`.

## 3. Checksums

| file | before (2026-09-16) | after (2026-09-17) |
| --- | --- | --- |
| `out/fig5tl_20260914/compute_scaling_law_blr.pdf` | `5f36b4cbe7bbbf7b96a7a26f20e06a8e` | `b2b1c7b5fbe1871155d20f5f6449c449` |
| `out/fig5tl_20260914/compute_scaling_law_blr.png` | `c3a22891135a2f61ead2364f1bf3c06e` | `4fa33f01a52abbff2340e9911a0bcbd0` |
| `out/fig5tl_20260914/scaling_law_blr.json` (fit constants) | `24bb0a42352af2d8b7b015df5716f967` | `24bb0a42352af2d8b7b015df5716f967` (unchanged) |

`pdftotext` of the new PDF no longer starts with the stray `c`; every other text token is unchanged.

## 4. Manuscript

- `main.tex`: the composite `figure*` (B2_topk_13 + compute_scaling_law_blr, caption "When a surrogate is needed, and what it
  costs", labels `fig:topk` + `fig:scaling_law`) is split into Fig. 4 (`fig:topk`, caption "Task difficulty and the need for a
  surrogate", panels a,b) placed before Results 2.5 and Fig. 5 (`fig:scaling_law`, caption "Computational scaling of surrogate
  fitting", no panel letter) placed before Results 2.6. The two in-text `Fig.~\ref{fig:scaling_law}c` citations become
  `Fig.~\ref{fig:scaling_law}`; `Fig.~\ref{fig:topk}a,b` is unchanged. Caption text otherwise verbatim; display-item header
  comment updated to six items. Body word count unchanged (Intro 777, Results 1,959, Discussion 764 by
  `notes/discussion_restructure_20260917/wc_body.py`).
- `reproducibility/figure_manifest.csv` row for the compute panel: `Fig. 4,c` -> `Fig. 5,-`, new md5 prefix `b2b1c7b5`.
- `reproducibility/claim_manifest.csv` C43 location `Fig. 4 c` -> `Fig. 5`; `REPRODUCIBILITY_RECONCILIATION.md` Fig. 4 c -> Fig. 5.
- `./build.sh clean` (main + SI, then the clean wrappers): no undefined references or float warnings; Fig. 4 and Fig. 5 both
  land on page 7 of `main_clean.pdf`.
