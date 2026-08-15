import json
from plotting import format_axes
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

plt.rcParams["font.family"] = "arial"

MATCH_ORDER = ["strict", "relaxed", "cosine"]

def load_metrics():
    metrics = {}

    for id in range(1, 12):
        with open(f"../../data/results/epis/biored_dev/epi_{id:03d}.json", "r") as f:
            data = json.load(f)
            epi_metrics = data["metrics"]

        metrics[f"epi_{id:03d}"] = epi_metrics

    return metrics

def latest_match_type(type_dict):
    """Return the most recent match type present for this entry."""
    for match_type in reversed(MATCH_ORDER):
        if match_type in type_dict:
            return match_type
    return None

def build_long_df(metrics, category):
    """category = "entity" or "relation"""
    rows = []
    for epi_id, epi_data in metrics.items():
        type_dict = epi_data.get(category, {})
        match_type = latest_match_type(type_dict)
        if match_type is None:
            continue
        scores = type_dict[match_type]
        for metric_name in ["precision", "recall", "f1"]:
            rows.append({
                "epi_id": epi_id,
                "match_type": match_type,
                "metric": metric_name,
                "value": scores[metric_name]
            })
    return pd.DataFrame(rows)

def metrics_dict(metrics):

    relation_df = build_long_df(metrics, "relation")
    entity_df = build_long_df(metrics, "entity")

    return {
        "relation": relation_df,
        "entity": entity_df
    }

def plot_performance_line(metrics, save: bool):

    relation_df = build_long_df(metrics, category="relation")
    entity_df = build_long_df(metrics, category="entity")

    dfs = (relation_df, entity_df)

    fig, axes = plt.subplots(
        2, 1,
        figsize=(11,9)
    )

    for df, ax in zip(dfs, axes):
        sns.lineplot(
            data=df,
            x="epi_id",
            y="value",
            ax=ax,
            hue="metric",
            style="metric",
            markers=True,
            dashes=True,
            linewidth=2,
            palette=["#9bafd9", "#103783", "#000000"]
        )

    axes[0].set_title("Relation", fontsize=18)
    axes[0].set_xlabel("")

    axes[1].set_title("Entity", fontsize=18)
    axes[1].set_xlabel("Extraction Pipeline Iteration", fontsize=18)

    for ax in axes:
        for spine in ("top", "right"):
            ax.spines[spine].set_visible(False)

        ax.grid(axis="y", color="black", alpha=0.2)

        ax.set_ylabel("Score", fontsize=18)
        ax.tick_params(labelrotation=35, axis="x")
        ax.tick_params(labelsize=13)
        ax.set_ylim(0, 1)

        for id, label in zip(("003",  "005", "006"), ("Relaxed evaluation", "Cosine evaluation", "Relation-order invariance")):
            ax.axvline(f"epi_{id}", color="black", alpha=0.5)

            ax.text(
                f"epi_{id}",
                0.3,
                label,
                transform=ax.get_xaxis_transform(),
                rotation=90,
                ha="right",
                va="center"
            )

    axes[0].legend().remove()
    axes[1].legend(title="Metric", title_fontsize=14, fontsize=14)

    plt.tight_layout()
    if save:
        fig.savefig("../../img/dev_analysis/epi_performance.png", dpi=150)

# def plot_relation_epis(metrics):
#     relation_df = build_long_df(metrics, category="relation")