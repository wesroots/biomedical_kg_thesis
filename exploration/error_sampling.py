import random
from evaluation import COSINE_THRESHOLD

def sample_errors_strict(predictions, ground_truth, n=20, label="items"):
    false_positives = list(predictions - ground_truth)
    false_negatives = list(ground_truth - predictions)

    fp_sample = random.sample(false_positives, min(n, len(false_positives)))
    fn_sample = random.sample(false_negatives, min(n, len(false_negatives)))

    print(f"--- {label}: False Positives (predicted, not in ground truth) ---")
    print(f"Sampled {len(fp_sample)} of {len(false_positives)} total FPs\n")
    for item in fp_sample:
        print(" ", item)

    print(f"\n--- {label}: False Negatives (in ground truth, not predicted) ---")
    print(f"Sampled {len(fn_sample)} of {len(false_negatives)} total FNs\n")
    for item in fn_sample:
        print(" ", item)

    return fp_sample, fn_sample

def sample_errors_cosine(predictions, ground_truth, match_fn, embeddings, threshold=COSINE_THRESHOLD, n=20, label="items"):
    matched_predictions = set()
    matched_gt = set()

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

    false_positives = list(predictions - matched_predictions)
    false_negatives = list(ground_truth - matched_gt)

    fp_sample = random.sample(false_positives, min(n, len(false_positives)))
    fn_sample = random.sample(false_negatives, min(n, len(false_negatives)))

    print(f"--- {label}: False Positives (predicted, no cosine match in ground truth) ---")
    print(f"Sampled {len(fp_sample)} of {len(false_positives)} total FPs\n")
    for item in fp_sample:
        print(" ", item)

    print(f"\n--- {label}: False Negatives (in ground truth, no cosine match in predictions) ---")
    print(f"Sampled {len(fn_sample)} of {len(false_negatives)} total FNs\n")
    for item in fn_sample:
        print(" ", item)

    return fp_sample, fn_sample