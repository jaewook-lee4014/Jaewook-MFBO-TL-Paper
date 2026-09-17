# Discussion restructure (2026-09-17)

Top-down plan behind the rewritten Discussion in main.tex. Results 2.1-2.6 and the Introduction were not touched.
Body word count (figures, storylines and citations excluded, brace-aware count as in wc_body.py of this note):
Introduction 777, Results 1,959, Discussion 764 (was 747); main text 3,500 against the NCS cap of 3,500.

## Section-level flow (five paragraphs)

| # | Question the paragraph answers | Must contain | Bridge to the next paragraph |
|---|---|---|---|
| 1 | Was the Introduction's hypothesis right? | Why the surrogate must be chosen before HF data exist; the hypothesis; verdict (supported on molecular/materials pools, not on the synthetic functions); TL-base vs GP-base and vs the best GP incl. the one loss (Elastic-SevenNet); the advantage is robustness; compute | "robustness" -> when it matters |
| 2 | When does the advantage appear? | Tie where the proxy ranks the optimum near the top (COFs, FreeSolv, Polarizability); separation where it misorders it (HOPV15, Matbench-gap, ExptGap-PBE); grid isolates agreement (rho -0.81) from R^2 (-0.09); correlation is the wrong axis for WHICH surrogate and for WHETHER one is needed (COFs screen, Note 7); a correlation-only map needs an agreement axis; agreement is known only in retrospect | "a surrogate that stays competitive when agreement is unknown" -> why TL-base has that property |
| 3 | Why does TL-base have that property? | The Introduction's mechanism (shared kernel vs HF-fitted head); ablations confirm the route but drop the representation; LF prediction = additive baseline corrected with few parameters, which is why TL-base holds where MFGPs fall; not exploration (acquisition swaps, five acquisitions, calibration); surrogate over acquisition within this construction; value lies in the predictive mean | "within this construction" -> limits |
| 4 | Where do the conclusions stop? | Grouped: (a) protocol scope + future work; (b) baseline coverage and representative (two-thirds narrowing on the grid; Park-Fav, Park-Unfav, Elastic-SevenNet beat GP-base but trail another GP) and tuning asymmetry (may inflate the Branin margin); (c) mechanism-conditional: single-substrate grid, optimistic BLR uncertainty for TL-PtJ/TL-E2E/TL-SPS so the exploration verdict is construction-specific; (d) retrospective pools | "within these limits" -> recommendation |
| 5 | What should a practitioner do? | TL-base as the default where proxy reliability is unknown; specific to TL-base (TL-SPS, TL-PtJ lose to GP-base on HOPV15); GPs for smooth analytic objectives; improve the transferred mean first; adoptable without changing the acquisition policy | closes the SDL framing of paragraph 1 |

## What changed relative to the previous Discussion

- Paragraph order: verdict -> when -> why -> limits -> recommendation (previously verdict -> why -> when).
  The "when" content that was split between old P1 and old P3 now sits in one paragraph.
- The Introduction's hypothesis is answered explicitly, and the ablation result is framed as a refinement of the
  hypothesis (route confirmed, representation dispensable) instead of an unexplained contradiction.
- The Introduction's proposed mechanism (shared kernel vs HF-fitted head) is closed in the Discussion for the first time.
- Results 2.5 (surrogate-free screen; COFs rank correlation 0.998 yet the screen fails) now carries the "whether a
  surrogate is needed" point; previously it was merged into a grid sentence with an unlicensed "therefore".
- Removed: the old P2 sentence "When abundant LF information already orders candidates well ..." (contradicted the
  misordering story); duplicated evidence between old P1 and old P5; the duplicated "invest in the transferred mean"
  sentence; the Park-Unfav 0.02 detail (TL-base is 0.03 below GP-SV in Supplementary Table 9).
- Added the honesty qualifiers requested by the 2026-09-15 claim judgment (C-K): TL-base beats GP-base but trails
  another GP on Park-Fav, Park-Unfav and Elastic-SevenNet; the recommendation is for TL-base specifically.
- "surrogate choice outweighs acquisition" is now stated only where its evidence sits (P3) and scoped to "within this
  construction" (claim-judgment item C081).
- The comparator is named in every sentence that carries a margin (GP-base vs best-performing GP).
- SI references follow the plain-number NCS convention: Tables 6/7 (ablations), 8 (HF-only controls), 9 (TL-base vs
  GPs); Notes 2 (BLR), 5 (acquisition/calibration), 7 (screen), 8 (compute).
- "about two thirds" is retained: verified in reproducibility/claim_manifest.csv (K-152; grid mean advantage
  0.0717 -> 0.0253).

## Addendum (2026-09-17, later): limitations paragraph reorganized

The limitations paragraph read as a list (eight sentences, eight subjects, one connective). It now has one scope
sentence and three groups, each with a one-line signpost:

1. Scope: "rest on retrospective evaluation of fixed ... pools under a two-fidelity protocol with a deterministic
   round-robin schedule", immediately followed by the two untested extensions that would relax those conditions
   (hierarchical fidelities, adaptive fidelity selection). Retrospective-ness is stated here as the type of evidence,
   not at the end as a doubt.
2. "Within that scope, the comparison could be biased in either direction": GP representative (advantage shrinks
   against stronger GPs; two-thirds narrowing; Park-Fav/Park-Unfav/Elastic-SevenNet) and, "Conversely", the tuning
   asymmetry (conservative where TL wins, may inflate the Branin margin).
3. "The mechanistic conclusions are tied to their constructions": BLR optimism -> exploration verdict is
   construction-specific; then the grid -> "the nine empirical pools, not the grid, carry the generalization".

The former closing sentence ("the surrogate ranking requires confirmation in deployment") was removed because it sat
directly before "Within these limits, we recommend TL-base as the default" and read as self-negation. The paragraph now
ends on the sentence that anchors the generalization in the nine pools, which is the population the recommendation
addresses. "err" was replaced by "biased" (more common academic usage).

## Addendum 2 (2026-09-17, later): recommendation paragraph trimmed to two sentences

Removed as repetition or overreach: "It is specific to TL-base, because outcomes depended on the transfer mechanism:
TL-SPS and TL-PtJ fell below GP-base on HOPV15" (evidence already in Results 2.2; the recommendation names TL-base
explicitly), "GPs remain preferable for smooth, low-dimensional analytic objectives such as Branin" (stated in
Results 2.1 and Discussion P1; the recommendation is already scoped to molecular and materials pools), and
"Surrogate development should first improve the transferred mean, with uncertainty-driven exploration a secondary
concern" (conflicts with P4's "limited value of exploration is specific to this construction" and generalizes beyond
the evidence; P3's scoped mainclaim already carries the finding). The closing sentence now pairs the two practical
properties: near-linear fitting cost (Results 2.6) and adoption without changing the acquisition policy (acquisition
swaps left the pattern unchanged). Body words: Discussion 731, main text 3,467.
