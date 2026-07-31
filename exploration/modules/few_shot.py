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