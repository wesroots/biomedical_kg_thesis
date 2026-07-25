### Initial Plan
1. LLM outputs JSON
	- JSON comprised of `pmid` (`int`), `entities` (`list`), `relationships` (`list`)
2. JSON exported
3. JSON parsed into tabular data to match BioRED ground truth
4. Evaluation can be conducted on corresponding entity & relationship CSVs
	- Evaluation includes deterministic metrics
		- Maybe P/R/F1?

### Supervisor-Advised Plan
1. LLM outputs tabular data in the form of BioRED ground truth
2. LLM fed another prompt that evaluates LLM-output extractions against BioRED ground truth annotations
	- Evaluation score is output

### Decision
**Output JSON format, parse to tabular**
- JSON is safer:
	- Explicit field names
	- Nested entities and relations
	- Schema validation
	- Reliable conversion into pandas