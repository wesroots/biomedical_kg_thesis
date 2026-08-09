import json
import os
import random
import pandas as pd

from evaluation import (
    COSINE_THRESHOLD,
    build_embedding_lookup,
    entity_match,
    entity_match_cosine,
    relationship_match,
    relationship_match_cosine,
    relationship_match_cosine_symmetric,
)

ERROR_DIR = "../../data/results/iteration_errors"

EVAL_MATCHERS = {
    "v1": {"approach": "strict"},
    "v2": {"approach": "relaxed", "entity_fn": entity_match, "relation_fn": relationship_match},
    "v3": {"approach": "cosine", "entity_fn": entity_match_cosine, "relation_fn": relationship_match_cosine},
    "v4": {"approach": "cosine", "entity_fn": entity_match_cosine, "relation_fn": relationship_match_cosine_symmetric},
}


def _diff_strict(predictions, ground_truth):
    fp = predictions - ground_truth
    fn = ground_truth - predictions
    return fp, fn


def _diff_relaxed(predictions, ground_truth, match_fn):
    matched_gt = set()
    matched_predictions = set()

    for p in predictions:
        for g in ground_truth:
            if g in matched_gt:
                continue
            if match_fn(p, g):
                matched_gt.add(g)
                matched_predictions.add(p)
                break

    fp = predictions - matched_predictions
    fn = ground_truth - matched_gt
    return fp, fn


def _diff_cosine(predictions, ground_truth, match_fn, embeddings, threshold=COSINE_THRESHOLD):
    matched_gt = set()
    matched_predictions = set()

    for p in predictions:
        best_score = -1
        best_g = None

        for g in ground_truth:
            if g in matched_gt:
                continue
            is_match, score = match_fn(p, g, embeddings, threshold)
            if is_match and score > best_score:
                best_score = score
                best_g = g

        if best_g is not None:
            matched_gt.add(best_g)
            matched_predictions.add(p)

    fp = predictions - matched_predictions
    fn = ground_truth - matched_gt
    return fp, fn


def _build_error_dict(fp_items, fn_items):
    return {
        "false_positives": [list(item) for item in fp_items],
        "false_negatives": [list(item) for item in fn_items],
    }


def get_errors(
    predictions_entities,
    predictions_relationships,
    ground_truth_entities,
    ground_truth_relationships,
    eval_version
):
    """
    Diff predictions against ground truth using the matching approach appropriate
    for eval_version, and return all false positive/negative errors.

    Returns (errors, approach) where errors = {"entities": [...], "relations": [...]}
    """

    matcher_cfg = EVAL_MATCHERS.get(eval_version)
    if matcher_cfg is None:
        raise KeyError(f"No error-sampling config for eval_version='{eval_version}'")

    approach = matcher_cfg["approach"]

    if approach == "strict":
        entity_fp, entity_fn = _diff_strict(predictions_entities, ground_truth_entities)
        relation_fp, relation_fn = _diff_strict(predictions_relationships, ground_truth_relationships)

    elif approach == "relaxed":
        entity_fp, entity_fn = _diff_relaxed(predictions_entities, ground_truth_entities, matcher_cfg["entity_fn"])
        relation_fp, relation_fn = _diff_relaxed(
            predictions_relationships, ground_truth_relationships, matcher_cfg["relation_fn"]
        )

    elif approach == "cosine":
        entity_embeddings = build_embedding_lookup(predictions_entities, ground_truth_entities, text_indices=[1])
        relation_embeddings = build_embedding_lookup(
            predictions_relationships, ground_truth_relationships, text_indices=[1, 3]
        )

        entity_fp, entity_fn = _diff_cosine(
            predictions_entities, ground_truth_entities, matcher_cfg["entity_fn"], entity_embeddings
        )
        relation_fp, relation_fn = _diff_cosine(
            predictions_relationships, ground_truth_relationships, matcher_cfg["relation_fn"], relation_embeddings
        )

    else:
        raise ValueError(f"Unknown approach '{approach}'")

    errors = {
        "entities": _build_error_dict(entity_fp, entity_fn),
        "relations": _build_error_dict(relation_fp, relation_fn),
    }

    return errors, approach


def error_summary(epi_log) -> pd.DataFrame:

    print(f"`{epi_log["epi_id"]}` Error Summary:")

    metrics = epi_log["metrics"]
    m_labels = ["Precision", "Recall", "F1"]
    m_approaches = ["cosine", "relaxed", "strict"]

    for appr in m_approaches:
        if appr in metrics["entity"]:
            approach = appr
            break

    entity_precision = round(metrics["entity"][approach]["precision"], 3)
    entity_recall = round(metrics["entity"][approach]["recall"], 3)
    entity_f1 = round(metrics["entity"][approach]["f1"], 3)

    relation_precision = round(metrics["relation"][approach]["precision"], 3)
    relation_recall = round(metrics["relation"][approach]["recall"], 3)
    relation_f1 = round(metrics["relation"][approach]["f1"], 3)

    summary = pd.DataFrame({
        "Metric": m_labels,
        "Entity": [entity_precision, entity_recall, entity_f1],
        "Relation": [relation_precision, relation_recall, relation_f1]
    })

    return summary.set_index("Metric").T