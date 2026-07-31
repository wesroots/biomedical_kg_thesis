import json

from parsing import parse_output
from evaluation import evaluation_v1, evaluation_v2, evaluation_v3, evaluation_v4
from exporting import export_run

EVALUATORS = {
    "v1": evaluation_v1,
    "v2": evaluation_v2,
    "v3": evaluation_v3,
    "v4": evaluation_v4
}

def process_run(output_dict, ground_truths):
    run_dict = parse_output(output_dict)

    evaluator = EVALUATORS[run_dict["eval_version"]]
    eval_results = evaluator(run_dict, ground_truths)

    run_log = export_run(run_dict, eval_results)

    return run_log


def load_run_config(run_name, path="run_configs.json"):
    with open(path) as f:
        configs = json.load(f)
    if run_name not in configs:
        raise KeyError(f"No config found for '{run_name}'")
    return configs[run_name]


def should_reuse_api_call(run_name, path="run_configs.json"):
    run_num = int(run_name.replace("run_", ""))
    if run_num == 1:
        return False  # no previous run to compare against

    current_cfg = load_run_config(run_name, path)
    prev_cfg = load_run_config(f"run_{run_num - 1:03d}", path)

    return current_cfg["prompt_version"] == prev_cfg["prompt_version"]