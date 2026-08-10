import pandas as pd
import matplotlib.pyplot as plt
from parsing import outputs_to_extractions, extractions_to_tuples

def plot_dist_comparison(epi_log, ground_truths, save=False) -> None:
    gt_relations = ground_truths["relations"]
    gt_relation_counts = pd.Series([r[2] for r in gt_relations]).value_counts()

    extractions, _ = outputs_to_extractions(epi_log["outputs"], confirmation=False)
    _, predictions_relations = extractions_to_tuples(extractions)

    extracted_relation_counts = pd.Series([r[2] for r in predictions_relations]).value_counts()

    # ---------- Plotting ----------
    plt.rcParams['font.family'] = 'arial'

    df = pd.concat(
        [gt_relation_counts.rename("Ground Truth"), extracted_relation_counts.rename("Extractions")],
        axis=1
    ).fillna(0)

    fig, ax = plt.subplots(
        figsize=(9,6)
    )

    plot_df = df.copy()
    plot_df["Ground Truth"] = -plot_df["Ground Truth"]

    plot_df[["Ground Truth", "Extractions"]].plot(
        kind="barh",
        stacked=True,
        ax=ax,
        color=["#103783", "#9bafd9"],
        edgecolor="black",
        linewidth=0.5
    )

    format_and_export(fig, ax, epi_log, save)

def format_and_export(fig, ax, epi_log, save):
    plt.axvline(0, color="black", alpha=0.5)
    plt.xlabel("Count")
    plt.ylabel("Relation Type")

    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)

    for spine in ("left", "bottom"):
        ax.spines[spine].set_linewidth(1.2)

    ax.set_ylabel("")
    ax.set_xlabel("Count", fontsize=16)
    ax.tick_params(labelsize=14, width=1.2)

    plt.tight_layout()
    if save:
        fig.savefig(f"../../img/{epi_log["epi_id"]}_relation_dist", dpi=150)