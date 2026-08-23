from Bio import Entrez
import pandas as pd

def construct_corpus(queries, summary: bool):

    """

    """

    # PMIDs
    pmids = []
    titles = []
    abstracts = []
    authors = []
    journals = []
    years = []
    dois = []
    search_queries = []

    for query in queries:

        papers = query["papers"]["PubmedArticle"]

        query_text = query["query text"]

        for paper in papers:

            medlinecitation = paper["MedlineCitation"]

            article = medlinecitation["Article"]

            # paper_id
            if medlinecitation.get("PMID"):
                paper_id = medlinecitation["PMID"]
            else:
                paper_id = None

            pmids.append(paper_id)

            # title
            if article.get("ArticleTitle"):
                title = f"{article ["ArticleTitle"]}"
            else:
                title = None

            titles.append(title)

            # abstract
            if article .get("Abstract"):
                if article ["Abstract"].get("AbstractText"):
                    abstract = " ".join(
                        str(text) for text in article ["Abstract"]["AbstractText"]
                    )
                else:
                    abstract = None
            else: abstract = None

            abstracts.append(abstract)

            # journal
            if article ["Journal"].get("Title"):
                journal = article ["Journal"]["Title"]
            else:
                journal = None

            journals.append(journal)

            # year
            if article["Journal"]["JournalIssue"]["PubDate"] .get("Year"):
                year = article["Journal"]["JournalIssue"]["PubDate"]["Year"]
            else:
                year = None

            years.append(year)

    corpus = pd.DataFrame({
        "pmid": pmids,
        "title": titles,
        "abstract": abstracts,
        "journal": journals,
        "year": years
    })

    processed_corpus = (
        corpus
        .drop_duplicates(subset="pmid")
        .dropna(subset=["pmid", "abstract"])
    )

    pre_length = len(corpus)
    post_length = len(processed_corpus)

    num_duplicates_dropped = len(corpus) - len(corpus.drop_duplicates(subset="pmid"))
    num_absna_dropped = len(corpus) - len(corpus.dropna(subset=["pmid", "abstract"]))

    if summary == True:
        construction_summary = pd.DataFrame({
            "Summary Metric": ["Value"],
            "Retrieved Papers": [pre_length],
            "Duplicates Removed": [num_duplicates_dropped],
            "Missing Abstracts Removed": [num_absna_dropped],
            "Final Corpus Size": [len(processed_corpus)]
        })

        construction_summary.set_index("Summary Metric", inplace=True)

    return processed_corpus

def fetch_papers(query, engine, num_articles):
    search_handle = Entrez.esearch(
        db=engine,
        term=query,
        retmax=num_articles
    )

    search_results = Entrez.read(search_handle)

    ids = search_results["IdList"]

    fetch_handle = Entrez.efetch(
        db=engine,
        id=",".join(ids),
        rettype="abstract",
        retmode="xml"
    )

    papers = Entrez.read(fetch_handle)

    return papers

def make_query_dict(query, engine, num_articles):

    papers = fetch_papers(query, engine, num_articles)

    query_dict = {
        "query text": query,
        "papers": papers
    }

    return query_dict