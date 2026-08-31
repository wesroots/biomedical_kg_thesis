import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

from IPython.display import display

sns.set_theme(style="white")

def plot_distribution_comparison(
    gt_entities, pred_entities,
    gt_relations, pred_relations,
    gt_entity_col="entity_type", pred_entity_col="type",
    gt_relation_col="relation", pred_relation_col="relation",
    figsize=(9, 8)
):
    # Greyscale palette: dark grey = Ground Truth, light grey = Extractions
    palette = {"Ground Truth": "#404040", "Extractions": "#b0b0b0"}

    fig, (ax_rel, ax_ent) = plt.subplots(2, 1, figsize=figsize)

    def _to_long(gt_series, pred_series):
        gt_counts = gt_series.value_counts()
        pred_counts = pred_series.value_counts()

        # union of labels, sorted by combined frequency (ascending -> biggest on top)
        labels = (gt_counts.add(pred_counts, fill_value=0)).sort_values().index

        gt_vals = gt_counts.reindex(labels, fill_value=0)
        pred_vals = pred_counts.reindex(labels, fill_value=0)

        df = pd.DataFrame({
            "label": list(labels) * 2,
            "count": np.concatenate([-gt_vals.values, pred_vals.values]),
            "source": ["Ground Truth"] * len(labels) + ["Extractions"] * len(labels),
        })
        # preserve sorted label order in the plot
        df["label"] = pd.Categorical(df["label"], categories=labels, ordered=True)
        return df

    def _diverging_bar(ax, long_df, xlabel):
        sns.barplot(
            data=long_df, x="count", y="label", hue="source",
            palette=palette, ax=ax, dodge=False, legend=False,
            linewidth=0.8, edgecolor="black"
        )

        ax.axvline(0, color="black", linewidth=0.8)
        ax.set_xlabel(xlabel)
        ax.set_ylabel("")

        xticks = ax.get_xticks()
        ax.set_xticklabels([f"{abs(int(x))}" for x in xticks])

        sns.despine(ax=ax, top=True, right=True, left=True)

    rel_long = _to_long(gt_relations[gt_relation_col], pred_relations[pred_relation_col])
    ent_long = _to_long(gt_entities[gt_entity_col], pred_entities[pred_entity_col])

    _diverging_bar(ax_rel, rel_long, "Relation Count")
    _diverging_bar(ax_ent, ent_long, "Entity Count")

    # Build a manual legend since we set legend=False above (dodge=False + hue plots
    # can duplicate legend entries per bar otherwise)
    handles = [
        plt.Rectangle((0, 0), 1, 1, facecolor=palette["Ground Truth"], edgecolor="black", linewidth=0.8),
        plt.Rectangle((0, 0), 1, 1, facecolor=palette["Extractions"], edgecolor="black", linewidth=0.8),
    ]
    ax_rel.legend(handles, ["Ground Truth", "Extractions"], loc="upper right", frameon=False)

    fig.tight_layout()
    return fig, (ax_rel, ax_ent)

def plot_gt_distribution_comparison(
    biored_entities, cbc_entities,
    biored_relations, cbc_relations,
    biored_entity_col="entity_type", cbc_entity_col="entity_type",
    biored_relation_col="relation", cbc_relation_col="relation",
    figsize=(9, 8)
):
    # Greyscale palette: dark grey = BioRED, light grey = CBC
    palette = {"BioRED": "#404040", "CBC": "#b0b0b0"}

    fig, (ax_rel, ax_ent) = plt.subplots(2, 1, figsize=figsize)

    def _to_long_normalized(biored_series, cbc_series):
        # normalize to % of total within each dataset
        biored_pct = biored_series.value_counts(normalize=True) * 100
        cbc_pct = cbc_series.value_counts(normalize=True) * 100

        labels = (biored_pct.add(cbc_pct, fill_value=0)).sort_values().index

        biored_vals = biored_pct.reindex(labels, fill_value=0)
        cbc_vals = cbc_pct.reindex(labels, fill_value=0)

        df = pd.DataFrame({
            "label": list(labels) * 2,
            "pct": np.concatenate([-biored_vals.values, cbc_vals.values]),
            "source": ["BioRED"] * len(labels) + ["CBC"] * len(labels),
        })
        df["label"] = pd.Categorical(df["label"], categories=labels, ordered=True)
        return df

    def _diverging_bar(ax, long_df, xlabel):
        sns.barplot(
            data=long_df, x="pct", y="label", hue="source",
            palette=palette, ax=ax, dodge=False, legend=False,
            linewidth=0.8, edgecolor="black",
        )
        ax.axvline(0, color="black", linewidth=0.8)
        ax.set_xlabel(xlabel)
        ax.set_ylabel("")

        xticks = ax.get_xticks()
        ax.set_xticklabels([f"{abs(x):.0f}%" for x in xticks])

        sns.despine(ax=ax, top=True, right=True, left=True)

    rel_long = _to_long_normalized(
        biored_relations[biored_relation_col], cbc_relations[cbc_relation_col]
    )
    ent_long = _to_long_normalized(
        biored_entities[biored_entity_col], cbc_entities[cbc_entity_col]
    )

    _diverging_bar(ax_rel, rel_long, "% of Relations")
    _diverging_bar(ax_ent, ent_long, "% of Entities")

    n_biored_ent, n_cbc_ent = len(biored_entities), len(cbc_entities)
    n_biored_rel, n_cbc_rel = len(biored_relations), len(cbc_relations)

    handles = [
        plt.Rectangle((0, 0), 1, 1, facecolor=palette["BioRED"], edgecolor="black", linewidth=0.8),
        plt.Rectangle((0, 0), 1, 1, facecolor=palette["CBC"], edgecolor="black", linewidth=0.8),
    ]
    ax_rel.legend(
        handles,
        [f"BioRED (n={n_biored_rel})", f"CBC (n={n_cbc_rel})"],
        loc="upper right", frameon=False,
    )

    ax_ent.legend(
        handles,
        [f"BioRED (n={n_biored_ent})", f"CBC (n={n_cbc_ent})"],
        loc="upper right", frameon=False,
    )

    # fig.suptitle(
    #     f"Ground Truth Annotation Distribution: BioRED (n={n_biored_ent} entities) "
    #     f"vs CBC (n={n_cbc_ent} entities)",
    #     fontsize=10, y=1.02,
    # )

    fig.tight_layout()
    return fig, (ax_rel, ax_ent)

def plot_gt_ext_num(br_gt_ent, br_gt_rel, cbc_gt_ent, cbc_gt_rel):
    n_biored_ent, n_cbc_ent = len(br_gt_ent), len(cbc_gt_ent)
    n_biored_rel, n_cbc_rel = len(br_gt_rel), len(cbc_gt_rel)

    p_biored_ent = n_biored_ent / len(br_gt_ent["pmid"].unique())
    p_biored_rel = n_biored_rel / len(br_gt_rel["pmid"].unique())
    p_cbc_ent = n_cbc_ent / len(cbc_gt_ent["pmid"].unique())
    p_cbc_rel = n_cbc_rel / len(cbc_gt_rel["pmid"].unique())

    df = pd.DataFrame({
        "dataset": ["BioRED", "CBC", "BioRED", "CBC"],
        "type": ["Entities", "Entities", "Relations", "Relations"],
        "per_abstract": [p_biored_ent, p_cbc_ent, p_biored_rel, p_cbc_rel]
    })

    display(df)

    fig, ax = plt.subplots(figsize=(6, 5))
    sns.barplot(
        data=df,
        x="type",
        y="per_abstract",
        hue="dataset",
        palette={"BioRED": "#404040", "CBC": "#b0b0b0"},
        edgecolor="black",
        linewidth=0.8,
        ax=ax,
    )

    for bars, hatch in zip(ax.containers, ["", "//"]):
        for bar in bars:
            bar.set_hatch(hatch)

    ax.set_xlabel("")
    ax.set_ylabel("Mean count per abstract")
    sns.despine(ax=ax)
    fig.tight_layout()
    return fig, ax