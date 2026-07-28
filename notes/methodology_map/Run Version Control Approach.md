>[!note] Modular structure built for easy parsing step version access and control
>- `parsing.py`
>- `evaluation.py`
>- `exporting.py`
>
>Easy application onto BioRED Dev. and Test sets

>[!warning] Why not existing evaluation logic?
>- Requires normalised concept IDs, not text spans
>	- Assumes entities already linked to a database ID (NCI Gene, MeSG, etc.)
>- Novelty tags are not in my extraction schema
>	- Adding would be a schema change, not evaluation change - out of scope
>- "Entity Pair" approach could be used but slightly redundant and requires excessive engineering at this point (by prompt v3, eval v2)
>	- Extracting entities and relations separately kind of tells us this anyway - relation extraction is far poorer than entity, therefore an EP approach would likely just tell us this again

### Prompt JSON
- **Allows easy access to different prompt versions**
- **Any pipeline combination can be easily applied to BioRED Dev set**
	- Structure applies to `parsing.py`, `evaluation.py` and `exporting.py` also

### Parsing Module
- **One parsing logic version** as of now

### Evaluation Module
- **`evaluation_v1`**
	- Strict matches
- **`evaluation_v2`**
	- Strict matches
	- Relaxed matches
- **`evaluation_v3`**
	- Relaxed matches
	- Strict matches
	- Cosine similarity logic

### Exporting Module
- **One exporting logic version** as of now