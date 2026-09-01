"""
Final pipeline evaluation module. Single approach: cosine entity/symmetric
relation matching, filtered to eval_pmids, with bootstrap CIs computed by
default (not a separate optional call).
"""

import numpy as np
from sentence_transformers import SentenceTransformer

COSINE_THRESHOLD = 0.85
_MODEL = None


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


def compute_prf_cosine(predictions, ground_truth, match_fn, embeddings, threshold):
    matched_gt = set()
    tp = 0
    for p in predictions:
        best_score, best_g = -1, None
        for g in ground_truth:
            if g in matched_gt:
                continue
            is_match, score = match_fn(p, g, embeddings, threshold)
            if is_match and score > best_score:
                best_score, best_g = score, g
        if best_g is not None:
            matched_gt.add(best_g)
            tp += 1

    fp = len(predictions) - tp
    fn = len(ground_truth) - len(matched_gt)
    precision = tp / (tp + fp) if (tp + fp) else 0
    recall = tp / (tp + fn) if (tp + fn) else 0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) else 0

    return {"precision": round(precision, 4), "recall": round(recall, 4), "f1": round(f1, 4), "tp": tp, "fp": fp, "fn": fn}


def _group_by_pmid(items):
    grouped = {}
    for item in items:
        grouped.setdefault(item[0], []).append(item)
    return grouped


def per_pmid_matches_cosine(predictions, ground_truth, match_fn, embeddings, threshold=COSINE_THRESHOLD):
    """
    Same greedy per-PMID matching as per_pmid_counts_cosine, but keeps the
    actual matched/unmatched tuples (not just their counts) so callers can
    inspect or export the specific TP/FP/FN items -- e.g. for error analysis
    without re-running extraction or embedding.
    """
    pred_by_pmid = _group_by_pmid(predictions)
    gt_by_pmid = _group_by_pmid(ground_truth)
    all_pmids = set(pred_by_pmid) | set(gt_by_pmid)

    matches = {}
    for pmid in all_pmids:
        p = pred_by_pmid.get(pmid, [])
        g = gt_by_pmid.get(pmid, [])
        matched_gt = set()
        tp_items, fp_items = [], []
        for pred_item in p:
            best_score, best_g = -1, None
            for gt_item in g:
                if gt_item in matched_gt:
                    continue
                is_match, score = match_fn(pred_item, gt_item, embeddings, threshold)
                if is_match and score > best_score:
                    best_score, best_g = score, gt_item
            if best_g is not None:
                matched_gt.add(best_g)
                tp_items.append(pred_item)
            else:
                fp_items.append(pred_item)
        fn_items = [gt_item for gt_item in g if gt_item not in matched_gt]
        matches[pmid] = {"tp": tp_items, "fp": fp_items, "fn": fn_items}
    return matches


def matches_to_counts(matches):
    """Collapse item-level matches down to counts, for bootstrap_ci/counts_to_prf."""
    return {
        pmid: {"tp": len(m["tp"]), "fp": len(m["fp"]), "fn": len(m["fn"])}
        for pmid, m in matches.items()
    }


def per_pmid_counts_cosine(predictions, ground_truth, match_fn, embeddings, threshold=COSINE_THRESHOLD):
    """Backward-compatible counts-only wrapper around per_pmid_matches_cosine."""
    return matches_to_counts(per_pmid_matches_cosine(predictions, ground_truth, match_fn, embeddings, threshold))


def counts_to_prf(counts_list):
    tp = sum(c["tp"] for c in counts_list)
    fp = sum(c["fp"] for c in counts_list)
    fn = sum(c["fn"] for c in counts_list)
    precision = tp / (tp + fp) if (tp + fp) else 0.0
    recall = tp / (tp + fn) if (tp + fn) else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) else 0.0
    return {"precision": precision, "recall": recall, "f1": f1, "tp": tp, "fp": fp, "fn": fn}


def bootstrap_ci(per_pmid_counts, n_boot=2000, ci=0.95, random_state=42):
    rng = np.random.default_rng(random_state)
    pmids = list(per_pmid_counts.keys())
    n = len(pmids)

    point_estimate = counts_to_prf(list(per_pmid_counts.values()))

    boot_p, boot_r, boot_f1 = [], [], []
    for _ in range(n_boot):
        sampled = rng.choice(pmids, size=n, replace=True)
        prf = counts_to_prf([per_pmid_counts[pmid] for pmid in sampled])
        boot_p.append(prf["precision"])
        boot_r.append(prf["recall"])
        boot_f1.append(prf["f1"])

    alpha = (1 - ci) / 2
    lo, hi = 100 * alpha, 100 * (1 - alpha)
    pct = lambda v: (float(np.percentile(v, lo)), float(np.percentile(v, hi)))

    return {
        "point_estimate": point_estimate,
        "ci": {"precision": pct(boot_p), "recall": pct(boot_r), "f1": pct(boot_f1)},
        "n_boot": n_boot,
        "n_pmids": n,
    }


def evaluate_extractions(predictions_entities, predictions_relationships, ground_truths, n_boot=2000, ci=0.95, random_state=42):

    eval_pmids = ground_truths["eval_pmids"]
    ground_truths_entities = ground_truths["ner"]
    ground_truths_relationships = ground_truths["re"]

    filtered_entities = {e for e in predictions_entities if e[0] in eval_pmids}
    filtered_relationships = {r for r in predictions_relationships if r[0] in eval_pmids}

    entity_embeddings = build_embedding_lookup(filtered_entities, ground_truths_entities, text_indices=[1])
    relationship_embeddings = build_embedding_lookup(filtered_relationships, ground_truths_relationships, text_indices=[1, 3])

    entity_matches = per_pmid_matches_cosine(
        filtered_entities, ground_truths_entities, entity_match_cosine, entity_embeddings, COSINE_THRESHOLD
    )
    relation_matches = per_pmid_matches_cosine(
        filtered_relationships, ground_truths_relationships,
        relationship_match_cosine_symmetric, relationship_embeddings, COSINE_THRESHOLD
    )

    entity_counts = matches_to_counts(entity_matches)
    relation_counts = matches_to_counts(relation_matches)

    return {
        "entity": bootstrap_ci(entity_counts, n_boot=n_boot, ci=ci, random_state=random_state),
        "relation": bootstrap_ci(relation_counts, n_boot=n_boot, ci=ci, random_state=random_state),
        # item-level TP/FP/FN per PMID -- only covers eval_pmids (the PMIDs
        # with ground truth), same scope as the metrics above
        "entity_matches": entity_matches,
        "relation_matches": relation_matches,
    }