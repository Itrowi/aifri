Health Agent — PubMed-based healthcare explainer

This small web agent searches PubMed for a topic, fetches top abstracts, and returns a very simple plain-language explanation for each result.

Important: This tool is for educational purposes only and is not medical advice. Always consult qualified health professionals for diagnosis or treatment.

Quick setup (PowerShell on Windows):

1. Create a virtual environment and activate it
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1

2. Install dependencies
   pip install -r requirements.txt

3. (Optional) Add an NCBI API key to increase request limits
   api sk-UzqJxmbR7WoHxCN1KR0eRw

4. Run the app
   uvicorn app:app --reload --port 8000

5. Open a browser at: http://localhost:8000

Notes and next steps
- The simplification is rule-based and intentionally simple. For higher-quality plain-language summaries, integrate a text-simplification model or an LLM.
- Respect PubMed/NCBI usage policies and add an API key if you will make many requests.
- This project is a minimal starting point. Add caching, rate-limiting, better parsing, and improved summarization for production use.
