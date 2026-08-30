import json


def outputs_to_extractions(outputs, confirmation=True):
    """Parse each output's JSON string into entities/relationships lists, per PMID."""
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
    """Flatten extractions into sets of tuples, ready for evaluation.py's match functions."""
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


def outputs_to_eval_tuples(outputs, confirmation=True):
    """
    One-call convenience wrapper for the final pipeline: takes the raw `outputs`
    list (pmid + JSON string per abstract) straight to eval-ready sets of tuples.

    Returns: (predictions_entities, predictions_relationships, parse_failures)
    """
    extractions, parse_failures = outputs_to_extractions(outputs, confirmation=confirmation)
    predictions_entities, predictions_relationships = extractions_to_tuples(extractions)
    return predictions_entities, predictions_relationships, parse_failures