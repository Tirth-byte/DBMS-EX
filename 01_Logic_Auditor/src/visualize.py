"""Create a restrained, honest comparison chart from measured results."""
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "results" / "benchmark_results.csv"
OUTPUT = ROOT / "results" / "performance_comparison.png"


def create_chart(input_path: Path = INPUT, output_path: Path = OUTPUT) -> None:
    data = pd.read_csv(input_path)
    scenarios = list(dict.fromkeys(data["scenario"]))
    short = ["ID lookup", "CGPA > 8.5", "Dept + sem", "Top 10", "Avg CGPA", "Dept count"]
    fig, axes = plt.subplots(2, 1, figsize=(12, 9), constrained_layout=True)
    fig.patch.set_facecolor("white")
    styles = [("CSV/Pandas", "#16B300"), ("SQLite", "#202428")]
    for ax, category in zip(axes, ["End-to-end", "Warm query"]):
        subset = data[data.category == category]
        x = np.arange(len(scenarios)); width = 0.36
        names = styles if category == "End-to-end" else [("Pandas", "#16B300"), ("SQLite", "#202428")]
        for offset, (system, colour) in zip([-width / 2, width / 2], names):
            ordered = subset.set_index("scenario").loc[scenarios]
            chosen = ordered[ordered.system == system]
            ax.bar(x + offset, chosen.median_ms, width, yerr=chosen.stddev_ms, label=system,
                   color=colour, capsize=3, error_kw={"elinewidth": 1, "ecolor": "#087D48"})
        ax.set_title(category, loc="left", color="#202428", fontweight="bold")
        ax.set_ylabel("Median elapsed time (ms)")
        ax.set_xticks(x, short)
        ax.set_ylim(bottom=0)
        ax.grid(axis="y", color="#E5E7E9", linewidth=0.8)
        ax.set_axisbelow(True); ax.spines[["top", "right"]].set_visible(False)
        ax.legend(frameon=False, ncol=2)
    fig.suptitle("CSV/Pandas vs SQLite retrieval performance", fontsize=17, fontweight="bold", color="#202428")
    fig.text(0.5, 0.001, "Bars show medians; error bars show sample standard deviation (30 measured runs).", ha="center", color="#4A5055")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=180, facecolor="white", bbox_inches="tight")
    plt.close(fig)
    print(f"Saved chart to {output_path.relative_to(ROOT)}")


if __name__ == "__main__":
    create_chart()

