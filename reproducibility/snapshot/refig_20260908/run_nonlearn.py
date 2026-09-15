#!/usr/bin/env python
"""Surrogate-free (non-learning) baselines under the 2026-09-08 regeneration protocol (2026-09-09):
  HFRandom   HF-only random search: n_init = max(2, int(0.1 B)) HF points by FPS (same seed -> same FPS start as the
             surrogates), then uniformly random HF queries of unevaluated candidates until the budget is spent.
  LFScreenRR LF screening on the surrogates' round-robin schedule: identical FPS initial design (n_init_lf LF + n_init_hf
             HF), LF turn = random LF-unevaluated candidate, HF turn = argmin of the OBSERVED LF values among HF-unevaluated
             candidates (LF-evaluated ones; random if none). Per-fidelity masking, same budget accounting.
  LFScreenBatch  the paper's LF-screening allocation: reserve max(5, int(0.1 B)) HF, screen n_lf = min(N, int((B - reserve)/rho))
             candidates at LF (initial design + random), then spend the rest on HF in ascending LF order.
Output: results_nonlearn/<method>/cells/summary_<bench>_<method>_<tag>.csv + traj_...  (same columns as run_tl.py)."""
from __future__ import annotations
import argparse, os, sys, time
from pathlib import Path
import numpy as np, pandas as pd
sys.path.insert(0, str(Path(__file__).resolve().parent))
from run_tl import fps, _append, HERE, REPO
import pools as POOLS
METHODS = ['HFRandom', 'LFScreenRR', 'LFScreenBatch']
INIT_DESIGN = os.environ.get('INIT_DESIGN', 'fps'); assert INIT_DESIGN in ('fps', 'random')
def _init(X, n, seed, N):
    return np.random.RandomState(seed + 7_000_000).choice(N, n, replace=False) if INIT_DESIGN == 'random' else fps(X, n, seed)

def _finish(bench, hf_idx, lf_idx, regrets, budgets, picks, extra):
    tr = np.trapezoid if hasattr(np, 'trapezoid') else np.trapz
    pct = (np.argsort(np.argsort(bench.y_hf)) + 1) / bench.n_candidates
    return dict(final_regret=regrets[-1], auc=float(tr(regrets, budgets) / max(budgets[-1] - budgets[0], 1e-9)), n_hf=len(hf_idx), n_lf=len(lf_idx),
                pick_prec_top5=float(np.mean([pct[i] <= 0.05 + 1e-12 for i in picks])) if picks else np.nan, budgets=budgets, regrets=regrets, **extra)

def hf_random(bench, cfg, seed):
    X, y_hf = bench.X, bench.y_hf; budget = cfg['budget']; rng = np.random.RandomState(seed + 10_000)
    n_init = max(2, int(0.1 * budget)); init = _init(X, n_init, seed, bench.n_candidates); hf_idx = set(int(i) for i in init); cur = float(n_init)
    regrets = [float(max(0.0, y_hf[list(hf_idx)].min() - bench.f_star))]; budgets = [cur]; picks = []
    while cur + 1.0 <= budget + 1e-9:
        avail = np.setdiff1d(np.arange(bench.n_candidates), np.array(sorted(hf_idx)))
        if len(avail) == 0: break
        nxt = int(rng.choice(avail)); hf_idx.add(nxt); picks.append(nxt); cur += 1.0
        regrets.append(float(max(0.0, y_hf[list(hf_idx)].min() - bench.f_star))); budgets.append(cur)
    return _finish(bench, hf_idx, set(), regrets, budgets, picks, dict(n_lf_on_hf=0, n_hf_on_lf=0))

def lf_screen_rr(bench, cfg, seed):
    X, y_hf, y_lf = bench.X, bench.y_hf, bench.y_lf; rho, budget = bench.cost_ratio, cfg['budget']; rng = np.random.RandomState(seed + 20_000)
    n_init_lf = max(2, int(0.1 * budget * 0.5 / rho)); n_init_hf = max(2, int(0.1 * budget * 0.5))
    init = _init(X, n_init_lf + n_init_hf, seed, bench.n_candidates)
    lf_idx = set(int(i) for i in init[:n_init_lf]); hf_idx = set(int(i) for i in init[n_init_lf:n_init_lf + n_init_hf])
    cur = len(lf_idx) * rho + len(hf_idx) * 1.0; lf_per_hf = max(1, int(1.0 / rho)); lfc = it = 0
    regrets = [float(max(0.0, y_hf[list(hf_idx)].min() - bench.f_star))]; budgets = [cur]; picks = []; promo = 0
    while cur < budget and it < 5000:
        it += 1; rem = budget - cur
        if rem >= 1.0: eval_hf = not (rem >= rho and lfc < lf_per_hf)
        elif rem >= rho: eval_hf = False
        else: break
        if eval_hf:
            cand = np.array(sorted((lf_idx - hf_idx)))
            if len(cand): nxt = int(cand[np.argmin(y_lf[cand])]); promo += 1
            else:
                avail = np.setdiff1d(np.arange(bench.n_candidates), np.array(sorted(hf_idx))); nxt = int(rng.choice(avail))
            hf_idx.add(nxt); picks.append(nxt); cur += 1.0; lfc = 0
        else:
            avail = np.setdiff1d(np.arange(bench.n_candidates), np.array(sorted(lf_idx)))
            if len(avail) == 0: cur += rho; lfc += 1; continue
            nxt = int(rng.choice(avail)); lf_idx.add(nxt); cur += rho; lfc += 1
        regrets.append(float(max(0.0, y_hf[list(hf_idx)].min() - bench.f_star))); budgets.append(cur)
    return _finish(bench, hf_idx, lf_idx, regrets, budgets, picks, dict(n_lf_on_hf=0, n_hf_on_lf=promo))

def lf_screen_batch(bench, cfg, seed):
    X, y_hf, y_lf = bench.X, bench.y_hf, bench.y_lf; rho, budget = bench.cost_ratio, cfg['budget']; rng = np.random.RandomState(seed + 30_000)
    N = bench.n_candidates; n_reserve = max(5, int(0.1 * budget)); n_lf_target = min(N, int((budget - n_reserve) / rho))
    n_init_lf = max(2, int(0.1 * budget * 0.5 / rho)); n_init_hf = max(2, int(0.1 * budget * 0.5))
    init = _init(X, n_init_lf + n_init_hf, seed, bench.n_candidates)
    lf_idx = set(int(i) for i in init[:n_init_lf]); hf_idx = set(int(i) for i in init[n_init_lf:n_init_lf + n_init_hf])
    cur = len(lf_idx) * rho + len(hf_idx) * 1.0
    regrets = [float(max(0.0, y_hf[list(hf_idx)].min() - bench.f_star))]; budgets = [cur]; picks = []
    while len(lf_idx) < n_lf_target and cur + rho <= budget + 1e-9:
        avail = np.setdiff1d(np.arange(N), np.array(sorted(lf_idx)))
        if len(avail) == 0: break
        nxt = int(rng.choice(avail)); lf_idx.add(nxt); cur += rho
        regrets.append(regrets[-1]); budgets.append(cur)
    order = sorted(lf_idx - hf_idx, key=lambda i: y_lf[i])
    while cur + 1.0 <= budget + 1e-9 and order:
        nxt = order.pop(0); hf_idx.add(nxt); picks.append(nxt); cur += 1.0
        regrets.append(float(max(0.0, y_hf[list(hf_idx)].min() - bench.f_star))); budgets.append(cur)
    return _finish(bench, hf_idx, lf_idx, regrets, budgets, picks, dict(n_lf_on_hf=0, n_hf_on_lf=len(picks)))

RUN = {'HFRandom': hf_random, 'LFScreenRR': lf_screen_rr, 'LFScreenBatch': lf_screen_batch}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--benches', nargs='*', default=list(POOLS.PAPER)); ap.add_argument('--methods', nargs='*', default=METHODS)
    ap.add_argument('--seeds', type=int, nargs='*', default=list(range(42, 82))); ap.add_argument('--outdir', default=str(HERE / ('results_nonlearn' + ('_initrand' if INIT_DESIGN == 'random' else ''))))
    args = ap.parse_args()
    tag = f's{min(args.seeds)}-{max(args.seeds)}'
    for bn in args.benches:
        b, cfg = POOLS.make_bench(bn, REPO / 'data'); print(f'{bn}: N={b.n_candidates} budget={cfg["budget"]} rho={cfg["cost_ratio"]}', flush=True)
        for me in args.methods:
            out = Path(args.outdir) / me / 'cells'; out.mkdir(parents=True, exist_ok=True)
            sf = out / f'summary_{bn}_{me}_{tag}.csv'; tf = out / f'traj_{bn}_{me}_{tag}.csv'
            if sf.exists(): os.remove(sf)
            if tf.exists(): os.remove(tf)
            srows, trows = [], []
            for seed in args.seeds:
                t0 = time.time(); r = RUN[me](b, cfg, seed)
                srows.append(dict(benchmark=bn, model=me, seed=seed, final_regret=r['final_regret'], auc=r['auc'], n_hf=r['n_hf'], n_lf=r['n_lf'],
                                  pick_prec_top5=r['pick_prec_top5'], n_lf_on_hf=r['n_lf_on_hf'], n_hf_on_lf=r['n_hf_on_lf'], elapsed=round(time.time() - t0, 2)))
                trows += [dict(benchmark=bn, model=me, seed=seed, budget=bb, regret=rr) for bb, rr in zip(r['budgets'], r['regrets'])]
            _append(sf, srows); _append(tf, trows)
            d = pd.DataFrame(srows); print(f'  {me:14s} final {d.final_regret.mean():.4f} ± {d.final_regret.std(ddof=1)/np.sqrt(len(d)):.4f}  n_hf {sorted(d.n_hf.unique())} n_lf {sorted(d.n_lf.unique())}', flush=True)

if __name__ == '__main__':
    main()
