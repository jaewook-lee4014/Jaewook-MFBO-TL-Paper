#!/usr/bin/env python
"""verify_paper_numbers_5tl.py (2026-09-14, five-transfer-learning-surrogate variant)

Independent recomputation of every number quoted in main.tex / si-content.tex (commit 304df98) from the RAW run cells
on the VM (experiments/refig_20260908 + experiments/ext_chem_20260909). The script re-implements the attainment metric,
the cell-selection rule ("largest horizon wins", seeds 42-81, NARGP dropped; five TL surrogates, DNGOJoint relabelled Frozen-representation transfer) and every
aggregation from scratch; it reads none of the value CSVs except to COMPARE against them. Nothing is modified.

Run on the VM:  OUT=/mnt/data/jaewook_mfbo/verify_out_5tl python verify_paper_numbers_5tl.py
Outputs: attainment_recomputed.csv, cell_sources.csv, fig2_endpoints.csv, grid_recomputed.csv, calibration_recomputed.csv,
screening_recomputed.csv, flops_recomputed.json, s1_recomputed.csv, s2_recomputed.csv, table1_recomputed.csv,
ext_prefix_recomputed.csv, crossenv_check.csv, report.json, report.md
"""
import glob, os, sys, json, math, time
from pathlib import Path
import numpy as np, pandas as pd
from scipy.stats import spearmanr, pearsonr

T0 = time.time()
E = '/mnt/data/jaewook_mfbo/MFBO-TL-Paper/experiments'
R = f'{E}/refig_20260908'; X = f'{E}/ext_chem_20260909'
DATA = Path('/mnt/data/jaewook_mfbo/MFBO-TL-Paper/data')
OUT = Path(os.environ.get('OUT', '/mnt/data/jaewook_mfbo/verify_out')); OUT.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, R); sys.path.insert(0, '/mnt/data/jaewook_mfbo/MFBO-TL-Paper/src')
import pools as POOLS  # noqa: E402

POOLS13 = ['Branin-Fav', 'Branin-Unfav', 'Park-Fav', 'Park-Unfav', 'COFs', 'FreeSolv', 'Polarizability', 'HOPV15', 'Matbench-Gap',
           'ExptGap-PBE', 'Elastic-CHGNet', 'Elastic-SevenNet', 'Elastic-MatterSim']
CHEM9 = POOLS13[4:]; B9 = POOLS13[:9]; LARGE4 = POOLS13[9:]
BFIG1 = {p: 50 for p in POOLS13[:4]}; BFIG1.update({p: 30 for p in POOLS13[4:]})
BORIG = {'Branin-Fav': 50, 'Branin-Unfav': 50, 'Park-Fav': 50, 'Park-Unfav': 50, 'COFs': 30, 'FreeSolv': 50, 'Polarizability': 30,
         'HOPV15': 30, 'Matbench-Gap': 20, 'ExptGap-PBE': 20, 'Elastic-CHGNet': 20, 'Elastic-SevenNet': 20, 'Elastic-MatterSim': 20}
BUD9_SI = dict(BFIG1); BUD9_SI['Matbench-Gap'] = 20       # SI acquisition figures: Matbench-Gap at 20
# 2026-09-14 (5-TL variant): the transfer-learning set is reduced to five surrogates. DNGOJoint is relabelled
# 'Frozen-representation transfer'; Sequential, Progressive, Adapter and Curriculum/KnowledgeDistillation/
# PseudoLabeling (the former merged 'Feature-extraction transfer' row) are dropped. Eight display surrogates.
# The names TL9/M12 are kept so that the rest of the script is unchanged; they now hold 5 and 8 entries.
MERGED = None
RENAME = {'DNGOGradient': 'End-to-End Joint', 'DNGO-Gradient': 'End-to-End Joint',
          'DNGOJoint': 'Frozen-representation transfer', 'DNGO-Joint': 'Frozen-representation transfer',
          'TwoStageJoint': 'Pretrain-then-Joint', 'Two-Stage Joint': 'Pretrain-then-Joint', 'DomainAdaptationMMD': 'Domain Adaptation (MMD)',
          'Domain Adaptation (MMD)': 'Domain Adaptation (MMD)', 'SoftParameterSharing': 'Soft Parameter Sharing', 'Soft Parameter Sharing': 'Soft Parameter Sharing',
          'MFGP': 'MFGP', 'SparseMFGP': 'Sparse MFGP', 'Sparse MFGP': 'Sparse MFGP', 'DKL': 'DKL', 'DKL Multi-Fidelity': 'DKL', 'NARGP': 'NARGP'}
GP3 = ['MFGP', 'Sparse MFGP', 'DKL']
TL5 = ['Frozen-representation transfer', 'Pretrain-then-Joint', 'End-to-End Joint', 'Soft Parameter Sharing', 'Domain Adaptation (MMD)']
TL9 = TL5
M8 = GP3 + TL5
M12 = M8
ABBR = {'MFGP': 'MFGP', 'Sparse MFGP': 'SV-MFGP', 'DKL': 'DKL', 'Frozen-representation transfer': 'Frozen',
        'Pretrain-then-Joint': 'PtJ', 'End-to-End Joint': 'E2E', 'Domain Adaptation (MMD)': 'MMD', 'Soft Parameter Sharing': 'SPS'}
SEEDS40 = set(range(42, 82)); SEEDS20 = set(range(42, 62))
REPORT = {}; MD = []

def log(*a):
    s = ' '.join(str(x) for x in a); print(s, flush=True); MD.append(s)

# ----------------------------------------------------------------------------------------------------------------------- pools
log('# 0. pools (pools.make_bench = the run-time loader)')
YS = {}
for p in POOLS13:
    b, cfg = POOLS.make_bench(p, DATA)
    YS[p] = (np.asarray(b.y_hf, float), np.asarray(b.y_lf, float), cfg)
    log(f'  {p}: n={len(b.y_hf)} dim={b.X.shape[1]} rho={cfg["cost_ratio"]} negate={cfg["negate"]} budget_cfg={cfg["budget"]} f_star={b.f_star:.6g}')

def thresholds(p):
    y = YS[p][0]; reg = np.sort(y - y.min()); n = len(y)
    return {k: float(reg[max(1, math.ceil(k / 100 * n)) - 1]) for k in (5, 2, 1, 0.5)}
THR = {p: thresholds(p) for p in POOLS13}
EXPL = json.load(open(f'{R}/figcand2_20260914_5tl/explorer_data.json'))
thr_diff = max(abs(THR[p][k] - EXPL['pools'][p]['thr'][str(k) if k != 0.5 else '0.5']) for p in POOLS13 for k in (5, 2, 1, 0.5))
log(f'  thresholds vs explorer_data.json: max |diff| = {thr_diff:.3g}'); REPORT['thr_max_diff_vs_explorer'] = thr_diff

# ----------------------------------------------------------------------------------------------------------------------- raw loading
def read_traj(files, src):
    parts = []
    for f in files:
        try:
            d = pd.read_csv(f, usecols=['benchmark', 'model', 'seed', 'budget', 'regret'])
        except Exception as e:
            log('  skip', f, e); continue
        d['src'] = src; d['file'] = os.path.basename(f); parts.append(d)
    if not parts:
        return pd.DataFrame(columns=['benchmark', 'model', 'seed', 'budget', 'regret', 'src', 'file'])
    return pd.concat(parts, ignore_index=True)

def to_cells(df, keep_models=None, seeds=SEEDS40):
    """(bench, model_display, seed) -> dict(hz, bud, reg, src, file). Within a file a seed's rows must be monotone in budget;
    a restart (budget decreasing) truncates to the first run. Across files/sources the LARGEST horizon wins (ties: first seen)."""
    cells = {}; dup_conflicts = 0
    df = df[df.seed.isin(seeds)]
    df = df.assign(model=df.model.map(lambda m: RENAME.get(m, m)))
    if keep_models is not None:
        df = df[df.model.isin(keep_models)]
    for (b, m, s, f), g in df.groupby(['benchmark', 'model', 'seed', 'file'], sort=False):
        bud = g.budget.values.astype(float); reg = g.regret.values.astype(float)
        cut = np.where(np.diff(bud) < 0)[0]
        if len(cut):
            bud, reg = bud[:cut[0] + 1], reg[:cut[0] + 1]
        hz = float(bud.max()); key = (b, m, int(s)); cur = cells.get(key)
        if cur is None or hz > cur['hz'] + 1e-9:
            cells[key] = dict(hz=hz, bud=bud, reg=reg, src=g.src.iloc[0], file=f)
        elif abs(hz - cur['hz']) <= 1e-9:
            # same horizon from another source: check identity of the endpoint
            if abs(reg[-1] - cur['reg'][-1]) > 1e-9: dup_conflicts += 1
    return cells, dup_conflicts

SRC = {
    'refig42_tl': glob.glob(f'{R}/results/blr_replace__hf_argmin/cells/traj_*.csv'),
    'refig42_gp': glob.glob(f'{R}/results_gp/gp_ei/cells/traj_*.csv') + glob.glob(f'{R}/results_gp_vm/gp_ei/cells/traj_*.csv') + glob.glob(f'{R}/results_gp_vm2/gp_ei/cells/traj_*.csv'),
    'conf62_tl': glob.glob(f'{R}/results_conf/blr_replace__hf_argmin/cells/traj_*.csv'),
    'conf62_gp': glob.glob(f'{R}/results_gp_conf/gp_ei/cells/traj_*.csv'),
    'ext': glob.glob(f'{X}/results/*/cells/traj_*.csv') + glob.glob(f'{X}/results_slurm/*/cells/traj_*.csv'),
    'ext100': glob.glob(f'{X}/results_ext100/*/cells/traj_*.csv'),
    'confirm_ext': glob.glob(f'{X}/results_confirm_ext/*/cells/traj_*.csv'),
    'confirm20': glob.glob(f'{R}/results_confirm/*/cells/traj_*.csv') + glob.glob(f'{R}/results_confirm_gp/*/cells/traj_*.csv'),
}
log('# 1. raw trajectory sources')
RAW = {}
for k, files in SRC.items():
    RAW[k] = read_traj(files, k); log(f'  {k}: {len(files)} files, {len(RAW[k])} rows')
ALL = pd.concat(RAW.values(), ignore_index=True)
ALL = ALL[ALL.benchmark.isin(POOLS13)]
CELLS, dupc = to_cells(ALL, keep_models=set(M12))
log(f'  cells selected: {len(CELLS)} (same-horizon duplicate conflicts: {dupc})'); REPORT['same_horizon_conflicts'] = dupc

# provenance of every Fig. 1/2 cell
rows = []
for (b, m, s), c in CELLS.items():
    rows.append(dict(pool=b, model=m, seed=s, src=c['src'], file=c['file'], horizon=c['hz']))
CS = pd.DataFrame(rows)
cs = CS[CS.model.isin(M12)].groupby(['pool', 'model', 'src']).agg(n=('seed', 'size'), hz_min=('horizon', 'min'), hz_max=('horizon', 'max')).reset_index()
cs.to_csv(OUT / 'cell_sources.csv', index=False)
log('  per-pool sources used (largest horizon wins):')
for p in POOLS13:
    g = cs[cs.pool == p].groupby('src').n.sum()
    log(f'    {p}: ' + ', '.join(f'{k}={v}' for k, v in g.items()))

# (2026-09-14) the Curriculum = KD = PL identity check is dropped with those three configurations.
log('  Curriculum/KD/PL identity check: NOT APPLICABLE (those three configurations are not part of the five-surrogate set)')
REPORT['fet_identity'] = 'n/a (Curriculum, KnowledgeDistillation and PseudoLabeling are not in the 5-TL set)'

# ----------------------------------------------------------------------------------------------------------------------- attainment
def attain(bud, reg, B, thrs):
    t0 = float(bud[0])
    if B <= t0 + 1e-9: return None
    acc = 0.0
    for thr in thrs:
        ok = np.where(reg <= thr + 1e-12)[0]
        if len(ok) and bud[ok[0]] <= B + 1e-9:
            acc += (B - max(float(bud[ok[0]]), t0)) / (B - t0)
    return acc / len(thrs)

def attain_table(cells, budgets, models=M12, pools=POOLS13):
    rows = []
    for p in pools:
        thrs = [THR[p][k] for k in (5, 2, 1, 0.5)]; B = budgets[p]
        for m in models:
            vals = [attain(c['bud'], c['reg'], B, thrs) for (b, mm, s), c in cells.items() if b == p and mm == m and c['hz'] + 0.26 >= B]
            vals = [v for v in vals if v is not None]
            if vals:
                v = np.array(vals); rows.append(dict(pool=p, model=m, n=len(v), mean=v.mean(), se=v.std(ddof=1) / np.sqrt(len(v)) if len(v) > 1 else 0.0))
    return pd.DataFrame(rows)

log('# 2. Fig. 1 b-p attainment (recomputed from raw cells)')
A = attain_table(CELLS, BFIG1); A.to_csv(OUT / 'attainment_recomputed.csv', index=False)
ref = pd.read_csv(f'{R}/figcand2_20260914_5tl/fig1_attainment_values.csv')
cmp = A.merge(ref[['pool', 'model', 'n', 'mean']], on=['pool', 'model'], suffixes=('', '_ref'))
log(f'  cells: {len(A)} (ref {len(ref)}); n identical: {(cmp.n == cmp.n_ref).all()}; max |mean diff| vs fig1_attainment_values.csv = {(cmp["mean"] - cmp.mean_ref).abs().max():.3g}')
REPORT['fig1_attainment_max_diff_vs_values_csv'] = float((cmp['mean'] - cmp.mean_ref).abs().max())
REPORT['fig1_n_not_40'] = A[A.n != 40][['pool', 'model', 'n']].to_dict('records')
piv = A.pivot(index='model', columns='pool', values='mean').loc[M12, POOLS13]
log('  attainment table (mean over seeds):'); log(piv.round(3).to_string())
best = []
for p in POOLS13:
    t = A[A.pool == p]; tl = t[t.model.isin(TL9)].sort_values('mean', ascending=False).iloc[0]; gp = t[t.model.isin(GP3)].sort_values('mean', ascending=False).iloc[0]
    d = tl['mean'] - gp['mean']; verdict = 'TL' if d > 0.01 + 1e-12 else ('GP' if d < -0.01 - 1e-12 else 'tie(<=0.01)')
    best.append(dict(pool=p, best_TL=ABBR[tl.model], TL=round(tl['mean'], 3), best_GP=ABBR[gp.model], GP=round(gp['mean'], 3), diff=round(d, 3), verdict=verdict,
                     min_all=round(t['mean'].min(), 3), max_all=round(t['mean'].max(), 3), min_TL=round(t[t.model.isin(TL9)]['mean'].min(), 3), max_GP=round(gp['mean'], 3)))
BEST = pd.DataFrame(best); log('  best-of-family per pool:'); log(BEST.to_string(index=False)); REPORT['fig1_best_of_family'] = best
chem = BEST[BEST.pool.isin(CHEM9)]
REPORT['chem9_wins_ties'] = dict(TL=int((chem.verdict == 'TL').sum()), tie=int(chem.verdict.str.startswith('tie').sum()), GP=int((chem.verdict == 'GP').sum()))
log(f'  chem/materials 9 pools: {REPORT["chem9_wins_ties"]}')

def score_summary(A, pools):
    t = A[A.pool.isin(pools)].copy()
    for p in pools:
        m = t.pool == p; lo, hi = t.loc[m, 'mean'].min(), t.loc[m, 'mean'].max(); t.loc[m, 'score'] = (t.loc[m, 'mean'] - lo) / (hi - lo) if hi > lo else 0.5
    s = t.groupby('model').agg(score=('score', 'mean'), attain=('mean', 'mean'), n=('score', 'size')).reindex(M12).sort_values('score', ascending=False)
    return s
So = score_summary(A, POOLS13); Sp = score_summary(A, CHEM9)
log('  panel o (13 pools) normalised score:'); log(So.round(3).to_string())
log('  panel p (9 chem/mat) normalised score:'); log(Sp.round(3).to_string())
refo = pd.read_csv(f'{R}/figcand2_20260914_5tl/fig1_attainment_summary_score.csv', index_col=0); refp = pd.read_csv(f'{R}/figcand2_20260914_5tl/fig1_attainment_summary_score_chem.csv', index_col=0)
REPORT['panel_o_max_diff'] = float((So['score'] - refo['mean'].reindex(So.index)).abs().max()); REPORT['panel_p_max_diff'] = float((Sp['score'] - refp['mean'].reindex(Sp.index)).abs().max())
log(f'  panel o/p max |diff| vs summary csvs: {REPORT["panel_o_max_diff"]:.3g} / {REPORT["panel_p_max_diff"]:.3g}')
REPORT['panel_o'] = So['score'].round(4).to_dict(); REPORT['panel_p'] = Sp['score'].round(4).to_dict()
gpmax_o = So.loc[GP3, 'score'].max(); REPORT['panel_o_TL_above_every_GP'] = int((So.loc[TL9, 'score'] > gpmax_o).sum())
gpmax_p = Sp.loc[GP3, 'score'].max(); REPORT['panel_p_TL_above_every_GP'] = int((Sp.loc[TL9, 'score'] > gpmax_p).sum())
log(f'  TL rows above every GP: o {REPORT["panel_o_TL_above_every_GP"]}/5, p {REPORT["panel_p_TL_above_every_GP"]}/5; TL score range o {So.loc[TL9,"score"].min():.2f}-{So.loc[TL9,"score"].max():.2f}')

# ----------------------------------------------------------------------------------------------------------------------- Fig. 2 endpoints
log('# 3. Fig. 2 trajectories: mean regret at budget points (recomputed)')
def mean_curve(p, m, grid):
    A_ = []
    for (b, mm, s), c in CELLS.items():
        if b == p and mm == m:
            idx = np.searchsorted(c['bud'], grid, side='right') - 1
            cur = np.where(idx >= 0, c['reg'][np.clip(idx, 0, len(c['reg']) - 1)], c['reg'][0]); cur = np.where(grid > c['hz'] + 0.26, np.nan, cur); A_.append(cur)
    A_ = np.array(A_); n = np.sum(~np.isnan(A_), axis=0)
    with np.errstate(all='ignore'):
        mu = np.where(n > 0, np.nanmean(A_, axis=0), np.nan)
    return mu, n
f2rows = []
for p in POOLS13:
    grid = np.round(np.arange(0, BFIG1[p] + 1e-9, 0.25), 3)
    for m in M12:
        mu, n = mean_curve(p, m, grid)
        f2rows.append(dict(pool=p, model=m, n_end=int(n[-1]), mean_at_B=float(mu[-1]), mean_at_20=float(mu[np.argmin(abs(grid - 20))]), mean_at_15=float(mu[np.argmin(abs(grid - 15))]),
                           mean_at_10=float(mu[np.argmin(abs(grid - 10))])))
F2 = pd.DataFrame(f2rows); F2.to_csv(OUT / 'fig2_endpoints.csv', index=False)
ref2 = pd.read_csv(f'{R}/figcand2_20260914_5tl/fig2_trajectories_values.csv')
c2 = F2.merge(ref2, on=['pool', 'model']); REPORT['fig2_max_diff_vs_values_csv'] = float((c2.mean_at_B - c2.mean_end).abs().max())
log(f'  max |mean at B diff| vs fig2_trajectories_values.csv: {REPORT["fig2_max_diff_vs_values_csv"]:.3g}')
for p in ('HOPV15', 'Matbench-Gap', 'Branin-Fav', 'Branin-Unfav'):
    t = F2[F2.pool == p].set_index('model')
    log(f'  {p} mean regret at B=30/50 (n): ' + ', '.join(f'{ABBR[m]} {t.loc[m,"mean_at_B"]:.3f} ({t.loc[m,"n_end"]})' for m in M12))
    log(f'  {p} mean regret at 20: ' + ', '.join(f'{ABBR[m]} {t.loc[m,"mean_at_20"]:.3f}' for m in M12))
REPORT['fig2_endpoints'] = {p: {ABBR[m]: round(float(F2[(F2.pool == p) & (F2.model == m)].mean_at_B.iloc[0]), 4) for m in M12} for p in ('HOPV15', 'Matbench-Gap')}
# Branin: GP (MFGP, DKL) below every TL curve throughout?
for p in ('Branin-Fav', 'Branin-Unfav'):
    grid = np.round(np.arange(0, 50 + 1e-9, 0.25), 3)
    tl = np.array([mean_curve(p, m, grid)[0] for m in TL9]); tlmin = np.nanmin(tl, axis=0)
    for m in ('MFGP', 'DKL', 'Sparse MFGP'):
        mu, _ = mean_curve(p, m, grid); ok = np.nanmean(mu <= tlmin + 1e-12)
        log(f'  {p}: {ABBR[m]} mean curve <= every TL mean curve on {100*ok:.0f}% of grid points')
        REPORT[f'fig2_{p}_{ABBR[m]}_below_all_TL_share'] = float(ok)
# Matbench: TL ahead after ~15 units (best 3 TL vs GPs)
t = F2[F2.pool == 'Matbench-Gap'].set_index('model')
log(f'  Matbench-Gap at 15: best TL {t.loc[TL9].mean_at_15.min():.3f} vs best GP {t.loc[GP3].mean_at_15.min():.3f}; at 20: {t.loc[TL9].mean_at_20.min():.3f} vs {t.loc[GP3].mean_at_20.min():.3f}')

# ----------------------------------------------------------------------------------------------------------------------- ext prefix vs refig
log('# 4. extension runs vs the original-budget runs: prefix identity (paper cells of HOPV15/FreeSolv/Polarizability/Matbench-Gap use the extension trajectories)')
ORIG = {}
for k in ('refig42_tl', 'refig42_gp', 'conf62_tl', 'conf62_gp'):
    c, _ = to_cells(RAW[k][RAW[k].benchmark.isin(B9)], keep_models=set(M12)); ORIG.update(c)
EXT = {}
for k in ('ext', 'ext100'):
    c, _ = to_cells(RAW[k], keep_models=set(M12))
    for key, v in c.items():
        if key not in EXT or v['hz'] > EXT[key]['hz']: EXT[key] = v
prow = []
for key, o in ORIG.items():
    b, m, s = key
    if b not in ('HOPV15', 'FreeSolv', 'Polarizability', 'Matbench-Gap') or key not in EXT: continue
    e = EXT[key]; Bm1 = BORIG[b] - 1.0
    bo = o['bud'] <= Bm1 + 1e-9; be = e['bud'] <= Bm1 + 1e-9
    n = min(bo.sum(), be.sum()); match = bool(n > 0 and np.allclose(o['bud'][:n], e['bud'][:n]) and np.allclose(o['reg'][:n], e['reg'][:n], atol=1e-9))
    prow.append(dict(pool=b, model=m, seed=s, prefix_match=match, n_compared=int(n), orig_final=float(o['reg'][-1]), ext_at_Borig=float(e['reg'][np.searchsorted(e['bud'], BORIG[b], side='right') - 1]), orig_src=o['src'], ext_src=e['src']))
PX = pd.DataFrame(prow); PX.to_csv(OUT / 'ext_prefix_recomputed.csv', index=False)
if len(PX):
    g = PX.groupby(['pool', 'model']).agg(n=('seed', 'size'), match=('prefix_match', 'sum')).reset_index(); g['mismatch'] = g.n - g.match
    log(g[g.mismatch > 0].to_string(index=False) if (g.mismatch > 0).any() else '  all compared prefixes identical')
    log(f'  total compared {len(PX)}, mismatches {int((~PX.prefix_match).sum())}')
    REPORT['ext_prefix'] = dict(compared=int(len(PX)), mismatches=int((~PX.prefix_match).sum()), by_model=g[g.mismatch > 0].to_dict('records'))

# ----------------------------------------------------------------------------------------------------------------------- Fig. 3 grid
log('# 5. Fig. 3 a-c: 126-cell grid (figrepo/results/grid; TL rows from results_grid, GP rows = public results/grid)')
man = pd.read_csv(f'{R}/figrepo/results/grid/grid_manifest.csv').set_index('cell_id')
# 2026-09-14: the grid's TL family is now the five retained classes. The 126-cell campaign was run only with
# Progressive / KnowledgeDistillation / PseudoLabeling, so this section has no data under the reduced set and is skipped.
FAM = {'TL': ['DNGOJoint', 'TwoStageJoint', 'DNGOGradient', 'SoftParameterSharing', 'DomainAdaptationMMD'],
       'MFGP': ['MFGP'], 'variants': ['DKL', 'SparseMFGP']}
_gfiles = sorted(glob.glob(f'{R}/figrepo/results/grid/cells/summary_cell_*.csv'))
_gmodels = sorted(pd.read_csv(_gfiles[0]).model.unique()) if _gfiles else []
GRID_OK = bool(set(FAM['TL']) & set(_gmodels))
if not GRID_OK:
    log(f'  SKIPPED: the grid cells contain only {_gmodels}; none of the five retained TL classes was run on the 126-cell grid.')
    log('  Fig. 3 is therefore out of scope for the 5-TL regeneration (no grid data exists for the reduced set).')
    REPORT['grid'] = f'skipped: grid cells contain only {_gmodels}, none of the five retained TL classes'


def _grid_section():
  grows = []; nseeds = set(); nhf = set(); nlf = set()
  for f in _gfiles:
    d = pd.read_csv(f); cid = d.benchmark.iloc[0]
    for m in FAM['TL'] + FAM['MFGP'] + FAM['variants']:
        nseeds.add(int(d[d.model == m].seed.nunique()))
    bf = {fam: min(d[d.model.isin(mem)].groupby('model').final_regret.mean()) for fam, mem in FAM.items()}
    ba = {fam: min(d[d.model.isin(mem)].groupby('model').auc.mean()) for fam, mem in FAM.items()}
    grows.append(dict(cell=cid, r2=man.loc[cid, 'r2'], top10=man.loc[cid, 'top10'], adv_TL_MFGP=bf['MFGP'] - bf['TL'], adv_TL_var=bf['variants'] - bf['TL'], adv_var_MFGP=bf['MFGP'] - bf['variants'],
                      auc_TL_MFGP=ba['MFGP'] - ba['TL'], auc_TL_var=ba['variants'] - ba['TL'], auc_var_MFGP=ba['MFGP'] - ba['variants']))
  G = pd.DataFrame(grows); G.to_csv(OUT / 'grid_recomputed.csv', index=False)
  yrange = float(YS['Polarizability'][0].max() - YS['Polarizability'][0].min())
  log(f'  cells {len(G)}; seeds per model per cell {sorted(nseeds)}; polarizability HF range {yrange:.4f} (advantages below are in raw HF units and in range units)')
  gres = {}
  for k, lab in [('adv_TL_MFGP', 'TL vs MFGP'), ('adv_TL_var', 'TL vs variants'), ('adv_var_MFGP', 'variants vs MFGP')]:
      pos = int((G[k] > 1e-12).sum()); tie = int((G[k].abs() <= 1e-12).sum()); neg = int((G[k] < -1e-12).sum())
      rt = spearmanr(G[k], G.top10).correlation; rr = spearmanr(G[k], G.r2).correlation
      ti = np.round(G.top10 * 10).astype(int); ri = np.clip(np.round((G.r2 - 0.1) / 0.1).astype(int), 0, 8)
      prof_t = G.groupby(ti)[k].mean(); prof_r = G.groupby(ri)[k].mean()
      gres[lab] = dict(pos=pos, tie=tie, neg=neg, rho_agreement=round(float(rt), 3), rho_r2=round(float(rr), 3), mean_raw=round(float(G[k].mean()), 4), mean_range_units=round(float(G[k].mean() / yrange), 4),
                       profile_agreement_raw={int(i): round(float(v), 4) for i, v in prof_t.items()}, profile_r2_raw={int(i): round(float(v), 4) for i, v in prof_r.items()},
                       profile_agreement_range={int(i): round(float(v / yrange), 4) for i, v in prof_t.items()}, profile_r2_range={int(i): round(float(v / yrange), 4) for i, v in prof_r.items()})
      log(f'  {lab}: pos {pos} tie {tie} neg {neg}; rho(agreement) {rt:+.2f} rho(R2) {rr:+.2f}; mean adv {G[k].mean():.4f} raw = {G[k].mean()/yrange:.4f} range units')
      log(f'     profile vs agreement (raw): ' + ' '.join(f'{i/10:.1f}:{v:.3f}' for i, v in prof_t.items()))
      log(f'     profile vs R2 (raw): ' + ' '.join(f'{(i+1)/10:.1f}:{v:.3f}' for i, v in prof_r.items()))
  REPORT['grid'] = gres
  refg = pd.read_csv(f'{R}/figrepo/figures/out/fig1ln_final_cells.csv')
  cg = G.merge(refg, on='cell'); REPORT['grid_max_diff_vs_fig1ln_cells'] = float(max((cg.adv_TL_MFGP - cg['TL|MFGP baseline']).abs().max(), (cg.adv_TL_var - cg['TL|MFGP variants']).abs().max(), (cg.adv_var_MFGP - cg['MFGP variants|MFGP baseline']).abs().max()))
  log(f'  max |diff| vs fig1ln_final_cells.csv: {REPORT["grid_max_diff_vs_fig1ln_cells"]:.3g}')
  # grid run sizes (n_hf, n_lf) from the TL grid summaries
  gt = pd.concat([pd.read_csv(f) for f in glob.glob(f'{R}/results_grid/blr_replace__hf_argmin/cells/summary_*.csv')[:50]])
  log(f'  grid TL runs: n_hf {sorted(gt.n_hf.unique())}, n_lf {sorted(gt.n_lf.unique())} (sample of 50 files)')
  REPORT['grid_n_hf_n_lf'] = dict(n_hf=sorted(int(x) for x in gt.n_hf.unique()), n_lf=sorted(int(x) for x in gt.n_lf.unique()))


if GRID_OK:
    _grid_section()

# ----------------------------------------------------------------------------------------------------------------------- Fig. 4 calibration
log('# 6. Fig. 4 a-m: loop-mean held-out LF ECE vs attainment (ECE from the summary CSVs of the original-budget runs)')
SRCS = ['results/blr_replace__hf_argmin', 'results_conf/blr_replace__hf_argmin', '../ext_chem_20260909/results_confirm_ext/blr_replace__hf_argmin',
        'results_gp/gp_ei', 'results_gp_vm/gp_ei', 'results_gp_vm2/gp_ei', 'results_gp_conf/gp_ei', '../ext_chem_20260909/results_confirm_ext/gp_ei']
summ = pd.concat([pd.read_csv(f) for d in SRCS for f in glob.glob(f'{R}/{d}/cells/summary_*.csv')], ignore_index=True)
summ = summ[summ.benchmark.isin(POOLS13) & summ.seed.between(42, 81)]
summ['model'] = summ.model.map(lambda m: RENAME.get(m, m)); summ = summ[summ.model.isin(M12)].drop_duplicates(['benchmark', 'model', 'seed'])
ece = summ.groupby(['benchmark', 'model']).agg(ece=('ece_lf_mean', 'mean'), n_ece=('seed', 'size'), nan_ece=('ece_lf_mean', lambda s: int(s.isna().sum()))).reset_index()
C = ece.merge(A.rename(columns={'pool': 'benchmark', 'mean': 'attainment'}), on=['benchmark', 'model'])
crows = []
for p in POOLS13:
    t = C[C.benchmark == p].set_index('model').reindex(M12)
    r = pearsonr(t.ece, t.attainment)[0] if t.attainment.std() > 0 else np.nan
    crows.append(dict(pool=p, r=round(float(r), 3), MFGP_lowest_ece=bool(t.ece.idxmin() == 'MFGP'), DKL_highest_ece=bool(t.ece.idxmax() == 'DKL'),
                      MFGP_att_rank=int(t.attainment.rank(ascending=False)['MFGP']), gp_ece_min=round(float(t.loc[GP3].ece.min()), 3), gp_ece_max=round(float(t.loc[GP3].ece.max()), 3),
                      tl_ece_min=round(float(t.loc[TL9].ece.min()), 3), tl_ece_max=round(float(t.loc[TL9].ece.max()), 3), att_min=round(float(t.attainment.min()), 3), att_max=round(float(t.attainment.max()), 3),
                      DKL_att_rank=int(t.attainment.rank(ascending=False)['DKL']), n_ece_min=int(t.n_ece.min()), nan_ece=int(t.nan_ece.sum())))
CR = pd.DataFrame(crows); CR.to_csv(OUT / 'calibration_recomputed.csv', index=False); C.to_csv(OUT / 'calibration_points.csv', index=False)
log(CR.to_string(index=False))
refc = pd.read_csv(f'{R}/figrepo/figures/out/fig4_calibration_attain_values.csv')
cc = C.merge(refc[['benchmark', 'model', 'ece_lf_mean', 'attainment']], on=['benchmark', 'model'], suffixes=('', '_ref'))
REPORT['fig4_max_diff_vs_values_csv'] = dict(ece=float((cc.ece - cc.ece_lf_mean).abs().max()), attainment=float((cc.attainment - cc.attainment_ref).abs().max()))
log(f'  max |diff| vs fig4_calibration_attain_values.csv: ece {REPORT["fig4_max_diff_vs_values_csv"]["ece"]:.3g}, attainment {REPORT["fig4_max_diff_vs_values_csv"]["attainment"]:.3g}')
REPORT['calibration'] = dict(r={r.pool: r.r for r in CR.itertuples()}, MFGP_lowest_ece_count=int(CR.MFGP_lowest_ece.sum()), DKL_highest_ece_count=int(CR.DKL_highest_ece.sum()),
                             MFGP_lower_half_chem=int((CR[CR.pool.isin(CHEM9)].MFGP_att_rank > 6).sum()), abs_r_ge_05=[r.pool for r in CR.itertuples() if abs(r.r) >= 0.5])
log(f'  MFGP lowest ECE on {REPORT["calibration"]["MFGP_lowest_ece_count"]}/13; DKL highest on {REPORT["calibration"]["DKL_highest_ece_count"]}/13; MFGP attainment rank > 6 on {REPORT["calibration"]["MFGP_lower_half_chem"]}/9 chem pools; |r|>=0.5: {REPORT["calibration"]["abs_r_ge_05"]}')

# ----------------------------------------------------------------------------------------------------------------------- Fig. 5 a,b screening
log('# 7. Fig. 5 a,b: top-k overlap and LF-only screening regret (from the pools as loaded by the runs)')
srows = []
for p in POOLS13:
    y_hf, y_lf, cfg = YS[p]; n = len(y_hf); o_hf, o_lf = np.argsort(y_hf, kind='stable'), np.argsort(y_lf, kind='stable')
    lf_best, hf_best = int(np.argmin(y_lf)), int(np.argmin(y_hf)); sr = float(y_hf[lf_best] - y_hf.min()); rng_ = float(y_hf.max() - y_hf.min())
    k1 = max(1, int(0.01 * n))
    srows.append(dict(pool=p, n=n, r2=float(np.corrcoef(y_hf, y_lf)[0, 1]) ** 2, spearman=float(spearmanr(y_hf, y_lf).correlation), top10_overlap=len(set(o_hf[:10]) & set(o_lf[:10])) / 10,
                      top1pct_overlap=len(set(o_hf[:k1]) & set(o_lf[:k1])) / k1, screening_regret=sr, screening_regret_pct_range=100 * sr / rng_,
                      lf_rank_of_hf_best=int(np.where(o_lf == hf_best)[0][0]) + 1, top1_hit=int(lf_best == hf_best), regime='A' if sr <= 0.3 else 'B', hf_range=rng_))
S = pd.DataFrame(srows); S.to_csv(OUT / 'screening_recomputed.csv', index=False); log(S.round(4).to_string(index=False))
refs = pd.read_csv(f'{R}/figrepo/figures/out/fig5_13/B2_topk_13_values.csv').rename(columns={'benchmark': 'pool'})
cs_ = S.merge(refs[['pool', 'screening_regret', 'top10_overlap', 'lf_rank_of_hf_best']], on='pool', suffixes=('', '_ref'))
REPORT['fig5_max_diff_vs_values_csv'] = float((cs_.screening_regret - cs_.screening_regret_ref).abs().max())
REPORT['screening'] = S.round(4).set_index('pool').to_dict('index')

# ----------------------------------------------------------------------------------------------------------------------- Fig. 5c / SI Fig. 3 FLOPs
log('# 8. Fig. 5c + SI Fig. 3: FLOPs (figrepo/results/flop_profile_blr/flop_profile.csv)')
d = pd.read_csv(f'{R}/figrepo/results/flop_profile_blr/flop_profile.csv'); d = d[(d.ok == 1) & (d.model != 'NARGP')].copy()
GPF = {'MFGP', 'Sparse MFGP', 'DKL Multi-Fidelity'}
# 2026-09-14: keep only the three GPs and the five retained TL configurations (profile-CSV spellings)
TLF5 = {'DNGO-Joint', 'Two-Stage Joint', 'DNGO-Gradient', 'Soft Parameter Sharing', 'Domain Adaptation (MMD)'}
assert TLF5 <= set(d.model.unique()), sorted(TLF5 - set(d.model.unique()))
d = d[d.model.isin(GPF | TLF5)].copy()
d['family'] = np.where(d.model.isin(GPF), 'GP', 'TL')
log(f'  rows {len(d)}; models {sorted(d.model.unique())}; benchmarks {sorted(d.benchmark.unique())}; seeds {sorted(d.seed.unique())}; fractions {sorted(d.fraction.unique())}')
med = d.groupby(['benchmark', 'model', 'family', 'fraction']).agg(N=('n_train', 'median'), fit=('fit_flops', 'median'), pred=('predict_flops', 'median')).reset_index(); med = med[med.fit > 0]
def family_slope(g):
    ly = np.log10(g.fit.values); dm = pd.get_dummies(g.model).values.astype(float); Amat = np.column_stack([dm, np.log10(g.N.values)])
    coef, *_ = np.linalg.lstsq(Amat, ly, rcond=None); pred = Amat @ coef; r2 = 1 - np.sum((ly - pred) ** 2) / np.sum((ly - ly.mean()) ** 2)
    return float(coef[-1]), float(r2), 10 ** np.mean(np.log10(g.N.values)), 10 ** np.mean(np.log10(g.fit.values))
laws = {}
for fam in ('GP', 'TL'):
    g = med[med.family == fam]; k, r2, xc, yc = family_slope(g); laws[fam] = (k, r2, xc, yc); log(f'  {fam}: k_N = {k:.2f} (R2 {r2:.2f})')
(kG, r2G, xcG, ycG), (kT, r2T, xcT, ycT) = laws['GP'], laws['TL']
Nx = 10 ** (((np.log10(ycT) - kT * np.log10(xcT)) - (np.log10(ycG) - kG * np.log10(xcG))) / (kG - kT))
ratio = lambda N: (ycG * (N / xcG) ** kG) / (ycT * (N / xcT) ** kT)
log(f'  break-even N = {Nx:.1f}; GP/TL fit-cost ratio at N=100: {ratio(100):.2f}x, N=200: {ratio(200):.2f}x')
perk = {}
for m in sorted(med.model.unique()):
    g = med[med.model == m]; k, _ = np.polyfit(np.log(g.N), np.log(np.maximum(g.fit, 1)), 1); perk[m] = round(float(k), 2)
log('  per-model exponent k: ' + ', '.join(f'{m} {k}' for m, k in perk.items()))
SCHED = {'Branin-Fav': (27, 283), 'Branin-Unfav': (7, 76), 'Park-Fav': (27, 280), 'Park-Unfav': (7, 76), 'COFs': (25, 245), 'FreeSolv': (27, 283), 'Polarizability': (10, 99), 'HOPV15': (17, 164), 'Matbench-Gap': (22, 209)}
def recon(m, b, col):
    g = med[(med.benchmark == b) & (med.model == m)].sort_values('N')
    if len(g) < 2: return np.nan
    a, bb = SCHED[b]; grid = np.arange(a, bb + 1); return float(np.interp(grid, g.N.values, g[col].values).sum())
lrows = []
for b in SCHED:
    for m in sorted(med.model.unique()):
        lrows.append(dict(benchmark=b, model=m, family='GP' if m in GPF else 'TL', tflops=(recon(m, b, 'fit') + recon(m, b, 'pred')) / 1e12))
L = pd.DataFrame(lrows); L.to_csv(OUT / 'flops_loop_recomputed.csv', index=False)
fl = {}
for b in SCHED:
    g = L[L.benchmark == b]; ch = g[g.family == 'TL'].tflops.min(); chm = g[g.family == 'TL'].sort_values('tflops').model.iloc[0]
    fl[b] = dict(cheapest_TL=chm, cheapest_TL_tflops=round(ch, 3), Sparse_x=round(float(g[g.model == 'Sparse MFGP'].tflops.iloc[0] / ch), 1), DKL_x=round(float(g[g.model == 'DKL Multi-Fidelity'].tflops.iloc[0] / ch), 1),
                 MFGP_x=round(float(g[g.model == 'MFGP'].tflops.iloc[0] / ch), 1), Sparse_tflops=round(float(g[g.model == 'Sparse MFGP'].tflops.iloc[0]), 3), cheapest_overall=g.sort_values('tflops').model.iloc[0])
    log(f'  {b:15s} cheapest TL {chm} {ch:.3f} TF; Sparse {fl[b]["Sparse_x"]}x DKL {fl[b]["DKL_x"]}x MFGP {fl[b]["MFGP_x"]}x; cheapest overall {fl[b]["cheapest_overall"]}')
REPORT['flops'] = dict(kN_GP=round(kG, 3), r2_GP=round(r2G, 3), kN_TL=round(kT, 3), r2_TL=round(r2T, 3), break_even=round(float(Nx), 1), ratio_100=round(float(ratio(100)), 2), ratio_200=round(float(ratio(200)), 2),
                       per_model_k=perk, loop=fl, max_Sparse_x=max(v['Sparse_x'] for v in fl.values()), max_DKL_x=max(v['DKL_x'] for v in fl.values()), max_MFGP_x=max(v['MFGP_x'] for v in fl.values()),
                       profile_sched_vs_paper_budget={'FreeSolv': 'SCHED (27,283) = B 50 schedule; paper B = 30', 'Matbench-Gap': 'SCHED (22,209) = B 20 schedule; paper B = 30'})
try:
    refl = json.load(open(f'{R}/figrepo/figures/out/fig5tl_20260914/scaling_law_blr.json')); REPORT['flops']['ref_scaling_law_json'] = refl
except Exception as e:
    log('  (no scaling_law_blr.json in out/fig5tl_20260914:', e, ')')

# ----------------------------------------------------------------------------------------------------------------------- SI Fig. 1 / 2 acquisition
log('# 9. SI Fig. 1 (S1) and SI Fig. 2 (S2): acquisition arms under attainment')
def arm_cells(roots_tl, arm, seeds, extra=()):
    files = []
    for r_ in roots_tl: files += sorted(glob.glob(f'{r_}/{arm}/cells/traj_*.csv'))
    df = read_traj(files, arm)
    for lab, fs in extra: df = pd.concat([df, read_traj(fs, lab)], ignore_index=True)
    return to_cells(df[df.benchmark.isin(B9)], seeds=seeds)[0]
TLR = [f'{R}/results', f'{R}/results_slurm']
# S1: MFGP EI (results_gp + results_gp_vm + results_gp_conf, as supp_attain.py; and again with results_gp_vm2 for n)
gp_ei_s1 = to_cells(read_traj(glob.glob(f'{R}/results_gp/gp_ei/cells/traj_*.csv') + glob.glob(f'{R}/results_gp_vm/gp_ei/cells/traj_*.csv') + glob.glob(f'{R}/results_gp_conf/gp_ei/cells/traj_*.csv'), 'gp_ei'), keep_models={'MFGP'})[0]
gp_gr = to_cells(read_traj(glob.glob(f'{R}/results_gp/gp_greedy/cells/traj_*.csv') + glob.glob(f'{R}/results_gp_conf/gp_greedy/cells/traj_*.csv'), 'gp_greedy'), keep_models={'MFGP'})[0]
tl_gr = arm_cells(TLR + [f'{R}/results_conf'], 'blr_replace__hf_argmin', SEEDS40)
tl_ei = arm_cells(TLR + [f'{R}/results_conf'], 'blr_replace__hf_ei', SEEDS40)
def att_of(cells, p, m, B):
    thrs = [THR[p][k] for k in (5, 2, 1, 0.5)]
    return {s: attain(c['bud'], c['reg'], B, thrs) for (b, mm, s), c in cells.items() if b == p and mm == m and c['hz'] + 0.26 >= B}
s1 = []
for p in B9:
    B = BUD9_SI[p]
    ge, gg = att_of(gp_ei_s1, p, 'MFGP', B), att_of(gp_gr, p, 'MFGP', B); com = sorted(set(ge) & set(gg))
    te, tg = att_of(tl_ei, p, 'End-to-End Joint', B), att_of(tl_gr, p, 'End-to-End Joint', B); comt = sorted(set(te) & set(tg))
    s1.append(dict(pool=p, B=B, MFGP_EI=np.mean(list(ge.values())), n_MFGP_EI=len(ge), MFGP_greedy=np.mean(list(gg.values())), n_MFGP_greedy=len(gg), MFGP_paired_delta_EI_minus_greedy=np.mean([ge[s] - gg[s] for s in com]), n_pairs_MFGP=len(com),
                   E2E_EI=np.mean(list(te.values())), n_E2E_EI=len(te), E2E_greedy=np.mean(list(tg.values())), n_E2E_greedy=len(tg), E2E_paired_delta=np.mean([te[s] - tg[s] for s in comt]), n_pairs_E2E=len(comt)))
S1 = pd.DataFrame(s1); S1.to_csv(OUT / 's1_recomputed.csv', index=False); log(S1.round(3).to_string(index=False))
# per-surrogate EI - greedy on HOPV15 (seeds 42-61)
tl_gr20 = arm_cells(TLR, 'blr_replace__hf_argmin', SEEDS20); tl_ei20 = arm_cells(TLR, 'blr_replace__hf_ei', SEEDS20)
hop = {}
for m in TL9:
    e, g = att_of(tl_ei20, 'HOPV15', m, 30), att_of(tl_gr20, 'HOPV15', m, 30); com = sorted(set(e) & set(g))
    hop[ABBR[m]] = (round(float(np.mean([e[s] - g[s] for s in com])), 3), len(com)) if com else (None, 0)
log(f'  HOPV15 EI - greedy per TL surrogate (42-61): {hop}')
REPORT['s1'] = dict(rows=S1.round(4).to_dict('records'), hopv15_per_surrogate=hop,
                    MFGP_within_0_02=int((S1.MFGP_paired_delta_EI_minus_greedy.abs() <= 0.02 + 1e-9).sum()), E2E_within_0_01=int((S1.E2E_paired_delta.abs() <= 0.01 + 1e-9).sum()))
# S2: portfolio, seeds 42-61, roots results + results_slurm (first wins)
ARMS = {'EI': 'blr_replace__hf_ei', 'PI': 'blr_replace__hf_pi', 'UCB': 'blr_replace__hf_ucb', 'MES': 'blr_replace__hf_mes', 'TS': 'blr_replace__hf_ts'}
s2 = []
for a, arm in ARMS.items():
    ca = arm_cells(TLR, arm, SEEDS20)
    for p in B9:
        B = BUD9_SI[p]; deltas = []; wins = 0; nm = 0; ns = []
        for m in TL9:
            e, g = att_of(ca, p, m, B), att_of(tl_gr20, p, m, B); com = sorted(set(e) & set(g))
            if not com: continue
            dlt = float(np.mean([e[s] - g[s] for s in com])); deltas.append(dlt); wins += int(dlt > 1e-12); nm += 1; ns.append(len(com))
        s2.append(dict(acq=a, pool=p, B=B, n_models=nm, mean_delta=np.mean(deltas) if deltas else np.nan, win_share=wins / nm if nm else np.nan, n_seeds_min=min(ns) if ns else 0, n_seeds_max=max(ns) if ns else 0))
S2 = pd.DataFrame(s2); S2.to_csv(OUT / 's2_recomputed.csv', index=False); log(S2.round(3).to_string(index=False))
REPORT['s2'] = S2.round(4).to_dict('records')
ref_s2 = pd.read_csv(f'{R}/figcand2_20260914_5tl/supp/supp_acq_portfolio_meandelta.csv', index_col=0)
log('  reference supp_acq_portfolio_meandelta.csv:'); log(ref_s2.round(3).to_string())

# ----------------------------------------------------------------------------------------------------------------------- Table 1
log('# 10. Table 1 / SI Table 4: pool sizes, R2, synthetic definitions')
sys.path.insert(0, '/mnt/data/jaewook_mfbo/MFBO-TL-Paper/src')
import synthetic_functions as SF  # noqa: E402
t1 = []
for p in POOLS13:
    y_hf, y_lf, cfg = YS[p]
    t1.append(dict(pool=p, n=len(y_hf), rho=cfg['cost_ratio'], r2_pool=round(float(np.corrcoef(y_hf, y_lf)[0, 1] ** 2), 4), budget_cfg=cfg['budget'], negate=cfg['negate'], csv=cfg['csv']))
T1 = pd.DataFrame(t1)
syn = {'Branin-Fav': (SF.branin_hf, SF.branin_lf, 2, 0.8), 'Branin-Unfav': (SF.branin_hf, SF.branin_lf, 2, 0.1), 'Park-Fav': (SF.park_hf, SF.park_lf, 4, 0.6), 'Park-Unfav': (SF.park_hf, SF.park_lf, 4, 0.0)}
for p, (fh, fl_, dim, al) in syn.items():
    r2u = SF.compute_r2(fh, fl_, dim, al, n_samples=1000, seed=42)
    csv = pd.read_csv(DATA / YS[p][2]['csv']); Xc = csv[[c for c in csv.columns if c.startswith('f')]].values
    hf_re = fh(Xc).ravel(); lf_re = fl_(Xc, al).ravel()
    ok = bool(np.allclose(hf_re, csv.HF.values, rtol=1e-9, atol=1e-12) and np.allclose(lf_re, csv.LF.values, rtol=1e-9, atol=1e-12))
    lat = sorted(set(np.round(Xc[:, 0], 12)))
    T1.loc[T1.pool == p, 'r2_1000uniform'] = round(float(r2u), 4); T1.loc[T1.pool == p, 'csv_regenerates_from_src'] = ok; T1.loc[T1.pool == p, 'alpha'] = al
    T1.loc[T1.pool == p, 'lattice_points_per_axis'] = len(lat); T1.loc[T1.pool == p, 'pool_min_HF'] = float(csv.HF.min())
    log(f'  {p}: alpha {al}; R2(1000 uniform, seed 42) {r2u:.4f}; R2(pool) {np.corrcoef(csv.HF, csv.LF)[0,1]**2:.4f}; csv == src functions: {ok}; lattice {len(lat)}^{dim}; pool min HF {csv.HF.min():.6g}')
T1.to_csv(OUT / 'table1_recomputed.csv', index=False); log(T1.to_string(index=False)); REPORT['table1'] = T1.to_dict('records')
# Park: which formula does the csv follow? standard Park (with -1 outside the root) vs code (sqrt(A))
csvp = pd.read_csv(DATA / 'synthetic_park_fav.csv'); Xp = csvp[['f0', 'f1', 'f2', 'f3']].values; x1 = np.maximum(Xp[:, 0], 1e-8); x4 = np.maximum(Xp[:, 3], 1e-8)
inner = (Xp[:, 1] + Xp[:, 2] ** 2) * x4 / (x1 ** 2)
std_park = x1 / 2 * (np.sqrt(1 + inner) - 1) + (x1 + 3 * x4) * np.exp(1 + np.sin(Xp[:, 2]))
si_park = x1 / 2 * np.sqrt(1 + inner) + (x1 + 3 * x4) * np.exp(1 + np.sin(Xp[:, 2]))
code_park = x1 / 2 * np.sqrt(np.maximum(inner, 0)) + (x1 + 3 * x4) * np.exp(1 + np.sin(Xp[:, 2]))
REPORT['park_formula'] = dict(max_abs_diff_vs_standard_park=float(np.max(np.abs(std_park - csvp.HF.values))), max_abs_diff_vs_SI_equation=float(np.max(np.abs(si_park - csvp.HF.values))),
                              max_abs_diff_vs_code=float(np.max(np.abs(code_park - csvp.HF.values))))
log(f'  Park csv vs formulas: standard Park (sqrt(1+A)-1) max diff {REPORT["park_formula"]["max_abs_diff_vs_standard_park"]:.3g}; SI equation (sqrt(1+A)) {REPORT["park_formula"]["max_abs_diff_vs_SI_equation"]:.3g}; code (sqrt(A)) {REPORT["park_formula"]["max_abs_diff_vs_code"]:.3g}')

# ----------------------------------------------------------------------------------------------------------------------- init sizes, n per cell, cross-env
log('# 11. initial design sizes, seeds per cell, environment cross-check')
init = []
for p in B9 + LARGE4:
    files = glob.glob(f'{R}/results/blr_replace__hf_argmin/cells/summary_{p}_DNGOJoint_*.csv') or glob.glob(f'{X}/results_confirm_ext/blr_replace__hf_argmin/cells/summary_{p}_DNGOJoint_*.csv')
    if not files: continue
    s = pd.concat([pd.read_csv(f) for f in files]); rho = YS[p][2]['cost_ratio']; Bc = YS[p][2]['budget']
    n_lf0 = max(2, int(0.1 * Bc * 0.5 / rho)); n_hf0 = max(2, int(0.1 * Bc * 0.5))
    init.append(dict(pool=p, budget_cfg=Bc, rho=rho, n_init_hf=n_hf0, n_init_lf=n_lf0, init_cost=round(n_hf0 + n_lf0 * rho, 3), n_hf_end=sorted(s.n_hf.unique().tolist()), n_lf_end=sorted(s.n_lf.unique().tolist())))
INIT = pd.DataFrame(init); log(INIT.to_string(index=False)); REPORT['init'] = INIT.to_dict('records')
# seeds per (pool, model) in the Fig. 1 cells
npc = A.pivot(index='model', columns='pool', values='n').loc[M12, POOLS13]; log('  n per cell (Fig. 1):'); log(npc.to_string())
# cross-environment: VM results vs SLURM results for the same arm/seed (blr_replace__hf_ei)
vm = pd.concat([pd.read_csv(f) for f in glob.glob(f'{R}/results/blr_replace__hf_ei/cells/summary_*.csv')]); sl = pd.concat([pd.read_csv(f) for f in glob.glob(f'{R}/results_slurm/blr_replace__hf_ei/cells/summary_*.csv')])
cx = vm.merge(sl, on=['benchmark', 'model', 'seed'], suffixes=('_vm', '_slurm'))
cx['final_equal'] = np.isclose(cx.final_regret_vm, cx.final_regret_slurm, rtol=0, atol=1e-12); cx['auc_equal'] = np.isclose(cx.auc_vm, cx.auc_slurm, rtol=1e-12, atol=1e-12)
cx[['benchmark', 'model', 'seed', 'final_regret_vm', 'final_regret_slurm', 'auc_vm', 'auc_slurm', 'final_equal', 'auc_equal']].to_csv(OUT / 'crossenv_check.csv', index=False)
log(f'  VM vs SLURM (blr_replace__hf_ei, same seeds): {len(cx)} overlapping runs; final regret identical {int(cx.final_equal.sum())}; auc identical {int(cx.auc_equal.sum())}; max |auc diff| {(cx.auc_vm - cx.auc_slurm).abs().max():.3g}')
REPORT['crossenv'] = dict(overlap=int(len(cx)), final_identical=int(cx.final_equal.sum()), auc_identical=int(cx.auc_equal.sum()), max_auc_diff=float((cx.auc_vm - cx.auc_slurm).abs().max()))
# figrepo/results collected CSVs vs raw (42-61)
mb = pd.read_csv(f'{R}/figrepo/results/main_9bench/results_summary.csv'); eb = pd.read_csv(f'{R}/figrepo/results/extra_baselines/results_summary.csv')
fr = pd.concat([mb, eb]); fr['model'] = fr.model.map(lambda m: RENAME.get(m, m)); fr = fr[fr.model.isin(M12)]
raw42 = {}
for k in ('refig42_tl', 'refig42_gp'):
    raw42.update(to_cells(RAW[k][RAW[k].benchmark.isin(B9)], keep_models=set(M12), seeds=SEEDS20)[0])
diffs = []; missing = 0
for r_ in fr.itertuples():
    c = raw42.get((r_.benchmark, r_.model, int(r_.seed)))
    if c is None: missing += 1; continue
    diffs.append(abs(c['reg'][-1] - r_.final_regret))
log(f'  figrepo/results (collect.py output) vs raw cells 42-61: {len(fr)} rows, {missing} not found in raw, max |final diff| {max(diffs) if diffs else float("nan"):.3g}; cells per model: ' + str(fr.groupby('model').seed.size().to_dict()))
REPORT['figrepo_vs_raw'] = dict(rows=int(len(fr)), missing=missing, max_diff=float(max(diffs)) if diffs else None)

json.dump(REPORT, open(OUT / 'report.json', 'w'), indent=1, default=str)
open(OUT / 'report.md', 'w').write('\n'.join(MD))
log(f'DONE in {time.time()-T0:.0f}s -> {OUT}')
