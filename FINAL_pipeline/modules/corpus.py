import os

import pandas as pd
import random
import json

def get_gt_dict(ner_gt, re_gt, abstracts_eval) -> dict:

    ner_dict = set(zip(
        ner_gt["pmid"],
        ner_gt["text"].str.strip().str.lower(),
        ner_gt["entity_type"]
    ))

    re_dict = set(zip(
        re_gt["pmid"],
        re_gt["entity_1"].str.strip().str.lower(),
        re_gt["relation"],
        re_gt["entity_2"].str.strip().str.lower()
    ))

    return {
        "ner": ner_dict,
        "re": re_dict,
        "eval_pmids": set(abstracts_eval.index)
    }