import os

import pandas as pd
import random
import json

def load_corpus(path: str, sample_size: None | int = None) -> pd.DataFrame:

    data = pd.read_csv(path)

    if sample_size is not None:
        if sample_size > len(data):
            raise ValueError(
                f"sample_size={sample_size} exceeds dataset size={len(data)}"
            )

        data_sample = data.sample(
            n=sample_size,
            random_state=42
        ).copy()

        return data_sample

    return data

def get_corpus_gt_csv(data, gt_path) -> pd.DataFrame:

    pmids = set(data["pmid"])

    gt = pd.read_csv(gt_path)

    gt_filtered = gt[gt["pmid"].isin(pmids)]

    return gt_filtered


def get_gt_dict(entity_relations_data, entities_data, eval_pmids=None) -> dict:
    ground_truth_entities = set(zip(
        entities_data["pmid"],
        entities_data["text"].str.strip().str.lower(),
        entities_data["entity_type"]
    ))
    ground_truth_relations = set(zip(
        entity_relations_data["pmid"],
        entity_relations_data["entity_1"].str.strip().str.lower(),
        entity_relations_data["relation"],
        entity_relations_data["entity_2"].str.strip().str.lower()
    ))

    result = {"entities": ground_truth_entities, "relations": ground_truth_relations}
    if eval_pmids is not None:
        result["eval_pmids"] = eval_pmids
    return result