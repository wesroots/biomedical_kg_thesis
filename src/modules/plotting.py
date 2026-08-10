import pandas as pd
import matplotlib.pyplot as plt
from parsing import outputs_to_extractions, extractions_to_tuples

ENTITY_TYPES = [
    "ChemicalEntity",
    "DiseaseOrPhenotypicFeature",
    "GeneOrGeneProduct",
    "SequenceVariant"
]

RELATION_TYPES = [
    "Association",
    "Bind",
    "Comparison",
    "Conversion",
    "Cotreatment",
    "Drug_Interaction",
    "Negative_Correlation",
    "Positive_Correlation"
]

def plot_dist_comparison(epi_log, ground_truths, save=False) -> None:
    gt_relations = ground_truths["relations"]
    gt_relation_counts = pd.Series([r[2] for r in gt_relations]).value_counts()

    gt_entities = ground_truths["entities"]
    gt_entity_counts = pd.Series([r[2] for r in gt_entities]).value_counts()

    extractions, ignore_val_counts = outputs_to_extractions(epi_log["outputs"], confirmation=False)
    entity_extractions, predictions_extractions = extractions_to_tuples(extractions)

    extracted_relation_counts = pd.Series([r[2] for r in predictions_extractions]).value_counts()
    extracted_entity_counts = pd.Series([r[2] for r in entity_extractions]).value_counts()

    # ---------- Plotting ----------
    plt.rcParams['font.family'] = 'arial'

    fig, axes = plt.subplots(
        2,1,
        figsize=(9,7)
    )

    for ext_counts,gt_counts, ax, label, categories in zip(
        (extracted_relation_counts, extracted_entity_counts),
        (gt_relation_counts, gt_entity_counts),
        axes,
        ("Relation", "Entity"),
        (RELATION_TYPES, ENTITY_TYPES)
        ):

        gt_counts = gt_counts.reindex(categories, fill_value=0).sort_values(ascending=False)
        ext_counts = ext_counts.reindex(categories, fill_value=0).sort_values(ascending=False)

        df = pd.concat(
            [gt_counts.rename("Ground Truth"), ext_counts.rename("Extractions")],
            axis=1
        ).fillna(0)

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

        max_count = plot_df.abs().to_numpy().max() * 1.1
        ax.set_xlim(-max_count, max_count)

        format_axes(ax, label)

    axes[1].get_legend().remove()

    plt.tight_layout()
    if save:
        save_path = f"../../img/extraction_sampling/{epi_log["epi_id"]}_gt_ext_dist.png"
        fig.savefig(save_path, dpi=100)
        print(f"Saved figure to `{save_path}` successfully.")

def format_axes(ax, label):
    ax.axvline(0, color="black", alpha=0.5)
    ax.set_xlabel("Count")
    ax.set_ylabel("Relation Type")

    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)

    for spine in ("left", "bottom"):
        ax.spines[spine].set_linewidth(1.2)

    ax.set_ylabel("")
    ax.set_xlabel(f"{label} Count", fontsize=14)
    ax.tick_params(labelsize=12, width=1.2)