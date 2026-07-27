### Run 001
- **Prompt v1**
- **Prompt v1**
#### Notes:
- No refinement - intended to only fit an initial test extraction + eval
- No-shot
- No normalisation
- Only schema (JSON format)
- R, P, F1 = 0 as expected

### Run 002
- **Prompt v2**
- **Parser v1**
#### Notes:
- Added BioRED entity and relation types on top of Run 001
- Entities: recall decent start, precision bad, f1 below moderate
- Relations: recall low, precision awful, f1 awful
- Suggests entities easier to extract & model over-extracts given significantly higher recall over precision

### Run 003
- **Prompt v2**
- **Parser v2**
#### Notes:
- New parser logic stores relaxed match as well as original strict match
	- Works by checking if predicted string matches or is in GT string or if GT string is in predicted string
- Relaxed matches expectedly better than strict for entities and relations
- Again, in relaxed match, recall far superior than precision
	- However, relation relaxed match recall & precision is still awful 

### Run 004
- **Prompt v3**
- **Parser v2**
#### Notes:
- Added few-shot on top of prompt v2
- Significant improvement in all metrics except entity relaxed-recall (slight decrease)
	- Biggest relative improvements seen in relations
- Relations still suffering massively
	- Strict: P = 0.1425, R = 0.1959, F1 = 0.165
	- Relaxed: P = 0.2555, R = 0.3514, F1 = 0.2959
- To refine for run 005, sampled FP & FN will be analysed

>[!note] Sample FP & FN Insights
>- LLM extracts semantically plausible concepts, not BioRED
>	- Suggest follow BioRED annotation policy?
>- Exact spans are an issue
>	- Model often chooses abbreviations
>	- Suggest same as above?
>- 

### Run 00x
- **Prompt v**
- **Parser v**
#### Notes:
