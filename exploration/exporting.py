import os
import glob
import json
import re

from datetime import date

def export_run(run_dict, eval_results, time_taken, eval_version, prompt_version, dataset="biored_train", prompt=None, run_dir="../prompt_runs"):

    """
    Save the results of an extraction pipeline run as a JSON log.

    The exported run log includes metadata about the run, evaluation metrics,
    pipeline configuration, prompt text, and all extracted entities and
    relationships. Each run is assigned a unique sequential run ID.
    """

    run_id = get_next_run_id(run_dir)

    run_log = {
        "run_id": run_id,
        "date": str(date.today()),
        "time_taken": time_taken,
        "config": {
            "dataset": dataset,
            "num_abstracts": len(run_dict["extractions"]),
            "prompt_version": run_dict["prompt_version"],
            "eval_version": run_dict["eval_version"]
        },
        "metrics": eval_results,
        "notes": run_dict["run_notes"],
        "prompt": prompt,
        "extractions": {
            "entities": list(run_dict["predictions_entities"]),
            "relations": list(run_dict["predictions_relationships"])
        }
    }

    os.makedirs(run_dir, exist_ok=True)
    with open(os.path.join(run_dir, f"{run_id}.json"), "w") as f:
        json.dump(run_log, f, indent=2, default=list)

    print(f"Saved {run_id} to {run_dir}")
    return run_log

def get_next_run_id(prompt_runs_dir="../prompt_runs"):

    """
    Generate the next available sequential run identifier.

    Searches the specified run directory for existing run files matching the
    pattern 'run_XXX' and returns the next unused identifier.
    """

    os.makedirs(prompt_runs_dir, exist_ok=True)
    existing = glob.glob(os.path.join(prompt_runs_dir, "run_*"))
    nums = [int(re.search(r"run_(\d+)", d).group(1)) for d in existing if re.search(r"run_(\d+)", d)]
    next_num = max(nums, default=0) + 1

    return f"run_{next_num:03d}"