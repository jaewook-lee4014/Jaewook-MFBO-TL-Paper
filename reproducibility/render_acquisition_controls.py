"""Render SI Fig. 1: GP-base and TL-base under EI and greedy LF selection.

Run from any directory with Python, pandas, numpy and matplotlib installed.
GP values retain the published 40-seed controls (39 for FreeSolv EI).
TL values use the 20-seed EI/greedy arms already underlying SI Fig. 2.
No model runs are generated or relabelled. The former j panel is omitted.
"""
from pathlib import Path
import json
import os

os.environ.setdefault("MPLCONFIGDIR", "/tmp/mfbo-acquisition-matplotlib")
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
VALUES = ROOT / "reproducibility/values/supp"
ARCHIVE = VALUES / "archive_20260917"
POOLS = ["Branin-Fav", "Branin-Unfav", "Park-Fav", "Park-Unfav", "COFs",
         "FreeSolv", "Polarizability", "HOPV15", "Matbench-Gap"]
CONDITIONS = ["GP-base EI", "GP-base greedy", "TL-base EI", "TL-base greedy"]


def main():
    previous = pd.read_csv(ARCHIVE / "supp_acq_matrix_values.csv")
    portfolio = pd.read_csv(VALUES / "supp_acq_portfolio_values.csv")
    rows = []
    for pool in POOLS:
        budget = int(previous.loc[previous.pool == pool, "budget"].iloc[0])
        for condition in CONDITIONS:
            model, policy = condition.split()
            if model == "GP-base":
                cell = previous[(previous.pool == pool) & (previous.condition == condition)]
            else:
                cell = portfolio[(portfolio.pool == pool) & (portfolio.model == model)
                                 & (portfolio.acq == policy.lower())]
            assert len(cell) == 1, (pool, condition)
            row = cell.iloc[0]
            rows.append(dict(pool=pool, condition=condition, mean=row["mean"],
                             se=row.se, n=int(row.n), budget=budget))
    values = pd.DataFrame(rows)
    assert len(values) == 36 and np.isfinite(values[["mean", "se"]]).all().all()
    values.to_csv(VALUES / "supp_acq_matrix_values.csv", index=False)

    # Preserve the other SI summaries and replace only the obsolete S1 content.
    summary = json.loads((VALUES / "supp_summary.json").read_text())
    summary["S1"] = {
        "conditions": CONDITIONS,
        "panels": "a-i; former panel j removed",
        "seeds": {"GP-base": "42-81 (FreeSolv EI: 39 successful runs)",
                  "TL-base": "42-61"},
        "values": {f"{r.pool}|{r.condition}": [float(r.mean), float(r.se), int(r.n)]
                   for r in values.itertuples()},
    }
    (VALUES / "supp_summary.json").write_text(json.dumps(summary, indent=1) + "\n")

    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 7,
                         "axes.linewidth": .5, "pdf.fonttype": 42,
                         "ps.fonttype": 42, "hatch.linewidth": .4})
    fig, axes = plt.subplots(3, 3, figsize=(7.2, 5.4))
    fig.subplots_adjust(left=.13, right=.985, top=.93, bottom=.12,
                        wspace=.92, hspace=.8)
    for i, (pool, ax) in enumerate(zip(POOLS, axes.flat)):
        data = values[values.pool == pool].set_index("condition")
        positions = np.arange(4)[::-1]
        for y, condition in zip(positions, CONDITIONS):
            row = data.loc[condition]
            color = "#f2aa84" if condition.startswith("GP") else "#4e95d9"
            hatch = "////" if condition.endswith("greedy") else None
            ax.barh(y, row["mean"], xerr=row.se, color=color, height=.7,
                    hatch=hatch, edgecolor="white" if hatch else "none",
                    linewidth=.4, error_kw=dict(lw=.5, capsize=1.5, ecolor="#333333"))
            ax.text(row["mean"] + row.se + .025, y, f'{row["mean"]:.2f}',
                    va="center", fontsize=5.7)
        ax.set_yticks(positions, CONDITIONS, fontsize=6)
        ax.set_xlim(0, 1.22)
        ax.set_xticks([0, .5, 1], ["0", "0.5", "1"])
        ax.tick_params(axis="y", length=0, pad=3)
        ax.tick_params(axis="x", labelsize=6, length=2, width=.5)
        ax.set_axisbelow(True)
        ax.grid(axis="x", alpha=.3, lw=.4)
        for side in ["top", "right"]:
            ax.spines[side].set_visible(False)
        label = pool.replace("Matbench-Gap", "Matbench-gap")
        ax.text(0, 1.2, f"{'abcdefghi'[i]}  {label}", transform=ax.transAxes, fontsize=7)
        gp_n = "39/40" if pool == "FreeSolv" else "40"
        ax.text(0, 1.04, f"B = {int(data.budget.iloc[0])} | n: GP {gp_n}, TL 20",
                transform=ax.transAxes, fontsize=5.4, color="#555555")
        if i >= 6:
            ax.set_xlabel("Attainment", fontsize=7)
    fig.text(.5, .028, "LF query: EI or greedy | HF query: greedy in all arms",
             ha="center", fontsize=7)
    output = ROOT / "paper_figures/supp_acq_matrix.pdf"
    fig.savefig(output, facecolor="white")
    plt.close(fig)
    print(f"Wrote {output}")


if __name__ == "__main__":
    main()
