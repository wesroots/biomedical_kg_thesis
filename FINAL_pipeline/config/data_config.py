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
        "log_directory": "../data/results/final/"
    },
    "contemporary": {
        "abstracts": {
            "abstracts_full": "../data/processed/contemporary/contemporary_corpus.csv",
            "abstracts_eval": "../data/processed/contemporary/cbc_downsampled_abstracts.csv"
        },
        "ground_truths": {
            "ner": "../data/processed/contemporary/cbc_ner.csv",
            "re": "../data/processed/contemporary/cbc_er.csv"
        },
        "log_directory": "../data/results/final/"
    }
}