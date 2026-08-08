### Run 001
- **Prompt v1**
- **Eval. v1**
#### Notes:
- No refinement - intended to only fit an initial test extraction + eval
- No-shot
- No normalisation
- Only schema (JSON format)
- R, P, F1 = 0 as expected

### Run 002
- **Prompt v2**
- **Eval. v1**
#### Notes:
- Added BioRED entity and relation types on top of Run 001
- Entities: recall decent start, precision bad, f1 below moderate
- Relations: recall low, precision awful, f1 awful
- Suggests entities easier to extract & model over-extracts given significantly higher recall over precision

### Run 003
- **Prompt v2**
- **Eval. v2**
#### Notes:
- New parser logic stores relaxed match as well as original strict match
	- Works by checking if predicted string matches or is in GT string or if GT string is in predicted string
- Relaxed matches expectedly better than strict for entities and relations
- Again, in relaxed match, recall far superior than precision
	- However, relation relaxed match recall & precision is still awful 

### Run 004
- **Prompt v3**
- **Eval. v2**
#### Notes:
- Added few-shot on top of prompt v2
- Significant improvement in all metrics except entity relaxed-recall (slight decrease)
	- Biggest relative improvements seen in relations
- Relations still suffering massively
	- Strict: P = 0.1527, R = 0.2027, F1 = 0.1742
	- Relaxed: P = 0.2316, R = 0.3074, F1 = 0.2642
- To refine for run 005, sampled FP & FN will be analysed

>[!note] Sample FP & FN Insights
>- LLM extracts semantically plausible concepts, not BioRED
>	- Suggest follow BioRED annotation policy?
>- Exact spans are an issue
>	- Model often chooses abbreviations
>	- Suggest same as above?

### Run 005
- **Prompt v3**
- **Eval. v3**
#### Notes:
- **Through analysis into FNs and FPs, the reason for the relations' terrible performance is slightly elucidated**
	- *Relationship extraction requires more independent things to be correct simultaneously* - this is an EVAL PROBLEM, not an extraction problem
		- *Entity match* -> 1 string match + one categorical match
			- One point of failure on hard part (text)
		- *Relationship match* -> 1 string match + 1 categorical match + 1 string match
			- Two points of failure on hard part (text)
- **Above is justification for using cosine similarity**
	- Matches by semantic similarity -> captures paraphrase/boundary variation
	- Gives fairer read on extraction quality vs. just span-matching "luck"
### Run 00x
- **Prompt v**
- **Eval. v**
#### Notes:
