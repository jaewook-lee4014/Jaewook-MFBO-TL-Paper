# Figure regeneration 2026-09-16 — Fig. 1 labels follow the "molecular and materials" wording

Label text only. The manuscript unified the phrase "chemistry and materials" into "molecular and materials",
and the two Fig. 1 images now match it:

- **Fig. 1 b--p** (`paper_figures/fig1_attainment.pdf`): the panel **p** title changes from `p  Chem & Mat` to
  `p  Mol & Mat`. The internal scope key `"9chem"` is unchanged, so the benchmark set, budgets, seed set,
  colours, sorting, axis limits and every plotted value are untouched.
- **Fig. 1 a** (`paper_figures/fig1_overview.pdf`): the three drawn labels reading `chemistry & materials`
  become `molecular & materials` (the schematic carries no data).

No run was repeated with different settings and no data path was touched. The regenerated
`fig1_attainment_values.csv` and both deficit summary CSVs are bit-identical to the copies already in
`reproducibility/values/figcand2_20260914_exact/` (section 3).

Fig. 1 b--p was rebuilt on the VM `l40s` with `/mnt/data/jaewook_mfbo/bo_env/bin/python`, root
`R = /mnt/data/jaewook_mfbo/MFBO-TL-Paper/experiments/refig_20260908`. The pre-edit script and PDF/PNG/SVG are
archived in `$R/_backup_molmat_20260916/` (with `md5_BEFORE.txt`).

## 1. Commands

### Fig. 1 b--p (VM `l40s`)

```bash
PY=/mnt/data/jaewook_mfbo/bo_env/bin/python
R=/mnt/data/jaewook_mfbo/MFBO-TL-Paper/experiments/refig_20260908
S=$R/figcand2_20260914_5tl/scripts/fig1_attainment_exact.py

mkdir -p $R/_backup_molmat_20260916
cp $S $R/figcand2_20260914_5tl/fig1_attainment.{pdf,png,svg} $R/_backup_molmat_20260916/
cd $R/_backup_molmat_20260916 && md5sum fig1_attainment_exact.py fig1_attainment.{pdf,png,svg} > md5_BEFORE.txt

# the single edit, line 136
sed -i '136s/"Chem & Mat"/"Mol \& Mat"/' $S

cd $R/figcand2_20260914_5tl/scripts && SUMMARY=deficit $PY fig1_attainment_exact.py
```

The whole edit, as `diff` against the backup:

```diff
136c136
< Mp = summary_panel(ax[14], letters[14], CHEM, "Chem & Mat", "9chem", ylab, bold=False)
---
> Mp = summary_panel(ax[14], letters[14], CHEM, "Mol & Mat", "9chem", ylab, bold=False)
```

Then, from the repository root:

```bash
scp l40s:$R/figcand2_20260914_5tl/fig1_attainment.pdf paper_figures/fig1_attainment.pdf
```

### Fig. 1 a (local, standalone TikZ)

```bash
# in paper_figures/fig1_overview.tex: chemistry \& materials -> molecular \& materials (3 drawn labels + 1 comment)
cp paper_figures/fig1_overview.tex /tmp/ovbuild/
cd /tmp/ovbuild && pdflatex -interaction=nonstopmode fig1_overview.tex
cp /tmp/ovbuild/fig1_overview.pdf paper_figures/fig1_overview.pdf
```

Built in a scratch directory so no `.aux`/`.log` lands in `paper_figures/`. The log reports no overfull or
underfull boxes, and a 300 dpi render confirms that `molecular` occupies the same width as `chemistry` in this
font: no label overflows or re-wraps.

## 2. Files changed

| File | Change |
| --- | --- |
| `paper_figures/fig1_attainment.pdf` | regenerated (panel p title) |
| `paper_figures/fig1_overview.tex`, `.pdf` | three drawn labels + header comment |
| `main.tex` line 108 | figure legend `(Chem \& Mat, …)` -> `(Mol \& Mat, …)` |
| `reproducibility/figure_manifest.csv` | md5 prefix + status for the `Fig. 1,a` and `Fig. 1,b-p` rows |
| `reproducibility/values/figcand2_20260914_exact/md5_outputs.txt` | new fig1_attainment pdf/png/svg md5s |
| `reproducibility/snapshot/refig_20260908/fig1_attainment.py` | same one-string change, line 109 |
| `reproducibility/snapshot/refig_20260908/figcand2_20260914_exact_scripts/fig1_attainment_exact.py` | same one-string change, line 109 |

The two snapshot scripts are older exports than the live VM script (87 and 102 differing lines), so they were
**not** overwritten with the VM copy; only the one label string was changed in place, leaving each snapshot a
faithful record of its own vintage.

## 3. md5 before / after

| File | Before | After |
| --- | --- | --- |
| `fig1_attainment.pdf` | `75ca3067830c23b521ade854686cb8a9` | `f964ecc4826d8c003953262901a75829` |
| `fig1_attainment.png` | `27478c0277e17115312fcfb213dd1ad3` | `c17a674a729abfec64ef2e4920819c82` |
| `fig1_attainment.svg` | `b15040a94d59fc3e0f78dee23a85abf8` | `4dee14d16c7e6388b2d5a401bf063d70` |
| `fig1_attainment_values.csv` | `648be30c64de32d74b57b771a5b45422` | `648be30c64de32d74b57b771a5b45422` (unchanged) |
| `fig1_attainment_summary_deficit.csv` | `a7dd3cd6d50cdb78f4f412ed80a6d309` | `a7dd3cd6d50cdb78f4f412ed80a6d309` (unchanged) |
| `fig1_attainment_summary_deficit_chem.csv` | `88d8ae68f5aad52936e72596da4a92b3` | `88d8ae68f5aad52936e72596da4a92b3` (unchanged) |
| `fig1_summary_deficit.csv` | `706be1246c6ceb7abf1869eb3fefa597` | `706be1246c6ceb7abf1869eb3fefa597` (unchanged) |
| `fig1_overview.pdf` | `20a7c214203b5a7db682de58c92b93a2` | `005c2a48fe6ecf9bf19945b5254123c0` |
| `fig1_attainment_exact.py` (VM) | `4bfe6052f78df5b68b3cbf5c113075fc` | `9f55315b6ca0cc2163e13408094c83c1` |
| `snapshot/…/fig1_attainment_exact.py` | `2c9b5d0f1183d691b2596c12af641bc5` | `ff7113c3078e2f2aaf181fdc44123fcd` |
| `snapshot/…/fig1_attainment.py` | `af67f0fd8b4ecbaa3c03ed8f64a1472e` | `6c7766c1c24f21b5b413f76f1fcd4ca6` |

The three value CSVs were regenerated by the run and came back byte-for-byte equal to the copies committed in
`reproducibility/values/figcand2_20260914_exact/`, which is the strongest available check that this change is
cosmetic.

> Note on a stale reference: the recipe for this edit quoted `55cdae422a9778388ec8b39acd489dfe` as the expected
> `fig1_attainment_values.csv` md5. That value was superseded on 2026-09-16 by the GP-base label rename, which
> rewrote only the `abbr` column (`REGEN_LABELS_GPBASE_20260916.md`, section 6); the current md5 is
> `648be30c64de32d74b57b771a5b45422`, matching both the VM output and the committed copy.
