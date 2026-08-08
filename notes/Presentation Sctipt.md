# MAST7865 Presentation Script
### Biomedical Knowledge Graph Construction Using LLMs: Evaluating Generalisation Beyond Benchmark Datasets
**Target length: ~10 minutes**

---

### Slide 1 — Title (≈20 seconds)

Hello, I'm Wesley Roots, and this presentation covers my Data Science Project on using large language models to construct biomedical knowledge graphs from scientific literature. The central question I'll be addressing is whether an extraction pipeline that performs well on a standard benchmark continues to perform well when applied to current, real-world literature.

---

### Slide 2 — Project Aim & Motivation (≈90 seconds)

**[1]** Biomedical literature is being published at an extremely high rate with tens of thousands of new papers each week making it increasingly difficult for researchers to track how entities such as genes, diseases, and drugs relate to one another across the literature. Knowledge graphs address this problem by representing relationships between biomedical concepts in a structured form that can be searched and queried, rather than requiring researchers to analyse papers individually.

**[2]** Constructing these graphs has traditionally required manual extraction of entities and relationships, which does not scale to the volume of literature being produced. Recent work has therefore explored using large language models to automate this extraction step.

**[3]** This is where the gap I'm addressing arises. Existing extraction systems are developed and evaluated exclusively on fixed benchmark datasets, and evaluation typically stops there. Whether a pipeline that performs well on a static benchmark continues to perform well when applied to newer literature that the benchmark does not exactly represent — literature published after a model's training cutoff — is rarely examined.

**[4]** This project therefore investigates the following: if an extraction pipeline is developed on an established benchmark, frozen, and then applied without modification to a newly assembled, unlabelled, contemporary corpus, how much does its performance degrade? Investigating that gap is the core contribution of this project.

---

### Slide 3 — Research Questions (≈60 seconds)

This motivation leads to two research questions.

**[1]** RQ1 asks how effectively an LLM-based information extraction pipeline can extract biomedical entities and relationships from scientific abstracts for the purpose of constructing a knowledge graph. This question is primarily concerned with establishing a well-evaluated pipeline in the first instance.

**[2]** RQ2 is the more novel of the two: to what extent does a pipeline developed on an existing benchmark corpus generalise to a newly assembled, contemporary biomedical corpus?

---

### Slide 4 — Three-Stage Methodology (≈120 seconds)

To answer this, a three-stage methodology was designed, summarised by the diagram shown.

**[1]** The first stage is pipeline development, conducted entirely on BioRED, a well-established, manually annotated benchmark corpus for biomedical relation extraction. At this stage, the extraction pipeline is iteratively refined through prompt engineering, structured JSON outputs, and evaluation logic improvements, with performance initially evaluated after each change using precision, recall and F1. Once performance is satisfactory, the pipeline is frozen. From that point onward, no further prompt or evaluation logic modifications are permitted, which is what allows the subsequent comparison to be fair.

**[2]** The second stage is contemporary application. A corpus of current biomedical abstracts is automatically retrieved from PubMed, meaning this data is unseen and unlabelled, in contrast to the benchmark corpus. The frozen pipeline is applied to this corpus without modification, and a knowledge graph is constructed from the extracted entities and relationships. Ontology-guided validation is also performed at this stage to normalise entity names and map them to standard identifiers. It should be emphasised that this step improves the quality of the resulting graph; it does not feed back into or tune the extraction pipeline in any way.

**[3]** The third stage is generalisation evaluation. A representative sample of the contemporary corpus is manually annotated to produce ground truth, and the frozen pipeline's extraction performance on that sample is evaluated using the evaluation metrics developed on the benchmark corpus. Comparing benchmark performance against contemporary performance is the central analysis of this project; any observed degradation is itself a meaningful finding, rather than a shortcoming.

---

### Slide 5 — Pipeline Development Progress (≈90 seconds)

**[1]** Development has proceeded along two parallel tracks that build cumulatively on one another: prompt design and evaluation logic. **[2]** Each row in this table represents a complete, finalised configuration where **[3]** performance is evaluated after every change, **[4]** and error analysis informs the subsequent refinement. **[5]** This is continued until performance plateaus.

**[Morph]** On the prompting side, development began with a baseline prompt using only unofficial, basic instructions. This provided a baseline reference for subsequent pipeline iterations. The official BioRED annotation guidelines were then incorporated directly into the prompt, so that the model follows the same entity and relation definitions used by the human annotators. Few-shot prompting was then added on top of this, providing the model with a small number of worked examples. Each version builds on the previous one; the few-shot version still includes the guidelines rather than replacing them.

On the evaluation side, development began with strict, exact-match metrics, which proved quite unforgiving, as they penalise any and all differences in wording or entity boundaries that do not reflect a genuinely incorrect extraction. Relaxed evaluation was introduced next, allowing partial matches which helped fix the entity boundaries issue, however, exact wording mismatches were still inflating errors. Cosine similarity scoring using pre-trained biomedical transformer embeddings were then added, providing a fairer semantic comparison — for example, recognising "myocardial infarction" as correct where the gold label reads "heart attack," rather than penalising it as a miss.

The latest refinement introduces relation-order invariance. Symmetric relations such as associations should be considered equivalent regardless of entity order. However, this is not true for directional relations such as causes. Ensuring order invariance is only applied where appropriate remains an active area of investigation.

---

### Slide 6 — Current Findings (≈90 seconds)

The findings from this iterative process to date are as follows.

**[1]** First, consistent, progressive improvement has been observed across successive iterations, with each refinement to either the prompt or the evaluation logic moving performance in the intended direction, indicating that the development process is well-founded.

**[2]** Second, entity extraction consistently outperforms relation extraction. This is unsurprising, as identifying that a span of text refers to, for example, a gene or a disease is a comparatively simpler task than correctly identifying the semantic relationship between two entities, particularly where a sentence from the literature contains several candidate relationships.

**[3]** Third, the introduction of cosine similarity scoring provided a considerably fairer assessment of semantic correctness than exact-match evaluation alone, which had been underestimating true performance by penalising valid paraphrasing.

**[4]** Finally, the most recent pipeline iteration exhibits very high recall — the model identifies almost all relations present in the text — but only with moderate precision, meaning it also proposes a meaningful number of incorrect relations.

**[5]** The current focus of ongoing work is therefore to improve precision without sacrificing recall, alongside resolving the relation-direction issue described previously. These are the two principal outstanding tasks before this stage of the project is complete.

---

### Slide 7 — Remaining Work (≈60 seconds)

Four main tasks remain. 

**[1]** First, finalise the pipeline refinement and select the best-performing configuration, including resolving the relation-order issue. 

**[2]** Second, carry out ontology-guided validation to normalise the extracted entities and relationships.

**[3]** Third, apply the frozen pipeline to the full contemporary PubMed corpus and construct the knowledge graph.

**[4]** Fourth, and most directly relevant to the research question, manually annotate a representative sample of the contemporary corpus and evaluate the extent to which extraction performance changes relative to BioRED.

This final comparison represents the central outcome of the project: it indicates whether benchmark performance can be considered a reliable proxy for real-world performance.

---

### Slide 8 — References (≈15 seconds)

*[Brief, don't read the list aloud — just gesture to it]*

Thank you for listening. 

---