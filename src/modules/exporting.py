import os
import glob
import json
import re

from datetime import date

def export_run(epi_dict, eval_results, dataset, epi_dir, errors=None):
    """
    """

    epi_id = epi_dict["epi_id"]

    epi_log = {
        "epi_id": epi_id,
        "date": str(date.today()),
        "time_taken": epi_dict["time_taken"],
        "config": {
            "dataset": dataset,
            "num_abstracts": len(epi_dict["extractions"]),
            "prompt_version": epi_dict["prompt_version"],
            "eval_version": epi_dict["eval_version"]
        },
        "metrics": eval_results,
        "errors": errors,
        "notes": epi_dict["epi_notes"],
        "prompt": epi_dict["raw_prompt"],
        "outputs": epi_dict["outputs"],
        "extractions": {
            "entities": list(epi_dict["predictions_entities"]),
            "relations": list(epi_dict["predictions_relationships"])
        }
    }

    os.makedirs(epi_dir, exist_ok=True)
    with open(os.path.join(epi_dir, f"{epi_id}.json"), "w") as f:
        json.dump(epi_log, f, indent=2, default=list)

    print(f"Saved {epi_id} to {epi_dir}")
    return epi_log