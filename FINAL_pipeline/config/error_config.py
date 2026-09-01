ERROR_CATEGORIES = {
    "1": {
        "name": "Wrong relation type",
        "description": "The correct entity pair is identified, but the predicted relation type differs from the BioRED ground truth."
    },
    "2": {
        "name": "Duplicate/coreference",
        "description": "The error results from duplicate entity mentions, abbreviations, aliases, or coreferential mentions of the same underlying entity."
    },
    "3": {
        "name": "Unsupported relation",
        "description": "The predicted relation is not supported by the abstract or BioRED annotation policy."
    },
    "4": {
        "name": "Entity boundary/synonyms mismatch",
        "description": "The prediction and ground truth refer to the same underlying entity, but differ in span, wording, abbreviation, or synonym representation."
    },
    "5": {
        "name": "Missing relation",
        "description": "A BioRED ground-truth relation is supported by the abstract but was not extracted by the system."
    },
    "6": {
        "name": "Evaluation artefact",
        "description": "The prediction is substantively compatible with the ground truth, but is counted as an error because of the evaluation or matching procedure."
    },
    "7": {
        "name": "Other/unclear",
        "description": "The primary cause cannot be confidently assigned to any other category."
    }
}