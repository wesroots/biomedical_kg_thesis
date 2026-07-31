import os

import pandas as pd

def load_biored(path: str, sample_size: None | int = None) -> pd.DataFrame:

    biored = pd.read_csv(path)

    if sample_size is not None:
        if sample_size > len(biored):
            raise ValueError(
                f"sample_size={sample_size} exceeds dataset size={len(biored)}"
            )

        biored_sampled = biored.sample(
            n=sample_size,
            random_state=42
        ).copy()

        return biored_sampled

    return biored

def get_biored_gts(data, gt_path) -> pd.DataFrame:

    pmids = set(data["pmid"])

    gt = pd.read_csv(gt_path)

    gt_filtered = gt[gt["pmid"].isin(pmids)]

    return gt_filtered

def export_biored(data, file_name):

    dir = "../data/filtered"

    os.makedirs(dir, exist_ok=True)

    path = f"{dir}/{file_name}"

    data.to_csv(path)

    print(f"Exported dataset ground truths to '{path}'.")

def get_gt_entities_relationships(data):

    ground_truth_entities = (
        set(zip(data["pmid"], data["entity_1"].str.strip().str.lower(), data["entity_1_type"]))
        | set(zip(data["pmid"], data["entity_2"].str.strip().str.lower(), data["entity_2_type"]))
    )

    ground_truth_relationships = set(zip(
        data["pmid"],
        data["entity_1"].str.strip().str.lower(),
        data["relation"],
        data["entity_2"].str.strip().str.lower()
    ))

    ground_truths = {
        "entities": ground_truth_entities,
        "relationships": ground_truth_relationships,
    }

    return ground_truths

import pandas as pd
import random
import json


def build_few_shot_example(pmid, example_num, biored_train, biored_gts):
    abstract = biored_train[biored_train["pmid"] == pmid]["abstract"].iloc[0]
    gt_rows = biored_gts[biored_gts["pmid"] == pmid]

    entities = list({
        (row["entity_1"], row["entity_1_type"]) for _, row in gt_rows.iterrows()
    } | {
        (row["entity_2"], row["entity_2_type"]) for _, row in gt_rows.iterrows()
    })

    relationships = [
        {"source": row["entity_1"], "relation": row["relation"], "target": row["entity_2"]}
        for _, row in gt_rows.iterrows()
    ]

    output_json = {
        "entities": [{"text": e[0], "type": e[1]} for e in entities],
        "relationships": relationships
    }

    return (
        f"## EXAMPLE {example_num + 1}:\n\n### Abstract:\n\n{abstract}\n\n"
        f"### Correct BioRED annotation:\n\n{json.dumps(output_json, indent=2)}"
    )


def get_few_shot_examples(
    path_to_train_set: str,
    path_to_train_gts: str,
    biored_train_samples: pd.DataFrame,
    few_shot_export_path: str,
    run_type: str = "train",
    n_examples: int = 3
):
    """
    Build a few-shot prompt block sampled from BioRED training abstracts.

    When run_type == "train", pmids in biored_train_samples (the abstracts
    being evaluated in this run) are excluded from the candidate pool to
    prevent leakage between few-shot examples and the evaluation set.
    For any other run_type, no exclusion is applied, since the evaluation
    abstracts come from a different corpus entirely.
    """

    biored_train = pd.read_csv(path_to_train_set)
    biored_gts = pd.read_csv(path_to_train_gts)

    if run_type == "train":
        sampled_pmids = set(biored_train_samples["pmid"])
        candidate_pmids = set(biored_train["pmid"]) - sampled_pmids
    else:
        candidate_pmids = set(biored_train["pmid"])

    few_shot_pmids = random.sample(list(candidate_pmids), n_examples)

    few_shot_block = "\n\n".join(
        build_few_shot_example(pmid, i, biored_train, biored_gts)
        for i, pmid in enumerate(few_shot_pmids)
    )

    os.makedirs("../data/few_shot", exist_ok=True)

    with open(few_shot_export_path, "w") as f:
        f.write(few_shot_block)

    return few_shot_block