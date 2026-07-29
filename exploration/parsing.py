import json

def parse_output(output_dict):
    outputs = output_dict["outputs"]
    run_notes = output_dict["run_notes"]
    prompt_version = output_dict["prompt_version"]
    eval_version = output_dict["eval_version"]

    extractions, parse_failures = outputs_to_extractions(outputs)

    predictions_entities, predictions_relationships = extractions_to_tuples(extractions)

    return {
        "extractions": extractions,
        "predictions_entities": predictions_entities,
        "predictions_relationships": predictions_relationships,
        "parse_failures": parse_failures,
        "run_notes": run_notes,
        "prompt_version": prompt_version,
        "eval_version": eval_version
    }

def outputs_to_extractions(outputs):
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