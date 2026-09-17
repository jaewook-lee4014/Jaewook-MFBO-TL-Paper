"""Count the seeds with a finite loop-mean LF ECE per (benchmark, surrogate) for the eight surrogates of SI Fig. 3,
using exactly the sources and filters of make_a1_calibration_13_attain_exact.py (2026-09-17 check of SI Note 4)."""
import glob
from pathlib import Path
import numpy as np, pandas as pd
R = Path('/mnt/data/jaewook_mfbo/MFBO-TL-Paper/experiments/refig_20260908')
POOLS = ['Branin-Fav', 'Branin-Unfav', 'Park-Fav', 'Park-Unfav', 'COFs', 'FreeSolv', 'Polarizability', 'HOPV15', 'Matbench-Gap',
         'ExptGap-PBE', 'Elastic-CHGNet', 'Elastic-SevenNet', 'Elastic-MatterSim']
DROP = {'NARGP', 'KnowledgeDistillation', 'PseudoLabeling', 'Curriculum', 'Sequential', 'Progressive', 'Adapter'}
NAMES = {'SparseMFGP': 'Sparse MFGP', 'DNGOGradient': 'End-to-End Joint', 'DNGOJoint': 'Frozen-representation transfer',
         'TwoStageJoint': 'Pretrain-then-Joint', 'DomainAdaptationMMD': 'Domain Adaptation (MMD)', 'SoftParameterSharing': 'Soft Parameter Sharing'}
SRC = ['results/blr_replace__hf_argmin', 'results_conf/blr_replace__hf_argmin', '../ext_chem_20260909/results_confirm_ext/blr_replace__hf_argmin',
       'results_gp/gp_ei', 'results_gp_vm/gp_ei', 'results_gp_conf/gp_ei', '../ext_chem_20260909/results_confirm_ext/gp_ei']
summ = pd.concat([pd.read_csv(f) for d in SRC for f in glob.glob(str(R / d / 'cells' / 'summary_*.csv'))], ignore_index=True)
summ = summ[summ.benchmark.isin(POOLS) & summ.seed.between(42, 81) & ~summ.model.isin(DROP)].drop_duplicates(['benchmark', 'model', 'seed'])
summ['model'] = summ.model.replace(NAMES)
g = summ.groupby(['benchmark', 'model']).agg(n_rows=('seed', 'size'), n_ece=('ece_lf_mean', lambda x: int(np.isfinite(x).sum())))
g = g.reset_index()
print('cells:', len(g), ' min n_ece:', g.n_ece.min(), ' max:', g.n_ece.max())
low = g[g.n_ece < 40].sort_values(['benchmark', 'model'])
print('cells with fewer than 40 finite ECE seeds:', len(low))
print(low.to_string(index=False))
