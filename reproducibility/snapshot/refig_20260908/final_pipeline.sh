#!/bin/bash
# Final regeneration on the VM after the confirmation pools: fresh GP seeds replace the fallback rows, all figures/stats
# for the four GP-set combos, extra metrics, multi-metric, interactive JSON, Fig 3/4 metric figures, BLR FLOPs figures, analysis.
cd /mnt/data/jaewook_mfbo/MFBO-TL-Paper/experiments/refig_20260908
export PY=/mnt/data/jaewook_mfbo/bo_env/bin/python PYBIN=/mnt/data/jaewook_mfbo/bo_env/bin/python
export GP_ROOTS="$PWD/results_gp:$PWD/results_gp_vm:$PWD/results_gp_vm2"
export OMP_NUM_THREADS=4 MKL_NUM_THREADS=4 OPENBLAS_NUM_THREADS=4 MPLBACKEND=Agg
rm -f final_pipeline.done
{ echo "== make_all $(date)"; bash make_all.sh; } > make_all_final.log 2>&1
{ echo "== extra $(date)"; bash run_extra_metrics.sh; } > extra_final.log 2>&1
{ echo "== mm $(date)"; $PY compute_multimetric.py; } > mm_final.log 2>&1
{ echo "== interactive $(date)"; $PY prep_interactive.py; } > prep_final.log 2>&1
{ echo "== fig34 $(date)"; bash run_fig34_metrics_vm.sh; } > fig34_final.log 2>&1
{ echo "== flops $(date)"; cd figrepo/figures && bash make_flops_blr.sh; cd ../..; } > flops_final.log 2>&1
{ echo "== analyze $(date)"; $PY analyze_conf.py; $PY status_conf.py; } > analyze_final.log 2>&1
touch final_pipeline.done; echo "FINAL PIPELINE DONE $(date)"
