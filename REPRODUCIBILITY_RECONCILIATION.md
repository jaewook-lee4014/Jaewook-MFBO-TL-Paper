# Reproducibility reconciliation (2026-09-14)

Purpose: identify, for the manuscript as it stands (`main.tex`, `si-content.tex`), the exact code, data, settings and raw results
behind every figure, table and quoted number; verify them by independent recomputation; fix what is uniquely resolvable; and
list what still needs an author decision or a release step. Nothing in this record is copied from earlier notes: every number
was recomputed on 2026-09-14 from the raw run cells by `reproducibility/verify/verify_paper_numbers.py`.

Text convention: `\new{...}` is the current text, `\del{...}` the superseded text (the "clean" build prints only `\new`).
Numbers below are the clean-text values.

## 1. State that was reconciled

| Item | State |
|---|---|
| Manuscript repository | `jaewook-lee4014/Jaewook-MFBO-TL-Paper`, branch `main` = `origin/main` = `304df98` (2026-09-14 01:25). Tracked files clean; untracked local folders: `notes/`, `perfid_check/`, `repo_patch/`, `MFBO-NaComMat.pdf`. This reconciliation is committed on the branch `worktree-repro-reconciliation-20260914` (not merged into `main`). |
| Public code/data repository | `MGuo-Lab/MFBO-TL`, `main` = `5c80420` (2026-08-21, "Typeset as a plain preprint"), verified with `git ls-remote`. It holds the **previous** run set and figure pipeline (see section 9). Local clone `../MFBO-TL-public` = `5c80420` plus an uncommitted patch of 2026-09-02 (9 modified, 11 untracked, 134 staged deletions under `results/traj_cells/`), never pushed. |
| Experiment package (canonical) | `/mnt/data/jaewook_mfbo/MFBO-TL-Paper/experiments/{refig_20260908, ext_chem_20260909}` on the VM `l40s` (no git). The cephfs mirror `../MFBO-TL-Paper-Copy260818/experiments/...` (git HEAD `7b9d476`, unrelated commit; 223 uncommitted changes) holds the same scripts and most raw results but **not** the primary TL arm `results/blr_replace__hf_argmin`, not `results_gp_vm*`, `results_conf`, `results_gp_conf`, `results_confirm_ext`, and its `figcand2_20260911/` is the stale B = 20 version (see run_manifest X07). |
| Environments | VM `bo_env`: Python 3.12.3, torch 2.4.1, botorch 0.10.0, gpytorch 1.11, numpy 2.0.2, scipy 1.13.1, scikit-learn 1.6.1. SLURM `paper_v1_py39`: Python 3.9, numpy 1.26.4, same torch/botorch/gpytorch/scipy (per the package notes). 1,846 transfer-learning runs executed in both environments are bit-identical (`verify/verify_out_20260914/crossenv_check.csv`). |

## 2. What the paper uses (figure -> experiments -> raw cells)

The machine-readable version is `reproducibility/run_manifest.csv` (experiments E01-E16, superseded sets X01-X07),
`figure_manifest.csv` and `claim_manifest.csv`. Summary:

| Display item | Experiments | Raw cells (VM) | Aggregation |
|---|---|---|---|
| Fig. 1 b-p (attainment, 13 pools, 12 surrogates, 40 seeds) | E01-E04 (nine pools, budget runs), E05-E07 (extension runs of FreeSolv, Polarizability, HOPV15, Matbench-Gap), E08 (four large pools, cap 60/31) | `refig_20260908/{results, results_gp, results_gp_vm, results_gp_vm2, results_conf, results_gp_conf}`, `ext_chem_20260909/{results, results_slurm, results_ext100, results_confirm_ext}` | `export_explorer.py` (longest run per seed, seeds 42-81, NARGP dropped, Curriculum = KD = PL merged) -> `explorer_data.json` -> `fig1_attainment.py` (targets = pool top 5/2/1/0.5 %, window [end of initial design, B], B = 50 / 30) |
| Fig. 2 a-m | same cells | same | `fig2_trajectories.py` (mean +- s.e. of best-so-far regret on a 0.25-unit grid; windows 50 / 30) |
| Fig. 3 a-c | E09 (TL grid rows, refig runner) + E10 (MFGP / SV-MFGP / DKL rows = public `results/grid`, June 2026) | `refig_20260908/figrepo/results/grid/cells` (merged by `collect.py`) | `make_fig1ln_final.py` best-of-family final regret, 126 cells x 10 seeds |
| Fig. 4 a-m | ECE from the summary CSVs of E01-E04 and E08; attainment from Fig. 1 | as above | `make_a1_calibration_13_attain.py ECE_X=mean` |
| Fig. 5 a,b | E15 (pool statistics) | the 13 pool CSVs | `make_b2_topk_13.py` |
| Fig. 5 c, SI Fig. 3 | E11 (FLOP profile, BLR head) | `figrepo/results/flop_profile_blr/flop_profile.csv` | `make_scaling_law_blr.py`, `plot_computing_flops_blr.py` (GP set = MFGP, SV-MFGP, DKL) |
| SI Fig. 1 | E01, E03 (TL greedy), E12 + E14 (TL EI), E02, E04 (MFGP EI), E13 (MFGP greedy) | `results*/blr_replace__hf_{argmin,ei}`, `results_gp*/gp_{ei,greedy}` | `supp_attain.py` S1 (40 seeds; Matbench-Gap at B = 20) |
| SI Fig. 2 | E12 (EI, PI, UCB, MES, Thompson; seeds 42-61) + E01 | `results/`, `results_slurm/` | `supp_attain.py` S2 |
| Table 1 | E16 (pools) | `data/*.csv` | pool sizes and `corrcoef^2`; synthetic R^2 from 1,000 uniform samples |

Cell provenance per pool (Fig. 1 / Fig. 2, from `verify/verify_out_20260914/cell_sources.csv`): Branin x2, Park x2, COFs = budget runs
(seeds 42-61 `results*`, 62-81 `results_conf*`); FreeSolv and Polarizability = extension runs for the TL rows of seeds 42-61 and
for SV-MFGP (all 40 seeds) and MFGP (FreeSolv), budget runs for the rest; HOPV15 and Matbench-Gap = extension runs for all 480
cells; the four large pools = the cap-60/31 re-runs for all 480 cells. The extension runs reproduce the budget runs exactly for
every TL surrogate and for MFGP; 19 of the 120 repeated SV-MFGP seeds differ (sparse GP fits are not bit-reproducible), which
is why the manuscript now states the "longest run per seed" rule in Methods.

## 3. Model description versus the prediction path (item 4-1 of the brief)

Verified in `refig_20260908/run_tl.py` (md5 `c89da997`) and `benchmark.py` (`24fb817e`), copies in `reproducibility/snapshot/`:

- Prediction used by the acquisition: `mu_H(x) = g_L(x) + w . [g_L(x), phi_L(x), 1]` from the Bayesian linear head fitted on the HF residuals
  (`Head.__init__`, `blr_fit`): prior precision 100 on the 64 representation features (then rescaled to `lambda * beta` with `lambda`
  chosen by leave-one-out error over {10, 30, 100, 300, 1000}), 10 on the `g_L` coefficient, 1 on the bias; noise precision `beta = 1 / LOO-MSE`
  clipped to [1, 100]. The residual MLP `g_H` is trained by each mechanism but its output is not used (`HF_HEAD=blr_replace`).
  This matches Methods ("Surrogate models") and SI Note 2. Consequence, verified on 720/720 trajectory pairs: Curriculum, Knowledge
  Distillation and Pseudo-Labelling are identical (reported as feature-extraction transfer).
- Uncertainty: `sigma_H` from the same head (`blr_predict`), used only by the acquisition-portfolio arms; the calibration analysis uses the
  LF head with alpha = beta = 1 (`benchmark.py _fit_lf_blr`, `run_tl.py` ECE on the held-out pool). SI Note 2 says the same.
- Queries: TL surrogates take `argmin mu_H` at both fidelities among the candidates not yet evaluated at that fidelity. GP baselines take
  EI on the HF-level posterior with the HF incumbent for the LF query and `argmin` of the posterior mean for the HF query (`run_gp.py`).
  The Methods and SI Note 1 previously implied EI at both GP steps; both now state the two rules (redline).
- Per-fidelity candidate masking in both runners (`run_tl.py` L291/L309, `run_gp.py` L66/L70-72), FPS initial design with 2 HF points
  and `max(2, int(0.05 B_cfg / rho))` LF points (3.0-4.5 units), round-robin `floor(1/rho)`, cold refit at every step. All as written.

## 4. Verification performed

`reproducibility/verify/verify_paper_numbers.py` was run on the VM (33 s) against the raw cells; its report is
`reproducibility/verify/verify_out_20260914/report.md` (+ csv/json). What it does independently of the figure pipeline:
re-implements the attainment metric and the cell-selection rule, recomputes every Fig. 1 / Fig. 2 / Fig. 3 / Fig. 4 / Fig. 5 / SI Fig. 1-3 /
Table 1 number, regenerates the synthetic pools from `src/synthetic_functions.py`, and checks the extension-run prefixes and the
VM-versus-SLURM identity. Outcome (details per claim in `claim_manifest.csv`, 72 claims):

- 55 claims **verified** as stated; 6 verified within two-decimal rounding (COFs tie 0.011, COFs R^2 0.958, etc.).
- 7 **mismatches**, all small and all fixed (section 5).
- 3 **clarifications** added where the text was correct but incomplete (GP acquisition rules, Park LF formula wording, regret reference).
- 1 **author action** (public repository, section 9) and 2 **ambiguous-version** items left to the authors (section 6).

Reproduced exactly (recomputed / quoted): grid 81/45/0, 60/65/1, 81; rho -0.79/-0.15, -0.62/+0.04; mean advantage 0.0636 / 0.0171;
calibration r -0.657 / -0.820 / -0.525 with |r| >= 0.5 nowhere else; MFGP lowest ECE 7/13, DKL highest 8/13; screening regrets 4.517 /
3.90 / 0.91 / 0.0892 / 1.15 eV / 384 / 369 / 3 GPa (73.6 / 96.6 / 0.57 % of range), LF rank 1033; FLOPs k_N 0.942 (R^2 0.995) and
2.294 (0.932), break-even 39.8, 3.47x / 8.86x, per-model k 3.04 / 2.32 / 1.52 / 0.89-0.99, loop ratios 43.1x / 27.8x / 11.0x; HOPV15
endpoints 2.31 / 2.61 / 3.32 vs 1.07 / 1.15; Matbench-Gap 0.051-0.071 vs 0.122-0.124; Table 1 sizes and R^2; SI Table 4 alphas
(the CSV pools regenerate from the code to 1e-15); SI Fig. 2 mean deltas to three decimals.

## 5. Discrepancies found and fixed (all as `\del{}` / `\new{}` redlines, uncommitted)

| # | Where | Finding | Fix |
|---|---|---|---|
| F1 | Fig. 1 b-p, Fig. 4 (attainment axis), Results 2.1, 2.2 | `export_explorer.py` stored regret change points rounded to 6 significant digits (`float(f"{y:.6g}")`); a run that reaches exactly the target candidate can then be counted as not reaching it. Effect: 21 of 156 Fig. 1 cells lower by up to 0.011 (Branin-Fav and Branin-Unfav, all surrogates; Polarizability MFGP 0.0004); no verdict changes. | Exact-precision export re-run into `refig_20260908/figcand2_20260914_exact/` (scripts and md5s in `reproducibility/snapshot/refig_20260908/figcand2_20260914_exact_scripts`, values in `reproducibility/values/figcand2_20260914_exact`); `paper_figures/fig1_attainment.pdf` and `fig4_calibration_attain.pdf` replaced; text 0.68 -> 0.69, 0.75 -> 0.76, 0.35 -> 0.36, panel-o E2E 0.73 -> 0.74. Fig. 2 unaffected (< 1e-6). Previous outputs kept in `figcand2_20260911` and `reproducibility/values/figcand2_20260911`. |
| F2 | Results 2.1 | "MFGP and DKL curves lie below every TL curve throughout the run": DKL is below all TL curves on 96 % of the budget grid, MFGP on 100 % / 96 %. | "over almost the whole run". |
| F3 | Results 2.6 | "5.1 versus 0.12 TFLOPs": the loop reconstruction gives 5.045 vs 0.117. | 5.0 versus 0.12. |
| F4 | Results 2.4 | "within 0.02 of EI on eight of nine": paired deltas are 0.022 on Matbench-Gap (and 0.083 on HOPV15). | within 0.03. |
| F5 | SI Note 5 | "no acquisition raises attainment by more than 0.05": +0.052 (PI, Branin-Fav) and +0.051 (Thompson, Branin-Unfav). | "about 0.05 (+0.052 and +0.051)". |
| F6 | SI Note 4 | The Park HF equation was written as `x1/2 sqrt(1 + A)`; the code and the candidate CSVs use `x1/2 sqrt(A)` (the constant cancelled inside the root; max |csv - code| 3.6e-15, |csv - SI equation| 0.50, |csv - classical Park| 0.34). The LF description "scales the exponential argument by alpha" is imprecise: only the sine term is scaled, `exp(1 + alpha sin x3)`. | Equation replaced by the as-run form with a sentence stating the difference from the classical Park function and the 1e-8 boundary guard; LF wording corrected. |
| F7 | Methods, SI Note 1, Results 2.4 | GP acquisition: the HF query is the posterior-mean argmin (greedy), EI is used for the LF query only; the default-protocol "asymmetry" concerns the LF query. | Sentences added. |
| F8 | SI Note 4 | Regret is measured against the best lattice candidate (Branin 0.4045, Park 1.1e-7), not the analytical minima listed as f*. | Sentence added. |
| F9 | Methods (implementation) | Only Python 3.9 was named although most runs were executed under Python 3.12 / NumPy 2.0.2 on the VM; the longest-run rule for repeated seeds was undocumented. | Sentence added (two environments, 1,846 identical TL runs, SV-MFGP not bit-reproducible, longest run per seed). |

Builds after the edits (`bash build.sh clean`): redline `main.pdf` 18 pp, `si.pdf` 7 pp; clean `main_clean.pdf` 15 pp, `si_clean.pdf` 6 pp;
no LaTeX errors, no undefined references or citations.

## 6. Open items and author decisions

1. **Public repository (blocking for the Data/Code availability statements).** `MGuo-Lab/MFBO-TL` main serves the previous run set
   (constant-std greedy LF EI, joint candidate masking in Fig. 1), nine pools, and a `paper/` folder two revisions old; its README,
   PROVENANCE.md and docs/ROOT_CAUSE_INVESTIGATION.md describe that pipeline. Nothing of E01-E14, the four new pools or their build
   scripts is public. `reproducibility/public_release_manifest.csv` lists what to add/replace; no push was made (out of scope).
2. **Fig. 4 ECE horizon (ambiguous version).** The x-axis is the loop-mean held-out LF ECE of the run each cell came from: the 30-unit
   evaluation reads ECE averaged over a 20-unit loop (Matbench-Gap), a 50-unit loop (FreeSolv) and 60/31-unit loops (large pools, TL/GP);
   6-8 seeds per large pool have no ECE (NaN) and are skipped in the mean. Per-refit ECE logs are not stored, so a 30-unit-window ECE
   would need a re-run. Decision: state the horizon in the caption, or re-run with per-refit logging.
3. **SV-MFGP cells of FreeSolv, HOPV15, Matbench-Gap (ambiguous version, resolved by rule).** Two valid runs exist per seed (budget run
   and extension run) and differ in 19/120 seeds; the pipeline keeps the longer one, now stated in Methods. Means at B differ by at most
   0.007 (FreeSolv 0.0135 vs 0.0202 regret). Decision needed only if the authors prefer the budget runs.
4. **Fig. 3 GP rows (missing provenance for the generating commit).** The 126 x 3 GP cells are byte-identical to the public
   `results/grid` (June 2026 campaign, `runners/grid/run_ext.py`); the commit and environment that produced them were not recorded.
   The protocol identity with the TL rows (FPS design, 2 HF + 5 LF, per-fidelity masking, EI/greedy) was checked at code level on
   2026-09-08 and the TL rows carry n_hf 25 / n_lf 249 as stated. Re-running the 3,780 GP grid runs would remove the caveat.
5. **FLOP profile budgets.** The compute comparison profiles FreeSolv on the 50-unit loop and Matbench-Gap on the 20-unit loop while the
   performance comparison evaluates both at 30 (stated in SI Note 6). A B = 30 profile would need `run_flop_profile_blr.py` with a
   changed SCHED (minutes on the VM).
6. **Fig. 1a wording** ("Transfer-learning wins") and the abstract phrase "smooth, low-dimensional functions" (TL wins Park-Fav) are
   editorial choices previously left to the authors; untouched.
7. **Superseded files in `paper_figures/`** (12 PDFs + one PNG not referenced by any `\includegraphics`) are listed in
   `figure_manifest.csv`; left in place.

## 7. How to tell current from previous results

- Current = anything produced by `refig_20260908` / `ext_chem_20260909` runners (`run_tl.py` with `HF_HEAD=blr_replace LF_TARGET=hf_argmin`,
  `run_gp.py` with `GP_ACQ=ei`), summary/trajectory cells named `summary_<pool>_<model>_s<a>-<b>.csv` with 2026-09-08 to 2026-09-13 mtimes,
  seeds 42-81, per-fidelity masking, ECE columns present. The paper's aggregate inputs are `explorer_data.json` (2026-09-14 exact export),
  `figrepo/results/grid`, `flop_profile_blr/flop_profile.csv`, the pool CSVs.
- Previous = the public repository `results/*` (`main_9bench`, `main_corrected`, `extra_baselines`, `gpfamily_newbench`, `mfgp_greedy_*`,
  `calibration_*`, `acq_portfolio`, `flop_profile`, `ranking_analysis`, `traj_cells`) and `paper_figures/{final_regret, regret_trajectory,
  fig1_anytime_row, fig1c_family_split_grid, A6_acquisition_matrix, acquisition_portfolio, A1_calibration_vs_regret, B2_topk_overlap_and_screening,
  compute_scaling_law, computing_time, si_star_sensitivity}.pdf`; anything with NARGP; the `results_confirm*` B = 20 runs of the four large
  pools; the arms `__warm`, `__relu`, `mlp_small`, `__maskboth`, `__initrand`, `results_nonlearn*`, `results_sf*`; other campaigns
  (`tl_ladder_20260902`, `cond_20260907`, `rho_sweep_20260904`, `fsraw_grid_20260908`, `refcompare_20260909`, `refgrid`, `fsref`,
  `phase0_20260914`). None of these feeds a manuscript number (run_manifest X01-X07).
- The cephfs mirror's `figcand2_20260911/` is the B = 20 state of 2026-09-11/13 and its `fig1_attainment.py`, `fig2_trajectories.py`,
  `prep_candidates2.py` are not mirrored: use the VM copies (in `reproducibility/snapshot`).

## 8. Regeneration commands (VM `l40s`, `cd /mnt/data/jaewook_mfbo/MFBO-TL-Paper/experiments/refig_20260908`, `PY=/mnt/data/jaewook_mfbo/e1_venv_cu121/bin/python` or `bo_env`)

```
# collected CSVs in the public layout (already done; inputs of Fig. 3 / SI figures)
bash make_all.sh                      # or: TL_ROOTS=... GP_ROOTS=results_gp:results_gp_vm:results_gp_vm2 python collect.py
# Fig. 1 b-p, Fig. 2, Fig. 4 (exact export, 2026-09-14)
$PY figcand2_20260914_exact/scripts/export_explorer_exact.py
SUMMARY=score $PY figcand2_20260914_exact/scripts/fig1_attainment_exact.py
$PY figcand2_20260914_exact/scripts/fig2_trajectories_exact.py
cd figrepo/figures && ECE_X=mean CAL_LETTERS=abcdefghijklm CAL_STEM=fig4_calibration_attain $PY ../../figcand2_20260914_exact/scripts/make_a1_calibration_13_attain_exact.py
# Fig. 3
cd figrepo/figures && FIG1LN_LETTERS=a,b,c FIG_STEM=fig_grid_final $PY make_fig1ln_final.py
# Fig. 5 a,b
cd figrepo/figures && MPLBACKEND=Agg FIG_OUT=fig5_13 $PY make_b2_topk_13.py
# Fig. 5 c and SI Fig. 3
cd figrepo/figures && GP_VARIANTS=DKL FIG_OUT=dkl $PY make_scaling_law_blr.py && GP_VARIANTS=DKL FIG_OUT=dkl $PY plot_computing_flops_blr.py
# SI Figs. 1-2
$PY supp_attain.py S1 S2
# verification of every quoted number
OUT=/mnt/data/jaewook_mfbo/verify_out $PY /path/to/reproducibility/verify/verify_paper_numbers.py
# manuscript
bash build.sh clean      # main.pdf / si.pdf (redline) and main_clean.pdf / si_clean.pdf
```
Exact reproduction of the PDFs requires the VM matplotlib (`figcand2_20260914_exact/scripts/env.txt`); values are environment-independent.

## 9. Public repository: what a reader of `MGuo-Lab/MFBO-TL` main would get wrong today

- `README.md` says the manuscript is a template-free preprint and maps Fig. 1 b-k to `results/main_9bench/final_regret.pdf` etc.: those are
  the previous figures (final-regret bars, NARGP included, joint masking, constant-std EI). The current Fig. 1 is attainment on 13 pools.
- `PROVENANCE.md` "Known paper-code gaps" and `docs/ROOT_CAUSE_INVESTIGATION.md` describe the constant-std LF EI of the previous pipeline;
  the current TL surrogates use `argmin mu_H` of the BLR HF head at both fidelities.
- `src/benchmark.py` in the public repo is the model code the paper uses (identical except an activation switch), but its BO loop
  (`run_bo*`) is not the loop that produced the paper's runs (`run_tl.py` / `run_gp.py`).
- `results/grid` is current (reused unchanged); every other `results/*` folder is superseded.
- Only nine pool CSVs and two benchmark build scripts are present; the four materials pools of Table 1 rows 10-13 are missing.
Draft wording for the release is in `reproducibility/public_release_manifest.csv` (action column). Suggested structure: keep `src/`,
`data/` (+4 CSVs), `benchmarks/` (+2 scripts), add `experiments/refig_20260908` and `experiments/ext_chem_20260909` (runners, task lists,
collected CSVs, raw cells), replace `figures/` and `paper/`, rewrite README/PROVENANCE, move the previous results to `results_previous/`
with a one-line label, add LICENSE and CITATION.cff, mint the DOI.

## 10. Minimum file set for an external review

1. This file, `README.md`, `reproducibility/run_manifest.csv|json`, `claim_manifest.csv`, `figure_manifest.csv`, `public_release_manifest.csv`.
2. `main.tex`, `si-content.tex`, `paper_figures/` (the ten referenced PDFs), the built PDFs.
3. `reproducibility/snapshot/` (runner, model, pipeline and figure code with `md5sums.txt`; the four new pool CSVs; benchmark builders).
4. `reproducibility/values/` (every value file behind the figures, the exact re-aggregation, `explorer_data.json`, FLOP profile, grid manifest, extension prefix check).
5. `reproducibility/verify/` (verification script, its outputs, the VM result inventory `inventory_vm_results_20260914.csv`).
6. For a full re-run: the raw cells listed in `run_manifest.csv` (VM paths; ~750 MB), the nine public pool CSVs and `data/grid_cells`.

## 11. Files changed by this reconciliation (branch `worktree-repro-reconciliation-20260914`)

`main.tex` (9 redline edits), `si-content.tex` (5), `paper_figures/fig1_attainment.pdf`, `paper_figures/fig4_calibration_attain.pdf`
(exact re-aggregation), new `README.md`, `REPRODUCIBILITY_RECONCILIATION.md`, `reproducibility/` (manifests, values, snapshot, verify).
Committed and pushed on this branch only (no merge into `main`, no release, no remote deletion); raw results were not modified; previous aggregate outputs were kept.
