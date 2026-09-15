# Transfer Learning Architectures for Scalable Multi-Fidelity Bayesian Optimization (manuscript repository)

Submission to Nature Computational Science. `main.tex` is the main text, `si-content.tex` the Supplementary Information
(built standalone by `si.tex`); `bash build.sh clean` builds the redline PDFs (`main.pdf`, `si.pdf`: struck = superseded text,
blue = current text) and the clean PDFs (`main_clean.pdf`, `si_clean.pdf`). `paper_figures/` holds the figures; only the ten
files referenced by `\includegraphics` are current (see `reproducibility/figure_manifest.csv` for the rest).

## Where to start as a reviewer

1. `REPRODUCIBILITY_RECONCILIATION.md`: which code, data, settings and raw results stand behind every figure and number,
   what was verified by recomputation on 2026-09-14, what was corrected, and what is still open.
2. `reproducibility/claim_manifest.csv`: every quoted number with its recomputed value, source experiment and verdict.
3. `reproducibility/run_manifest.csv` (and `.json`): the experiments (dataset, model, seeds, budget, acquisition, code, paths,
   environment) including the superseded sets that must not be mistaken for current results.
4. `reproducibility/figure_manifest.csv`: figure file -> generating script -> inputs -> md5.
5. `reproducibility/snapshot/`: the run and figure code as executed (md5 list), the benchmark builders and the four
   materials pools not yet in the public repository (check with `cd reproducibility && md5sum -c snapshot/md5sums.txt`);
   `reproducibility/values/`: the value files behind each figure; `reproducibility/verify/`: the verification script and its outputs.

The public code and data repository named in the manuscript, `MGuo-Lab/MFBO-TL`, currently serves the previous run set;
`reproducibility/public_release_manifest.csv` lists what must be published to match the manuscript.
