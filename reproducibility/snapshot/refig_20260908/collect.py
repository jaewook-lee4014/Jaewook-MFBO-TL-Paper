#!/usr/bin/env python
"""Merge the 2026-09-08 regeneration runs into the public-repo result layout under figrepo/results,
so the (patched) public figure scripts regenerate every manuscript figure.

Sources (roots given on the command line via env; first occurrence of (benchmark, model, seed) wins):
  TL_ROOTS   colon-separated dirs holding <arm>/cells/{summary,traj}_*.csv   (VM results, SLURM results)
  GP_ROOTS   dirs holding gp_ei/cells and gp_greedy/cells                    (run_gp.py outputs)
  GP_FALLBACK dirs of older per-fidelity GP runs (summary_*.csv/traj_*.csv anywhere below), used only
             for (benchmark, model, seed) missing from GP_ROOTS
  GRID_TL_ROOTS dirs holding blr_replace__hf_argmin/cells for cell_XX pools
  GRID_GP_ROOTS dirs holding gp_ei/cells for cell_XX pools (NARGP)
  PUBGRID    public results/grid (manifest + cells with MFGP / SparseMFGP / DKL)
"""
import os, sys, glob
from pathlib import Path
import numpy as np, pandas as pd

HERE = Path(__file__).resolve().parent
OUT = HERE / 'figrepo' / 'results'
PRIMARY = os.environ.get('PRIMARY_ARM', 'blr_replace__hf_argmin')
EI_ARM = os.environ.get('EI_ARM', 'blr_replace__hf_ei')
UQ_ARMS = {'ei': 'blr_replace__hf_ei', 'pi': 'blr_replace__hf_pi', 'ucb': 'blr_replace__hf_ucb',
           'mes': 'blr_replace__hf_mes', 'ts': 'blr_replace__hf_ts'}
B9 = ['Branin-Fav', 'Branin-Unfav', 'Park-Fav', 'Park-Unfav', 'COFs', 'FreeSolv', 'Polarizability', 'HOPV15', 'Matbench-Gap']
TL11 = ['Sequential', 'Curriculum', 'DNGOGradient', 'Progressive', 'TwoStageJoint', 'DNGOJoint', 'KnowledgeDistillation',
        'DomainAdaptationMMD', 'SoftParameterSharing', 'PseudoLabeling', 'Adapter']
GP3 = ['MFGP', 'NARGP', 'SparseMFGP', 'DKL']   # all GP baselines carried; figure scripts select
PUBNAME = {'DNGOGradient': 'DNGO-Gradient', 'TwoStageJoint': 'Two-Stage Joint', 'DNGOJoint': 'DNGO-Joint',
           'KnowledgeDistillation': 'Knowledge Distillation', 'DomainAdaptationMMD': 'Domain Adaptation (MMD)',
           'SoftParameterSharing': 'Soft Parameter Sharing', 'PseudoLabeling': 'Pseudo-Labeling', 'SparseMFGP': 'Sparse MFGP', 'DKL': 'DKL Multi-Fidelity'}
SEEDS = list(range(42, 62))
EARLY = {'Park-Fav', 'Park-Unfav'}; EARLY_B = 10

def _roots(k):
    v = os.environ.get(k, '')
    return [Path(p) for p in v.split(':') if p]

def load_cells(dirs, kind, pattern=None):
    """Concatenate cells/<kind>_*.csv under each dir (recursively), first occurrence wins."""
    parts = []
    for d in dirs:
        for f in sorted(glob.glob(str(d / '**' / f'{kind}_*.csv'), recursive=True)):
            try:
                df = pd.read_csv(f)
            except Exception as e:
                print('skip', f, e); continue
            if len(df): parts.append(df)
    if not parts:
        cols = ['benchmark', 'model', 'seed', 'final_regret', 'auc', 'n_hf', 'n_lf', 'ece_lf_final', 'ece_lf_mean'] if kind == 'summary' else ['benchmark', 'model', 'seed', 'budget', 'regret']
        return pd.DataFrame(columns=cols)
    df = pd.concat(parts, ignore_index=True)
    key = ['benchmark', 'model', 'seed'] if kind == 'summary' else ['benchmark', 'model', 'seed', 'budget']
    if kind == 'traj':
        # keep the whole trajectory of the first (benchmark, model, seed) occurrence
        first = df.drop_duplicates(['benchmark', 'model', 'seed'])[['benchmark', 'model', 'seed']]
        df['_src'] = np.arange(len(df))
        return df
    return df.drop_duplicates(key, keep='first').reset_index(drop=True)

def load_arm(roots, arm):
    s = load_cells([r / arm for r in roots], 'summary')
    t = load_cells([r / arm for r in roots], 'traj')
    return s, dedupe_traj(t, s)

def dedupe_traj(t, s):
    if t.empty: return pd.DataFrame(columns=['benchmark', 'model', 'seed', 'budget', 'regret'])
    # a trajectory file appends per seed; if a seed appears in several source files keep the first file's rows
    t = t.copy(); t['_file_rank'] = t.groupby(['benchmark', 'model', 'seed']).cumcount()
    # rows are contiguous per seed within a file; detect restarts (budget decreasing) to split duplicates
    out = []
    for (b, m, sd), g in t.groupby(['benchmark', 'model', 'seed'], sort=False):
        bud = g['budget'].values
        cut = np.where(np.diff(bud) < 0)[0]
        end = (cut[0] + 1) if len(cut) else len(g)
        out.append(g.iloc[:end])
    t = pd.concat(out, ignore_index=True)
    return t[['benchmark', 'model', 'seed', 'budget', 'regret']]

def pub(df):
    df = df.copy(); df['model'] = df['model'].replace(PUBNAME); return df

def coverage(df, benches, models, tag):
    miss = []
    for b in benches:
        for m in models:
            n = df[(df.benchmark == b) & (df.model == m)]['seed'].nunique()
            if n < 20: miss.append(f'{b}/{m}:{n}')
    print(f'[{tag}] cells below 20 seeds: {len(miss)}', ' '.join(miss[:12]))

def early_regret(traj, b, models):
    rows = [dict(benchmark=b, model=None, seed=None, final_regret=np.nan)][:0]
    bd = traj[traj.benchmark == b]
    for m in models:
        for s, sd in bd[bd.model == m].groupby('seed'):
            sd = sd.sort_values('budget'); v = sd[sd.budget <= EARLY_B]
            rows.append(dict(benchmark=b, model=m, seed=s, final_regret=(v.iloc[-1] if len(v) else sd.iloc[0])['regret']))
    return pd.DataFrame(rows, columns=['benchmark', 'model', 'seed', 'final_regret'])

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    tl_roots, gp_roots, gp_fb = _roots('TL_ROOTS'), _roots('GP_ROOTS'), _roots('GP_FALLBACK')
    # ---------------- TL primary arm + GP (EI) -> main_9bench / extra_baselines ----------------
    s_tl, t_tl = load_arm(tl_roots, PRIMARY)
    s_tl = s_tl[s_tl.benchmark.isin(B9) & s_tl.model.isin(TL11)]; t_tl = t_tl[t_tl.benchmark.isin(B9) & t_tl.model.isin(TL11)]
    coverage(s_tl, B9, TL11, 'TL primary')
    s_gp = load_cells([r / 'gp_ei' for r in gp_roots], 'summary'); t_gp = dedupe_traj(load_cells([r / 'gp_ei' for r in gp_roots], 'traj'), s_gp)
    s_gp = s_gp[s_gp.benchmark.isin(B9) & s_gp.model.isin(GP3)] if len(s_gp) else s_gp
    t_gp = t_gp[t_gp.benchmark.isin(B9) & t_gp.model.isin(GP3)] if len(t_gp) else t_gp
    coverage(s_gp, B9, GP3, 'GP fresh')
    if gp_fb:
        s_fb = load_cells(gp_fb, 'summary'); t_fb = dedupe_traj(load_cells(gp_fb, 'traj'), s_fb)
        s_fb = s_fb[s_fb.benchmark.isin(B9) & s_fb.model.isin(GP3) & s_fb.seed.isin(SEEDS)]
        have = set(map(tuple, s_gp[['benchmark', 'model', 'seed']].values)) if len(s_gp) else set()
        add = s_fb[[tuple(x) not in have for x in s_fb[['benchmark', 'model', 'seed']].values]]
        add = add.drop_duplicates(['benchmark', 'model', 'seed'])
        print(f'[GP fallback] adding {len(add)} seed rows from older per-fidelity runs')
        addk = set(map(tuple, add[['benchmark', 'model', 'seed']].values))
        t_add = t_fb[[tuple(x) in addk for x in t_fb[['benchmark', 'model', 'seed']].values]]
        s_gp = pd.concat([s_gp, add], ignore_index=True); t_gp = pd.concat([t_gp, t_add], ignore_index=True)
        coverage(s_gp, B9, GP3, 'GP merged')
    cols = ['benchmark', 'model', 'seed', 'final_regret', 'n_hf', 'n_lf']
    tcols = ['benchmark', 'model', 'seed', 'budget', 'regret']
    (OUT / 'main_9bench').mkdir(exist_ok=True)
    main_s = pd.concat([s_tl, s_gp[s_gp.model == 'MFGP']], ignore_index=True)
    main_t = pd.concat([t_tl, t_gp[t_gp.model == 'MFGP']], ignore_index=True)
    pub(main_s)[cols].to_csv(OUT / 'main_9bench' / 'results_summary.csv', index=False)
    pub(main_t)[tcols].to_csv(OUT / 'main_9bench' / 'results_trajectory.csv', index=False)
    (OUT / 'extra_baselines').mkdir(exist_ok=True); (OUT / 'gpfamily_newbench').mkdir(exist_ok=True)
    pub(s_gp[s_gp.model != 'MFGP'])[cols].to_csv(OUT / 'extra_baselines' / 'results_summary.csv', index=False)
    pub(t_gp[t_gp.model != 'MFGP'])[tcols].to_csv(OUT / 'extra_baselines' / 'results_trajectory.csv', index=False)
    pd.DataFrame(columns=cols).to_csv(OUT / 'gpfamily_newbench' / 'results_summary.csv', index=False)
    pd.DataFrame(columns=tcols).to_csv(OUT / 'gpfamily_newbench' / 'results_trajectory.csv', index=False)
    # ---------------- Fig 3: TL EI arm -> main_corrected ; MFGP greedy -> mfgp_greedy_7bench ----------------
    s_ei, t_ei = load_arm(tl_roots, EI_ARM); coverage(s_ei, B9, TL11, 'TL hf_ei')
    (OUT / 'main_corrected').mkdir(exist_ok=True)
    pub(s_ei)[cols].to_csv(OUT / 'main_corrected' / 'results_summary.csv', index=False)
    pub(t_ei)[tcols].to_csv(OUT / 'main_corrected' / 'results_trajectory.csv', index=False)
    s_gg = load_cells([r / 'gp_greedy' for r in gp_roots], 'summary'); t_gg = dedupe_traj(load_cells([r / 'gp_greedy' for r in gp_roots], 'traj'), s_gg)
    coverage(s_gg, B9, ['MFGP'], 'MFGP greedy')
    (OUT / 'mfgp_greedy_7bench').mkdir(exist_ok=True); (OUT / 'mfgp_greedy_newbench').mkdir(exist_ok=True)
    s_gg[cols].to_csv(OUT / 'mfgp_greedy_7bench' / 'summary_all.csv', index=False)
    t_gg[tcols].to_csv(OUT / 'mfgp_greedy_7bench' / 'results_trajectory.csv', index=False)
    pd.DataFrame(columns=cols).to_csv(OUT / 'mfgp_greedy_newbench' / 'results_summary.csv', index=False)
    # ---------------- Fig 4a-d: acquisition portfolio ----------------
    arms = {'greedy': (s_tl, t_tl)}
    for a, arm in UQ_ARMS.items():
        arms[a] = load_arm(tl_roots, arm); coverage(arms[a][0], B9, TL11, f'TL {a}')
    rows = []
    for a, (s, t) in arms.items():
        for b in B9:
            d = early_regret(t, b, TL11) if b in EARLY else s[s.benchmark == b]
            for m, g in d.groupby('model'):
                rows.append(dict(benchmark=b, model=PUBNAME.get(m, m), acq=a, mean=float(g.final_regret.mean()), n=int(g.seed.nunique())))
    means = pd.DataFrame(rows)
    wr = {}
    for a in UQ_ARMS:
        wr[a] = {}
        for b in B9:
            g = means[(means.benchmark == b) & (means.acq == 'greedy')].set_index('model')['mean']
            u = means[(means.benchmark == b) & (means.acq == a)].set_index('model')['mean']
            com = g.index.intersection(u.index)
            wr[a][b] = float(np.mean(u[com].values < g[com].values)) if len(com) else np.nan
    (OUT / 'acq_portfolio').mkdir(exist_ok=True)
    pd.DataFrame(wr).T.to_csv(OUT / 'acq_portfolio' / 'surrogates_winrate.csv')
    means.to_csv(OUT / 'acq_portfolio' / 'surrogates_means.csv', index=False)
    # ---------------- Fig 4e-m: calibration (LF ECE at the final refit) ----------------
    def calib(s, t):
        rows = []
        for b in B9:
            d = s[s.benchmark == b]
            if b in EARLY:
                e = early_regret(t, b, sorted(d.model.unique())).merge(d[['benchmark', 'model', 'seed', 'ece_lf_final', 'ece_lf_mean']], on=['benchmark', 'model', 'seed'])
            else:
                e = d[['benchmark', 'model', 'seed', 'final_regret', 'ece_lf_final', 'ece_lf_mean']]
            rows.append(e)
        e = pd.concat(rows, ignore_index=True).rename(columns={'ece_lf_final': 'lf_ece', 'ece_lf_mean': 'lf_ece_mean'})
        return pub(e)
    c_tl = calib(s_tl, t_tl); c_gp = calib(s_gp, t_gp)
    for d in ('calibration_sweep', 'calibration_park_early', 'calibration_gpfamily', 'calibration_newbench', 'calibration_synthetic'):
        (OUT / d).mkdir(exist_ok=True)
    c_tl[~c_tl.benchmark.isin(EARLY)].to_csv(OUT / 'calibration_sweep' / 'results_summary.csv', index=False)
    c_tl[c_tl.benchmark.isin(EARLY)].assign(calib_budget=EARLY_B).to_csv(OUT / 'calibration_park_early' / 'results_summary.csv', index=False)
    c_gp.to_csv(OUT / 'calibration_gpfamily' / 'results_summary.csv', index=False)
    print('[calibration] NaN ECE rows:', int(c_tl.lf_ece.isna().sum()), int(c_gp.lf_ece.isna().sum()))
    # ---------------- Fig 1 l-n / SI grid: 126 cells ----------------
    pubgrid = Path(os.environ['PUBGRID'])
    gtl = load_cells([r / PRIMARY for r in _roots('GRID_TL_ROOTS')], 'summary')
    ggp = load_cells([r / 'gp_ei' for r in _roots('GRID_GP_ROOTS')], 'summary')
    (OUT / 'grid' / 'cells').mkdir(parents=True, exist_ok=True)
    man = pd.read_csv(pubgrid / 'grid_manifest.csv'); man.to_csv(OUT / 'grid' / 'grid_manifest.csv', index=False)
    gcols = ['benchmark', 'model', 'seed', 'final_regret', 'auc']
    short = []
    for cid in man.cell_id:
        p = pd.read_csv(pubgrid / 'cells' / f'summary_{cid}.csv')
        p = p[p.model.isin(['MFGP', 'SparseMFGP', 'DKL'])][gcols]
        n = ggp[(ggp.benchmark == cid) & (ggp.model == 'NARGP')][gcols] if len(ggp) else pd.DataFrame(columns=gcols)
        t = gtl[gtl.benchmark == cid][gcols] if len(gtl) else pd.DataFrame(columns=gcols)
        d = pd.concat([p, n, t], ignore_index=True)
        for m in ['NARGP', 'Progressive', 'KnowledgeDistillation', 'PseudoLabeling']:
            k = d[d.model == m].seed.nunique()
            if k < 10: short.append(f'{cid}/{m}:{k}')
        d.to_csv(OUT / 'grid' / 'cells' / f'summary_{cid}.csv', index=False)
    print(f'[grid] cells/models below 10 seeds: {len(short)}', ' '.join(short[:30]))
    # extra arms summary table for the report (warm / relu / small head)
    ex = []
    for arm in ['blr_replace__hf_argmin', 'blr_replace__hf_argmin__warm', 'blr_replace__hf_argmin__relu', 'mlp_small__hf_argmin']:
        s, t = load_arm(tl_roots, arm)
        if len(s): ex.append(s.assign(arm=arm))
    if ex:
        pd.concat(ex, ignore_index=True).to_csv(OUT / 'tl_arms_all_summary.csv', index=False)
    s_gp.to_csv(OUT / 'gp_all_summary.csv', index=False)
    print('done ->', OUT)

if __name__ == '__main__':
    main()
