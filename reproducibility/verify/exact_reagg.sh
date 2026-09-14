#!/bin/bash
# Re-aggregation of Fig. 1 b-p / Fig. 4 a-m WITHOUT the 6-significant-digit rounding of export_explorer.py (2026-09-14).
# Nothing in figcand2_20260911 is touched; every output goes to figcand2_20260914_exact/. The figure scripts are byte-identical
# copies of the 2026-09-13 scripts except for the output/input directory (sed) and the precision line.
set -euo pipefail
R=/mnt/data/jaewook_mfbo/MFBO-TL-Paper/experiments/refig_20260908
N=$R/figcand2_20260914_exact
PY=/mnt/data/jaewook_mfbo/e1_venv_cu121/bin/python
[ -x $PY ] || PY=/mnt/data/jaewook_mfbo/bo_env/bin/python
mkdir -p $N/scripts
cd $R
# 1. exporter with full precision
sed -e 's|\[round(x, 3), float(f"{y:.6g}")\]|[float(x), float(y)]|' -e 's|figcand2_20260911/explorer_data.json|figcand2_20260914_exact/explorer_data.json|' export_explorer.py > $N/scripts/export_explorer_exact.py
grep -n "float(x), float(y)" $N/scripts/export_explorer_exact.py || { echo "precision patch failed"; exit 1; }
# 2. fig1 / fig2 scripts pointed at the new directory
sed -e 's|refig_20260908/figcand2_20260911"|refig_20260908/figcand2_20260914_exact"|' fig1_attainment.py > $N/scripts/fig1_attainment_exact.py
sed -e 's|refig_20260908/figcand2_20260911"|refig_20260908/figcand2_20260914_exact"|' fig2_trajectories.py > $N/scripts/fig2_trajectories_exact.py
grep -c figcand2_20260914_exact $N/scripts/fig1_attainment_exact.py $N/scripts/fig2_trajectories_exact.py
# 3. calibration figure: read the exact fig1 values, write into the new directory
sed -e "s|R / 'figcand2_20260911' / 'fig1_attainment_values.csv'|R / 'figcand2_20260914_exact' / 'fig1_attainment_values.csv'|" -e "s|OUT = R / 'figrepo' / 'figures' / 'out'|OUT = R / 'figcand2_20260914_exact'|" figrepo/figures/make_a1_calibration_13_attain.py > $N/scripts/make_a1_calibration_13_attain_exact.py
grep -c figcand2_20260914_exact $N/scripts/make_a1_calibration_13_attain_exact.py
md5sum export_explorer.py fig1_attainment.py fig2_trajectories.py figrepo/figures/make_a1_calibration_13_attain.py prep_candidates2.py $N/scripts/*.py > $N/scripts/md5_sources.txt
$PY -c "import matplotlib,numpy,pandas;print('matplotlib',matplotlib.__version__,'numpy',numpy.__version__,'pandas',pandas.__version__)" > $N/scripts/env.txt
echo "python $PY" >> $N/scripts/env.txt
# run
$PY $N/scripts/export_explorer_exact.py 2>&1 | tail -2
SUMMARY=score $PY $N/scripts/fig1_attainment_exact.py 2>&1 | tail -2
$PY $N/scripts/fig2_trajectories_exact.py 2>&1 | tail -2
cd figrepo/figures && ECE_X=mean CAL_LETTERS=abcdefghijklm CAL_STEM=fig4_calibration_attain $PY $N/scripts/make_a1_calibration_13_attain_exact.py 2>&1 | tail -16
cd $N && ls -la && md5sum *.pdf *.csv *.json > md5_outputs.txt
echo "---- compare with figcand2_20260911"
$PY - <<'EOF'
import pandas as pd, numpy as np
R='/mnt/data/jaewook_mfbo/MFBO-TL-Paper/experiments/refig_20260908'
a=pd.read_csv(f'{R}/figcand2_20260911/fig1_attainment_values.csv'); b=pd.read_csv(f'{R}/figcand2_20260914_exact/fig1_attainment_values.csv')
c=a.merge(b,on=['pool','model'],suffixes=('_old','_new')); c['d']=c.mean_new-c.mean_old
print('fig1 cells changed (>1e-9):', int((c.d.abs()>1e-9).sum()), 'max |d|', c.d.abs().max())
print(c[c.d.abs()>1e-9][['pool','model','n_old','n_new','mean_old','mean_new','d']].round(4).to_string(index=False))
for s in ['fig1_attainment_summary_score.csv','fig1_attainment_summary_score_chem.csv']:
    o=pd.read_csv(f'{R}/figcand2_20260911/{s}',index_col=0); n=pd.read_csv(f'{R}/figcand2_20260914_exact/{s}',index_col=0)
    print(s); print(pd.DataFrame({'old':o['mean'],'new':n['mean'].reindex(o.index)}).round(4).to_string())
o=pd.read_csv(f'{R}/figcand2_20260911/fig2_trajectories_values.csv'); n=pd.read_csv(f'{R}/figcand2_20260914_exact/fig2_trajectories_values.csv')
c=o.merge(n,on=['pool','model'],suffixes=('_old','_new')); print('fig2 max |mean_end diff|', (c.mean_end_old-c.mean_end_new).abs().max())
o=pd.read_csv(f'{R}/figrepo/figures/out/fig4_calibration_attain_values.csv'); n=pd.read_csv(f'{R}/figcand2_20260914_exact/fig4_calibration_attain_values.csv')
c=o.merge(n,on=['benchmark','model'],suffixes=('_old','_new')); print('fig4 max |attainment diff|', (c.attainment_old-c.attainment_new).abs().max(), 'max |ece diff|', (c.ece_lf_mean_old-c.ece_lf_mean_new).abs().max())
import numpy as np
for p in ['Branin-Fav','Branin-Unfav']:
    t=n[n.benchmark==p]; print(p, 'new Pearson r', round(float(np.corrcoef(t.ece_lf_mean,t.attainment)[0,1]),3))
EOF
echo "EXACT REAGG DONE"
