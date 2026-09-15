#!/bin/bash
# args: HF_HEAD LF_TARGET WARM ACT OUTDIR BENCH MODEL SEED...
export HF_HEAD=$1 LF_TARGET=$2 WARM=$3 ACT=$4 WARM_EPOCHS=50
export SKIP_DIRS=""
export CUDA_VISIBLE_DEVICES="" TORCH_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 PYTHONUNBUFFERED=1
cd "$(dirname "$0")"
OUT=$5; B=$6; M=$7; shift 7
mkdir -p logs_grid5tl
PY=${PYBIN:-/mnt/data/jaewook_mfbo/bo_env/bin/python}
$PY -u run_tl.py --benches "$B" --models "$M" --seeds "$@" --outdir "$PWD/$OUT" > "logs_grid5tl/${OUT}__${B}__${M}__s$1.log" 2>&1
echo "[done] $(date +%H:%M:%S) $OUT $B $M $* rc=$?" >> logs_grid5tl/_progress.log
