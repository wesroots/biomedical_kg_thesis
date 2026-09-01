import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

from IPython.display import display

sns.set_theme(style="white")

# Shared hatch pattern: first hue level solid, second hatched (matches
# entity_generalisation.png / relation_generalisation.png)
HATCHES = ["", "//"]


def _add_gridlines(ax, axis="y"):
    ax.grid(axis=axis, color="black", alpha=0.2)
    ax.set_axisbelow(True)


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

        # Hatch the second hue group (Extractions) to match reference style
        for bars, hatch in zip(ax.containers, HATCHES):
            for bar in bars:
                bar.set_hatch(hatch)

        ax.axvline(0, color="black", linewidth=0.8)
        ax.set_xlabel(xlabel)
        ax.set_ylabel("")

        xticks = ax.get_xticks()
        ax.set_xticklabels([f"{abs(int(x))}" for x in xticks])

        _add_gridlines(ax, axis="x")
        sns.despine(ax=ax, top=True, right=True, left=True)

    rel_long = _to_long(gt_relations[gt_relation_col], pred_relations[pred_relation_col])
    ent_long = _to_long(gt_entities[gt_entity_col], pred_entities[pred_entity_col])

    _diverging_bar(ax_rel, rel_long, "Relation Count")
    _diverging_bar(ax_ent, ent_long, "Entity Count")

    # Manual legend, hatch-matched to the bars (dodge=False + hue legends
    # can otherwise duplicate/omit hatch info)
    handles = [
        plt.Rectangle((0, 0), 1, 1, facecolor=palette["Ground Truth"], edgecolor="black",
                      linewidth=0.8, hatch=HATCHES[0]),
        plt.Rectangle((0, 0), 1, 1, facecolor=palette["Extractions"], edgecolor="black",
                      linewidth=0.8, hatch=HATCHES[1]),
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

        # Hatch the second hue group (CBC) to match reference style
        for bars, hatch in zip(ax.containers, HATCHES):
            for bar in bars:
                bar.set_hatch(hatch)

        ax.axvline(0, color="black", linewidth=0.8)
        ax.set_xlabel(xlabel)
        ax.set_ylabel("")

        xticks = ax.get_xticks()
        ax.set_xticklabels([f"{abs(x):.0f}%" for x in xticks])

        _add_gridlines(ax, axis="x")
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
        plt.Rectangle((0, 0), 1, 1, facecolor=palette["BioRED"], edgecolor="black",
                      linewidth=0.8, hatch=HATCHES[0]),
        plt.Rectangle((0, 0), 1, 1, facecolor=palette["CBC"], edgecolor="black",
                      linewidth=0.8, hatch=HATCHES[1]),
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


def plot_error_type_distribution(
    entity_fp, entity_fn,
    relation_fp, relation_fn,
    entity_col="type", relation_col="relation",
    figsize=(9, 8)
):
    """
    Diverging horizontal bars comparing the distribution of a single
    dataset's False Positives vs False Negatives, normalized to % of that
    dataset's own FP/FN totals. Expects entity_fp/entity_fn/relation_fp/
    relation_fn to be DataFrames (or anything pd.DataFrame-able), e.g. built
    from a `<split>_predictions.json`'s "errors" field via:

        pd.DataFrame(predictions["errors"]["entities"]["false_positives"])
        pd.DataFrame(predictions["errors"]["entities"]["false_negatives"])

    entity_col/relation_col let this double as an error-*type* distribution
    (default "type"/"relation") or an error-*category* distribution (pass
    entity_col="category", relation_col="category") depending on what
    column the FP/FN DataFrames carry.
    """
    # Greyscale palette: dark grey = False Positives, light grey = False Negatives
    palette = {"False Positives": "#404040", "False Negatives": "#b0b0b0"}

    fig, (ax_rel, ax_ent) = plt.subplots(2, 1, figsize=figsize)

    def _to_long_normalized(fp_series, fn_series):
        fp_pct = fp_series.value_counts(normalize=True) * 100
        fn_pct = fn_series.value_counts(normalize=True) * 100

        labels = (fp_pct.add(fn_pct, fill_value=0)).sort_values().index

        fp_vals = fp_pct.reindex(labels, fill_value=0)
        fn_vals = fn_pct.reindex(labels, fill_value=0)

        df = pd.DataFrame({
            "label": list(labels) * 2,
            "pct": np.concatenate([-fp_vals.values, fn_vals.values]),
            "source": ["False Positives"] * len(labels) + ["False Negatives"] * len(labels),
        })
        df["label"] = pd.Categorical(df["label"], categories=labels, ordered=True)
        return df

    def _diverging_bar(ax, long_df, xlabel):
        sns.barplot(
            data=long_df, x="pct", y="label", hue="source",
            palette=palette, ax=ax, dodge=False, legend=False,
            linewidth=0.8, edgecolor="black",
        )

        # Hatch the second hue group (False Negatives) to match reference style
        for bars, hatch in zip(ax.containers, HATCHES):
            for bar in bars:
                bar.set_hatch(hatch)

        ax.axvline(0, color="black", linewidth=0.8)
        ax.set_xlabel(xlabel)
        ax.set_ylabel("")

        xticks = ax.get_xticks()
        ax.set_xticklabels([f"{abs(x):.0f}%" for x in xticks])

        _add_gridlines(ax, axis="x")
        sns.despine(ax=ax, top=True, right=True, left=True)

    rel_long = _to_long_normalized(relation_fp[relation_col], relation_fn[relation_col])
    ent_long = _to_long_normalized(entity_fp[entity_col], entity_fn[entity_col])

    _diverging_bar(ax_rel, rel_long, "% of Relation Errors")
    _diverging_bar(ax_ent, ent_long, "% of Entity Errors")

    n_rel_fp, n_rel_fn = len(relation_fp), len(relation_fn)
    n_ent_fp, n_ent_fn = len(entity_fp), len(entity_fn)

    handles = [
        plt.Rectangle((0, 0), 1, 1, facecolor=palette["False Positives"], edgecolor="black",
                      linewidth=0.8, hatch=HATCHES[0]),
        plt.Rectangle((0, 0), 1, 1, facecolor=palette["False Negatives"], edgecolor="black",
                      linewidth=0.8, hatch=HATCHES[1]),
    ]
    ax_rel.legend(
        handles,
        [f"False Positives (n={n_rel_fp})", f"False Negatives (n={n_rel_fn})"],
        loc="upper right", frameon=False,
    )
    ax_ent.legend(
        handles,
        [f"False Positives (n={n_ent_fp})", f"False Negatives (n={n_ent_fn})"],
        loc="upper right", frameon=False,
    )

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

    palette = {"BioRED": "#404040", "CBC": "#b0b0b0"}

    fig, ax = plt.subplots(figsize=(6, 5))
    sns.barplot(
        data=df,
        x="type",
        y="per_abstract",
        hue="dataset",
        palette=palette,
        edgecolor="black",
        linewidth=0.8,
        ax=ax,
        legend=False,
    )

    for bars, hatch in zip(ax.containers, HATCHES):
        for bar in bars:
            bar.set_hatch(hatch)

    # Manual, hatch-matched legend (consistent with the other two plots)
    handles = [
        plt.Rectangle((0, 0), 1, 1, facecolor=palette["BioRED"], edgecolor="black",
                      linewidth=0.8, hatch=HATCHES[0]),
        plt.Rectangle((0, 0), 1, 1, facecolor=palette["CBC"], edgecolor="black",
                      linewidth=0.8, hatch=HATCHES[1]),
    ]
    ax.legend(handles, ["BioRED", "CBC"], frameon=False)

    ax.set_xlabel("")
    ax.set_ylabel("Mean count per abstract")
    _add_gridlines(ax)
    sns.despine(ax=ax)
    fig.tight_layout()
    return fig, ax