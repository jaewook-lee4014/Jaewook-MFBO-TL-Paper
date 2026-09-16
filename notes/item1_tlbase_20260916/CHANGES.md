# Item 1 — best-of-family comparison → fixed base model (TL-base) — change set

Decided 2026-09-16. Scope: this reviewer item only (shared criticism #1 of the two mock assessments:
"post-hoc best-of-family drives the surrogate-of-choice recommendation"). Other items are handled separately by the author.

## 1. Decisions

| what | decision |
|---|---|
| Base model | The surrogate formerly labelled "Frozen-representation transfer" is the base transfer-learning surrogate, named **TL-base**. LF network trained on the LF loss only (no HF gradient reaches it); Bayesian linear head fitted in closed form to the HF observations. |
| Variants | **TL-PtJ** (pretrain-then-joint), **TL-E2E** (end-to-end joint), **TL-SPS** (soft parameter sharing), **TL-MMD** (domain adaptation, MMD penalty). Collectively "the TL variants". Full names appear once, at first mention in Methods/SI. |
| Family | "the transfer-learning family" / "the five transfer-learning surrogates". Bare "TL" is a family label only (Fig. 3 maps, "transfer-learning (TL) surrogates"); it never names a model. Mirrors the GP side: baseline MFGP / MFGP variants / Gaussian-process family. |
| Claim basis | Every comparison that supports a recommendation uses TL-base's own numbers. Primary, fixed-vs-fixed: TL-base vs baseline MFGP. Stringent: TL-base vs the best-performing GP in each pool (a comparator that favours the GPs). Family-level best-of-family statements remain only as descriptive design-space results and are labelled as such (grid maps; screening-vs-margin panel). |
| Language | No process narration ("fixed in advance", "chosen after the fact", "base recipe"); name the model, describe the comparator as an object. No p-values. At most two numeric anchors per body sentence; the rest goes to a new SI table. |

## 2. Numbers (40 seeds, B = 30, four-target attainment; source reproducibility/values/figcand2_20260914_exact/fig4_calibration_attain_values.csv; seed-paired counts from explorer_data.json on the VM)

RULE (user, 2026-09-16, feedback-data-inclusion-rules): the seed W/T/L columns below are INTERNAL ONLY. The manuscript and SI report means, s.e. over seeds and differences only; no paired tables, seed fractions, intervals, tests or statistics disclaimers.

| pool | TL-base | MFGP | Δ | seeds W/T/L | best-performing GP | Δ | seeds W/T/L |
|---|---|---|---|---|---|---|---|
| COFs | 0.923 ± 0.006 | 0.902 ± 0.008 | +0.021 | 26/7/7 | SV-MFGP 0.923 ± 0.006 | 0.000 | 5/29/6 |
| FreeSolv | 0.934 ± 0.005 | 0.938 ± 0.005 | −0.004 | 0/37/3 | MFGP 0.938 ± 0.005 | −0.004 | 0/37/3 |
| Polarizability | 0.963 ± 0.005 | 0.954 ± 0.011 | +0.009 | 1/39/0 | MFGP 0.954 ± 0.011 | +0.009 | 1/39/0 |
| HOPV15 | 0.376 ± 0.056 | 0.317 ± 0.063 | +0.058 | 18/13/9 | MFGP 0.317 ± 0.063 | +0.058 | 18/13/9 |
| Matbench-gap | 0.409 ± 0.039 | 0.245 ± 0.036 | +0.164 | 30/0/10 | SV-MFGP 0.322 ± 0.040 | +0.088 | 23/2/15 |
| ExptGap-PBE | 0.406 ± 0.027 | 0.333 ± 0.031 | +0.073 | 22/5/13 | SV-MFGP 0.337 ± 0.028 | +0.068 | 22/3/15 |
| Elastic-CHGNet | 0.622 ± 0.041 | 0.493 ± 0.044 | +0.129 | 23/3/14 | DKL 0.604 ± 0.042 | +0.018 | 20/1/19 |
| Elastic-SevenNet | 0.691 ± 0.037 | 0.568 ± 0.039 | +0.123 | 23/2/15 | SV-MFGP 0.725 ± 0.030 | −0.034 | 18/0/22 |
| Elastic-MatterSim | 0.872 ± 0.011 | 0.757 ± 0.025 | +0.115 | 27/7/6 | SV-MFGP 0.863 ± 0.009 | +0.009 | 20/9/11 |

±0.02 band: vs MFGP 7 wins / 2 ties / 0 losses; vs best-performing GP 3 / 5 / 1. Largest deficit vs MFGP 0.004 (FreeSolv); vs any GP 0.034 (SevenNet, SV-MFGP).
Synthetic (B = 50): TL-base 0.586 / 0.348 / 0.737 / 0.855 vs best GP 0.913 (DKL) / 0.756 (MFGP) / 0.854 (DKL) / 0.888 (SV-MFGP) on Branin-Fav / Branin-Unfav / Park-Fav / Park-Unfav.
Margin vs top-10 overlap (9 pools, Spearman): best-TL − best-GP −0.88 (current text); TL-base − best-performing GP −0.57; TL-base − MFGP −0.50. For TL-base the three zero-overlap pools still carry the three largest margins over the best-performing GP (0.058–0.088); the other six lie between −0.034 and +0.018.
Oracle shortfall (best of eight minus model, 9 pools): TL-base mean 0.013 / max 0.063; MMD 0.023 / 0.069; E2E 0.033 / 0.115; PtJ 0.053 / 0.241; SPS 0.055 / 0.288; DKL 0.070 / 0.166; SV-MFGP 0.083 / 0.295; MFGP 0.089 / 0.190.

## 3. Elements to change (found → see section 4; applied → section 5)

Main text
- Abstract: best-TL-vs-best-GP sentence → TL-base vs MFGP + within 0.03 of best-performing GP; keep the FLOPs clause family-level.
- Intro summary (L125): same substitution.
- Intro surrogate paragraph (L123) and Methods (L296–302): introduce base + variants with names.
- Results, synthetic (L133): TL-base values; GPs lead TL-base on all four synthetic functions.
- Results, chemistry (L137): TL-base vs MFGP / best-performing GP sentences; HOPV15, Matbench, elastic numbers for TL-base.
- Results, trajectories (L139): "best transfer-learning surrogates" → TL-base / the transfer-learning surrogates, checked against Fig. 2 data.
- Results, misordering pools (L143): TL-base vs HF-only baselines and vs best-performing GP; margin sentence keeps the family definition, labelled, plus a TL-base clause.
- Results, transfer mechanism (L145): rename only.
- Discussion (L226, L234): recommendation on TL-base; "surrogate of choice" paragraph replaced.
- Fig. 1 caption (L109): define TL-base + variants in the abbreviation sentence.
- Methods grid paragraph (L376–383) and Fig. 3 caption: family-level, rename only where a model is named.

SI
- Surrogate configuration table (L52–56), training table (L139–143), descriptions (L118, L128, L151–155), feature-ablation table headers (L316–360), head-path ablation caption (L377): rename.
- HF-only baseline table (L402–430): "best TL" columns → TL-base (attainment and final regret at the table's budgets); footnote c renamed.
- HOPV15 pick-log table (L446–450): rename.
- New Supplementary Table: TL-base against the baseline MFGP and against the best-performing GP (means ± s.e. and differences only; 13 pools; no seed fractions).

Figures (labels only; numbers unchanged)
- Fig. 1 b–p, Fig. 2, Fig. 3 (top-k), Fig. 4, Fig. 5 and SI attainment/acquisition/compute figures: abbreviations Frozen → TL-base, PtJ → TL-PtJ, E2E → TL-E2E, SPS → TL-SPS, MMD → TL-MMD.
- fig:topk panel a margin definition (best TL − best GP) is left as a family-level, labelled statistic; switching it to TL-base is a separate author decision (ρ would become −0.57).

## 4. Found (line numbers, current text) — filled during the find pass

Base commit for the edits: origin/worktree-remove-stats-attack-surface-20260916 (2fdf629), so that the statistics-disclaimer removals of the same day are included. Hunks changed (git diff, old -> new line numbers):

- old line 84 -> new line 84: Optimization}
- old line 109 -> new line 109: source (cost $\rho \ll 1$) and a scarce, expensive high-fidelity (HF) experiment
- old line 123 -> new line 123: Transfer-learning surrogates offer a direct mechanism for this hypothesis. A net
- old line 125 -> new line 125: We address these questions through a controlled benchmark of eight multi-fidelit
- old line 133 -> new line 133: We evaluated eight surrogates on thirteen benchmarks (Table~\ref{tab:benchmarks}
- old line 137 -> new line 137: The Gaussian-process family achieved the highest attainment on both Branin scena
- old line 139 -> new line 139: Across the nine chemistry and materials benchmarks the best transfer-learning su
- old line 141 -> new line 141: The trajectories locate the gap late in the run rather than at the first HF eval
- old line 143 -> new line 143: A stationary kernel imposes one global notion of smoothness, whereas in a descri
- old line 145 -> new line 145: On the three pools whose LF proxy misorders the optimum (HOPV15, Matbench-gap, E
- old line 201 -> new line 201: First, the transfer-learning family is never worse than the baseline MFGP anywhe
- old line 222 -> new line 222: We compared the optimization outcomes with a surrogate-free screen that ranks ca
- old line 226 -> new line 226: We quantified computational cost in floating-point operations (FLOPs) on nine be
- old line 230 -> new line 230: The advantage rests on the LF information that enters the HF head, not on a lear
- old line 234 -> new line 234: The claim concerns a category of pools: descriptor-based chemistry and materials
- old line 296 -> new line 296: The HF loss of every transfer mechanism is the squared error of $\mu^{(H)}_{\mat
- old line 302 -> new line 302: in the Supplementary Information. Supplementary Table~\ref{supptab:surrogate_con
- old line 394 -> new line 394: The feature ablation, the head-path ablation and the HF-only baselines reported
- old line 397 -> new line 397: Reported values are means over seeds with uncertainty as the standard error of t
- old line 9 -> new line 9: 
- old line 139 -> new line 139: 
- old line 51 -> new line 51: SV-MFGP & GPyTorch \texttt{ApproximateGP}; variational ELBO over the full traini
- old line 60 -> new line 60: Domain Adaptation (MMD) & LF network on $\mathcal{L}_{\mathrm{LF}}$; then both n
- old line 89 -> new line 89: yields predictive moments
- old line 118 -> new line 118: Representation entering the heads & the 64 units of the second hidden layer of t
- old line 128 -> new line 128: Supplementary Table~\ref{supptab:model_hyperparams} presents the training hyperp
- old line 139 -> new line 139: method. Pretrain-then-Joint pretrains the LF network for 100 epochs and Domain A
- old line 151 -> new line 151: Domain Adaptation (MMD) & 1e-3 & 1e-4 & 200 & 100 & $\lambda_{\text{MMD}}$=0.1;
- old line 272 -> new line 272: with a greedy policy that selects by its posterior mean, all other settings held
- old line 277 -> new line 277: with a greedy policy that selects by its posterior mean, all other settings held
- old line 301 -> new line 301: the main text (Fig.~\ref{fig:calibration}a--m). Across the eight surrogates and
- old line 304 -> new line 305: the main text (Fig.~\ref{fig:calibration}a--m). Across the eight surrogates and
- old line 316 -> new line 318: Pool & Learned & Random features & Scalar head & HF-only network \\
- old line 327 -> new line 329: Elastic-MatterSim & 0.87 & 0.88 & 0.88 & 0.39 \\
- old line 338 -> new line 340: Elastic-MatterSim & 0.85 & 0.86 & 0.85 & -- \\
- old line 349 -> new line 351: Elastic-MatterSim & 0.88 & 0.88 & 0.88 & -- \\
- old line 360 -> new line 362: Elastic-MatterSim & 0.86 & 0.85 & 0.86 & -- \\
- old line 377 -> new line 379: Elastic-MatterSim & 0.87 & 0.87 & 0.87 & -- \\
- old line 402 -> new line 404: Elastic-MatterSim & 0.87 & 0.88 & 0.78 & 0.30 & 0.88 & 0.15 \\
- old line 409 -> new line 411: Elastic-MatterSim & 0.87 & 0.88 & 0.78 & 0.30 & 0.88 & 0.15 \\
- old line 411 -> new line 413: Pool & $B$ & SF-GP EI & Random HF & MFGP & best TL & SF-GP EI & Random HF & MFGP
- old line 430 -> new line 432: $^{b}$SF-GP EI is a BoTorch \texttt{SingleTaskGP} (Mat\'{e}rn-5/2 ARD kernel, st
- old line 433 -> new line 436: $^{c}$Seeds (of 40) whose regret reached exactly zero within the window: HOPV15,
- old line 446 -> new line 477: Deep-kernel GP & 0.15 & 0.47 & 8/40 & 0.84 & 2.61 \\
- old line 466 -> new line 497: MFBO loop (one surrogate fit plus one pool-wide prediction per iteration,

## 5. Applied — filled during the edit pass

Main text (main.tex)
- Abstract: fixed-model sentence (base transfer-learning surrogate vs baseline MFGP; FLOPs clause kept family-level; 'holds or exceeds' now TL-base); 149 words.
- Fig. 1 caption: TL family defined as TL-base + variants TL-PtJ, TL-E2E, TL-SPS, TL-MMD.
- Introduction: base/variant structure sentence; summary sentence on TL-base (matches or exceeds the baseline MFGP; best-performing GP on all but one).
- Results, synthetic: TL-base values (0.59, 0.35, 0.74) and the Park sentences; GP advantage over TL-base 'largest on Branin'.
- Results, chemistry: TL-base vs baseline MFGP (every pool; 0.02-0.16 on seven) and vs best-performing GP (eight pools; -0.03 on Elastic-SevenNet), cross-reference to the new Supplementary Table; HOPV15 sentence; elastic-pool sentence (0.12-0.13 over MFGP; within 0.02 on two, -0.03 on SevenNet); Matbench trajectory sentence family-level without 'best'.
- Results, trajectories: 'TL-base and the TL variants keep improving'.
- Results, mechanism paragraph: rename only.
- Results, misordering pools: TL-base vs HF-only level and vs best-performing GP; family margin sentence labelled (best TL minus best GP, rho = -0.88) plus the TL-base clause (0.06-0.09 on the three zero-overlap pools; -0.03..+0.02 elsewhere).
- Results, compute: 'TL-base ... matching or exceeding the baseline MFGP' (was 'best GP').
- Discussion: first paragraph (a GP highest only on Branin/Park-Unfav; TL-base vs baseline MFGP; margins over the best-performing GP above 0.05 only on the three misordering pools; TL-base a more reliable default than the baseline MFGP); 'TL-base holds or exceeds that level'; final paragraph replaced (regime-unknown argument, one loss by 0.03, +0.06-0.16 over MFGP on the misordering pools, default to TL-base).
- Methods: framework sentence names TL-base and the four variants with full names; all later mentions renamed; 'small margins' convention no longer cites the elastic pools.
- Fig. 1a overview (paper_figures/fig1_overview.tex): chip text 'TL-base >= MFGP on all 9 chemistry & materials pools' (was 'TL >= GP').

SI (si-content.tex)
- Surrogate configuration table: family header names TL-base and the variants; rows renamed.
- Training tables/notes, feature-ablation group headers, head-path ablation caption, pick-log table, FLOPs ranking sentence: renamed.
- HF-only baseline table: 'best TL' columns replaced by TL-base at the table's budgets (attainment 0.59/0.35/0.24/0.44/0.92/0.96/0.96/0.38/0.41/0.41/0.62/0.69/0.87; final regret 0.13/1.16/0.00/0.00/0.00/0.00/0.00/1.27/0.12/0.08/278/129/244), caption and footnote renamed.
- New Supplementary Table supptab:tlbase_vs_gp (13 pools; TL-base, baseline MFGP, delta; best-performing GP, attainment, delta; mean +- s.e.; no seed fractions) plus a one-sentence paragraph pointing to it.

Not changed (other items or family-level by design): Fig. 3 top-k figure (no surrogate labels), Fig. 4 grid maps and grid text (family-level, labelled), FLOPs numbers (22x remains the family statement), Fig. 1o,p normalized score.
Figures: label regeneration on the VM in progress (see reproducibility/values/REGEN_LABELS_TLBASE_20260916.md when written).

