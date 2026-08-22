import pandas as pd
import json

def entities_to_df(predictions_entities) -> pd.DataFrame:
    """Matches br_{split}_entities.csv structure (minus identifier/offsets,
    which require entity normalisation the LLM doesn't do)."""
    return pd.DataFrame(predictions_entities, columns=["pmid", "text", "entity_type"])


def relationships_to_df(predictions_relationships) -> pd.DataFrame:
    """Matches br_{split}_entity_relations.csv structure (minus identifiers)."""
    return pd.DataFrame(predictions_relationships, columns=["pmid", "entity_1", "relation", "entity_2"])

def parse_output(output_dict):
    epi_id = output_dict["epi_id"]
    outputs = output_dict["outputs"]
    time_taken = output_dict["time_taken"]
    raw_prompt = output_dict["raw_prompt"]
    epi_notes = output_dict["epi_notes"]
    prompt_version = output_dict["prompt_version"]
    eval_version = output_dict["eval_version"]

    extractions, parse_failures = outputs_to_extractions(outputs)

    predictions_entities, predictions_relationships = extractions_to_tuples(extractions)

    predictions_entities_df = entities_to_df(predictions_entities)
    predictions_relations_df = relationships_to_df(predictions_relationships)

    return {
        "extractions": extractions,
        "predictions_entities": predictions_entities,
        "predictions_relationships": predictions_relationships,
        "predictions_entities_df": predictions_entities_df,
        "predictions_relations_df": predictions_relations_df,
        "parse_failures": parse_failures,
        "epi_notes": epi_notes,
        "prompt_version": prompt_version,
        "eval_version": eval_version,
        "time_taken": time_taken,
        "raw_prompt": raw_prompt,
        "outputs": outputs,
        "epi_id": epi_id
    }

def outputs_to_extractions(outputs, confirmation=True) -> tuple[list, int]:
    extractions = []
    parse_failures = 0

    for item in outputs:
        try:
            parsed = json.loads(item["output"])
        except json.JSONDecodeError:
            parse_failures += 1
            parsed = {"entities": [], "relationships": []}

        extractions.append({
            "pmid": item["pmid"],
            "entities": parsed.get("entities", []),
            "relationships": parsed.get("relationships", [])
        })

    if confirmation:
        print(f"Parsed {len(extractions)} extractions, {parse_failures} failed to parse as JSON")

    return extractions, parse_failures

def extractions_to_tuples(extractions):
    predictions_entities = {
        (extraction["pmid"], e["text"].strip().lower(), e["type"])
        for extraction in extractions
        for e in extraction["entities"]
    }

    predictions_relationships = {
        (
            extraction["pmid"],
            r["source"].strip().lower(),
            r["relation"],
            r["target"].strip().lower()
        )
        for extraction in extractions
        for r in extraction["relationships"]
    }

    return predictions_entities, predictions_relationships