
import requests
import csv
import xml.etree.ElementTree as ET

# PubMed search settings
url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"

params = {
    "db": "pubmed",
    "term": '("female genital mutilation"[Title/Abstract] OR "female genital cutting"[Title/Abstract]) AND Nigeria[Title/Abstract]',
    "retmax": 100,
    "retmode": "json",
    "sort": "relevance",
    "datetype": "pdat",
    "mindate": "2015",
    "maxdate": "2026"
}

headers = {
    "User-Agent": "FGMNigeriaResearch/1.0"
}

print("Searching PubMed for FGM research related to Nigeria...")

response = requests.get(
    url, params=params, headers=headers, timeout=30
)
response.raise_for_status()

ids = response.json()["esearchresult"]["idlist"]

if not ids:
    print("No articles found. We will adjust the search.")
    raise SystemExit

# Fetch article details
fetch_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"

fetch_params = {
    "db": "pubmed",
    "id": ",".join(ids),
    "retmode": "xml"
}

response = requests.get(
    fetch_url, params=fetch_params, headers=headers, timeout=60
)
response.raise_for_status()

root = ET.fromstring(response.content)
dataset = []
seen_ids = set()

for article in root.findall(".//PubmedArticle"):
    pmid = article.findtext(".//PMID", default="")

    if not pmid or pmid in seen_ids:
        continue

    seen_ids.add(pmid)

    title_element = article.find(".//ArticleTitle")
    title = "".join(title_element.itertext()).strip() if title_element is not None else ""

    abstract_parts = [
        "".join(item.itertext()).strip()
        for item in article.findall(".//Abstract/AbstractText")
    ]
    abstract = " ".join(abstract_parts)

    authors = []
    for author in article.findall(".//Author"):
        last = author.findtext("LastName", default="")
        fore = author.findtext("ForeName", default="")
        name = f"{fore} {last}".strip()
        if name:
            authors.append(name)

    year = ""
    for date_path in [
        ".//PubDate/Year",
        ".//ArticleDate/Year"
    ]:
        year = article.findtext(date_path, default="")
        if year:
            break

    journal = article.findtext(".//Journal/Title", default="")
    doi = ""

    for identifier in article.findall(".//ArticleId"):
        if identifier.attrib.get("IdType") == "doi":
            doi = identifier.text or ""
            break

    dataset.append({
        "pmid": pmid,
        "title": title,
        "authors": "; ".join(authors),
        "publication_year": year,
        "journal": journal,
        "abstract": abstract,
        "doi": doi,
        "article_url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"
    })

filename = "fgm_pubmed_sample.csv"

fieldnames = [
    "pmid", "title", "authors", "publication_year",
    "journal", "abstract", "doi", "article_url"
]

with open(filename, "w", newline="", encoding="utf-8-sig") as file:
    writer = csv.DictWriter(file, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(dataset)

print(f"Collected {len(dataset)} unique PubMed records.")
print(f"Saved to {filename}")
print("Next, we will validate each article's Nigerian study relevance.")
