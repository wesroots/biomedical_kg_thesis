"""
Named Entity Normalisation (NEN) against type-appropriate public ontologies:

    GeneOrGeneProduct           -> NCBI Gene            (E-utilities, db=gene)
    ChemicalEntity               -> MeSH                 (E-utilities, db=mesh)
    DiseaseOrPhenotypicFeature    -> MeSH                 (E-utilities, db=mesh)
    OrganismTaxon                -> NCBI Taxonomy        (E-utilities, db=taxonomy)
    CellLine                     -> Cellosaurus          (REST API)
    SequenceVariant               -> dbSNP / NCBI Variation Services (best-effort)

No UMLS license required -- all of these are open, unauthenticated services.

Rate limiting: NCBI E-utilities allow 3 req/sec without an API key, 10/sec with
one (set NCBI_EMAIL / NCBI_API_KEY below). A simple on-disk cache avoids
re-querying the same (type, text) pair across runs -- important since this
notebook can be re-run while iterating on downstream steps.
"""

import json
import re
import time
from pathlib import Path
from urllib.parse import quote

import requests

EUTILS_BASE = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
CELLOSAURUS_BASE = "https://api.cellosaurus.org/search/cell-line"
NCBI_VARIATION_BASE = "https://api.ncbi.nlm.nih.gov/variation/v0"

# NCBI asks for an email/tool identifier, and more req/sec if you have an API key.
# Get a free key at https://www.ncbi.nlm.nih.gov/account/settings/ (Settings -> API Key Management).
NCBI_EMAIL = None
NCBI_API_KEY = None
_REQUEST_DELAY = 0.34  # ~3/sec without an API key; set to 0.11 (~9/sec) if NCBI_API_KEY is set

RSID_PATTERN = re.compile(r"^rs\d+$", re.IGNORECASE)


# ---------------------------------------------------------------------------
# Cache
# ---------------------------------------------------------------------------

def load_cache(cache_path):
    cache_path = Path(cache_path)
    if cache_path.exists():
        with open(cache_path, "r") as f:
            return json.load(f)
    return {}


def save_cache(cache, cache_path):
    cache_path = Path(cache_path)
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    with open(cache_path, "w") as f:
        json.dump(cache, f, indent=2)


def _cache_key(entity_type, text):
    return f"{entity_type}::{text.strip().lower()}"


# ---------------------------------------------------------------------------
# Low-level E-utilities helper
# ---------------------------------------------------------------------------

def _eutils_esearch(db, term, retmax=1):
    params = {"db": db, "term": term, "retmode": "json", "retmax": retmax}
    if NCBI_EMAIL:
        params["email"] = NCBI_EMAIL
    if NCBI_API_KEY:
        params["api_key"] = NCBI_API_KEY

    resp = requests.get(EUTILS_BASE + "esearch.fcgi", params=params, timeout=15)
    resp.raise_for_status()
    time.sleep(_REQUEST_DELAY)
    return resp.json()


def _eutils_esummary(db, uid):
    params = {"db": db, "id": uid, "retmode": "json"}
    if NCBI_EMAIL:
        params["email"] = NCBI_EMAIL
    if NCBI_API_KEY:
        params["api_key"] = NCBI_API_KEY

    resp = requests.get(EUTILS_BASE + "esummary.fcgi", params=params, timeout=15)
    resp.raise_for_status()
    time.sleep(_REQUEST_DELAY)
    return resp.json()


# ---------------------------------------------------------------------------
# Type-specific normalisers
# Each returns: {"normalized_id": str|None, "normalized_name": str|None,
#                "source": str, "resolved": bool, "note": str|None}
# ---------------------------------------------------------------------------

def normalize_gene(text, organism=None):
    term = f"{text}[sym]"
    if organism:
        term += f' AND "{organism}"[orgn]'

    try:
        result = _eutils_esearch("gene", term)
        ids = result.get("esearchresult", {}).get("idlist", [])
        if not ids:
            # fall back to a broader, unrestricted-field search
            result = _eutils_esearch("gene", text)
            ids = result.get("esearchresult", {}).get("idlist", [])
        if not ids:
            return {"normalized_id": None, "normalized_name": None,
                    "source": "NCBI Gene", "resolved": False, "note": "no match"}

        gene_id = ids[0]
        summary = _eutils_esummary("gene", gene_id)
        doc = summary.get("result", {}).get(gene_id, {})
        name = doc.get("name") or doc.get("description") or text

        return {"normalized_id": f"NCBIGene:{gene_id}", "normalized_name": name,
                "source": "NCBI Gene", "resolved": True, "note": None}
    except requests.RequestException as e:
        return {"normalized_id": None, "normalized_name": None,
                "source": "NCBI Gene", "resolved": False, "note": f"request error: {e}"}


def normalize_mesh(text):
    try:
        result = _eutils_esearch("mesh", text)
        ids = result.get("esearchresult", {}).get("idlist", [])
        if not ids:
            return {"normalized_id": None, "normalized_name": None,
                    "source": "MeSH", "resolved": False, "note": "no match"}

        mesh_id = ids[0]
        summary = _eutils_esummary("mesh", mesh_id)
        doc = summary.get("result", {}).get(mesh_id, {})
        name = doc.get("ds_meshterms", [text])
        name = name[0] if isinstance(name, list) and name else text

        return {"normalized_id": f"MeSH:{mesh_id}", "normalized_name": name,
                "source": "MeSH", "resolved": True, "note": None}
    except requests.RequestException as e:
        return {"normalized_id": None, "normalized_name": None,
                "source": "MeSH", "resolved": False, "note": f"request error: {e}"}


def normalize_taxon(text):
    try:
        result = _eutils_esearch("taxonomy", text)
        ids = result.get("esearchresult", {}).get("idlist", [])
        if not ids:
            return {"normalized_id": None, "normalized_name": None,
                    "source": "NCBI Taxonomy", "resolved": False, "note": "no match"}

        tax_id = ids[0]
        summary = _eutils_esummary("taxonomy", tax_id)
        doc = summary.get("result", {}).get(tax_id, {})
        name = doc.get("scientificname", text)

        return {"normalized_id": f"NCBITaxon:{tax_id}", "normalized_name": name,
                "source": "NCBI Taxonomy", "resolved": True, "note": None}
    except requests.RequestException as e:
        return {"normalized_id": None, "normalized_name": None,
                "source": "NCBI Taxonomy", "resolved": False, "note": f"request error: {e}"}


def normalize_cellline(text):
    try:
        params = {"q": text, "format": "json", "fields": "id,ac", "rows": 1}
        resp = requests.get(CELLOSAURUS_BASE, params=params, timeout=15)
        resp.raise_for_status()
        time.sleep(_REQUEST_DELAY)
        data = resp.json()

        results = data.get("Cellosaurus", {}).get("cell-line-list", [])
        if not results:
            return {"normalized_id": None, "normalized_name": None,
                    "source": "Cellosaurus", "resolved": False, "note": "no match"}

        cl = results[0]
        ac = cl.get("accession", {}).get("value") if isinstance(cl.get("accession"), dict) else cl.get("accession")
        name = cl.get("name", {}).get("value") if isinstance(cl.get("name"), dict) else cl.get("name", text)

        if not ac:
            return {"normalized_id": None, "normalized_name": None,
                    "source": "Cellosaurus", "resolved": False,
                    "note": "match found but accession missing -- check response shape"}

        return {"normalized_id": f"Cellosaurus:{ac}", "normalized_name": name,
                "source": "Cellosaurus", "resolved": True, "note": None}
    except requests.RequestException as e:
        return {"normalized_id": None, "normalized_name": None,
                "source": "Cellosaurus", "resolved": False, "note": f"request error: {e}"}


def normalize_variant(text):
    """
    Best-effort only, per the 'moderate' practicality noted for variants:
    - Bare rsIDs (rs1234...) resolve cleanly via dbSNP.
    - Free-text HGVS-style notation (e.g. "c.274C>T") without a transcript/
      genomic accession CANNOT be reliably resolved automatically -- NCBI
      Variation Services needs a fully qualified reference (e.g.
      "NM_000518.4:c.27dupG"), which these extractions don't carry. These are
      marked unresolved rather than guessed at.
    """
    cleaned = text.strip()

    if RSID_PATTERN.match(cleaned):
        try:
            resp = requests.get(f"{EUTILS_BASE}esummary.fcgi",
                                 params={"db": "snp", "id": cleaned.lstrip("rR").lstrip("sS"),
                                         "retmode": "json"}, timeout=15)
            resp.raise_for_status()
            time.sleep(_REQUEST_DELAY)
            return {"normalized_id": f"dbSNP:{cleaned.lower()}", "normalized_name": cleaned.lower(),
                    "source": "dbSNP", "resolved": True, "note": None}
        except requests.RequestException as e:
            return {"normalized_id": None, "normalized_name": None,
                    "source": "dbSNP", "resolved": False, "note": f"request error: {e}"}

    # Has an explicit transcript/genomic accession prefix -> try NCBI Variation Services
    if ":" in cleaned and re.match(r"^[A-Z]{1,2}_\d+", cleaned):
        try:
            resp = requests.get(f"{NCBI_VARIATION_BASE}/hgvs/{quote(cleaned)}/contextuals", timeout=15)
            resp.raise_for_status()
            time.sleep(_REQUEST_DELAY)
            data = resp.json()
            spdi = data.get("data", {}).get("spdis", [{}])[0] if data.get("data") else {}
            spdi_str = ":".join(str(spdi[k]) for k in ("seq_id", "position", "deleted_sequence", "inserted_sequence")
                                 if k in spdi) if spdi else None
            if spdi_str:
                return {"normalized_id": f"SPDI:{spdi_str}", "normalized_name": cleaned,
                        "source": "NCBI Variation Services", "resolved": True, "note": None}
        except (requests.RequestException, KeyError, IndexError) as e:
            return {"normalized_id": None, "normalized_name": None,
                    "source": "NCBI Variation Services", "resolved": False, "note": f"request error: {e}"}

    return {"normalized_id": None, "normalized_name": None, "source": "unresolved",
            "resolved": False, "note": "free-text variant notation lacks a transcript/genomic accession"}


NORMALIZERS = {
    "GeneOrGeneProduct": normalize_gene,
    "ChemicalEntity": normalize_mesh,
    "DiseaseOrPhenotypicFeature": normalize_mesh,
    "OrganismTaxon": normalize_taxon,
    "CellLine": normalize_cellline,
    "SequenceVariant": normalize_variant,
}


def normalize_entity(text, entity_type, cache=None, cache_path=None):
    """
    Dispatch to the correct type-specific normalizer, with optional caching.
    Returns the same dict shape as the individual normalize_* functions.
    """
    if cache is not None:
        key = _cache_key(entity_type, text)
        if key in cache:
            return cache[key]

    normalizer = NORMALIZERS.get(entity_type)
    if normalizer is None:
        result = {"normalized_id": None, "normalized_name": None, "source": "unsupported",
                   "resolved": False, "note": f"no normalizer registered for type '{entity_type}'"}
    else:
        result = normalizer(text)

    if cache is not None:
        cache[_cache_key(entity_type, text)] = result
        if cache_path is not None:
            save_cache(cache, cache_path)

    return result
