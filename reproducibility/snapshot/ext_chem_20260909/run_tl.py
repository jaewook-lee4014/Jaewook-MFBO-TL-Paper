#!/usr/bin/env python
"""Figure-regeneration runner (2026-09-08): all eleven TL surrogates under per-fidelity
candidate masking with the improved HF head / LF query rule of the fairness ladder.

Arms (environment variables):
  HF_HEAD   mlp | mlp_small | blr_replace
            mlp        : paper's residual MLP (64 x 2); HF prediction = its output
            mlp_small  : residual MLP 16 x 1
            blr_replace: HF prediction = g_L(x) + Bayesian linear head on [g_L(x), phi_L(x), 1]
                         (residual MLP unused -> removes the over-parameterised HF head)
  LF_TARGET lf | hf_argmin | hf_ei | hf_pi | hf_ucb | hf_mes | hf_ts
            lf        : LF query = argmin LF-BLR mean (paper's greedy rule)
            hf_argmin : LF query = argmin mu_H (greedy on the HF prediction)
            hf_*      : LF query = UQ acquisition on (mu_H, sigma_H) with the HF incumbent
  WARM      0 | 1  warm-start the networks across refits (WARM_EPOCHS); Adapter: cold refit
  ACT       tanh | relu  (activation of all TL networks; Adapter handled explicitly)
HF step: argmin mu_H over candidates not yet HF-evaluated. Each fidelity masks only its own
evaluated candidates. Budgets, cost ratios, warm-up and round-robin as in the paper.
Calibration: LF ECE / NLL / sharpness on the unsampled pool at every refit, with EXACTLY
experiments/_shared_calibration.py (as uq_calib_rerun_20260702/run_uq.py).
Output: <outdir>/<arm>/cells/summary_<bench>_<model>_<tag>.csv and traj_... (per-seed rows).
"""
from __future__ import annotations
import argparse, os, sys, time, traceback
from pathlib import Path
import numpy as np, pandas as pd

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
sys.path.insert(0, str(REPO / 'src'))
sys.path.insert(0, str(HERE))   # local benchmark.py / pools.py / _shared_calibration.py
from _shared_calibration import ece_gaussian, nll_gaussian  # noqa: E402
import pools as POOLS  # noqa: E402


# ---- ext_chem_20260909: budget extension with pick logging and pick-replay resume ----
def _ext_budgets():
    d = {}
    for kv in os.environ.get('EXT_BUDGETS', '').split(','):
        if '=' in kv:
            k, v = kv.split('='); d[k.strip()] = float(v)
    return d
EXT_BUDGETS = _ext_budgets()

def _load_picks(bn, ml, seed, sub):
    """Find a picks_<bn>_<ml>_*.csv holding this seed under <root>/<sub>/cells for root in RESUME_DIRS."""
    import glob
    for root in os.environ.get('RESUME_DIRS', '').split(':'):
        if not root: continue
        for f in sorted(glob.glob(str(Path(root) / sub / 'cells' / f'picks_{bn}_{ml}_*.csv'))):
            try: df = pd.read_csv(f)
            except Exception: continue
            df = df[df.seed == seed]
            if len(df): return df.sort_values('step', kind='stable')
    return None

def _replay(picks_df, y_hf, f_star, pct, rho, lf_idx, hf_idx):
    """Rebuild the loop state from a pick log without any model fit.
    Log rows: fid in {L0,H0} = initial design (step 0), {L,H} = loop picks (step = it)."""
    lf_idx.clear(); hf_idx.clear()
    init = picks_df[picks_df.step == 0]; loop = picks_df[picks_df.step > 0]
    for r in init.itertuples():
        (lf_idx if r.fid == 'L0' else hf_idx).add(int(r.idx))
    cur = len(lf_idx) * rho + len(hf_idx) * 1.0; lfc = it = 0
    regrets = [float(max(0.0, y_hf[list(hf_idx)].min() - f_star))]; budgets = [cur]; picks = []
    for r in loop.itertuples():
        it += 1
        if r.fid == 'H':
            hf_idx.add(int(r.idx)); cur += 1.0; lfc = 0; picks.append(float(pct[int(r.idx)]))
        else:
            lf_idx.add(int(r.idx)); cur += rho; lfc += 1
        regrets.append(float(max(0.0, y_hf[list(hf_idx)].min() - f_star))); budgets.append(cur)
    return cur, lfc, it, regrets, budgets, picks

SEEDS = list(range(42, 62))
MODELS = ['Sequential', 'Curriculum', 'DNGOGradient', 'Progressive', 'TwoStageJoint', 'DNGOJoint',
          'KnowledgeDistillation', 'DomainAdaptationMMD', 'SoftParameterSharing', 'PseudoLabeling', 'Adapter']
HF_HEAD = os.environ.get('HF_HEAD', 'blr_replace')
LF_TARGET = os.environ.get('LF_TARGET', 'hf_argmin')
WARM = int(os.environ.get('WARM', '0'))
WARM_EPOCHS = int(os.environ.get('WARM_EPOCHS', '50'))
ACT = os.environ.get('ACT', 'tanh').lower()
os.environ['ACT'] = ACT          # benchmark.LFNetwork / HFNetwork read it at construction
SMALL = HF_HEAD == 'mlp_small'
assert HF_HEAD in ('mlp', 'mlp_small', 'blr_replace'), HF_HEAD
assert LF_TARGET in ('lf', 'hf_argmin', 'hf_ei', 'hf_pi', 'hf_ucb', 'hf_mes', 'hf_ts'), LF_TARGET
assert ACT in ('tanh', 'relu'), ACT
if LF_TARGET not in ('lf', 'hf_argmin'):
    assert HF_HEAD == 'blr_replace', 'UQ acquisitions on the HF prediction need the BLR head (sigma_H)'


# ----------------------------------------------------------------------------- BLR (as run_ladder.py)
def blr_fit(Z, y, alpha_vec, beta, ev_dims=None, grid=(10.0, 30.0, 100.0, 300.0, 1000.0)):
    Z = np.asarray(Z, float); y = np.asarray(y, float).ravel(); N, D = Z.shape
    alpha = np.asarray(alpha_vec, float).copy()
    ZtZ = Z.T @ Z; Zty = Z.T @ y
    def solve(alpha, beta):
        A = np.diag(alpha) + beta * ZtZ + 1e-9 * np.eye(D)
        S = np.linalg.pinv(A); m = beta * S @ Zty
        return m, S
    if ev_dims is not None and N >= 4:
        ev = np.asarray(ev_dims); best = None
        for lam in grid:
            a = alpha.copy(); a[ev] = lam
            m, S = solve(a, 1.0)
            Hm = Z @ S @ Z.T
            loo = (y - Z @ m) / np.maximum(1.0 - np.diag(Hm), 1e-3)
            mse = float(np.mean(loo ** 2))
            if best is None or mse < best[0]:
                best = (mse, lam)
        mse, lam = best
        beta = float(np.clip(1.0 / max(mse, 1e-6), 1.0, 100.0))
        alpha[ev] = lam * beta
        alpha[[i for i in range(D) if i not in set(ev.tolist())]] *= beta
    m, S = solve(alpha, beta)
    return m, S, alpha, beta


def blr_predict(Z, m, S, beta):
    mu = Z @ m
    var = 1.0 / beta + np.einsum('ij,jk,ik->i', Z, S, Z)
    return mu, np.sqrt(np.maximum(var, 1e-12))


def _lf_out_and_phi(model, Xt):
    """(g_L(x), phi_L(x)) in standardized units for any of the eleven TL surrogates."""
    import torch
    if hasattr(model, 'lf_net'):
        model.lf_net.eval()
        with torch.no_grad():
            return model.lf_net(Xt).cpu().numpy(), model.lf_net.extract_features(Xt).cpu().numpy()
    # Adapter: LF backbone + LF output layer
    model.backbone.eval()
    with torch.no_grad():
        phi = model.backbone(Xt)
        return model.out_layer(phi).cpu().numpy(), phi.cpu().numpy()


class Head:
    """(mu_H, sigma_H) in raw y units for a fitted TL model."""
    def __init__(self, model, X_hf, y_hf):
        import torch
        self.model = model; self.kind = HF_HEAD
        if self.kind != 'blr_replace':
            return
        Xs = model.scaler_x.transform(X_hf); ys = model.scaler_y.transform(np.asarray(y_hf).reshape(-1, 1)).ravel()
        Xt = torch.FloatTensor(Xs).to(model.device)
        lo, phi = _lf_out_and_phi(model, Xt)
        Z = np.hstack([lo, phi, np.ones((len(Xs), 1))])
        D = Z.shape[1]; alpha = np.full(D, 100.0); alpha[0] = 10.0; alpha[-1] = 1.0
        self.m, self.S, self.alpha, self.beta = blr_fit(Z, ys - lo.ravel(), alpha, 10.0, ev_dims=np.arange(1, D - 1))

    def predict(self, X):
        import torch
        model = self.model
        if self.kind != 'blr_replace':
            mu, _ = model.predict(X); return np.asarray(mu, float), None
        Xs = model.scaler_x.transform(X); Xt = torch.FloatTensor(Xs).to(model.device)
        lo, phi = _lf_out_and_phi(model, Xt)
        Z = np.hstack([lo, phi, np.ones((len(Xs), 1))])
        d_s, sd_s = blr_predict(Z, self.m, self.S, self.beta)
        mu_s = lo.ravel() + d_s
        scale = float(model.scaler_y.scale_[0])
        mu = model.scaler_y.inverse_transform(mu_s.reshape(-1, 1)).ravel()
        return mu, np.maximum(sd_s * scale, 1e-9)


# ----------------------------------------------------------------------------- warm start (as run_ladder.py)
def warm_fit(model, name, X_lf, y_lf, X_hf, y_hf):
    import torch, torch.nn.functional as F
    Xa = np.vstack([X_lf, X_hf]); ya = np.concatenate([np.ravel(y_lf), np.ravel(y_hf)])
    Xs = model.scaler_x.fit_transform(Xa); ys = model.scaler_y.fit_transform(ya.reshape(-1, 1)).ravel()
    nl = len(X_lf)
    Xl = torch.FloatTensor(Xs[:nl]).to(model.device); yl = torch.FloatTensor(ys[:nl]).view(-1, 1).to(model.device)
    Xh = torch.FloatTensor(Xs[nl:]).to(model.device); yh = torch.FloatTensor(ys[nl:]).view(-1, 1).to(model.device)
    E = WARM_EPOCHS
    if name in ('DNGOGradient', 'DNGOJoint', 'TwoStageJoint', 'SoftParameterSharing'):
        for p in model.lf_net.parameters(): p.requires_grad = True
        for p in model.hf_net.parameters(): p.requires_grad = True
        opt = torch.optim.Adam([{'params': model.lf_net.parameters(), 'lr': 1e-3},
                                {'params': model.hf_net.parameters(), 'lr': 5e-4}], weight_decay=1e-4)
        model.lf_net.train(); model.hf_net.train()
        for _ in range(E):
            opt.zero_grad()
            loss = F.mse_loss(model.lf_net(Xl), yl) + F.mse_loss(model.hf_net(Xh, model.lf_net(Xh)), yh)
            loss.backward(); opt.step()
        model._fit_lf_blr(Xl, ys[:nl]); model.is_fitted = True; return
    for p in model.lf_net.parameters(): p.requires_grad = True
    model.lf_net.train()
    opt = torch.optim.Adam(model.lf_net.parameters(), lr=1e-3, weight_decay=1e-4)
    for _ in range(E):
        opt.zero_grad(); F.mse_loss(model.lf_net(Xl), yl).backward(); opt.step()
    model._fit_lf_blr(Xl, ys[:nl])
    for p in model.lf_net.parameters(): p.requires_grad = False
    for p in model.hf_net.parameters(): p.requires_grad = True
    model.hf_net.train()
    opt = torch.optim.Adam(model.hf_net.parameters(), lr=1e-3, weight_decay=1e-4)
    nh = len(Xh)
    for e in range(E):
        if name == 'Curriculum':
            n_use = min(nh, max(2, int((e + 1) / E * nh))); idx = torch.arange(n_use)
        else:
            idx = torch.arange(nh)
        opt.zero_grad()
        with torch.no_grad():
            ylp = model.lf_net(Xh[idx])
        F.mse_loss(model.hf_net(Xh[idx], ylp), yh[idx]).backward(); opt.step()
    model.is_fitted = True


# ----------------------------------------------------------------------------- loop
def fps(X, n, seed):
    from scipy.spatial.distance import cdist
    rng = np.random.RandomState(seed)
    sel = [int(rng.randint(len(X)))]
    mind = cdist(X, X[sel]).min(axis=1); mind[sel] = -np.inf
    for _ in range(n - 1):
        nx = int(np.argmax(mind)); sel.append(nx)
        mind = np.minimum(mind, np.linalg.norm(X - X[nx], axis=1)); mind[nx] = -np.inf
    return np.array(sel)


_RELU_ADAPTER = None
def _cls(name):
    import benchmark as B
    if name == 'Adapter' and ACT == 'relu':
        global _RELU_ADAPTER
        if _RELU_ADAPTER is None:
            import torch, torch.nn as nn, torch.nn.functional as F
            class AdapterReLU(B.Adapter):
                """benchmark.Adapter with a ReLU backbone; adapters inserted after each ReLU
                (the frozen class hard-codes nn.Tanh and isinstance(module, nn.Tanh))."""
                def fit(self, X_lf, y_lf, X_hf, y_hf):
                    X_all = np.vstack([X_lf, X_hf]); y_all = np.concatenate([y_lf.flatten(), y_hf.flatten()])
                    X_scaled = self.scaler_x.fit_transform(X_all); y_scaled = self.scaler_y.fit_transform(y_all.reshape(-1, 1)).flatten()
                    X_lf_s, X_hf_s = X_scaled[:len(X_lf)], X_scaled[len(X_lf):]
                    y_lf_s, y_hf_s = y_scaled[:len(y_lf)], y_scaled[len(y_lf):]
                    X_lf_t = torch.FloatTensor(X_lf_s).to(self.device); y_lf_t = torch.FloatTensor(y_lf_s).view(-1, 1).to(self.device)
                    X_hf_t = torch.FloatTensor(X_hf_s).to(self.device); y_hf_t = torch.FloatTensor(y_hf_s).view(-1, 1).to(self.device)
                    self.backbone = nn.Sequential(nn.Linear(self.input_dim, self.hidden_dim), nn.ReLU(),
                                                  nn.Linear(self.hidden_dim, self.hidden_dim), nn.ReLU()).to(self.device)
                    self.out_layer = nn.Linear(self.hidden_dim, 1).to(self.device)
                    self.adapters = nn.ModuleList([B.AdapterLayer(self.hidden_dim, self.bottleneck_dim) for _ in range(2)]).to(self.device)
                    self.hf_out = nn.Linear(self.hidden_dim, 1).to(self.device)
                    opt = torch.optim.Adam(list(self.backbone.parameters()) + list(self.out_layer.parameters()), lr=1e-3)
                    for _ in range(self.lf_epochs):
                        opt.zero_grad(); F.mse_loss(self.out_layer(self.backbone(X_lf_t)), y_lf_t).backward(); opt.step()
                    self.backbone.eval()
                    with torch.no_grad():
                        features = self.backbone(X_lf_t).cpu().numpy()
                    self.lf_blr = B.BayesianLinearRegression(alpha=1.0, beta=1.0); self.lf_blr.fit(features, y_lf_s); self.has_lf_blr = True
                    for p in self.backbone.parameters(): p.requires_grad = False
                    for p in self.out_layer.parameters(): p.requires_grad = False
                    opt = torch.optim.Adam(list(self.adapters.parameters()) + list(self.hf_out.parameters()), lr=1e-3)
                    for _ in range(self.adapter_epochs):
                        opt.zero_grad(); h = X_hf_t; ai = 0
                        for module in self.backbone:
                            h = module(h)
                            if isinstance(module, nn.ReLU) and ai < len(self.adapters):
                                h = self.adapters[ai](h); ai += 1
                        F.mse_loss(self.hf_out(h), y_hf_t).backward(); opt.step()
                    self.is_fitted = True
                def predict(self, X):
                    X_t = torch.FloatTensor(self.scaler_x.transform(X)).to(self.device); self.backbone.eval()
                    with torch.no_grad():
                        h = X_t; ai = 0
                        for module in self.backbone:
                            h = module(h)
                            if isinstance(module, nn.ReLU) and ai < len(self.adapters):
                                h = self.adapters[ai](h); ai += 1
                        mean_s = self.hf_out(h).cpu().numpy().flatten()
                    mean = self.scaler_y.inverse_transform(mean_s.reshape(-1, 1)).flatten()
                    return mean, np.ones_like(mean) * 0.1
            _RELU_ADAPTER = AdapterReLU
        return _RELU_ADAPTER
    return {'Sequential': B.Sequential, 'Curriculum': B.Curriculum, 'DNGOGradient': B.DNGOGradient,
            'Progressive': B.Progressive, 'TwoStageJoint': B.TwoStageJoint, 'DNGOJoint': B.DNGOJoint,
            'KnowledgeDistillation': B.KnowledgeDistillation, 'DomainAdaptationMMD': B.DomainAdaptationMMD,
            'SoftParameterSharing': B.SoftParameterSharing, 'PseudoLabeling': B.PseudoLabeling,
            'Adapter': B.Adapter}[name]


def run_one(bench, cfg, model_name, seed, device):
    import torch
    import benchmark as B
    from benchmark import (expected_improvement, probability_of_improvement, lower_confidence_bound,
                           max_value_entropy_search, thompson_sample)
    if SMALL and not hasattr(B, '_OrigHFNetwork'):
        B._OrigHFNetwork = B.HFNetwork
        B.HFNetwork = lambda input_dim, hidden_dim=64, num_layers=2: B._OrigHFNetwork(input_dim, 16, num_layers=1)
    cls = _cls(model_name)
    np.random.seed(seed); torch.manual_seed(seed)
    acq_rng = np.random.default_rng(seed)
    X, y_hf, y_lf = bench.X, bench.y_hf, bench.y_lf
    rho = bench.cost_ratio; budget = float(EXT_BUDGETS.get(cfg['_name'], cfg['budget']))
    pct = (np.argsort(np.argsort(y_hf)) + 1) / bench.n_candidates
    init_budget = float(cfg.get('init_budget', os.environ.get('INIT_BUDGET', cfg['budget'])))   # init from the ORIGINAL budget
    n_init_lf = max(2, int(0.1 * init_budget * 0.5 / rho)); n_init_hf = max(2, int(0.1 * init_budget * 0.5))
    init = fps(X, n_init_lf + n_init_hf, seed)
    lf_idx = set(int(i) for i in init[:n_init_lf]); hf_idx = set(int(i) for i in init[n_init_lf:n_init_lf + n_init_hf])
    cur = len(lf_idx) * rho + len(hf_idx) * 1.0
    lf_per_hf = max(1, int(1.0 / rho)); lfc = it = 0
    regrets = [float(max(0.0, y_hf[list(hf_idx)].min() - bench.f_star))]; budgets = [cur]; picks = []
    cal = []; model = None
    plog = [dict(step=0, fid='L0', idx=int(i), budget=cur) for i in init[:n_init_lf]] + [dict(step=0, fid='H0', idx=int(i), budget=cur) for i in init[n_init_lf:n_init_lf + n_init_hf]]
    resumed_from = np.nan
    pk = _load_picks(cfg['_name'], model_name, seed, arm_name())
    if pk is not None:
        cur, lfc, it, regrets, budgets, picks = _replay(pk, y_hf, bench.f_star, pct, rho, lf_idx, hf_idx)
        plog = [dict(step=int(r.step), fid=r.fid, idx=int(r.idx), budget=float(r.budget)) for r in pk.itertuples()]
        resumed_from = cur; print(f'  [resume] {cfg["_name"]} {model_name} s{seed}: replayed {it} picks to budget {cur:.3f}', flush=True)
        import pickle
        for root in os.environ.get('RESUME_DIRS', '').split(':'):
            rf = Path(root) / arm_name() / 'cells' / f'rng_{cfg["_name"]}_{model_name}_s{seed}.pkl'
            if root and rf.exists():
                st = pickle.load(open(rf, 'rb')); np.random.set_state(st['np']); torch.set_rng_state(st['torch']); acq_rng.bit_generator.state = st['acq']
                print(f'  [resume] RNG state restored from {rf.name}', flush=True); break
    max_it = int(budget / rho) + 1000; fit_failed_at = np.nan
    while cur < budget and it < max_it:
        it += 1
        rem = budget - cur
        if rem >= 1.0:
            eval_hf = not (rem >= rho and lfc < lf_per_hf)
        elif rem >= rho:
            eval_hf = False
        else:
            break
        L = np.array(sorted(lf_idx)); Hh = np.array(sorted(hf_idx))
        if WARM and model is not None and hasattr(model, 'lf_net'):
            warm_fit(model, model_name, X[L], y_lf[L], X[Hh], y_hf[Hh])
        else:
            model = cls(X.shape[1], device=device)
            try: model.fit(X[L], y_lf[L], X[Hh], y_hf[Hh])
            except Exception as e:
                fit_failed_at = cur; print(f'  [fit-fail] budget {cur:.3f}: {type(e).__name__}', flush=True); break
        head = Head(model, X[Hh], y_hf[Hh])
        mu_H, sd_H = head.predict(X)
        # ---- LF predictive over the pool: calibration (every refit) + paper LF rule ----
        lf_mean, lf_std = model.predict_lf(X)
        lf_mean = np.asarray(lf_mean, float); lf_std = np.asarray(lf_std, float)
        held = np.setdiff1d(np.arange(bench.n_candidates), np.array(sorted(lf_idx | hf_idx)))
        if len(held) >= 5:
            mh, sh = lf_mean[held], lf_std[held]
            cal.append((float(ece_gaussian(y_lf[held], mh, sh)), float(nll_gaussian(y_lf[held], mh, sh)), float(np.mean(sh))))
        if eval_hf:
            mm = mu_H.copy(); mm[list(hf_idx)] = np.inf
            nxt = int(np.argmin(mm)); hf_idx.add(nxt); cur += 1.0; lfc = 0; picks.append(float(pct[nxt])); plog.append(dict(step=it, fid='H', idx=nxt, budget=cur))
        else:
            ybest = float(y_hf[list(hf_idx)].min())
            if LF_TARGET == 'lf':
                acq = -lf_mean
            elif LF_TARGET == 'hf_argmin':
                acq = -mu_H
            elif LF_TARGET == 'hf_ei':
                acq = expected_improvement(mu_H, sd_H, ybest)
            elif LF_TARGET == 'hf_pi':
                acq = probability_of_improvement(mu_H, sd_H, ybest)
            elif LF_TARGET == 'hf_ucb':
                acq = lower_confidence_bound(mu_H, sd_H)
            elif LF_TARGET == 'hf_mes':
                acq = max_value_entropy_search(mu_H, sd_H, acq_rng)
            elif LF_TARGET == 'hf_ts':
                acq = thompson_sample(mu_H, sd_H, acq_rng)
            acq = np.asarray(acq, float).copy(); acq[list(lf_idx)] = -np.inf
            nxt = int(np.argmax(acq)); lf_idx.add(nxt); cur += rho; lfc += 1; plog.append(dict(step=it, fid='L', idx=nxt, budget=cur))
        regrets.append(float(max(0.0, y_hf[list(hf_idx)].min() - bench.f_star))); budgets.append(cur)
    tr = np.trapezoid if hasattr(np, 'trapezoid') else np.trapz
    auc = float(tr(regrets, budgets) / max(budgets[-1] - budgets[0], 1e-9))
    if cal:
        ece_m, nll_m, sh_m = (float(np.mean([c[i] for c in cal])) for i in range(3)); ece_f, nll_f, sh_f = cal[-1]
    else:
        ece_m = nll_m = sh_m = ece_f = nll_f = sh_f = np.nan
    rng_state = dict(np=np.random.get_state(), torch=torch.get_rng_state(), acq=acq_rng.bit_generator.state)
    return dict(final_regret=regrets[-1], auc=auc, n_hf=len(hf_idx), n_lf=len(lf_idx), rng_state=rng_state,
                pick_prec_top5=float(np.mean([p <= 0.05 + 1e-12 for p in picks])) if picks else np.nan,
                budgets=budgets, regrets=regrets, plog=plog, resumed_from=resumed_from, budget_used=budget, fit_failed_at=fit_failed_at,
                ece_lf_mean=ece_m, nll_lf_mean=nll_m, sharp_lf_mean=sh_m,
                ece_lf_final=ece_f, nll_lf_final=nll_f, sharp_lf_final=sh_f)


def _append(path, rows):
    df = pd.DataFrame(rows)
    if path.exists():
        df = pd.concat([pd.read_csv(path), df], ignore_index=True)
    tmp = path.with_suffix(path.suffix + '.tmp'); df.to_csv(tmp, index=False); os.replace(tmp, path)


def arm_name():
    return f'{HF_HEAD}__{LF_TARGET}' + ('__warm' if WARM else '') + ('__relu' if ACT == 'relu' else '')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--benches', nargs='*', default=list(POOLS.PAPER))
    ap.add_argument('--models', nargs='*', default=MODELS)
    ap.add_argument('--seeds', type=int, nargs='*', default=SEEDS)
    ap.add_argument('--outdir', default=str(HERE / 'results'))
    args = ap.parse_args()
    import torch
    dev = torch.device(os.environ.get('TL_DEVICE', 'cpu')); torch.set_num_threads(int(os.environ.get('TORCH_THREADS', '1')))   # TL_DEVICE=cuda only for the GPU timing test
    arm = arm_name()
    out = Path(args.outdir) / arm; (out / 'cells').mkdir(parents=True, exist_ok=True)
    print(f'refig | arm={arm} benches={args.benches} models={args.models} seeds={args.seeds}', flush=True)
    tag = f's{min(args.seeds)}-{max(args.seeds)}' if len(args.seeds) > 1 else f's{args.seeds[0]}'
    for bn in args.benches:
        b, cfg = POOLS.make_bench(bn, REPO / 'data'); cfg = dict(cfg); cfg['_name'] = bn
        print(f'{bn}: N={b.n_candidates} dim={b.dim} budget={cfg["budget"]} ext_budget={EXT_BUDGETS.get(bn, cfg["budget"])} rho={cfg["cost_ratio"]}', flush=True)
        for ml in args.models:
            sf = out / 'cells' / f'summary_{bn}_{ml}_{tag}.csv'; tf = out / 'cells' / f'traj_{bn}_{ml}_{tag}.csv'; pf = out / 'cells' / f'picks_{bn}_{ml}_{tag}.csv'
            done = set(pd.read_csv(sf)['seed'].tolist()) if sf.exists() else set()
            for root in os.environ.get('SKIP_DIRS', '').split(':'):   # seeds finished elsewhere (e.g. SLURM copies)
                f2 = Path(root) / arm / 'cells' / sf.name
                if root and f2.exists():
                    try: done |= set(pd.read_csv(f2)['seed'].tolist())
                    except Exception: pass
            for seed in args.seeds:
                if seed in done:
                    continue
                t0 = time.time()
                try:
                    r = run_one(b, cfg, ml, seed, dev)
                except Exception:
                    print(f'[FAIL] {bn} {ml} s{seed}', flush=True); traceback.print_exc(); continue
                _append(sf, [dict(benchmark=bn, model=ml, seed=seed, final_regret=r['final_regret'], auc=r['auc'],
                                  n_hf=r['n_hf'], n_lf=r['n_lf'], pick_prec_top5=r['pick_prec_top5'],
                                  ece_lf_mean=r['ece_lf_mean'], nll_lf_mean=r['nll_lf_mean'], sharp_lf_mean=r['sharp_lf_mean'],
                                  ece_lf_final=r['ece_lf_final'], nll_lf_final=r['nll_lf_final'], sharp_lf_final=r['sharp_lf_final'],
                                  elapsed=round(time.time() - t0, 1), hf_head=HF_HEAD, lf_target=LF_TARGET, warm=WARM, act=ACT,
                                  budget_used=r['budget_used'], resumed_from=r['resumed_from'], fit_failed_at=r['fit_failed_at'])])
                _append(pf, [dict(benchmark=bn, model=ml, seed=seed, **p) for p in r['plog']])
                import pickle; pickle.dump(r['rng_state'], open(out / 'cells' / f'rng_{bn}_{ml}_s{seed}.pkl', 'wb'))
                _append(tf, [dict(benchmark=bn, model=ml, seed=seed, budget=bb, regret=rr) for bb, rr in zip(r['budgets'], r['regrets'])])
                print(f'{bn} {ml} s{seed}: final={r["final_regret"]:.4f} auc={r["auc"]:.4f} ece={r["ece_lf_mean"]:.3f} ({time.time()-t0:.0f}s)', flush=True)


if __name__ == '__main__':
    main()
