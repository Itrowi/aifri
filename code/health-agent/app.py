from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import httpx
import os
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

NCBI_API_KEY = os.getenv("NCBI_API_KEY")

PUBMED_SEARCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
PUBMED_FETCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"


async def search_pubmed(term: str, retmax: int = 5):
    params = {
        "db": "pubmed",
        "term": term,
        "retmode": "json",
        "retmax": str(retmax),
    }
    if NCBI_API_KEY:
        params["api_key"] = NCBI_API_KEY

    async with httpx.AsyncClient(timeout=10.0) as client:
        r = await client.get(PUBMED_SEARCH_URL, params=params)
        r.raise_for_status()
        data = r.json()
        ids = data.get("esearchresult", {}).get("idlist", [])
        return ids


async def fetch_abstract(pmid: str):
    params = {
        "db": "pubmed",
        "id": pmid,
        "retmode": "xml",
    }
    if NCBI_API_KEY:
        params["api_key"] = NCBI_API_KEY

    async with httpx.AsyncClient(timeout=10.0) as client:
        r = await client.get(PUBMED_FETCH_URL, params=params)
        r.raise_for_status()
        xml = r.text
        soup = BeautifulSoup(xml, "lxml")
        abstract_text = ""
        for abst in soup.find_all("abstract"):
            abstract_text += " ".join(p.get_text(separator=" ") for p in abst.find_all("abstracttext"))
        title = soup.find("articletitle").get_text() if soup.find("articletitle") else ""
        return {"pmid": pmid, "title": title, "abstract": abstract_text}


def simplify_text(text: str) -> str:
    # Very simple rule-based simplification: short sentences, remove parentheses content, replace jargon with plain words via small dict
    import re

    replacements = {
        "randomized": "randomly assigned",
        "placebo": "inactive treatment",
        "cohort": "group of people",
        "mortality": "death rate",
        "morbidity": "illness",
    }

    # remove bracketed content
    text = re.sub(r"\([^)]*\)", "", text)
    for k, v in replacements.items():
        text = re.sub(rf"\b{k}\b", v, text, flags=re.IGNORECASE)

    # split into shorter sentences
    sentences = re.split(r"(?<=[.!?]) +", text)
    short = []
    for s in sentences:
        if len(s) > 300:
            parts = [s[i:i+200] for i in range(0, len(s), 200)]
            short.extend(parts)
        else:
            short.append(s)
    return " ".join(short)


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/explain", response_class=HTMLResponse)
async def explain(request: Request, topic: str = Form(...)):
    ids = await search_pubmed(topic, retmax=5)
    results = []
    for pmid in ids:
        item = await fetch_abstract(pmid)
        simple = simplify_text(item.get("abstract", ""))
        if not simple:
            simple = "No abstract available."
        results.append({"pmid": pmid, "title": item.get("title"), "simple": simple})
    return templates.TemplateResponse("results.html", {"request": request, "topic": topic, "results": results})
