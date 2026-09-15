#!/usr/bin/env python
"""Merge the budget-extension runs (VM results/ + SLURM copies in results_slurm/), verify that every
trajectory reproduces the refig_20260908 prefix, and summarise / plot the extended trajectories.
Run on the VM:  python analyze_ext.py   -> out/ext_summary.csv, out/ext_prefix_check.csv, out/ext_traj.{pdf,png}, out/ext_report.md"""
import glob, os, sys
from pathlib import Path
import numpy as np, pandas as pd
HERE = Path(__file__).resolve().parent; OUT = HERE / os.environ.get('EXT_OUT', 'out'); OUT.mkdir(exist_ok=True)   # EXT_OUT=out_ext100 for the Matbench 100 pass
REF = HERE.parent / 'refig_20260908'
SEEDS = list(range(42, 62))
BENCH = ['FreeSolv', 'Polarizability', 'HOPV15', 'Matbench-Gap']
ORIG = {'FreeSolv': 50, 'Polarizability': 30, 'HOPV15': 30, 'Matbench-Gap': 20}
EXT = {'FreeSolv': 100, 'Polarizability': 60, 'HOPV15': 45, 'Matbench-Gap': 40}
for kv in os.environ.get('EXT_BUDGETS_OVERRIDE', '').split(','):   # e.g. 'Matbench-Gap=100' with EXT_ROOTS=results_ext100:results
    if '=' in kv: k, v = kv.split('='); EXT[k.strip()] = int(float(v))
GP = ['MFGP', 'SparseMFGP', 'NARGP']
TL = ['Sequential', 'Curriculum', 'DNGOGradient', 'Progressive', 'TwoStageJoint', 'DNGOJoint',
      'KnowledgeDistillation', 'DomainAdaptationMMD', 'SoftParameterSharing', 'PseudoLabeling', 'Adapter']
ROOTS = [HERE / r for r in os.environ.get('EXT_ROOTS', 'results:results_slurm').split(':') if r]   # first root wins on duplicates
SUB = {'gp': 'gp_ei', 'tl': 'blr_replace__hf_argmin'}

def load(kind, sub):
    S, T = [], []
    for root in ROOTS:
        for f in glob.glob(str(root / sub / 'cells' / f'{kind}_*.csv')):
            try: df = pd.read_csv(f)
            except Exception: continue
            df['src'] = root.name; (S if kind == 'summary' else T).append(df)
    return pd.concat(S + T, ignore_index=True) if (S + T) else pd.DataFrame()

def dedupe(df, keys=('benchmark', 'model', 'seed')):
    if df.empty: return df
    first = df.drop_duplicates(list(keys), keep='first')[list(keys) + ['src']]
    return df.merge(first, on=list(keys) + ['src'])

summ = pd.concat([dedupe(load('summary', SUB['gp'])), dedupe(load('summary', SUB['tl']))], ignore_index=True)
traj = pd.concat([dedupe(load('traj', SUB['gp'])), dedupe(load('traj', SUB['tl']))], ignore_index=True)
summ = summ[summ.seed.isin(SEEDS) & summ.benchmark.isin(BENCH) & summ.model.isin(GP + TL)]; traj = traj[traj.seed.isin(SEEDS) & traj.benchmark.isin(BENCH) & traj.model.isin(GP + TL)]   # drops DKL etc. from other campaigns sharing results/

# ---- reference (original budget) trajectories and summaries ----
def load_ref(sub, kind):
    fs = glob.glob(str(REF / ('results_gp' if sub.startswith('gp') else 'results') / sub / 'cells' / f'{kind}_*.csv'))
    df = pd.concat([pd.read_csv(f) for f in fs], ignore_index=True)
    return df[df.seed.isin(SEEDS) & df.benchmark.isin(BENCH)].drop_duplicates(['benchmark', 'model', 'seed'] + (['budget'] if kind == 'traj' else []))
rsum = pd.concat([load_ref(SUB['gp'], 'summary'), load_ref(SUB['tl'], 'summary')], ignore_index=True)
rtraj = pd.concat([load_ref(SUB['gp'], 'traj'), load_ref(SUB['tl'], 'traj')], ignore_index=True)

# ---- prefix check: the new trajectory restricted to the original budget must equal the reference ----
rows = []
for (b, m, s), g in traj.groupby(['benchmark', 'model', 'seed']):
    r = rtraj[(rtraj.benchmark == b) & (rtraj.model == m) & (rtraj.seed == s)].sort_values('budget')
    g = g.sort_values('budget')
    if len(r) == 0: rows.append(dict(benchmark=b, model=m, seed=s, status='no_ref')); continue
    # compare only the region before the end-of-budget remainder rule of the ORIGINAL run (budget <= B_orig - 1):
    # there the original run spends the remainder on LF picks while the extended run continues the round-robin.
    r = r[r.budget <= ORIG[b] - 1.0 + 1e-9]; n = len(r)
    ok = len(g) >= n and np.allclose(g.regret.values[:n], r.regret.values, atol=1e-9) and np.allclose(g.budget.values[:n], r.budget.values, atol=1e-6)
    ndiff = int(np.argmax(~np.isclose(g.regret.values[:n], r.regret.values, atol=1e-9) | ~np.isclose(g.budget.values[:n], r.budget.values, atol=1e-6))) if not ok and len(g) >= n else -1
    rows.append(dict(benchmark=b, model=m, seed=s, status='match' if ok else 'MISMATCH', first_diff_step=ndiff, n_compared=n, ref_at_Bm1=r.regret.values[-1], new_at_Bm1=g.regret.values[n - 1] if len(g) >= n else np.nan, new_final=g.regret.values[-1], src=g.src.iloc[0]))
chk = pd.DataFrame(rows); chk.to_csv(OUT / 'ext_prefix_check.csv', index=False)

# ---- summary per (benchmark, model): zero-reach at original and extended budget, mean regret, cost to zero ----
def regret_at(g, B):
    g = g.sort_values('budget'); v = g[g.budget <= B + 1e-9]
    return float(v.regret.values[-1]) if len(v) else np.nan
def cost_to_zero(g):
    g = g.sort_values('budget'); z = g[g.regret <= 1e-9]
    return float(z.budget.values[0]) if len(z) else np.inf
rows = []
for (b, m), g in traj.groupby(['benchmark', 'model']):
    per = []
    for s, gs in g.groupby('seed'):
        per.append(dict(seed=s, r_orig=regret_at(gs, ORIG[b]), r_ext=regret_at(gs, EXT[b]), ctz=cost_to_zero(gs)))
    p = pd.DataFrame(per)
    ctz = p.ctz.replace(np.inf, np.nan)
    rows.append(dict(benchmark=b, family='GP' if m in GP else 'TL', model=m, n_seeds=len(p), B_orig=ORIG[b], B_ext=EXT[b],
                     zero_frac_orig=float((p.r_orig <= 1e-9).mean()), zero_frac_ext=float((p.r_ext <= 1e-9).mean()),
                     mean_regret_orig=float(p.r_orig.mean()), mean_regret_ext=float(p.r_ext.mean()),
                     median_cost_to_zero=float(np.median(p.ctz)) if np.isfinite(np.median(p.ctz)) else np.inf,
                     n_never_zero=int((~np.isfinite(p.ctz)).sum())))
tab = pd.DataFrame(rows).sort_values(['benchmark', 'family', 'model']); tab.to_csv(OUT / 'ext_summary.csv', index=False)

# ---- figure: mean regret vs budget, 4 panels, original budget marked ----
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
fig, axes = plt.subplots(1, 4, figsize=(17, 3.9))
cols_gp = {'MFGP': '#c0392b', 'SparseMFGP': '#e67e22', 'NARGP': '#8e44ad'}
for ax, b in zip(axes, BENCH):
    grid = np.linspace(0, EXT[b], 200)
    for m in TL + GP:
        g = traj[(traj.benchmark == b) & (traj.model == m)]
        if g.empty: continue
        curves = []
        for s, gs in g.groupby('seed'):
            gs = gs.sort_values('budget'); curves.append(np.interp(grid, gs.budget.values, gs.regret.values, left=np.nan, right=gs.regret.values[-1]))
        mu = np.nanmean(np.vstack(curves), axis=0)
        if m in GP: ax.plot(grid, mu, color=cols_gp[m], lw=2.2, label=m, zorder=3)
        else: ax.plot(grid, mu, color='#2c7fb8', lw=0.9, alpha=0.55, label='TL (11 models)' if m == TL[0] else None)
    ax.axvline(ORIG[b], color='k', ls='--', lw=0.8); ax.set_title(f'{b}  (B {ORIG[b]} -> {EXT[b]})'); ax.set_xlabel('cost'); ax.set_yscale('symlog', linthresh=1e-2)
    ax.set_ylabel('simple regret (mean of 20 seeds)')
axes[0].legend(fontsize=7, frameon=False)
fig.tight_layout(); fig.savefig(OUT / 'ext_traj.pdf'); fig.savefig(OUT / 'ext_traj.png', dpi=130)

# ---- zero-reach figure: fraction of seeds at zero vs budget ----
fig, axes = plt.subplots(1, 4, figsize=(17, 3.6))
for ax, b in zip(axes, BENCH):
    grid = np.linspace(0, EXT[b], 200)
    for m in TL + GP:
        g = traj[(traj.benchmark == b) & (traj.model == m)]
        if g.empty: continue
        z = []
        for s, gs in g.groupby('seed'):
            c = cost_to_zero(gs); z.append((grid >= c).astype(float))
        mu = np.mean(np.vstack(z), axis=0)
        if m in GP: ax.plot(grid, mu, color=cols_gp[m], lw=2.2, label=m, zorder=3)
        else: ax.plot(grid, mu, color='#2c7fb8', lw=0.9, alpha=0.55, label='TL (11 models)' if m == TL[0] else None)
    ax.axvline(ORIG[b], color='k', ls='--', lw=0.8); ax.set_title(b); ax.set_xlabel('cost'); ax.set_ylabel('fraction of seeds at regret 0'); ax.set_ylim(-0.02, 1.02)
axes[0].legend(fontsize=7, frameon=False)
fig.tight_layout(); fig.savefig(OUT / 'ext_zero_reach.pdf'); fig.savefig(OUT / 'ext_zero_reach.png', dpi=130)

# ---- report ----
with open(OUT / 'ext_report.md', 'w') as f:
    f.write('# Chemistry budget extension (ext_chem_20260909)\n\n')
    f.write(f'runs merged: {len(summ)} summaries, {traj.groupby(["benchmark","model","seed"]).ngroups} trajectories; expected {len(BENCH)*(len(GP)+len(TL))*len(SEEDS)}\n\n')
    f.write('## Prefix check (new trajectory == refig_20260908 for budget <= B_orig - 1, i.e. before the remainder rule)\n\n')
    f.write(chk.status.value_counts().to_string() + '\n\n')
    bad = chk[chk.status == 'MISMATCH']
    if len(bad): f.write(bad.groupby(['benchmark', 'model']).agg(n=('seed', 'size'), first_diff_min=('first_diff_step', 'min'), mean_delta_at_Bm1=('new_at_Bm1', lambda x: float((x - bad.loc[x.index, 'ref_at_Bm1']).mean()))).round(3).to_string() + '\n\n')
    f.write('## Per model\n\n' + tab.round(3).to_string(index=False) + '\n')
print(open(OUT / 'ext_report.md').read())
