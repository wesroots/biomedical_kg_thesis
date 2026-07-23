# ---- Summary Status ----
- **Exploring LLM options**
	- Extraction performance, pricing, implementation / feasibility, etc.
- **Exploring contemporary corpus sampling** feasibility + approach

# What LLM?
### OpenAI's GPT-5.6 Luna
- **Input price:** $1 / Input MTok
- **Output price:** $6 / Output MTok
- **Max output:** 128k tokens
- **Knowledge cutoff:** Feb 16, 2026
- **Other:**
	- Allows file search
	- Designed for cost-sensitive, high-volume workloads

### Anthropic's Claude Haiku 4.5
- **Input price:** $1 / Input MTok
- **Output price:** $5 / Output MTok
- **Max output:** 64k tokens
- **Knowledge cutoff:** Feb 2025

# Method of Calling LLM
### OpenAI API (Paid)
- Stable, well-documented API
- Strong structured JSON support (reliable type-safety)
- Manageable estimated cost (<£50)

```python
from openai import OpenAI
from pydantic import BaseModel

client = OpenAI()

class CalendarEvent(BaseModel):
    name: str
    date: str
    participants: list[str]

response = client.responses.parse(
    model="gpt-5.6",
    input=[
        {"role": "system", "content": "Extract the event information."},
        {
            "role": "user",
            "content": "Alice and Bob are going to a science fair on Friday.",
        },
    ],
    text_format=CalendarEvent,
)

event = response.output_parsed
```

# Contemporary Corpus + Sampling Size?
**BioRED:** 600
**BC5CDR:** 1500

### Current Contemporary Sizes:
- **Full corpus:** 990 (25 results per each of the 7 queries; 7 years per query)
- **Planned annotation sample:** 10% (99)
	- Pilot annotation of ~10 can help gauge time to annotate full sample

# What Evaluation?
### Benchmark Corpus
- Compare extracted entities and relationships against BioRED's annotations
	- Use precision, recall & F1 score
### Contemporary Corpus
- Frozen pipeline applied to contemporary corpus
	- Same evaluation procedure

# Why Cardiology?
- Well represented in PubMed
- CVD and related conditions within cardiology are hugely important + prevalent

# Why Just Abstracts?
- Easier to access at scale
- Aligns with existing research (BioRED & BC5CDR)

# Other
- Not using BioBERT or similar as task is to explore performance of generally-trained LLMs
- Contemporary corpus explores generalisation as it is independently assembled from recent literature, rather than being a fixed, semi-manually-curated benchmark dataset