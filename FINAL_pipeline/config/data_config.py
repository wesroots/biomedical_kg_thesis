DATA_CONFIG = {
    "biored_test": {
        "abstracts": {
            "abstracts_full": "../data/processed/biored/br_test.csv",
            "abstracts_eval": "../data/processed/biored/br_test.csv"
        },
        "ground_truths": {
            "ner": "../data/processed/biored/br_test_entities.csv",
            "re": "../data/processed/biored/br_test_entity_relations.csv"
        },
        "output_directory": "../data/results/final/biored_test/"
    },
    "contemporary": {
        "abstracts": {
            "abstracts_full": "../data/processed/contemporary/contemporary_corpus.csv",
            "abstracts_eval": "../data/processed/contemporary/cbc_downsampled_abstracts.csv"
        },
        "ground_truths": {
            "ner": "../data/processed/contemporary/cbc_ner_gt.csv",
            "re": "../data/processed/contemporary/cbc_re_gt.csv"
        },
        "output_directory": "../data/results/final/contemporary/"
    }
}

FEW_SHOT_PATH = "../data/few_shot/few_shot_block.txt"

BIORED_GUIDELINES_PATH = "../data/processed/biored/guidelines.txt"