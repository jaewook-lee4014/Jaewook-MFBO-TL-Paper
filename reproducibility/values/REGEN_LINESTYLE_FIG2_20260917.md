# Figure regeneration 2026-09-17 — Fig. 2 line styles: the base surrogate of each family solid, the variants dashed

Styling only. No run was executed, and no metric, budget, seed set, panel order, window or data path was touched.
The values file is bit-identical to the 2026-09-16 render (section 4).

Work was done on the VM `l40s` with `/mnt/data/jaewook_mfbo/bo_env/bin/python`, root
`R = /mnt/data/jaewook_mfbo/MFBO-TL-Paper/experiments/refig_20260908`. The pre-edit PDF/PNG/SVG, values csv and script
are archived in `$R/_backup_linestyle_20260917/` (`md5_BEFORE.txt`, `md5_AFTER.txt`); the 110 dpi render used for the
layout check is in `$R/_backup_linestyle_20260917/render/`.

## 1. Rule change

Before (2026-09-14 to 2026-09-16): the three GP surrogates solid (oranges, lw 1.35), the five TL surrogates dashed or dotted
(blues, lw 1.0). Legend title `GP family (solid)`.

After: the base surrogate of each family is solid in the darkest shade of its hue at lw 1.35; the six variants are dashed or
dotted at lw 1.0. Legend title `GP family`. The first footnote line gains
`Solid lines: GP-base and TL-base; dashed or dotted: the other surrogates.`

| label | colour before | style before | colour after | style after |
| --- | --- | --- | --- | --- |
| GP-base | `#b5532e` | solid 1.35 | `#b5532e` | solid 1.35 (unchanged) |
| GP-SV | `#f2aa84` | solid 1.35 | `#f2aa84` | dotted (1.2, 1.2) 1.0 |
| GP-DKL | `#e07b4f` | solid 1.35 | `#e07b4f` | dashed (4, 1.5) 1.0 |
| TL-base | `#4e95d9` | dotted 1.0 | `#0b3d7a` | solid 1.35 |
| TL-PtJ | `#0b3d7a` | dashed 1.0 | `#2467b3` | dashed (4, 1.5) 1.0 |
| TL-E2E | `#2467b3` | dashed 1.0 | `#4e95d9` | dashed (4, 1.5) 1.0 |
| TL-SPS | `#8fc0ec` | dotted 1.0 | `#8fc0ec` | dotted (1.2, 1.2) 1.0 (unchanged) |
| TL-MMD | `#8fc0ec` | dashed 1.0 | `#8fc0ec` | dashed (4, 1.5) 1.0 (unchanged) |

The three TL blues are the same three hex values as before, rotated so that the darkest (`#0b3d7a`) goes to TL-base.

## 2. Files edited

### VM `$R/figcand2_20260914_5tl/scripts/fig2_trajectories_exact.py` (md5 `98e1b45d` -> `75c6cdef`)
- `STYLE` dict as in the table above; comment lines above it and the module docstring updated.
- `ax[13].legend(... title="GP family (solid)")` -> `title="GP family"`.
- `FOOTNOTE[0]` extended with the solid/dashed key.

### Repository
- `paper_figures/fig2_trajectories.pdf` replaced (md5 `22509c7e` -> `66d62d2b`).
- `main.tex` Fig. 2 caption: `The GP family uses solid orange lines, and TL surrogates use dashed and dotted blue lines.` ->
  `Orange denotes the GP family and blue denotes TL surrogates. GP-base and TL-base are drawn as solid lines, and the other six surrogates as dashed or dotted lines.`
- `reproducibility/figure_manifest.csv` Fig. 2 row (md5 prefix, generated date, status note).
- `reproducibility/snapshot/refig_20260908/figcand2_20260914_exact_scripts/fig2_trajectories_exact.py` refreshed to the VM
  script (the snapshot had not been refreshed since the 2026-09-14 render; it now matches the VM file, md5 `75c6cdef`).

## 3. Command

```
cd $R
$PY figcand2_20260914_5tl/scripts/fig2_trajectories_exact.py
```

Per-pool seed counts printed by the script are unchanged (40/40 on every pool that prints).

## 4. md5

| file | before | after |
| --- | --- | --- |
| `fig2_trajectories.pdf` | `22509c7e1bd118621406d63e6eff20c4` | `66d62d2b20fab3ed57ce2832796c14ea` |
| `fig2_trajectories.png` | `5fc2f60230fb15383102ea9b4b05b868` | `9e71fee144c0bfc9442580ea79822812` |
| `fig2_trajectories.svg` | `10c6501c846d38baec8c1b1a3fdab72d` | `78d5367a5a42da22eeb64722ef4dba8d` |
| `fig2_trajectories_values.csv` | `97d733d9e1dfd4ac2a5029b3f2802af7` | `97d733d9e1dfd4ac2a5029b3f2802af7` (bit-identical) |

Page size 518.4 x 403.2 pt before and after. The footnote's first line (the longest) stays inside the 7.2 in width at 6.5 pt
(checked on the 110 dpi render).

## 5. Not changed

Other figures that draw the GP family solid and the TL surrogates dashed (the `figrepo/figures/make_regret_trajectory*.py`
family and `prep_candidates2.py`'s trajectory panels) are not part of the manuscript and were left as they are.
