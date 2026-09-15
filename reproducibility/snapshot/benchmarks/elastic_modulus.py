#!/usr/bin/env python
"""MLIP-vs-DFT shear-modulus multi-fidelity benchmark (R^2 tuned by MLIP choice).

Fills the empty mid / very-low cells of the LF-HF-agreement (R^2) axis with a
NON-gap property. Built from a gen CSV produced by
experiments/matbench_budget_ext/mlip_elastic/gen_mlip_elastic.py on the l40s VM:
columns `formula, mlip_G, mlip_K, dft_G` (GPa).

* HF : DFT shear modulus G_VRH (matbench_log_gvrh; de Jong 2015 / Materials Project).
* LF : MLIP-predicted G_VRH (CHGNet -> low R^2, MatterSim/SevenNet -> mid R^2),
       same relaxed structure, ~1000x cheaper than DFT (genuine cheap/accurate).

Objective: MAXIMIZE shear modulus (find the stiffest material). Encoded for the
min-oriented frozen pipeline as HF = -G_VRH (negate handled by caller writing the
already-signed columns), OR log10 first if the raw tail is degenerate -- chosen
per the verify_elastic.py diagnostics and passed via OBJECTIVE_MODE.

Featurize: composition -> Magpie ElementProperty -> StandardScaler -> PCA(10),
identical to matbench_gap.py / jarvis_gap.py so the comparison isolates R^2.

    python -m benchmarks.elastic_modulus --gen mlip_elastic/chgnet_full.csv \
        --name elastic_chgnet --rho 0.001
"""
import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

from benchmarks import _common

# rho: an MLIP elastic prediction is ~1000x cheaper than a DFT elastic calc
# (Choudhary-style order-of-magnitude; MLIP ~1-3 s vs DFT hours). Default small.
DEFAULT_RHO = 0.001
OBJECTIVE = "maximize shear modulus G_VRH (MLIP LF / DFT HF); negate=True"


def _young(K, G):
    den = 3.0 * K + G
    return np.where(den > 0, 9.0 * K * G / den, np.nan)


def _lf_hf(gen, prop):
    """Return (LF, HF) modulus arrays in GPa for the chosen property."""
    mg, dg = gen["mlip_G"].to_numpy(float), gen["dft_G"].to_numpy(float)
    if prop == "shear":
        return mg, dg
    # bulk / young need DFT K (matbench_log_kvrh, row-aligned to gvrh by idx)
    from matminer.datasets import load_dataset
    dft_k_all = 10.0 ** load_dataset("matbench_log_kvrh")["log10(K_VRH)"].to_numpy(float)
    dk = dft_k_all[gen["idx"].to_numpy()]
    mk = gen["mlip_K"].to_numpy(float)
    if prop == "bulk":
        return mk, dk
    if prop == "young":
        return _young(mk, mg), _young(dk, dg)
    raise ValueError(prop)


def build(gen_csv, name, rho, objective_mode="log", floor=1e-3, subsample=0, seed=0,
          prop="shear"):
    gen = pd.read_csv(gen_csv).dropna(subset=["mlip_G", "dft_G"])
    if prop in ("bulk", "young"):
        gen = gen.dropna(subset=["mlip_K"])
    gen = gen.reset_index(drop=True)
    lf_raw, hf_raw = _lf_hf(gen, prop)
    keep = np.isfinite(lf_raw) & np.isfinite(hf_raw) & (lf_raw > 0) & (hf_raw > 0)
    gen = gen[keep].reset_index(drop=True)
    lf_raw, hf_raw = lf_raw[keep], hf_raw[keep]
    # subsample to match the gap-benchmark N (~3.5k) so the controlled (R^2)
    # comparison varies ONLY R^2, not N. Fixed seed -> reproducible pool.
    if subsample and len(gen) > subsample:
        idx = np.random.RandomState(seed).choice(len(gen), subsample, replace=False)
        gen = gen.iloc[idx].reset_index(drop=True)
        lf_raw, hf_raw = lf_raw[idx], hf_raw[idx]
        print(f"[{name}] subsampled to N={len(gen)} (seed={seed})", flush=True)

    # Objective: MAXIMIZE the modulus. matbench's native target is log10(modulus);
    # the log scale also broadens the (otherwise needle-like, heavy-tailed)
    # optimum cluster. maximize x -> minimize -x for the frozen pipeline.
    if objective_mode == "log":
        hf_raw = np.log10(np.clip(hf_raw, floor, None))
        lf_raw = np.log10(np.clip(lf_raw, floor, None))
    y_hf = -hf_raw
    y_lf = -lf_raw

    from matminer.featurizers.composition import ElementProperty
    from pymatgen.core import Composition
    ep = ElementProperty.from_preset("magpie")
    ep.set_n_jobs(1)
    print(f"[{name}] Magpie-featurizing {len(gen)} compositions ...", flush=True)
    comps = [Composition(f) for f in gen["formula"]]
    X_magpie = np.array(ep.featurize_many(comps, ignore_errors=True, pbar=False),
                        dtype=np.float64)
    X_pca = _common.matrix_to_pca(X_magpie)

    _common.save_cache(name, X_pca, y_hf, y_lf,
                       meta={"rho": rho, "negate": False, "objective": OBJECTIVE,
                             "objective_mode": objective_mode, "source": str(gen_csv),
                             "formula": gen["formula"].tolist()})
    _common.write_benchmark_csv(name, X_pca, y_hf, y_lf)
    _common.print_diagnostics(name, X_pca, y_hf, y_lf, rho, OBJECTIVE)
    return {"X_pca": X_pca, "y_hf": y_hf, "y_lf": y_lf}


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--gen", required=True, help="gen CSV (formula,mlip_G,mlip_K,dft_G)")
    ap.add_argument("--name", required=True, help="benchmark name -> data/<name>.csv")
    ap.add_argument("--rho", type=float, default=DEFAULT_RHO)
    ap.add_argument("--objective-mode", default="log", choices=["raw", "log"])
    ap.add_argument("--property", default="shear", choices=["shear", "bulk", "young"])
    ap.add_argument("--subsample", type=int, default=0, help="0 = keep all; else random N")
    ap.add_argument("--seed", type=int, default=0)
    a = ap.parse_args()
    build(a.gen, a.name, a.rho, a.objective_mode, subsample=a.subsample, seed=a.seed,
          prop=a.property)
