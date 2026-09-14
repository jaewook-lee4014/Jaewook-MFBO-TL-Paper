#!/bin/bash
#SBATCH --partition=cpu,interruptible_cpu
#SBATCH --requeue
#SBATCH --output=/users/k23070952/mfbo_confirm_ext/logs/%x_%A_%a.out
# Budget extension of the four large materials pools (ExptGap-PBE, Elastic-CHGNet/SevenNet/MatterSim) with the
# pick-log runner (ext_chem_20260909 run_tl.py / run_gp.py). From scratch, initial design of the ORIGINAL budget 20
# (2 HF + 20 LF = 3 units, identical FPS init), run to CAP HF-equivalent units.
# usage: CAP=60 sbatch -J confirm_ext_tl --mem=6G  --time=24:00:00 --cpus-per-task=1 --array=0-239 submit_confirm_ext.sbatch tasks_confirm_ext_tl.txt 240
#        CAP=60 sbatch -J confirm_ext_gp --mem=28G --time=24:00:00 --cpus-per-task=1 --array=0-479 submit_confirm_ext.sbatch tasks_confirm_ext_gp.txt 480
# Results / checkpoints / logs go to the HOME volume (never the project cephfs: 2026-09-11 MDS stall rule); rsync back once at the end.
# Re-submitting the same command continues: finished seeds are skipped (SKIP_DIRS), killed GP seeds resume from their 50-step checkpoint (RESUME_DIRS).
set -uo pipefail
HERE=/cephfs/volumes/hpc_data_prj/eng_waste_to_protein/ae035a41-20d2-44f3-aa46-14424ab0f6bf/repositories/MFBO-TL-Paper-Copy260818/experiments/ext_chem_20260909
PY=/users/k23070952/.conda/envs/paper_v1_py39/bin/python
W=/users/k23070952/mfbo_confirm_ext
source $HERE/ext_env.sh
CAP=${CAP:?set CAP (HF-equivalent budget cap, e.g. 60)}
export EXT_BUDGETS="ExptGap-PBE=$CAP,Elastic-CHGNet=$CAP,Elastic-SevenNet=$CAP,Elastic-MatterSim=$CAP"
T=${SLURM_CPUS_PER_TASK:-1}; export TORCH_THREADS=$T OMP_NUM_THREADS=$T MKL_NUM_THREADS=$T
export OUTDIR=$W/results CKPT_DIR=$W/ckpt RESUME_DIRS=$W/ckpt SKIP_DIRS=$W/results
TASKFILE=$1; K=$2; ID=$SLURM_ARRAY_TASK_ID
echo "[element] $(date) cap=$CAP threads=$T host=$(hostname) taskfile=$TASKFILE K=$K id=$ID"
awk -v k="$K" -v id="$ID" '(NR-1)%k==id' "$HERE/$TASKFILE" | while read -r KIND MODEL BENCH SEED; do
  echo "[start] $(date +%H:%M:%S) $KIND $MODEL $BENCH s$SEED"
  if [ "$KIND" = gp ]; then R=run_gp.py; else R=run_tl.py; fi
  "$PY" -u "$HERE/$R" --benches "$BENCH" --models "$MODEL" --seeds $SEED --outdir "$OUTDIR" 2>&1 | grep -v "^$"
  echo "[done] $(date +%H:%M:%S) $KIND $MODEL $BENCH s$SEED"
done
echo "[ELEMENT DONE] $(date)"
