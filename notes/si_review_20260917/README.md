# Supplementary Information review (2026-09-17)

Scope: si-content.tex on top of origin/main f7222aa. Main text untouched. Extended Data not used (decision 2026-09-17).

## Criteria (NCS "Preparing your material", NCS "Content types", Nature "Supplementary information")

1. Every SI item is referred to at least once in the main text (Nature rule). Status: Notes 1-8, Tables 1-11 and
   Figs 1-4 are all cited. The earlier report that Table 3 was uncited was a parser bug; Methods 4.10 cites
   "Supplementary Tables 2 and 3". Checker: si_refs.py in this folder.
2. Nothing in the SI restates the Methods. Each Note keeps one orienting sentence and points to the Methods
   subsection (Methods 4.x, plain numbers, because NCS receives the SI as a separate file). Sentence-level
   duplicates (8-word shingles, >= 50 percent shared): 1 before, 0 after. Topic-level duplicates removed as
   listed below.
3. Only material relevant to the conclusions and needed to understand or replicate the study (NCS wording).
4. Terminology as in the main text (SI is not copy-edited); every table and figure has a title and a caption
   (15 of 15).
5. Numbering follows display order inside the SI (Nature rule), so the current scheme stands; plain-number
   cross-references in main.tex were re-checked after the edit.
6. Deferred to submission: the SI reference list (18 citations with their own bibliography; Nature asks to avoid
   SI references or to continue the main-text numbering), the Reporting Summary and Source Data (submission
   system items, not SI content).

## Per-Note relevance and action

| Note | Supports (main text) | Words before -> after | Action |
|---|---|---|---|
| 1 Surrogate configurations | Methods 4.3 (GP priors, "Supplementary Note 1"; Table 1 pointer) | 622 -> 558 | Intro restatement of the shared protocol replaced by pointers to Methods 4.2, 4.3 and 4.10. GP-base fitting sentences repeating Methods 4.3 and the EI/greedy acquisition sentence repeating Methods 4.2 removed. GP priors, GP-DKL and GP-SV details kept. |
| 2 BLR | Methods 4.3 (head, leave-one-out rule); Discussion limits (optimistic uncertainty for TL-PtJ/E2E/SPS) | 433 -> 433 | Kept. |
| 3 Implementation | Methods 4.10 ("Supplementary Tables 2 and 3"); Methods 4.4 ("Supplementary Note 3 gives full loss functions and method-specific hyperparameters") | 476 -> 212 | The per-surrogate prose recipes (same numbers as Methods 4.4 and Table 3) and the closing paragraph (same as Table 1 footnote b and Methods 4.3) deleted. Kept only what neither the tables nor Methods state: the DNGOJoint code name, the exact TL-SPS penalty, the TL-MMD truncation to the first n_HF points and its HF-stage loss. |
| 4 Benchmark definitions | Table 1 caption; Methods 4.5 (four pointers); Methods 4.1 (R^2) | 933 -> 770 | Cost-accounting sentences of the intro, the "Molecular pools" paragraph (FreeSolv direction and optimum are in Table 4 and Methods 4.5) and the "Cost ratios" paragraph (all in Methods 4.5 and the rho column of Table 4) deleted. Band-gap/elastic paragraph reduced to the three facts found nowhere else (ExptGap-PBE averaging and matching, SevenNet coverage, maximum moduli). Scharber proxy, Branin and Park definitions and the scenario table kept in full. Table 4 caption pointer "(see text)" now "(Methods 4.5)". |
| 5 Acquisition variants and calibration | Results 2.4 ("no consistent improvement / gains / association"); Methods 4.2 | 680 -> 613 | Protocol sentences now in Methods 4.2 replaced by pointers. Kept the settings Methods does not state (LCB beta = 2, MES Gumbel with ten samples, 5 x 9 x 20 runs, shared TL-base arms, matched control only for GP-base) and every result paragraph. The unreported "negative log-likelihood and sharpness" removed. |
| 6 Controls and pick logs | Results 2.3 and 2.4 (Tables 6-9, 11); Methods 4.10 (Table 10) | 366 -> 175 | Protocol paragraphs now in Methods 4.8 reduced to one pointer sentence per table; head-path ablation specifics kept. |
| 7 Screen | Results 2.5; Fig. 4 | 152 -> 103 | Definition paragraph (Methods 4.6) replaced by a pointer; regime placements with their numbers kept. |
| 8 Compute | Results 2.6 (22-fold, 15-fold); Fig. 5 | 186 -> 120 | Profiling protocol (Methods 4.9) replaced by a pointer; the absolute costs and rank results kept. |

SI body words 3,848 -> 2,984 (tables and figures excluded). si_clean.pdf 0.77 MB against the 30 MB limit.
Build: bash build.sh clean, no undefined references or float warnings.

## Left for the user to decide

- Tables 2 and 3 repeat the TL rows of Table 1 (fitting procedure, epochs, learning rates, weight decay).
  Either delete Tables 2 and 3 and cite Table 1 from Methods 4.10 (renumbers Tables 4-11 to 2-9 in both files), or
  keep them as the readable TL-only summary. Left as is.
- SI Fig. 4 caption reports the GP-base fit exponent k = 3.0; main Fig. 5 reports the family slope 2.29. Consistent
  (per-surrogate versus shared-slope fit) but worth one glance.
- Terminology check found only "DNGOJoint" (deliberate code-name mapping) and "MFGP" as the expansion of
  "multi-fidelity GP" in Note 1; no other code names.
