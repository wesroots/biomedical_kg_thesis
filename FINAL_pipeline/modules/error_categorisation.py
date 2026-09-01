"""
LLM-based root-cause categorisation of entity/relation False Positive and
False Negative errors. Pulled out of error_analysis.ipynb so it can be
imported via `from modules.error_categorisation import ...` instead of
living as notebook-local closures.
"""

import json
import random

import pandas as pd

GT_KEYS = {"entities": "ner", "relations": "re"}


def _build_category_list_str(error_categories):
    return "\n".join(
        f"{num}. {cat['name']}: {cat['description']}"
        for num, cat in error_categories.items()
    )


def _entity_prompt(error_type, error, matching_gts, abstract_row, category_list_str):
    return f"""You are reviewing an entity-extraction error made by an NLP system.

Error type: {error_type}
- fp: a predicted entity that did not match the BioRED ground truth under the evaluation procedure.
- fn: a BioRED ground-truth entity that was not matched by a prediction.

Entity being analysed:
{error}

Abstract:
{abstract_row}

Ground-truth entities for this abstract:
{chr(10).join(str(gt) for gt in matching_gts)}

Categorise the primary cause of this error into exactly one of the categories below. Each category has a name and a description explaining when it applies — use the descriptions to guide your decision.

{category_list_str}

Use the abstract and BioRED ground truth as the reference when making your decision.
If multiple categories could apply, select the category that best explains why the prediction and ground truth did not match.

Respond with ONLY the category number, nothing else."""


def _relation_prompt(error_type, error, matching_gts, abstract_row, category_list_str):
    return f"""You are reviewing a relation-extraction error made by an NLP system.

Error type: {error_type}
- fp: a predicted relation that did not match the BioRED ground truth under the evaluation procedure.
- fn: a BioRED ground-truth relation that was not matched by a prediction.

Relation being analysed:
{error}

Abstract:
{abstract_row}

Ground-truth relations for this abstract:
{chr(10).join(str(gt) for gt in matching_gts)}

Categorise the primary cause of this error into exactly one of the categories below. Each category has a name and a description explaining when it applies — use the descriptions to guide your decision.

{category_list_str}

Use the abstract and BioRED ground truth as the reference when making your decision.
If multiple categories could apply, select the category that best explains why the prediction and ground truth did not match.

Respond with ONLY the category number, nothing else."""


PROMPT_BUILDERS = {"entities": _entity_prompt, "relations": _relation_prompt}


def sample_errors(error_list, sample_size, seed=42):
    """Downsample an FP or FN list to sample_size (deterministic, seeded).
    Returns the list unchanged if it's already at or below sample_size."""
    if sample_size is None or len(error_list) <= sample_size:
        return error_list
    return random.Random(seed).sample(error_list, sample_size)


def categorise_errors(
    kind,
    client,
    errors,
    gt_dict,
    abstracts_eval,
    error_categories,
    save_path,
    dataset_split,
    sample_size=50,
    seed=42,
    model="gpt-5.6-luna",
):
    """
    Categorise every (or, if sample_size is set, a sampled subset of) FP/FN
    error for `kind` ("entities" or "relations") into one of
    `error_categories`, using the source abstract and matching ground-truth
    items as context. Results are saved incrementally to
    `{save_path}/{dataset_split}_{kind}_error_codes.json`, so an interrupted
    run can be resumed by loading that partial file instead of restarting.

    Returns a list of dicts: {"error_type": "fp"|"fn", "error": <item>, "category": {...}}
    """
    fp = sample_errors(errors[kind]["false_positives"], sample_size, seed)
    fn = sample_errors(errors[kind]["false_negatives"], sample_size, seed)

    print(f"'{kind}' FP Sample Length: {len(fp)}")
    print(f"'{kind}' FN Sample Length: {len(fn)}")

    prompt_fn = PROMPT_BUILDERS[kind]
    gt_key = GT_KEYS[kind]
    category_list_str = _build_category_list_str(error_categories)

    results = []
    for error_type, error_list in (("fp", fp), ("fn", fn)):
        for error in error_list:
            pmid = error["pmid"]
            matching_gts = [gt for gt in gt_dict[gt_key] if gt[0] == pmid]
            abstract_row = (
                abstracts_eval.loc[pmid] if pmid in abstracts_eval.index
                else "Abstract not found."
            )

            prompt = prompt_fn(error_type, error, matching_gts, abstract_row, category_list_str)

            response = client.responses.create(
                model=model,
                input=prompt
            )
            category_code = response.output_text.strip()

            results.append({
                "error_type": error_type,
                "error": error,
                "category": error_categories.get(category_code, "Invalid")
            })

            with open(f"{save_path}/{dataset_split}_{kind}_error_codes.json", "w") as f:
                json.dump(results, f, indent=2, default=str)

    return results


def load_cached_error_codes(save_path, dataset_split, kind):
    with open(f"{save_path}/{dataset_split}_{kind}_error_codes.json", "r") as f:
        return json.load(f)


def category_df(error_codes, error_type):
    """Flatten a categorise_errors() result into a single-column DataFrame
    of category names, filtered to the given error_type ("fp" or "fn") --
    ready to hand to plot_error_type_distribution(..., entity_col="category")."""
    categories = [e["category"]["name"] for e in error_codes if e["error_type"] == error_type]
    return pd.DataFrame({"category": categories})
