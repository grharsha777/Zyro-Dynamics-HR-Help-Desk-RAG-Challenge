# Zyro Dynamics — HR Help Desk (AI Policy Assistant)

**NIAT × Kaggle RAG Challenge submission**

An HR policy chatbot that answers employee questions — leave, payroll, WFH, performance reviews, POSH, benefits, onboarding, separation, travel — grounded strictly in Zyro Dynamics' internal HR policy PDFs. Built as a hybrid-retrieval RAG pipeline with a scope guard so it refuses to answer anything outside HR policy.

## What it does

- Answers employee HR questions using **only** the content of the uploaded policy PDFs — no hallucinated numbers or dates.
- Refuses out-of-scope questions instead of guessing, via a dedicated LLM-based scope classifier.
- Cites the source document, page number, and HR category for every answer.
- Ships as a single-file Streamlit app (`app.py`) that works both on Kaggle and on a normal git-based Streamlit Cloud deployment.

## How it works — pipeline

1. **Corpus discovery** — scans `data/`, `corpus/`, `docs/`, the app directory, and Kaggle input paths for HR policy PDFs, so the same code runs unmodified on Kaggle or Streamlit Cloud.
2. **Loading & chunking** — `PyPDFLoader` loads each PDF; `RecursiveCharacterTextSplitter` splits into 1000-character chunks with 200-character overlap.
3. **HR category tagging** — each chunk is auto-tagged into one or more of 11 categories (Leave, Compensation, WFH/Remote, Performance, Benefits, IT/Security, POSH, Onboarding, Separation, Travel, Conduct) via keyword matching.
4. **Embeddings** — `BAAI/bge-large-en-v1.5` (via `langchain-huggingface`, CPU, normalized embeddings).
5. **Hybrid retrieval** — FAISS (MMR search, k=6, fetch_k=20) ensembled with BM25 (k=10) at a 70/30 weight. Falls back to FAISS-only if `rank_bm25` isn't installed.
6. **4-layer answer pipeline** (`ask_bot`):
   - **Layer 1 — Scope guard**: an LLM classifier tags the question `IN_SCOPE` / `OUT_OF_SCOPE` against an explicit list of HR topics; out-of-scope questions get a polite refusal instead of a retrieval attempt.
   - **Layer 2 — Hybrid retrieval**: pulls candidate chunks via the ensemble retriever (with a similarity-search fallback on failure).
   - **Layer 3 — Relevance floor**: if the top relevance score is below 0.20, the app refuses rather than answering from weak context.
   - **Layer 4 — Grounded generation**: LLaMA-3.3-70B (via Groq) generates the answer strictly from retrieved context, instructed to cite exact numbers/dates and to say so explicitly when the policy docs don't cover the question.
7. **Source attribution** — every answer displays deduplicated source file, page number, and HR category in an expandable citation panel, plus response time.

## Tech stack

| Component | Choice |
|---|---|
| LLM | LLaMA-3.3-70B-Versatile via Groq |
| Embeddings | BAAI/bge-large-en-v1.5 |
| Vector store | FAISS (MMR retrieval) |
| Keyword retrieval | BM25 (`rank_bm25`), ensembled 70/30 with FAISS |
| Orchestration | LangChain (`langchain`, `langchain-community`, `langchain-core`, `langchain-groq`, `langchain-huggingface`, `langchain-text-splitters`) |
| PDF parsing | `pypdf` via `PyPDFLoader` |
| UI | Streamlit |

## Repository contents

- `app.py` — the full Streamlit application (pipeline, scope guard, retrieval, UI).
- `Completed_Notebook.ipynb` — the original Kaggle notebook developing/validating the RAG pipeline.
- `README.md` — this file.

## Running locally

```bash
git clone https://github.com/grharsha777/Zyro-Dynamics-HR-Help-Desk-RAG-Challenge.git
cd Zyro-Dynamics-HR-Help-Desk-RAG-Challenge

pip install streamlit langchain langchain-community langchain-text-splitters \
    langchain-huggingface langchain-groq langchain-core faiss-cpu pypdf \
    sentence-transformers rank_bm25

# Add your HR policy PDFs to a `data/` folder next to app.py
mkdir data && cp /path/to/your/hr_policies/*.pdf data/

streamlit run app.py
```

You'll need a free [Groq API key](https://console.groq.com) — enter it in the sidebar at runtime (or set it as the `GROQ_API_KEY` environment variable).

## Sample questions the app is tuned for

- How many earned leave days per year?
- When is salary credited each month?
- What is the WFH policy for L3 employees?
- What health insurance do employees receive?
- How long does a PIP last?
- What are the POSH policy guidelines?
- What are travel expense reimbursement limits?
- How many days notice for resignation?

## Notes

- The corpus (HR policy PDFs) is not bundled in this repo — supply your own under `data/`, or attach the Kaggle dataset if running in a Kaggle environment.
- Answers are strictly grounded: if the policy documents don't cover a question, the assistant says so explicitly instead of guessing.

---
Built by [G R Harsha](https://github.com/grharsha777) for the NIAT × Kaggle RAG Challenge.
