# -*- coding: utf-8 -*-
"""One-shot patch of the VM figure pipeline for the B = 30 unification (2026-09-13): the four large pools are evaluated at 30
from the cap-31/60 re-runs (ext_chem_20260909/results_confirm_ext). Backs up each script as <name>.bak_b20_20260913. Idempotent."""
import os, shutil
R = "/mnt/data/jaewook_mfbo/MFBO-TL-Paper/experiments/refig_20260908"

def patch(path, reps):
    s = open(path).read(); orig = s
    for a, b in reps:
        if b in s and a not in s:
            continue                                   # already patched
        assert s.count(a) == 1, (path, a[:70], s.count(a))
        s = s.replace(a, b)
    if s != orig:
        bak = path + ".bak_b20_20260913"
        if not os.path.exists(bak):
            shutil.copy(path, bak)
        open(path, "w").write(s); print("patched", os.path.basename(path))
    else:
        print("unchanged (already patched)", os.path.basename(path))

patch(f"{R}/prep_candidates2.py", [
    ('"ExptGap-PBE": 20, "Elastic-CHGNet": 20, "Elastic-SevenNet": 20, "Elastic-MatterSim": 20}\nB_MAX = dict(B_ORIG); B_MAX.update({"FreeSolv": 100, "Polarizability": 60, "HOPV15": 45, "Matbench-Gap": 100})',
     '"ExptGap-PBE": 30, "Elastic-CHGNet": 30, "Elastic-SevenNet": 30, "Elastic-MatterSim": 30}   # 2026-09-13: four large pools evaluated at 30\nB_MAX = dict(B_ORIG); B_MAX.update({"FreeSolv": 100, "Polarizability": 60, "HOPV15": 45, "Matbench-Gap": 100})'),
    ('    "confirm": glob.glob(f"{REFIG}/results_confirm/**/traj_*.csv", recursive=True) + glob.glob(f"{REFIG}/results_confirm_gp/**/traj_*.csv", recursive=True),\n}',
     '    "confirm": glob.glob(f"{REFIG}/results_confirm/**/traj_*.csv", recursive=True) + glob.glob(f"{REFIG}/results_confirm_gp/**/traj_*.csv", recursive=True),\n    "confirm_ext": glob.glob(f"{EXT}/results_confirm_ext/*/cells/traj_*.csv"),   # 2026-09-13 re-runs of the four large pools (TL to 60, GP to >= 31); largest horizon wins over the B = 20 runs\n}'),
])
patch(f"{R}/fig1_attainment.py", [
    ('"ExptGap-PBE": 20, "Elastic-CHGNet": 20, "Elastic-SevenNet": 20, "Elastic-MatterSim": 20}',
     '"ExptGap-PBE": 30, "Elastic-CHGNet": 30, "Elastic-SevenNet": 30, "Elastic-MatterSim": 30}'),
])
patch(f"{R}/fig2_trajectories.py", [
    ('        "ExptGap-PBE": 20, "Elastic-CHGNet": 20, "Elastic-SevenNet": 20, "Elastic-MatterSim": 20}\nBFIG1',
     '        "ExptGap-PBE": 30, "Elastic-CHGNet": 30, "Elastic-SevenNet": 30, "Elastic-MatterSim": 30}\nBFIG1'),
    ('         "ExptGap-PBE": 20, "Elastic-CHGNet": 20, "Elastic-SevenNet": 20, "Elastic-MatterSim": 20}\nLABEL',
     '         "ExptGap-PBE": 30, "Elastic-CHGNet": 30, "Elastic-SevenNet": 30, "Elastic-MatterSim": 30}\nLABEL'),
])
patch(f"{R}/figrepo/figures/make_a1_calibration_13_attain.py", [
    ("BUDGET.update({p: 20 for p in POOLS[9:]})", "BUDGET.update({p: 30 for p in POOLS[9:]})"),
    ("SRC = ['results/blr_replace__hf_argmin', 'results_conf/blr_replace__hf_argmin', 'results_confirm/blr_replace__hf_argmin',\n       'results_gp/gp_ei', 'results_gp_vm/gp_ei', 'results_gp_conf/gp_ei', 'results_confirm_gp/gp_ei']",
     "SRC = ['results/blr_replace__hf_argmin', 'results_conf/blr_replace__hf_argmin', '../ext_chem_20260909/results_confirm_ext/blr_replace__hf_argmin',\n       'results_gp/gp_ei', 'results_gp_vm/gp_ei', 'results_gp_conf/gp_ei', '../ext_chem_20260909/results_confirm_ext/gp_ei']   # 2026-09-13: four large pools from the B = 30 re-runs"),
])
print("OK")
