import json
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

plt.rcParams["font.family"] = "arial"

MATCH_ORDER = ["strict", "relaxed", "cosine"]
METRICS = ["precision", "recall", "f1"]

LINE_PALETTE = ["#1a1a1a", "#4d4d4d", "#999999"]
BAR_PALETTE = ["#1a1a1a", "#4d4d4d", "#bfbfbf"]
BAR_HATCHES = ["", "//", "xx"]

# (epi id suffix, label) for each point where the evaluation methodology changed
TRANSITIONS = (
    ("003", "Relaxed evaluation"),
    ("005", "Cosine evaluation"),
    ("006", "Relation-order invariance"),
)

EPI_RESULTS_DIR = Path("../../data/results/epis/biored_dev")
FIGURE_DIR = Path("../../img/dev_analysis")


def load_metrics(results_dir: Path = EPI_RESULTS_DIR, n_epis: int = 9) -> dict:
    """Load the `metrics` block from every epi_{n:03d}.json in `results_dir`."""
    metrics = {}
    for i in range(1, n_epis + 1):
        epi_id = f"epi_{i:03d}"
        with open(results_dir / f"{epi_id}.json") as f:
            metrics[epi_id] = json.load(f)["metrics"]
    return metrics


def _latest_match_type(type_dict: dict) -> str | None:
    """Return the most advanced match type present for this entry (cosine > relaxed > strict)."""
    for match_type in reversed(MATCH_ORDER):
        if match_type in type_dict:
            return match_type
    return None


def build_long_df(metrics: dict, category: str) -> pd.DataFrame:
    """Long-format precision/recall/f1 scores for one category ("entity" or "relation")."""
    rows = []
    for epi_id, epi_data in metrics.items():
        type_dict = epi_data.get(category, {})
        match_type = _latest_match_type(type_dict)
        if match_type is None:
            continue
        scores = type_dict[match_type]
        for metric_name in METRICS:
            rows.append({
                "epi_id": epi_id,
                "match_type": match_type,
                "metric": metric_name,
                "value": scores[metric_name]
            })
    return pd.DataFrame(rows)


def metrics_dict(metrics: dict) -> dict:
    """Build both long-format dataframes ({"entity": df, "relation": df}) in one call."""
    return {
        "entity": build_long_df(metrics, "entity"),
        "relation": build_long_df(metrics, "relation")
    }


def top_n_epis(long_df: pd.DataFrame, n: int = 3, by: str = "f1") -> pd.DataFrame:
    """
    Return the top-`n` epis by `by` metric, melted back to long format and
    ready for plotting. Replaces the inline pivot/sort/melt previously done
    by hand in the notebook.
    """
    wide = (
        long_df.pivot(index=["epi_id", "match_type"], columns="metric", values="value")
        .reset_index()
    )
    wide.columns.name = None

    top = wide.sort_values(by=by, ascending=False).head(n)

    return top.drop(columns="match_type").melt(id_vars="epi_id", var_name="metric")


def _style_axis(ax, ylabel="Score", xlabel=""):
    """Shared spine/grid/label styling used by every figure in this module."""
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)
    ax.grid(axis="y", color="black", alpha=0.2)
    ax.set_axisbelow(True)
    ax.set_ylabel(ylabel, fontsize=18)
    ax.set_xlabel(xlabel, fontsize=18)
    ax.tick_params(labelsize=13)


def _save_figure(fig, filename: str):
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)
    fig.savefig(FIGURE_DIR / filename, dpi=150)


def plot_performance_line(metrics: dict, save: bool = False) -> None:
    """Precision/recall/f1 across epi iterations, for both entity and relation extraction."""
    dfs = metrics_dict(metrics)

    fig, axes = plt.subplots(2, 1, figsize=(11, 9))

    for (category, df), ax in zip(dfs.items(), axes):
        sns.lineplot(
            data=df, x="epi_id", y="value", ax=ax,
            hue="metric", style="metric",
            markers=True, dashes=True, linewidth=2,
            palette=LINE_PALETTE
        )
        ax.set_title(category.capitalize(), fontsize=18)
        _style_axis(ax)
        ax.tick_params(labelrotation=35, axis="x")
        ax.set_ylim(0, 1)

        for epi_suffix, _ in TRANSITIONS:
            ax.axvline(f"epi_{epi_suffix}", color="black", alpha=0.5, linestyle="--", linewidth=1)

    axes[1].set_xlabel("Extraction Pipeline Iteration", fontsize=18)

    axes[0].legend().remove()
    axes[1].legend(title="Metric", title_fontsize=14, fontsize=14)

    plt.tight_layout()

    if save:
        _save_figure(fig, "epi_performance.png")


def plot_top_n_bar(
    long_df: pd.DataFrame,
    n: int = 3,
    by: str = "f1",
    ylim: tuple | None = None,
    save_as: str | None = None
) -> None:
    """Bar chart comparing the top-`n` epis (by `by` metric) across precision/recall/f1."""
    plot_df = top_n_epis(long_df, n=n, by=by)
    epi_order = sorted(plot_df["epi_id"].unique())

    fig, ax = plt.subplots(figsize=(9, 6))
    sns.barplot(
        data=plot_df, x="epi_id", y="value", hue="metric",
        order=epi_order,
        edgecolor="black", linewidth=0.5, palette=BAR_PALETTE, ax=ax
    )

    for hatch, container in zip(BAR_HATCHES, ax.containers):
        for bar in container:
            bar.set_hatch(hatch)
            bar.set_edgecolor("black")

    if ylim:
        ax.set_ylim(ylim)

    _style_axis(ax, xlabel="")
    ax.legend(title="Metric", title_fontsize=14, fontsize=14)

    fig.tight_layout()

    if save_as:
        _save_figure(fig, save_as)