#!/bin/bash
# Regenerate Fig 5c / SI Fig 3 from the BLR-head FLOPs profile for the four GP-set combos (run on the VM, from figrepo/figures).
set -e; cd "$(dirname "$0")"; PY=${PYBIN:-/mnt/data/jaewook_mfbo/bo_env/bin/python}
for combo in "base:" "nargp:NARGP" "dkl:DKL" "nargp_dkl:NARGP,DKL"; do
  FIG_OUT=${combo%%:*}; GPV=${combo#*:}; export FIG_OUT GP_VARIANTS=$GPV; mkdir -p out/$FIG_OUT
  MPLBACKEND=Agg $PY plot_computing_flops_blr.py > out/$FIG_OUT/plot_computing_flops_blr.log 2>&1 && echo "$FIG_OUT flops ok" || { echo "FAILED flops $FIG_OUT"; tail -5 out/$FIG_OUT/plot_computing_flops_blr.log; }
  MPLBACKEND=Agg $PY make_scaling_law_blr.py > out/$FIG_OUT/make_scaling_law_blr.log 2>&1 && echo "$FIG_OUT scaling ok" || { echo "FAILED scaling $FIG_OUT"; tail -5 out/$FIG_OUT/make_scaling_law_blr.log; }
  for f in compute_scaling_law_blr computing_time_blr; do pdftoppm -jpeg -r 100 -jpegopt quality=78 -singlefile out/$FIG_OUT/$f.pdf out/$FIG_OUT/$f; done
done
grep -h "k_N\|break-even" out/*/make_scaling_law_blr.log
