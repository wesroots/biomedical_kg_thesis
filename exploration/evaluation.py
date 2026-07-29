import numpy as np
from sentence_transformers import SentenceTransformer


def evaluation_v1(run_dict, ground_truths):

    ground_truths_entities = ground_truths["entities"]
    ground_truths_relationships = ground_truths["relationships"]

    predictions_entities = run_dict["predictions_entities"]
    predictions_relationships = run_dict["predictions_relationships"]

    entity_metrics_strict = compute_prf_strict(predictions_entities, ground_truths_entities)
    relationship_metrics_strict = compute_prf_strict(predictions_relationships, ground_truths_relationships)

    return {
        "entity": {"strict": entity_metrics_strict},
        "relation": {"strict": relationship_metrics_strict}
    }


def evaluation_v2(run_dict, ground_truths):

    ground_truths_entities = ground_truths["entities"]
    ground_truths_relationships = ground_truths["relationships"]

    predictions_entities = run_dict["predictions_entities"]
    predictions_relationships = run_dict["predictions_relationships"]

    entity_metrics_strict = compute_prf_strict(predictions_entities, ground_truths_entities)
    relationship_metrics_strict = compute_prf_strict(predictions_relationships, ground_truths_relationships)

    entity_metrics_relaxed = compute_prf_relaxed(predictions_entities, ground_truths_entities, entity_match)
    relationship_metrics_relaxed = compute_prf_relaxed(predictions_relationships, ground_truths_relationships, relationship_match)

    return {
        "entity": {"strict": entity_metrics_strict, "relaxed": entity_metrics_relaxed},
        "relation": {"strict": relationship_metrics_strict, "relaxed": relationship_metrics_relaxed}
    }

_MODEL = None
COSINE_THRESHOLD = 0.85

def evaluation_v3(run_dict, ground_truths):

    ground_truths_entities = ground_truths["entities"]
    ground_truths_relationships = ground_truths["relationships"]

    predictions_entities = run_dict["predictions_entities"]
    predictions_relationships = run_dict["predictions_relationships"]

    entity_metrics_strict = compute_prf_strict(predictions_entities, ground_truths_entities)
    relationship_metrics_strict = compute_prf_strict(predictions_relationships, ground_truths_relationships)

    entity_metrics_relaxed = compute_prf_relaxed(predictions_entities, ground_truths_entities, entity_match)
    relationship_metrics_relaxed = compute_prf_relaxed(predictions_relationships, ground_truths_relationships, relationship_match)

    entity_embeddings = build_embedding_lookup(predictions_entities, ground_truths_entities, text_indices=[1])
    relationship_embeddings = build_embedding_lookup(predictions_relationships, ground_truths_relationships, text_indices=[1, 3])

    entity_metrics_cosine = compute_prf_cosine(
        predictions_entities, ground_truths_entities, entity_match_cosine, entity_embeddings, COSINE_THRESHOLD
    )
    relationship_metrics_cosine = compute_prf_cosine(
        predictions_relationships, ground_truths_relationships, relationship_match_cosine, relationship_embeddings, COSINE_THRESHOLD
    )

    return {
        "entity": {"strict": entity_metrics_strict, "relaxed": entity_metrics_relaxed, "cosine": entity_metrics_cosine},
        "relation": {"strict": relationship_metrics_strict, "relaxed": relationship_metrics_relaxed, "cosine": relationship_metrics_cosine}
    }

def evaluation_v4(run_dict, ground_truths):

    ground_truths_entities = ground_truths["entities"]
    ground_truths_relationships = ground_truths["relationships"]

    predictions_entities = run_dict["predictions_entities"]
    predictions_relationships = run_dict["predictions_relationships"]

    entity_metrics_strict = compute_prf_strict(predictions_entities, ground_truths_entities)
    entity_metrics_relaxed = compute_prf_relaxed(predictions_entities, ground_truths_entities, entity_match)

    relationship_metrics_strict = compute_prf_relaxed(
        predictions_relationships, ground_truths_relationships, relationship_match_strict_symmetric
    )
    relationship_metrics_relaxed = compute_prf_relaxed(
        predictions_relationships, ground_truths_relationships, relationship_match_symmetric
    )

    entity_embeddings = build_embedding_lookup(predictions_entities, ground_truths_entities, text_indices=[1])
    relationship_embeddings = build_embedding_lookup(predictions_relationships, ground_truths_relationships, text_indices=[1, 3])

    entity_metrics_cosine = compute_prf_cosine(
        predictions_entities, ground_truths_entities, entity_match_cosine, entity_embeddings, COSINE_THRESHOLD
    )
    relationship_metrics_cosine = compute_prf_cosine(
        predictions_relationships, ground_truths_relationships, relationship_match_cosine_symmetric, relationship_embeddings, COSINE_THRESHOLD
    )

    return {
        "entity": {"strict": entity_metrics_strict, "relaxed": entity_metrics_relaxed, "cosine": entity_metrics_cosine},
        "relation": {"strict": relationship_metrics_strict, "relaxed": relationship_metrics_relaxed, "cosine": relationship_metrics_cosine},
        "eval_version": "v4"
    }

def get_embedding_model():
    global _MODEL
    if _MODEL is None:
        _MODEL = SentenceTransformer("pritamdeka/S-PubMedBert-MS-MARCO")
    return _MODEL


def build_embedding_lookup(predictions, ground_truth, text_indices):
    """Embed every unique text span once, return {text: vector}."""
    texts = set()
    for item in predictions:
        for i in text_indices:
            texts.add(item[i])
    for item in ground_truth:
        for i in text_indices:
            texts.add(item[i])

    texts = list(texts)
    model = get_embedding_model()
    vectors = model.encode(texts, convert_to_numpy=True)

    return dict(zip(texts, vectors))


def cosine_similarity(vec1, vec2):
    return float(np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2)))


def entity_match_cosine(pred, gt, embeddings, threshold):
    if pred[0] != gt[0] or pred[2] != gt[2]:
        return False, 0.0
    score = cosine_similarity(embeddings[pred[1]], embeddings[gt[1]])
    return score >= threshold, score


def relationship_match_cosine(pred, gt, embeddings, threshold):
    if pred[0] != gt[0] or pred[2] != gt[2]:
        return False, 0.0
    source_score = cosine_similarity(embeddings[pred[1]], embeddings[gt[1]])
    target_score = cosine_similarity(embeddings[pred[3]], embeddings[gt[3]])
    is_match = source_score >= threshold and target_score >= threshold
    return is_match, min(source_score, target_score)


def compute_prf_cosine(predictions, ground_truth, match_fn, embeddings, threshold):
    matched_gt = set()
    tp = 0

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
            tp += 1

    fp = len(predictions) - tp
    fn = len(ground_truth) - len(matched_gt)

    precision = tp / (tp + fp) if (tp + fp) else 0
    recall = tp / (tp + fn) if (tp + fn) else 0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) else 0

    return {
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1": round(f1, 4),
        "tp": tp,
        "fp": fp,
        "fn": fn
    }


def compute_prf_strict(predictions, ground_truth):
    tp = len(predictions & ground_truth)
    fp = len(predictions - ground_truth)
    fn = len(ground_truth - predictions)

    precision = tp / (tp + fp) if (tp + fp) else 0
    recall = tp / (tp + fn) if (tp + fn) else 0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) else 0

    return {
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1": round(f1, 4),
        "tp": tp,
        "fp": fp,
        "fn": fn
    }


def span_matches(predicted, ground_truth):
    predicted = predicted.strip().lower()
    ground_truth = ground_truth.strip().lower()

    return (
        predicted == ground_truth
        or predicted in ground_truth
        or ground_truth in predicted
    )


def entity_match(pred, gt):
    return pred[0] == gt[0] and pred[2] == gt[2] and span_matches(pred[1], gt[1])


def relationship_match(pred, gt):
    return (
        pred[0] == gt[0]
        and pred[2] == gt[2]
        and span_matches(pred[1], gt[1])
        and span_matches(pred[3], gt[3])
    )


def compute_prf_relaxed(predictions, ground_truth, match_fn):
    matched_gt = set()
    tp = 0

    for p in predictions:
        for g in ground_truth:
            if g in matched_gt:
                continue
            if match_fn(p, g):
                matched_gt.add(g)
                tp += 1
                break

    fp = len(predictions) - tp
    fn = len(ground_truth) - len(matched_gt)

    precision = tp / (tp + fp) if (tp + fp) else 0
    recall = tp / (tp + fn) if (tp + fn) else 0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) else 0

    return {
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1": round(f1, 4),
        "tp": tp,
        "fp": fp,
        "fn": fn
    }


def relationship_match_strict_symmetric(pred, gt):
    if pred[0] != gt[0] or pred[2] != gt[2]:
        return False
    same_order = pred[1] == gt[1] and pred[3] == gt[3]
    swapped_order = pred[1] == gt[3] and pred[3] == gt[1]
    return same_order or swapped_order


def relationship_match_symmetric(pred, gt):
    if pred[0] != gt[0] or pred[2] != gt[2]:
        return False
    same_order = span_matches(pred[1], gt[1]) and span_matches(pred[3], gt[3])
    swapped_order = span_matches(pred[1], gt[3]) and span_matches(pred[3], gt[1])
    return same_order or swapped_order


def relationship_match_cosine_symmetric(pred, gt, embeddings, threshold):
    if pred[0] != gt[0] or pred[2] != gt[2]:
        return False, 0.0

    same_source = cosine_similarity(embeddings[pred[1]], embeddings[gt[1]])
    same_target = cosine_similarity(embeddings[pred[3]], embeddings[gt[3]])
    same_ok = same_source >= threshold and same_target >= threshold
    same_score = min(same_source, same_target)

    swap_source = cosine_similarity(embeddings[pred[1]], embeddings[gt[3]])
    swap_target = cosine_similarity(embeddings[pred[3]], embeddings[gt[1]])
    swap_ok = swap_source >= threshold and swap_target >= threshold
    swap_score = min(swap_source, swap_target)

    is_match = same_ok or swap_ok
    best_score = max(same_score, swap_score)
    return is_match, best_score