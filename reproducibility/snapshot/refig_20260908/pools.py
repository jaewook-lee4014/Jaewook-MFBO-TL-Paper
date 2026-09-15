"""Pool definitions shared by run_ladder.py (TL) and run_gp_raw.py (GP).
Raw (no-PCA) variants keep HF, LF and candidate order identical to the paper pools; only the
input representation changes. Grid cells reproduce the controlled-grid protocol (warm-up 2 HF + 5 LF)."""
import numpy as np

PAPER = {
    'COFs': dict(csv='cofs.csv', cost_ratio=0.065, use_smiles=False, negate=True, budget=30),
    'FreeSolv': dict(csv='freesolv.csv', cost_ratio=0.1, use_smiles=True, negate=False, budget=50),
    'Polarizability': dict(csv='polarizability.csv', cost_ratio=0.167, use_smiles=True, negate=True, budget=30),
    'HOPV15': dict(csv='hopv15.csv', cost_ratio=0.1, use_smiles=False, negate=True, budget=30),
    'Matbench-Gap': dict(csv='matbench_gap.csv', cost_ratio=0.05, use_smiles=False, negate=False, budget=20),
    'Branin-Fav': dict(csv='synthetic_branin_fav.csv', cost_ratio=0.1, use_smiles=False, negate=False, budget=50),
    'Branin-Unfav': dict(csv='synthetic_branin_unfav.csv', cost_ratio=0.5, use_smiles=False, negate=False, budget=50),
    'Park-Fav': dict(csv='synthetic_park_fav.csv', cost_ratio=0.1, use_smiles=False, negate=False, budget=50),
    'Park-Unfav': dict(csv='synthetic_park_unfav.csv', cost_ratio=0.5, use_smiles=False, negate=False, budget=50),
}
RAW = {
    'FreeSolv-raw': dict(csv='freesolv.csv', cost_ratio=0.1, use_smiles=True, negate=False, budget=50, pca=None),
    'Polarizability-raw': dict(csv='polarizability.csv', cost_ratio=0.167, use_smiles=True, negate=True, budget=30, pca=None),
    'Matbench-Gap-raw': dict(csv='matbench_gap_highd.csv', cost_ratio=0.05, use_smiles=False, negate=False, budget=20, pca=None),
    'HOPV15-raw': dict(csv='hopv15_raw.csv', cost_ratio=0.1, use_smiles=True, negate=True, budget=30, pca=None),
}

# Representation-dimension sweep (2026-09-03): same HF/LF/candidates as the paper pools, input = PCA-k of the raw
# descriptors (RDKit 2D for SMILES pools; the 132 composition features for Matbench-Gap). k=10 for SMILES pools is the
# paper pipeline itself; 'Matbench-Gap-pca10r' recomputes PCA-10 from the 132-d file (the paper used a precomputed file).
SWEEP = {}
for _k in (5, 20, 50):
    SWEEP[f'FreeSolv-pca{_k}'] = dict(csv='freesolv.csv', cost_ratio=0.1, use_smiles=True, negate=False, budget=50, pca=_k)
    SWEEP[f'Polarizability-pca{_k}'] = dict(csv='polarizability.csv', cost_ratio=0.167, use_smiles=True, negate=True, budget=30, pca=_k)
    SWEEP[f'HOPV15-pca{_k}'] = dict(csv='hopv15_raw.csv', cost_ratio=0.1, use_smiles=True, negate=True, budget=30, pca=_k)
    SWEEP[f'Matbench-Gap-pca{_k}'] = dict(csv='matbench_gap_highd.csv', cost_ratio=0.05, use_smiles=False, negate=False, budget=20, pca=_k)
SWEEP['Matbench-Gap-pca10r'] = dict(csv='matbench_gap_highd.csv', cost_ratio=0.05, use_smiles=False, negate=False, budget=20, pca=10)
# Real low-agreement materials pools (top-10 agreement 0.0 in landscape_metrics.csv): same convention as Matbench-Gap.
SWEEP['JARVIS-gap'] = dict(csv='jarvis_gap.csv', cost_ratio=0.05, use_smiles=False, negate=False, budget=20)
SWEEP['ExptGap'] = dict(csv='expt_gap_pbe.csv', cost_ratio=0.05, use_smiles=False, negate=False, budget=20)

# Landscape-shape intervention (2026-09-03): same candidates and features as the paper pools, objective changed.
#  Polarizability-tgtNN : minimise |alpha - alpha*| with alpha* = the NN-th percentile of HF alpha (interior optimum);
#                         LF transformed the same way. Features/PCA/init design identical to 'Polarizability'.
#  COFs-sel605 / COFs-Xe605 : the 605 COFs with GCMC + Henry data in the Gantzler et al. repository; -sel605 keeps the
#                         paper's Xe/Kr selectivity (control), -Xe605 maximises the mixture Xe uptake (mmol/g; LF = Henry
#                         coefficient x 0.2 bar). Features identical between the two, so the init design is identical.
TARGET = {
    # 2026-09-09: FreeSolv with the reference (Sabanza-Gil, chem-MFBO) objective direction. The csv HF/LF columns are
    # already -dG_solv (their preprocessing negates expt/calc); negate=True + minimise = most NEGATIVE dG (optimum -25.47),
    # which the reference maximises. 'FreeSolv' (negate=False) minimises the same column = most POSITIVE dG (C4F8, +3.43).
    # Same csv, features, PCA and FPS init as 'FreeSolv'; only the sign of y changes.
    'FreeSolv-ref': dict(csv='freesolv.csv', cost_ratio=0.1, use_smiles=True, negate=True, budget=50),
    'Polarizability-tgt85': dict(csv='polarizability.csv', cost_ratio=0.167, use_smiles=True, negate=False, budget=30, target_q=85),
    'Polarizability-tgt50': dict(csv='polarizability.csv', cost_ratio=0.167, use_smiles=True, negate=False, budget=30, target_q=50),
    'COFs-sel605': dict(csv='cofs_sel605.csv', cost_ratio=0.065, use_smiles=False, negate=True, budget=30),
    'COFs-Xe605': dict(csv='cofs_xe605.csv', cost_ratio=0.065, use_smiles=False, negate=True, budget=30),
}

# Confirmation pools for the HOPV15 / Matbench-Gap trajectory-shape analysis (2026-09-09, analysis_why_hm):
# real pools whose LF top-10 does not contain the HF optimum, plus two reachability controls built from the paper
# pools themselves (hopv15_far = HOPV15 without its HF optimum, so the new optimum sits at LF rank 87 instead of 13;
# matbench_gap_far = Matbench-Gap without the two zero-gap materials at LF rank 12 and 49, so the nearest optimum
# sits at LF rank 112). Features are used as stored (no PCA re-fit); budgets follow the paper pool of the same family.
CONFIRM = {
    'ExptGap-PBE':      dict(csv='expt_gap_pbe.csv',           cost_ratio=0.05, use_smiles=False, negate=False, budget=20),
    'JARVIS-MBJ':       dict(csv='jarvis_gap.csv',             cost_ratio=0.05, use_smiles=False, negate=False, budget=20),
    'Matbench-sub525a': dict(csv='matbench_gap_sub525a.csv',   cost_ratio=0.05, use_smiles=False, negate=False, budget=20),
    'Matbench-sub525b': dict(csv='matbench_gap_sub525b.csv',   cost_ratio=0.05, use_smiles=False, negate=False, budget=20),
    'Elastic-CHGNet':   dict(csv='elastic_chgnet_shear.csv',   cost_ratio=0.05, use_smiles=False, negate=False, budget=20),
    'Elastic-SevenNet': dict(csv='elastic_sevennet_shear.csv', cost_ratio=0.05, use_smiles=False, negate=False, budget=20),
    'Elastic-MatterSim':dict(csv='elastic_mattersim_shear.csv',cost_ratio=0.05, use_smiles=False, negate=False, budget=20),
    'HOPV15-far':       dict(csv='hopv15_far.csv',             cost_ratio=0.1,  use_smiles=False, negate=True,  budget=30),
    'Matbench-Gap-far': dict(csv='matbench_gap_far.csv',       cost_ratio=0.05, use_smiles=False, negate=False, budget=20),
}

def grid_cell(name):
    return dict(csv=f'grid_cells/{name}.csv', cost_ratio=0.1, use_smiles=False, negate=False, budget=50, init_budget=10)

# Cross-substrate synthetic grids (built 2026-06-26 on the COFs and FreeSolv substrates with the same two knobs).
def cofs_cell(name):   # 'cofscell_XX' -> data/cofs_grid_cells/cell_XX.csv ; June-26 runs used budget 30, rho 0.1
    return dict(csv=f'cofs_grid_cells/{name.replace("cofscell_", "cell_")}.csv', cost_ratio=0.1, use_smiles=False, negate=False, budget=30, init_budget=10)
def fs_cell(name):     # 'fscell_XX' -> data/freesolv_grid_cells/cell_XX.csv ; FreeSolv budget 50 as in the paper pool
    return dict(csv=f'freesolv_grid_cells/{name.replace("fscell_", "cell_")}.csv', cost_ratio=0.1, use_smiles=False, negate=False, budget=30, init_budget=10)  # June-26 FreeSolv grid runs used budget 30

# Reference-style informativeness x cost grid (2026-09-11, Sabanza-Gil et al. Fig. 4 scenario): Branin-2D and Park-4D
# candidate lattices with the LF biased by alpha (one csv per alpha in data/refgrid_cells/), cost ratio rho set by the name.
#   name = 'RG-<Branin|Park>-a<alpha>-r<rho>'  ->  csv refgrid_cells/<branin|park>_a<alpha>.csv, cost_ratio=rho, budget 50,
#   init 10 % of the budget split 50/50 in cost (the paper protocol; no init_budget override).
def refgrid_cell(name):
    _, fn, a, r = name.split('-')
    assert a.startswith('a') and r.startswith('r'), name
    # Park is MAXIMISED in the reference (chem-MFBO park.py negate=False, optimum 25.5893); Branin minimised (they negate it).
    return dict(csv=f'refgrid_cells/{fn.lower()}_{a}.csv', cost_ratio=float(r[1:]), use_smiles=False, negate=(fn.lower() == 'park'), budget=50)

def config(name):
    if name in PAPER: return PAPER[name]
    if name in RAW: return RAW[name]
    if name in SWEEP: return SWEEP[name]
    if name in TARGET: return TARGET[name]
    if name in CONFIRM: return CONFIRM[name]
    if name.startswith('cell_'): return grid_cell(name)
    if name.startswith('cofscell_'): return cofs_cell(name)
    if name.startswith('fscell_'): return fs_cell(name)
    if name.startswith('RG-'): return refgrid_cell(name)
    raise KeyError(name)

def _raw_rdkit_features(self, smiles_list):
    """RDKit 2D descriptors -> NaN/inf to 0 -> StandardScaler; NO PCA (replaces the class method)."""
    from rdkit import Chem
    from rdkit.Chem import Descriptors
    from rdkit.ML.Descriptors import MoleculeDescriptors
    from sklearn.preprocessing import StandardScaler
    names = [d[0] for d in Descriptors._descList]
    calc = MoleculeDescriptors.MolecularDescriptorCalculator(names)
    feats = []
    for s in smiles_list:
        mol = Chem.MolFromSmiles(str(s))
        feats.append(list(calc.CalcDescriptors(mol)) if mol is not None else [0.0] * len(names))
    X = np.nan_to_num(np.asarray(feats, dtype=float), nan=0.0, posinf=0.0, neginf=0.0)
    X = np.clip(X, -1e6, 1e6)
    return StandardScaler().fit_transform(X)

def make_bench(name, data_dir):
    """Construct ChemistryBenchmark for any pool name; raw pools bypass PCA."""
    import benchmark as B
    cfg = config(name)
    orig = B.ChemistryBenchmark._smiles_to_rdkit_features
    if cfg.get('pca', 10) is None and cfg['use_smiles']:
        B.ChemistryBenchmark._smiles_to_rdkit_features = _raw_rdkit_features
    k = cfg.get('pca', 10)
    try:
        if cfg['use_smiles'] and k is not None and k != 10:
            b = B.ChemistryBenchmark(name, str(data_dir / cfg['csv']), cfg['cost_ratio'], cfg['use_smiles'], True, cfg['negate'], pca_dim=k)
        else:
            b = B.ChemistryBenchmark(name, str(data_dir / cfg['csv']), cfg['cost_ratio'], cfg['use_smiles'], True, cfg['negate'])
    finally:
        B.ChemistryBenchmark._smiles_to_rdkit_features = orig
    if (not cfg['use_smiles']) and k is not None and name in SWEEP:
        # numeric high-d features (already standardised by the class): PCA-k, then re-standardise like the class does
        from sklearn.decomposition import PCA
        from sklearn.preprocessing import StandardScaler
        Xp = PCA(n_components=k, random_state=42).fit_transform(b.X)
        b.X = StandardScaler().fit_transform(Xp); b.dim = b.X.shape[1]
    if cfg.get('target_q') is not None:
        assert not cfg['negate']
        t = float(np.percentile(b.y_hf, cfg['target_q']))
        b.target_value = t
        b.y_hf = np.abs(b.y_hf - t); b.y_lf = np.abs(b.y_lf - t)
        b.f_star = b.y_hf.min(); b.r2 = np.corrcoef(b.y_hf, b.y_lf)[0, 1] ** 2
    return b, cfg
