import json

from parsing import parse_output
from evaluation import evaluation_v1, evaluation_v2, evaluation_v3, evaluation_v4
from exporting import export_run
from error_sampling import get_errors

EVALUATORS = {
    "v1": evaluation_v1,
    "v2": evaluation_v2,
    "v3": evaluation_v3,
    "v4": evaluation_v4
}

EPI_TYPES = {
    "train": "biored_train",
    "dev": "biored_dev",
    "test": "biored_test",
    "contemporary": "contemporary"
}

def setup_epi(epi_num: str, dataset_stage: str) -> dict:

    with open("../../configs/prompt_config.json", "r") as f:
        PROMPTS = json.load(f)

    if dataset_stage not in EPI_TYPES:
        raise ValueError(
                f"Invalid dataset stage '{dataset_stage}'. "
                f"Expected one of {sorted(EPI_TYPES)}."
        )

    dataset_str = EPI_TYPES[dataset_stage]
    epi_id = f"epi_{epi_num}"

    cfg = load_epi_config(epi_name=f"epi_{epi_num}")

    prompt_version = cfg["prompt_version"]
    prompt_description = PROMPTS[prompt_version]["description"]
    prompt_template = PROMPTS[prompt_version]["template"]

    eval_version = cfg["eval_version"]
    epi_notes = cfg["notes"]
    reuse_api_call = should_reuse_api_call(epi_id)

    prompt = {
        "version": prompt_version,
        "description": prompt_description,
        "template": prompt_template
    }

    epi_setup = {
        "dataset": dataset_str,
        "id": epi_id,
        "eval_version": eval_version,
        "notes": epi_notes,
        "reuse_api_call": reuse_api_call,
        "prompt": prompt
    }

    return epi_setup


def process_epi(output_dict, ground_truths, dataset=None):
    epi_dict = parse_output(output_dict)

    evaluator = EVALUATORS[epi_dict["eval_version"]]
    eval_results = evaluator(epi_dict, ground_truths)

    epi_dir = output_dict["export_path"]

    errors, error_approach = get_errors(
        predictions_entities=epi_dict["predictions_entities"],
        predictions_relationships=epi_dict["predictions_relationships"],
        ground_truth_entities=ground_truths["entities"],
        ground_truth_relationships=ground_truths["relations"],
        eval_version=epi_dict["eval_version"]
    )

    epi_log = export_run(
        epi_dict,
        eval_results,
        epi_dir=epi_dir,
        dataset=dataset,
        errors={"matching_approach": error_approach, "errors": errors},
        save_log=True
    )

    return epi_log


def load_epi_config(epi_name, path="../../configs/epi_config.json"):
    with open(path) as f:
        configs = json.load(f)
    if epi_name not in configs:
        raise KeyError(f"No config found for '{epi_name}'")
    return configs[epi_name]


def should_reuse_api_call(epi_name, path="../../configs/epi_config.json"):
    epi_num = int(epi_name.replace("epi_", ""))
    if epi_num == 1:
        return False

    current_cfg = load_epi_config(epi_name, path)
    prev_cfg = load_epi_config(f"epi_{epi_num - 1:03d}", path)

    return current_cfg["prompt_version"] == prev_cfg["prompt_version"]