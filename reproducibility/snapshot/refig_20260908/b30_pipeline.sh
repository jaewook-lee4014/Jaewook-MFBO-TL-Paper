#!/bin/bash
# Run on the VM after the cap-31 GP campaign and the report job have landed (results_confirm_ext complete).
# Regenerates explorer_data.json, Fig. 1 b-p (attainment, score summary), Fig. 2 a-m and Fig. 4 (calibration x attainment,
# letters a-m as in the manuscript) with the four large pools evaluated at B = 30. Previous outputs are kept in figcand2_20260911.bak_b20_20260913.
set -euo pipefail
R=/mnt/data/jaewook_mfbo/MFBO-TL-Paper/experiments/refig_20260908; E=/mnt/data/jaewook_mfbo/MFBO-TL-Paper/experiments/ext_chem_20260909
PY=/mnt/data/jaewook_mfbo/e1_venv_cu121/bin/python
ntl=$(ls $E/results_confirm_ext/blr_replace__hf_argmin/cells/summary_*.csv 2>/dev/null | wc -l); ngp=$(ls $E/results_confirm_ext/gp_ei/cells/summary_*.csv 2>/dev/null | wc -l)
echo "results_confirm_ext: TL $ntl/1440, GP $ngp/480"
if [ "${FORCE:-0}" != 1 ] && { [ "$ntl" -lt 1440 ] || [ "$ngp" -lt 480 ]; }; then echo "incomplete; set FORCE=1 to run anyway"; exit 2; fi
[ -d $R/figcand2_20260911.bak_b20_20260913 ] || cp -a $R/figcand2_20260911 $R/figcand2_20260911.bak_b20_20260913
cd $R && $PY export_explorer.py 2>&1 | tail -3
SUMMARY=score $PY fig1_attainment.py 2>&1 | tail -3
$PY fig2_trajectories.py 2>&1 | tail -3
cd $R/figrepo/figures && ECE_X=mean $PY make_a1_calibration_13_attain.py 2>&1 | tail -3
ECE_X=mean CAL_LETTERS=abcdefghijklm CAL_STEM=fig4_calibration_attain $PY make_a1_calibration_13_attain.py 2>&1 | tail -2
echo "---- four-pool attainment at B = 30 (mean over the seeds present):"
$PY - <<'PY'
import pandas as pd
d = pd.read_csv('/mnt/data/jaewook_mfbo/MFBO-TL-Paper/experiments/refig_20260908/figcand2_20260911/fig1_attainment_values.csv')
for p in ['ExptGap-PBE', 'Elastic-CHGNet', 'Elastic-SevenNet', 'Elastic-MatterSim']:
    t = d[d.pool == p].sort_values('mean', ascending=False)
    print(p, ' | '.join(f"{r.model}:{r['mean']:.2f}(n{int(r.n)})" for _, r in t.iterrows()))
PY
echo "B30 PIPELINE DONE $(date)"
