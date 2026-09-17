# Figure regeneration 2026-09-17 — Fig. 2 y axes on h (HOPV15) and i (Matbench-gap) tightened to the data

Axis limits only. No run was executed, and no metric, budget, seed set, panel order, window, line style or data path was
touched. The values file is bit-identical to the 2026-09-17 line-style render (section 4).

Work was done on the VM `l40s` with `/mnt/data/jaewook_mfbo/bo_env/bin/python`, root
`R = /mnt/data/jaewook_mfbo/MFBO-TL-Paper/experiments/refig_20260908`. The pre-edit PDF/PNG/SVG, values csv and script
are archived in `$R/_backup_ylim_hi_20260917/` (`md5_BEFORE.txt`, `md5_AFTER.txt`).

## 1. Rule change

Before: every non-Park, non-large panel used `symlog(linthresh=1e-3)` with the bottom at 0, so panels h and i showed
four decades plus a zero floor while their mean ± s.e. bands occupy a fraction of that range.

| panel | band (min of mean − s.e., max of mean + s.e.) | axis before | axis after |
| --- | --- | --- | --- |
| h HOPV15 | 0.92 – 6.03 | symlog, 0 → 10^1 | linear, same rule as the four large pools (`ymin = min(mean_end) − 0.12·range`, ≈ 0.8 – 6.4) |
| i Matbench-gap | 0.041 – 1.21 | symlog, 0 → 10^0 | log, 0.03 – 1.5 (major ticks 10^-1, 10^0; minor ticks unlabelled) |

The other eleven panels are unchanged (a, b, e, f, g symlog to zero; c, d symlog with the 1e-9 floor; j–m linear).

## 2. Files edited

### VM `$R/figcand2_20260914_5tl/scripts/fig2_trajectories_exact.py` (md5 `75c6cdef` -> `82dc83a9`)
- `LINEAR = LARGE + ["HOPV15"]` and `YLOG = {"Matbench-Gap": (0.03, 1.5)}` added after `LARGE`.
- The per-panel axis block: `if p in LARGE` -> `if p in LINEAR`; new branch `elif p in YLOG: a.set_yscale("log"); a.set_ylim(*YLOG[p])`
  before the Park branch.
- Module docstring updated.

### Repository
- `paper_figures/fig2_trajectories.pdf` replaced (md5 `66d62d2b` -> `b897ac76`).
- `main.tex` Fig. 2 caption: `Regret axes are logarithmic, with zero shown at the floor. The panels for the four larger materials pools use linear axes because their regrets span about one decade or less.` ->
  `Regret axes are logarithmic, with zero shown at the floor, except on Matbench-gap (i), where no mean curve approaches zero and the axis is logarithmic without a zero floor. The panels for HOPV15 (h) and the four larger materials pools (j–m) use linear axes because their regrets span about one decade or less.`
- `reproducibility/figure_manifest.csv` Fig. 2 row (md5 prefix, status note).
- `reproducibility/snapshot/refig_20260908/figcand2_20260914_exact_scripts/fig2_trajectories_exact.py` refreshed to the VM
  script (md5 `82dc83a9`).

## 3. Command

```
cd $R
$PY figcand2_20260914_5tl/scripts/fig2_trajectories_exact.py
```

Per-pool seed counts printed by the script are unchanged (40/40 on every pool that prints).

## 4. md5

| file | before | after |
| --- | --- | --- |
| `fig2_trajectories.pdf` | `66d62d2b20fab3ed57ce2832796c14ea` | `b897ac764797b7bf8065d4cee8e22208` |
| `fig2_trajectories.png` | `9e71fee144c0bfc9442580ea79822812` | `ef6ba8ddbc0313aa9a6775f339887e8c` |
| `fig2_trajectories.svg` | `78d5367a5a42da22eeb64722ef4dba8d` | `0ca85a9cb06155347a2697925d06d074` |
| `fig2_trajectories_values.csv` | `97d733d9e1dfd4ac2a5029b3f2802af7` | `97d733d9e1dfd4ac2a5029b3f2802af7` (bit-identical) |

Page size 518.4 x 403.2 pt before and after.
