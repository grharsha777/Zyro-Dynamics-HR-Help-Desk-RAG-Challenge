"""
╔══════════════════════════════════════════════════════════════════╗
║   ZYRO DYNAMICS — HR HELP DESK · AI-POWERED POLICY ASSISTANT    ║
║   NIAT × Kaggle RAG Challenge  |  Enterprise Edition            ║
║   Stack: Groq LLaMA-3.3-70B · FAISS + BM25 · BAAI/bge-large    ║
╚══════════════════════════════════════════════════════════════════╝
"""

import os
import glob
import time
import json
import traceback
from datetime import datetime

import streamlit as st

# ─────────────────────────────────────────────────────────────────────────────
# PAGE CONFIG  (must be the very first Streamlit call)
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Zyro Dynamics · HR Help Desk",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "Get Help": "https://github.com/grharsha777/Zyro-Dynamics-HR-Help-Desk-RAG-Challenge",
        "Report a bug": "https://github.com/grharsha777/Zyro-Dynamics-HR-Help-Desk-RAG-Challenge/issues",
        "About": "Zyro Dynamics HR Help Desk — powered by LangChain + Groq + FAISS.\nBuilt for the NIAT × Kaggle RAG Challenge.",
    },
)

# ─────────────────────────────────────────────────────────────────────────────
# CUSTOM CSS  — dark-navy enterprise theme
# ─────────────────────────────────────────────────────────────────────────────
st.markdown(
    """
<style>
/* ── Global resets ─────────────────────────────── */
html, body, [class*="css"] {
    font-family: 'Inter', 'Segoe UI', system-ui, sans-serif;
}
#MainMenu, footer, header { visibility: hidden; }

/* ── Sidebar ────────────────────────────────────── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0d1117 0%, #161b27 100%);
    border-right: 1px solid #21262d;
}
[data-testid="stSidebar"] * { color: #c9d1d9 !important; }
[data-testid="stSidebar"] .stButton > button {
    background: #1f2937;
    border: 1px solid #374151;
    color: #e5e7eb !important;
    border-radius: 8px;
    font-size: 0.82rem;
    text-align: left;
    transition: all 0.2s ease;
    padding: 0.5rem 0.75rem;
}
[data-testid="stSidebar"] .stButton > button:hover {
    background: #1e40af;
    border-color: #3b82f6;
    color: #fff !important;
    transform: translateX(3px);
}

/* ── Hero banner ────────────────────────────────── */
.hero-banner {
    background: linear-gradient(135deg, #0f172a 0%, #1e3a5f 50%, #0f172a 100%);
    border: 1px solid #1e40af33;
    border-radius: 16px;
    padding: 2.5rem 2rem 2rem;
    margin-bottom: 1.5rem;
    position: relative;
    overflow: hidden;
}
.hero-banner::before {
    content: '';
    position: absolute;
    top: -40%;
    right: -10%;
    width: 400px;
    height: 400px;
    background: radial-gradient(circle, #1e40af22, transparent 70%);
    border-radius: 50%;
}
.hero-tagline {
    font-size: 0.8rem;
    letter-spacing: 0.18em;
    color: #60a5fa;
    font-weight: 600;
    text-transform: uppercase;
    margin-bottom: 0.5rem;
}
.hero-title {
    font-size: 2.4rem;
    font-weight: 800;
    color: #f0f6ff;
    margin: 0 0 0.25rem;
    line-height: 1.1;
}
.hero-title em {
    font-style: italic;
    background: linear-gradient(90deg, #60a5fa, #818cf8);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.hero-desc {
    color: #94a3b8;
    font-size: 0.97rem;
    margin: 0.5rem 0 1.2rem;
    max-width: 680px;
    line-height: 1.6;
}
.hero-pills {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
    margin-bottom: 0.25rem;
}
.pill {
    display: inline-flex;
    align-items: center;
    gap: 0.3rem;
    background: #1e293b;
    border: 1px solid #334155;
    border-radius: 100px;
    padding: 0.25rem 0.75rem;
    font-size: 0.75rem;
    color: #94a3b8;
    font-weight: 500;
}
.pill-green  { border-color: #16a34a55; color: #4ade80; }
.pill-blue   { border-color: #1d4ed855; color: #60a5fa; }
.pill-purple { border-color: #7c3aed55; color: #a78bfa; }
.pill-yellow { border-color: #d9770655; color: #fbbf24; }

/* ── Stats row ──────────────────────────────────── */
.stats-row {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 1rem;
    margin-bottom: 1.5rem;
}
.stat-card {
    background: #0d1117;
    border: 1px solid #21262d;
    border-radius: 12px;
    padding: 1rem 1.25rem;
    text-align: center;
    transition: border-color 0.2s;
}
.stat-card:hover { border-color: #3b82f6; }
.stat-number {
    font-size: 2rem;
    font-weight: 800;
    color: #60a5fa;
    line-height: 1;
}
.stat-label {
    font-size: 0.72rem;
    color: #6b7280;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin-top: 0.35rem;
}

/* ── Chat bubbles ───────────────────────────────── */
[data-testid="stChatMessage"] {
    border-radius: 12px;
    padding: 0.25rem 0.5rem;
    margin-bottom: 0.5rem;
}

/* ── Source badges ──────────────────────────────── */
.src-badge {
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    background: #1e293b;
    border: 1px solid #334155;
    border-radius: 8px;
    padding: 0.35rem 0.85rem;
    font-size: 0.78rem;
    color: #93c5fd;
    margin: 0.25rem 0.25rem 0 0;
    font-weight: 500;
}
.src-badge .src-page {
    background: #1e3a5f;
    border-radius: 4px;
    padding: 1px 6px;
    font-size: 0.7rem;
    color: #60a5fa;
}

/* ── Info footer bar ────────────────────────────── */
.info-bar {
    background: #0d1117;
    border: 1px solid #21262d;
    border-radius: 10px;
    padding: 0.75rem 1rem;
    font-size: 0.78rem;
    color: #6b7280;
    margin-top: 1.5rem;
}
.info-bar strong { color: #60a5fa; }

/* ── OOS warning box ────────────────────────────── */
.oos-box {
    background: #1c0a0a;
    border-left: 4px solid #f87171;
    border-radius: 0 8px 8px 0;
    padding: 0.85rem 1rem;
    font-size: 0.9rem;
    color: #fca5a5;
}

/* ── Response time chip ─────────────────────────── */
.rt-chip {
    display: inline-block;
    background: #0f2027;
    border: 1px solid #1e3a5f;
    border-radius: 100px;
    padding: 2px 10px;
    font-size: 0.72rem;
    color: #38bdf8;
    margin-top: 0.4rem;
}

/* ── Expander tweak ─────────────────────────────── */
[data-testid="stExpander"] summary {
    font-size: 0.83rem;
    color: #60a5fa !important;
}
</style>
""",
    unsafe_allow_html=True,
)

# ─────────────────────────────────────────────────────────────────────────────
# SESSION STATE INIT
# ─────────────────────────────────────────────────────────────────────────────
def _init_state() -> None:
    defaults = {
        "chat_history"        : [],   # list of {"role", "content", "sources", "in_scope", "elapsed"}
        "generated_responses" : 0,
        "retrieved_sources"   : [],
        "pending_question"    : None,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

_init_state()

# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        """
        <div style="display:flex;align-items:center;gap:0.75rem;margin-bottom:1rem">
            <span style="font-size:2rem">🏢</span>
            <div>
                <div style="font-weight:700;color:#f0f6ff;font-size:1rem">Zyro Dynamics</div>
                <div style="font-size:0.72rem;color:#64748b">HR HELP DESK · AI</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.divider()

    # ── API keys ─────────────────────────────────────────────────────────────
    st.markdown("**⚙️ CONFIGURATION**")
    groq_key = st.text_input(
        "Groq API Key",
        type="password",
        value=os.environ.get("GROQ_API_KEY", ""),
        help="Get a free key at https://console.groq.com",
        placeholder="gsk_••••••••••••••••",
    )
    langchain_key = st.text_input(
        "LangChain API Key (optional)",
        type="password",
        value=os.environ.get("LANGCHAIN_API_KEY", ""),
        help="Enables LangSmith tracing for debugging & monitoring",
        placeholder="ls__••••••••••••••••",
    )

    st.divider()

    # ── Sample questions ─────────────────────────────────────────────────────
    st.markdown("**💡 SAMPLE QUERIES**")
    sample_qs = [
        "How many earned leave days per year?",
        "When is salary credited each month?",
        "What is the WFH policy for L3 employees?",
        "What health insurance coverage do employees get?",
        "How long is the PIP duration?",
        "What is the Annual Performance Review process?",
        "What is the payroll cut-off date?",
        "Explain the POSH policy at Zyro Dynamics.",
        "What are the travel expense reimbursement limits?",
        "How many days notice for resignation?",
    ]
    for sq in sample_qs:
        if st.button(sq, use_container_width=True, key=f"sq_{hash(sq)}"):
            st.session_state.pending_question = sq

    st.divider()

    # ── Status + controls ─────────────────────────────────────────────────────
    st.markdown("**📊 SESSION**")
    col_s1, col_s2 = st.columns(2)
    col_s1.metric("Queries", st.session_state.generated_responses)
    col_s2.metric("Turns", len(st.session_state.chat_history))

    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.chat_history        = []
        st.session_state.generated_responses = 0
        st.session_state.retrieved_sources   = []
        st.rerun()

    st.divider()
    st.markdown(
        "<div style='font-size:0.72rem;color:#4b5563;line-height:1.6'>"
        "<strong style='color:#60a5fa'>v2.0 · Enterprise Edition</strong><br>"
        "NIAT × Kaggle RAG Challenge<br>"
        "LangChain · FAISS · BM25 · Groq<br>"
        "BAAI/bge-large-en-v1.5<br>"
        "</div>",
        unsafe_allow_html=True,
    )

# ─────────────────────────────────────────────────────────────────────────────
# ENV VARS  (apply sidebar keys to environment)
# ─────────────────────────────────────────────────────────────────────────────
if groq_key:
    os.environ["GROQ_API_KEY"] = groq_key
if langchain_key:
    os.environ["LANGCHAIN_API_KEY"]    = langchain_key
    os.environ["LANGCHAIN_TRACING_V2"] = "true"
    os.environ["LANGCHAIN_PROJECT"]    = "zyro-rag-challenge"

# ─────────────────────────────────────────────────────────────────────────────
# RAG PIPELINE  (cached — loads ONCE per Streamlit session)
# ─────────────────────────────────────────────────────────────────────────────
@st.cache_resource(show_spinner="📚 Building HR knowledge base — please wait…")
def build_pipeline(_groq_key: str):
    """
    Full RAG pipeline:
      PDF loading → chunking → BAAI/bge-large embeddings → FAISS index
      BM25 retriever → Ensemble (FAISS 0.7 + BM25 0.3)
      Groq LLaMA-3.3-70B · dual-layer guardrails
    """
    from langchain_community.document_loaders import PyPDFLoader, TextLoader, CSVLoader
    from langchain_text_splitters import RecursiveCharacterTextSplitter
    from langchain_huggingface import HuggingFaceBgeEmbeddings
    from langchain_community.vectorstores import FAISS
    from langchain_community.retrievers import BM25Retriever
    from langchain.retrievers import EnsembleRetriever
    from langchain_groq import ChatGroq
    from langchain_core.prompts import ChatPromptTemplate
    from langchain_core.output_parsers import StrOutputParser

    # ── Locate corpus ─────────────────────────────────────────────────────────
    search_paths = [
        "/kaggle/input/niat-masterclass-rag-challenge/",
        "/kaggle/input/zyro-dynamics-hr-corpus/",
        "/kaggle/input/",
        "./data/",
        ".",
    ]
    pdf_files = []
    for base in search_paths:
        found = sorted(glob.glob(os.path.join(base, "**/*.pdf"), recursive=True))
        if found:
            pdf_files = found
            break

    if not pdf_files:
        st.error(
            "⚠️ No PDF files found. Attach the HR corpus dataset in Kaggle, "
            "or place PDFs in a `./data/` folder alongside app.py.",
            icon="📂",
        )
        st.stop()

    # ── Load documents ────────────────────────────────────────────────────────
    documents = []
    for path in pdf_files:
        try:
            loader = PyPDFLoader(path)
            docs   = loader.load()
            # Normalise source to just the filename
            for d in docs:
                d.metadata["source"] = os.path.splitext(os.path.basename(path))[0]
            documents.extend(docs)
        except Exception as exc:
            st.warning(f"Could not load {os.path.basename(path)}: {exc}")

    # Load TXTs and CSVs if present
    for base in search_paths:
        for txt in glob.glob(os.path.join(base, "*.txt")):
            try:
                docs = TextLoader(txt).load()
                for d in docs:
                    d.metadata["source"] = os.path.splitext(os.path.basename(txt))[0]
                documents.extend(docs)
            except Exception:
                pass
        for csv_f in glob.glob(os.path.join(base, "*.csv")):
            try:
                docs = CSVLoader(csv_f).load()
                for d in docs:
                    d.metadata["source"] = os.path.splitext(os.path.basename(csv_f))[0]
                documents.extend(docs)
            except Exception:
                pass
        if documents:
            break

    if not documents:
        st.error("No document content loaded. Check your corpus path.")
        st.stop()

    # ── Chunk ─────────────────────────────────────────────────────────────────
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    chunks = splitter.split_documents(documents)

    # Enrich metadata with HR category tags
    HR_CATEGORIES = {
        "Leave"         : ["leave", "earned leave", "sick leave", "maternity", "paternity",
                           "casual leave", "cl ", "el ", "sl "],
        "Compensation"  : ["salary", "payroll", "ctc", "bonus", "increment", "compensation",
                           "pay slip", "deduction", "tax"],
        "WFH/Remote"    : ["work from home", "wfh", "hybrid", "remote", "work location"],
        "Performance"   : ["performance", "pip", "apr", "kra", "kpi", "review", "rating",
                           "promotion", "appraisal"],
        "Benefits"      : ["insurance", "health", "medical", "dental", "vision", "benefit",
                           "provident fund", "pf ", "gratuity"],
        "IT/Security"   : ["it policy", "cybersecurity", "data protection", "password",
                           "device", "laptop", "software"],
        "POSH"          : ["posh", "harassment", "sexual", "iqc", "complaint"],
        "Onboarding"    : ["onboarding", "probation", "joining", "induction", "background"],
        "Separation"    : ["separation", "resignation", "notice period", "fnf", "full and final",
                           "termination", "exit"],
        "Travel"        : ["travel", "expense", "reimbursement", "per diem", "ticket", "hotel"],
        "Conduct"       : ["code of conduct", "ethics", "discipline", "misconduct", "nda"],
    }
    for chunk in chunks:
        text_lower = chunk.page_content.lower()
        tags = [cat for cat, kws in HR_CATEGORIES.items() if any(kw in text_lower for kw in kws)]
        chunk.metadata["hr_category"] = ", ".join(tags) if tags else "General"

    # ── Embeddings — BAAI/bge-large-en-v1.5 ──────────────────────────────────
    embeddings = HuggingFaceBgeEmbeddings(
        model_name="BAAI/bge-large-en-v1.5",
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True},
    )

    # ── FAISS vector store ────────────────────────────────────────────────────
    vectorstore = FAISS.from_documents(chunks, embeddings)
    faiss_retriever = vectorstore.as_retriever(
        search_type="mmr",
        search_kwargs={"k": 6, "fetch_k": 20, "lambda_mult": 0.65},
    )

    # ── BM25 keyword retriever ────────────────────────────────────────────────
    bm25_retriever        = BM25Retriever.from_documents(chunks)
    bm25_retriever.k      = 10

    # ── Ensemble retriever (semantic 70% + keyword 30%) ───────────────────────
    ensemble_retriever = EnsembleRetriever(
        retrievers=[faiss_retriever, bm25_retriever],
        weights=[0.7, 0.3],
    )

    # ── LLM ──────────────────────────────────────────────────────────────────
    llm = ChatGroq(
        model="llama-3.3-70b-versatile",
        temperature=0.1,
        max_tokens=768,
        api_key=_groq_key,
        streaming=True,
    )
    parser = StrOutputParser()

    # ── Prompts ───────────────────────────────────────────────────────────────
    RAG_PROMPT = ChatPromptTemplate.from_template(
        """You are an expert HR Help Desk assistant for Zyro Dynamics (also known as Acrux Dynamics).

Your role: Answer employee HR questions with precision using ONLY the policy context below.

Guidelines:
- Quote exact numbers, dates, percentages, and limits from the context.
- If multiple policies apply, mention each one with its source.
- Never invent information not present in the context.
- Format answers clearly — use bullet points for lists.
- If the context is insufficient, respond:
  "The HR policy documents do not contain sufficient detail to answer this question. Please contact HR directly."

HR Policy Context:
{context}

Employee Question: {question}

Grounded Answer:"""
    )

    OOS_PROMPT = ChatPromptTemplate.from_template(
        """You are a strict scope classifier for an HR policy chatbot.

Classify whether this question can be answered using Zyro Dynamics internal HR policy documents.

In-scope topics (HR policy documents cover ONLY):
- Leave entitlements (earned, sick, maternity, paternity, casual, etc.)
- Work-from-home, hybrid, and remote-work arrangements
- Employee code of conduct and ethics
- Performance reviews, PIP, APR, KRAs, promotions
- Salary, compensation, payroll dates, bonuses
- Health insurance and employee benefits (PF, gratuity, etc.)
- IT and cybersecurity policies
- Prevention of Sexual Harassment (POSH)
- Onboarding, probation, induction
- Separation, resignation, notice period, full-and-final settlement
- Business travel and expense reimbursement
- General company overview, grade structure, office policies

Question: {question}

Reply with EXACTLY one token: IN_SCOPE or OUT_OF_SCOPE"""
    )

    REFUSAL_MSG = (
        "I'm sorry — I can only answer HR-related questions using "
        "Zyro Dynamics internal policy documents. Your question appears to be "
        "outside that scope. Please reach out to the relevant department "
        "or consult an external resource for assistance."
    )

    # ── Document formatter ────────────────────────────────────────────────────
    def format_docs(docs) -> str:
        parts = []
        for i, doc in enumerate(docs, 1):
            src  = doc.metadata.get("source", "Unknown")
            page = doc.metadata.get("page", "?")
            cat  = doc.metadata.get("hr_category", "")
            tag  = f"  [{cat}]" if cat else ""
            parts.append(
                f"[Source {i}: {src}, page {page}{tag}]\n{doc.page_content}"
            )
        return "\n\n---\n\n".join(parts)

    # ── Core ask_bot function ─────────────────────────────────────────────────
    def ask_bot(question: str) -> dict:
        # Layer 1 — LLM scope guard
        try:
            verdict = parser.invoke(
                llm.invoke(OOS_PROMPT.invoke({"question": question}))
            ).strip().upper()
        except Exception:
            verdict = "IN_SCOPE"  # Fail open — let retrieval decide

        if "OUT_OF_SCOPE" in verdict:
            return {"answer": REFUSAL_MSG, "sources": [], "in_scope": False}

        # Layer 2 — Hybrid retrieval
        try:
            docs = ensemble_retriever.invoke(question)
        except Exception:
            docs = vectorstore.similarity_search(question, k=5)

        if not docs:
            return {"answer": REFUSAL_MSG, "sources": [], "in_scope": False}

        # Layer 3 — FAISS relevance score sanity check
        try:
            docs_scores = vectorstore.similarity_search_with_relevance_scores(question, k=3)
            if docs_scores and docs_scores[0][1] < 0.20:
                return {"answer": REFUSAL_MSG, "sources": [], "in_scope": False}
        except Exception:
            pass  # Skip score check if unsupported; carry on

        context = format_docs(docs)
        try:
            answer = parser.invoke(
                llm.invoke(RAG_PROMPT.invoke({"context": context, "question": question}))
            )
        except Exception as exc:
            return {
                "answer" : f"⚠️ LLM error: {exc}. Please try again.",
                "sources": [],
                "in_scope": True,
            }

        sources = []
        seen    = set()
        for doc in docs:
            src  = doc.metadata.get("source", "Unknown")
            page = doc.metadata.get("page", "?")
            cat  = doc.metadata.get("hr_category", "")
            key  = (src, page)
            if key not in seen:
                seen.add(key)
                sources.append({"file": src, "page": page, "category": cat})

        return {"answer": answer, "sources": sources, "in_scope": True}

    # ── Expose corpus stats for the hero banner ───────────────────────────────
    ask_bot._meta = {
        "n_docs"  : len(pdf_files),
        "n_chunks": len(chunks),
    }

    return ask_bot, vectorstore

# ─────────────────────────────────────────────────────────────────────────────
# GATE: require API key before loading pipeline
# ─────────────────────────────────────────────────────────────────────────────
if not groq_key:
    # Hero banner (teaser)
    st.markdown(
        """
        <div class="hero-banner">
            <div class="hero-tagline">Zyro Dynamics — Internal HR Platform</div>
            <div class="hero-title">HR Help Desk <em>powered by AI</em></div>
            <div class="hero-desc">
                Ask any question about company policies — leave entitlements, compensation,
                performance reviews, WFH arrangements, POSH guidelines, and more.
                Answers are grounded in official Zyro Dynamics HR documents.
            </div>
            <div class="hero-pills">
                <span class="pill pill-green">● Enter your Groq API key to start</span>
                <span class="pill pill-blue">LLaMA 3.3 · 70B via Groq</span>
                <span class="pill pill-purple">FAISS + BM25 Hybrid Search</span>
                <span class="pill pill-yellow">BAAI/bge-large-en-v1.5</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.info(
        "👈 **Enter your Groq API Key** in the sidebar to initialise the HR assistant.  \n"
        "Get a free key at [console.groq.com](https://console.groq.com).",
        icon="🔑",
    )
    st.stop()

# ─────────────────────────────────────────────────────────────────────────────
# BUILD PIPELINE
# ─────────────────────────────────────────────────────────────────────────────
try:
    ask_bot, vectorstore = build_pipeline(groq_key)
    meta    = getattr(ask_bot, "_meta", {"n_docs": "—", "n_chunks": "—"})
    n_docs  = meta["n_docs"]
    n_vecs  = vectorstore.index.ntotal
except Exception as exc:
    st.error(f"Failed to initialise pipeline: {exc}")
    st.code(traceback.format_exc())
    st.stop()

# ─────────────────────────────────────────────────────────────────────────────
# HERO BANNER  (shown after pipeline loads)
# ─────────────────────────────────────────────────────────────────────────────
st.markdown(
    f"""
    <div class="hero-banner">
        <div class="hero-tagline">Zyro Dynamics — Internal HR Platform</div>
        <div class="hero-title">HR Help Desk <em>powered by AI</em></div>
        <div class="hero-desc">
            Ask any question about company policies — leave entitlements, compensation,
            performance reviews, WFH arrangements, POSH guidelines, and more.
            Answers are grounded in official Zyro Dynamics HR documents.
        </div>
        <div class="hero-pills">
            <span class="pill pill-green">● SYSTEM ONLINE</span>
            <span class="pill pill-blue">LLAMA 3.3 · 70B VIA GROQ</span>
            <span class="pill pill-purple">FAISS SEMANTIC SEARCH</span>
            <span class="pill pill-yellow">{n_docs} POLICY DOCUMENTS · {n_vecs} CHUNKS</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ─────────────────────────────────────────────────────────────────────────────
# STATS DASHBOARD
# ─────────────────────────────────────────────────────────────────────────────
st.markdown(
    f"""
    <div class="stats-row">
        <div class="stat-card">
            <div class="stat-number">{n_docs}</div>
            <div class="stat-label">Policy Documents</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">{n_vecs}</div>
            <div class="stat-label">Vector Chunks</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">{st.session_state.generated_responses}</div>
            <div class="stat-label">Queries Answered</div>
        </div>
        <div class="stat-card">
            <div class="stat-number" style="font-size:1.3rem;color:#a78bfa">LLaMA 3.3</div>
            <div class="stat-label">70B · Groq Inference</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ─────────────────────────────────────────────────────────────────────────────
# RENDER CHAT HISTORY
# ─────────────────────────────────────────────────────────────────────────────
for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]):
        if msg["role"] == "assistant":
            if not msg.get("in_scope", True):
                st.markdown(
                    f'<div class="oos-box">⚠️ {msg["content"]}</div>',
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(msg["content"])

            # Source citations
            if msg.get("sources"):
                label = f"📚 View Sources & Citations ({len(msg['sources'])} documents referenced)"
                with st.expander(label, expanded=False):
                    for s in msg["sources"]:
                        cat_tag = f" · <em>{s.get('category','')}</em>" if s.get("category") else ""
                        st.markdown(
                            f'<span class="src-badge">📑 {s["file"]}'
                            f'<span class="src-page">page {s["page"]}</span>'
                            f'{cat_tag}</span>',
                            unsafe_allow_html=True,
                        )

            # Response time chip
            elapsed = msg.get("elapsed")
            if elapsed:
                st.markdown(
                    f'<div class="rt-chip">⏱️ Response time: {elapsed:.2f}s</div>',
                    unsafe_allow_html=True,
                )
        else:
            st.markdown(msg["content"])

# ─────────────────────────────────────────────────────────────────────────────
# QUESTION HANDLER
# ─────────────────────────────────────────────────────────────────────────────
def handle_question(prompt: str) -> None:
    # Append user message
    st.session_state.chat_history.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("🔍 Searching HR policy documents…"):
            t0     = time.perf_counter()
            try:
                result = ask_bot(prompt)
            except Exception as exc:
                result = {
                    "answer"  : f"⚠️ An error occurred: {exc}. Please try again.",
                    "sources" : [],
                    "in_scope": True,
                }
            elapsed = time.perf_counter() - t0

        answer   = result["answer"]
        sources  = result.get("sources", [])
        in_scope = result.get("in_scope", True)

        if not in_scope:
            st.markdown(
                f'<div class="oos-box">⚠️ {answer}</div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(answer)

        if sources:
            label = f"📚 View Sources & Citations ({len(sources)} documents referenced)"
            with st.expander(label, expanded=True):
                for s in sources:
                    cat_tag = f" · <em>{s.get('category','')}</em>" if s.get("category") else ""
                    st.markdown(
                        f'<span class="src-badge">📑 {s["file"]}'
                        f'<span class="src-page">page {s["page"]}</span>'
                        f'{cat_tag}</span>',
                        unsafe_allow_html=True,
                    )

        st.markdown(
            f'<div class="rt-chip">⏱️ Response time: {elapsed:.2f}s</div>',
            unsafe_allow_html=True,
        )

    # Persist to session state
    st.session_state.chat_history.append({
        "role"    : "assistant",
        "content" : answer,
        "sources" : sources,
        "in_scope": in_scope,
        "elapsed" : elapsed,
    })
    st.session_state.generated_responses += 1

# ─────────────────────────────────────────────────────────────────────────────
# HANDLE SIDEBAR SAMPLE CLICK
# ─────────────────────────────────────────────────────────────────────────────
if st.session_state.pending_question:
    q = st.session_state.pending_question
    st.session_state.pending_question = None
    handle_question(q)

# ─────────────────────────────────────────────────────────────────────────────
# CHAT INPUT
# ─────────────────────────────────────────────────────────────────────────────
if prompt := st.chat_input("Ask a question about Zyro Dynamics HR policies…"):
    handle_question(prompt)

# ─────────────────────────────────────────────────────────────────────────────
# INFO BAR
# ─────────────────────────────────────────────────────────────────────────────
st.markdown(
    f"""
    <div class="info-bar">
        🔍 Retrieval method: <strong>FAISS cosine similarity + BM25 keyword (Ensemble)</strong> ·
        Model: <strong>LLaMA-3.3-70B-Versatile</strong> ·
        Embeddings: <strong>BAAI/bge-large-en-v1.5</strong> ·
        Answers are grounded in policy documents only — hallucinations are actively suppressed.
    </div>
    """,
    unsafe_allow_html=True,
)
