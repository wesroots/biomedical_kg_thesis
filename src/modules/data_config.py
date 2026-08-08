DATA_CONFIG = {
    "train": {
        "paths": {
            "abstracts": "../../data/processed/biored/br_train.csv",
            "ground_truths": "../../data/processed/biored/br_train_entity_relations.csv",
            "epis": "../../data/results/epis/biored_train"
        },
        "sample_size": 35,
    },
    "dev": {
        "paths": {
            "abstracts": "../../data/processed/biored/br_dev.csv",
            "ground_truths": "../../data/processed/biored/br_dev_entity_relations.csv",
            "epi_dir": "../../data/results/epis/biored_dev"
        },
        "sample_size": None,
    },
    "test": {
        "paths": {
            "abstracts": "../../data/processed/biored/br_test.csv",
            "ground_truths": "../../data/processed/biored/br_test_entity_relations.csv",
            "epi_dir": "../../data/results/epis/biored_test"
        },
        "sample_size": None,
    },
    "contemporary": {
        "paths": {
            "abstracts": "../../data/processed/contemporary/contemporary_corpus.csv",
            "ground_truths": "../../data/processed/contemporary/[NULL].csv", # <--- NEEDS FIXING
            "epi_dir": "../../data/results/epis/contemporary"
        },
        "sample_size": None,
    }
}

FEW_SHOT_PATH = "../../data/few_shot/few_shot_block.txt"