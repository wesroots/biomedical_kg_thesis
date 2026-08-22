DATA_CONFIG = {
    "train": {
        "name": "biored_train",
        "paths": {
            "abstracts": "../../data/processed/biored/br_train.csv",
            "ground_truths": "../../data/processed/biored/br_train_entity_relations.csv",
            "entities_ground_truths": "../../data/processed/biored/br_train_entities.csv",
            "epi_dir": "../../data/results/epis/biored_train"
        },
        "sample_size": 35,
    },
    "dev": {
        "name": "biored_dev",
        "paths": {
            "abstracts": "../../data/processed/biored/br_dev.csv",
            "ground_truths": "../../data/processed/biored/br_dev_entity_relations.csv",
            "entities_ground_truths": "../../data/processed/biored/br_dev_entities.csv",
            "epi_dir": "../../data/results/epis/biored_dev"
        },
        "sample_size": None,
    },
    "test": {
        "name": "biored_test",
        "paths": {
            "abstracts": "../../data/processed/biored/br_test.csv",
            "ground_truths": "../../data/processed/biored/br_test_entity_relations.csv",
            "entities_ground_truths": "../../data/processed/biored/br_test_entities.csv",
            "epi_dir": "../../data/results/epis/biored_test"
        },
        "sample_size": None,
    },
    "contemporary": {
        "name": "contemporary",
        "paths": {
            "abstracts": "../../data/processed/contemporary/contemporary_corpus.csv",
            "ground_truths": "", # <--- NEEDS FIXING
            "entities_ground_truths": "", # <--- NEEDS FIXING
            "epi_dir": "../../data/results/epis/contemporary"
        },
        "sample_size": None,
    }
}

FEW_SHOT_PATH = "../../data/few_shot/few_shot_block.txt"