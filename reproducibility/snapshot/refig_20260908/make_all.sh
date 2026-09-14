#!/bin/bash
# Run on the VM: merge results, regenerate figures + statistics. Env overrides see collect.py.
set -e
cd "$(dirname "$0")"
export PY=${PYBIN:-/mnt/data/jaewook_mfbo/bo_env/bin/python}
export TL_ROOTS=${TL_ROOTS:-"$PWD/results:$PWD/results_slurm"}
export GP_ROOTS=${GP_ROOTS:-"$PWD/results_gp:$PWD/results_gp_vm"}
export GP_FALLBACK=${GP_FALLBACK:-"$PWD/gp_fallback"}
export GRID_TL_ROOTS=${GRID_TL_ROOTS:-"$PWD/results_grid:$PWD/results_grid_slurm"}
export GRID_GP_ROOTS=${GRID_GP_ROOTS:-"$PWD/results_grid_gp:$PWD/results_grid_gp_vm"}
export PUBGRID=${PUBGRID:-"$PWD/pubgrid"}
$PY collect.py 2>&1 | tee figrepo/collect.log
cd figrepo/figures
for combo in "base:" "nargp:NARGP" "dkl:DKL" "nargp_dkl:NARGP,DKL"; do
  FIG_OUT=${combo%%:*}; GPV=${combo#*:}
  export FIG_OUT GP_VARIANTS=$GPV; mkdir -p out/$FIG_OUT
  echo "=== variant $FIG_OUT (GP_VARIANTS='$GPV')"
  for s in make_final_regret make_final_regret_collapsed make_regret_trajectory make_a6_acquisition_matrix make_acquisition_portfolio make_a1_calibration make_fig1c_and_anytime_row make_si_star_sensitivity plot_computing_flops make_scaling_law stats_friedman_nemenyi_9bench; do
    echo "== $s"; MPLBACKEND=Agg $PY $s.py > out/$FIG_OUT/$s.log 2>&1 && echo ok || { echo "FAILED $s"; tail -20 out/$FIG_OUT/$s.log; }
  done
  ( cd ../..; MPLBACKEND=Agg $PY stats_refig.py > figrepo/figures/out/$FIG_OUT/stats_refig.log 2>&1 && echo "stats ok" || { echo "stats FAILED"; tail -20 figrepo/figures/out/$FIG_OUT/stats_refig.log; } )
done
ls figrepo/figures/out/*/*.pdf 2>/dev/null | wc -l
