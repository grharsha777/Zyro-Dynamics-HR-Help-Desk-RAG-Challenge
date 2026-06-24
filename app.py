"""
Zyro Dynamics — HR Help Desk · AI-Powered Policy Assistant
NIAT × Kaggle RAG Challenge  |  Enterprise Edition v3.0
Stack: Groq LLaMA-3.3-70B · FAISS + BM25 Ensemble · BAAI/bge-large-en-v1.5
"""

# ══════════════════════════════════════════════════════════════
#  TOP-LEVEL IMPORTS  (never inside @st.cache_resource)
# ══════════════════════════════════════════════════════════════
import os
import glob
import time
import traceback

import streamlit as st

from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import FAISS
from langchain_community.retrievers import BM25Retriever
from langchain.retrievers import EnsembleRetriever
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# ══════════════════════════════════════════════════════════════
#  PAGE CONFIG  — must be the absolute first Streamlit call
# ══════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="Zyro Dynamics · HR Help Desk",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "Get Help": "https://github.com/grharsha777/Zyro-Dynamics-HR-Help-Desk-RAG-Challenge",
        "About": "Zyro Dynamics HR Help Desk — LangChain + Groq + FAISS. NIAT × Kaggle RAG Challenge.",
    },
)

# ══════════════════════════════════════════════════════════════
#  DESIGN SYSTEM  — single CSS block, dark enterprise theme
# ══════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

/* ── base ── */
html, body, [class*="css"] {
    font-family: 'Inter', system-ui, sans-serif;
}
[data-testid="stAppViewContainer"] {
    background: #060d18;
}
[data-testid="stMain"] > div {
    padding-top: 1.5rem;
}
#MainMenu, footer, header { visibility: hidden; }

/* ── sidebar ── */
[data-testid="stSidebar"] {
    background: #07111f;
    border-right: 1px solid #0f2035;
}
[data-testid="stSidebar"] * { color: #8ba3be !important; }
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 { color: #c8daea !important; }

/* sample-query buttons */
[data-testid="stSidebar"] .stButton > button {
    width: 100%;
    background: #0d1e30;
    border: 1px solid #133045;
    border-radius: 8px;
    color: #7fa8c9 !important;
    font-size: 0.78rem;
    font-weight: 500;
    text-align: left;
    padding: 0.5rem 0.75rem;
    margin-bottom: 2px;
    transition: all 0.18s ease;
    cursor: pointer;
}
[data-testid="stSidebar"] .stButton > button:hover {
    background: #102840;
    border-color: #1e6091;
    color: #a8d4f5 !important;
    transform: translateX(4px);
    box-shadow: -3px 0 0 #1e6091;
}

/* clear-chat button */
.clear-btn button {
    background: #1a0a0a !important;
    border: 1px solid #5c1a1a !important;
    color: #f87171 !important;
}
.clear-btn button:hover {
    background: #2d0f0f !important;
    border-color: #ef4444 !important;
}

/* ── hero banner ── */
.hero {
    background: linear-gradient(135deg, #060d18 0%, #0a1e35 45%, #081828 100%);
    border: 1px solid #112236;
    border-radius: 16px;
    padding: 2.25rem 2.5rem 2rem;
    margin-bottom: 1.25rem;
    position: relative;
    overflow: hidden;
}
.hero::before {
    content: '';
    position: absolute;
    top: -80px; right: -80px;
    width: 320px; height: 320px;
    background: radial-gradient(circle, #1a4d7a18, transparent 70%);
    border-radius: 50%;
    pointer-events: none;
}
.hero::after {
    content: '';
    position: absolute;
    bottom: -60px; left: 20%;
    width: 250px; height: 250px;
    background: radial-gradient(circle, #7c3aed10, transparent 70%);
    border-radius: 50%;
    pointer-events: none;
}
.hero-eyebrow {
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: #2d7fc1;
    margin-bottom: 0.6rem;
}
.hero-title {
    font-size: 2.2rem;
    font-weight: 800;
    color: #ddeeff;
    line-height: 1.1;
    margin: 0 0 0.5rem;
}
.hero-title span {
    background: linear-gradient(90deg, #3b9ded, #818cf8);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-style: italic;
}
.hero-sub {
    font-size: 0.92rem;
    color: #4a7a9b;
    max-width: 640px;
    line-height: 1.65;
    margin-bottom: 1.4rem;
}
.pill-row { display: flex; flex-wrap: wrap; gap: 0.45rem; }
.pill {
    display: inline-flex;
    align-items: center;
    gap: 0.35rem;
    padding: 0.28rem 0.85rem;
    border-radius: 100px;
    font-size: 0.73rem;
    font-weight: 600;
    letter-spacing: 0.03em;
}
.pill-online  { background:#052412; border:1px solid #14532d55; color:#4ade80; }
.pill-model   { background:#05112b; border:1px solid #1e3a8a55; color:#60a5fa; }
.pill-search  { background:#160b2a; border:1px solid #4c1d9555; color:#a78bfa; }
.pill-docs    { background:#1a0f04; border:1px solid #78350f55; color:#fbbf24; }

/* ── stats grid ── */
.stats {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 0.875rem;
    margin-bottom: 1.25rem;
}
.stat {
    background: #07111f;
    border: 1px solid #0f2035;
    border-radius: 12px;
    padding: 1.1rem 1.25rem;
    text-align: center;
    transition: border-color 0.2s, transform 0.2s;
    cursor: default;
}
.stat:hover {
    border-color: #1e6091;
    transform: translateY(-2px);
}
.stat-val {
    font-size: 1.9rem;
    font-weight: 800;
    color: #3b9ded;
    line-height: 1;
    letter-spacing: -0.02em;
}
.stat-val.purple { color: #a78bfa; font-size: 1.25rem; }
.stat-lbl {
    font-size: 0.68rem;
    font-weight: 600;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #274a65;
    margin-top: 0.4rem;
}

/* ── chat area ── */
[data-testid="stChatMessage"] {
    background: transparent;
    padding: 0.2rem 0;
}
[data-testid="stChatMessageContent"] p {
    color: #c8daea;
    line-height: 1.7;
    font-size: 0.93rem;
}

/* ── source badges ── */
.src-wrap { display: flex; flex-wrap: wrap; gap: 0.4rem; margin-top: 0.5rem; }
.src-badge {
    display: inline-flex;
    align-items: center;
    gap: 0.45rem;
    background: #0a1e30;
    border: 1px solid #112f4a;
    border-radius: 8px;
    padding: 0.38rem 0.8rem;
    font-size: 0.76rem;
    font-weight: 500;
    color: #7fb8e0;
    transition: border-color 0.15s;
}
.src-badge:hover { border-color: #2d7fc1; }
.src-page {
    background: #112f4a;
    border-radius: 4px;
    padding: 1px 7px;
    font-size: 0.68rem;
    color: #3b9ded;
    font-weight: 600;
}
.src-cat {
    font-size: 0.68rem;
    color: #2d5f7a;
    font-style: italic;
}

/* ── OOS box ── */
.oos-box {
    background: #110708;
    border-left: 3px solid #dc2626;
    border-radius: 0 8px 8px 0;
    padding: 0.85rem 1.1rem;
    color: #fca5a5;
    font-size: 0.88rem;
    line-height: 1.6;
}

/* ── response time chip ── */
.rt-chip {
    display: inline-block;
    background: #050e1a;
    border: 1px solid #0d2235;
    border-radius: 100px;
    padding: 2px 12px;
    font-size: 0.7rem;
    font-weight: 500;
    color: #2d7fc1;
    margin-top: 0.5rem;
}

/* ── info footer ── */
.info-bar {
    background: #07111f;
    border: 1px solid #0f2035;
    border-radius: 10px;
    padding: 0.8rem 1.25rem;
    font-size: 0.76rem;
    color: #274a65;
    margin-top: 1.5rem;
    line-height: 1.7;
}
.info-bar b { color: #3b9ded; }

/* ── expander ── */
details summary {
    color: #2d7fc1 !important;
    font-size: 0.81rem !important;
    font-weight: 600 !important;
}
[data-testid="stExpander"] {
    background: #07111f !important;
    border: 1px solid #0f2035 !important;
    border-radius: 8px !important;
}

/* ── chat input ── */
[data-testid="stChatInput"] {
    background: #07111f !important;
    border: 1px solid #112f4a !important;
    border-radius: 12px !important;
}
[data-testid="stChatInput"] textarea {
    color: #c8daea !important;
    font-size: 0.9rem !important;
}
[data-testid="stChatInput"] textarea::placeholder {
    color: #274a65 !important;
}

/* ── divider ── */
hr { border-color: #0f2035 !important; opacity: 1 !important; }

/* ── metric ── */
[data-testid="stMetric"] label { color: #274a65 !important; font-size: 0.72rem !important; }
[data-testid="stMetricValue"]  { color: #3b9ded !important; font-size: 1.4rem !important; }

/* ── scrollbar ── */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: #060d18; }
::-webkit-scrollbar-thumb { background: #0f2035; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #1e4060; }
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
#  SESSION STATE
# ══════════════════════════════════════════════════════════════
for _k, _v in {
    "chat_history": [],
    "queries_answered": 0,
    "pending_question": None,
}.items():
    if _k not in st.session_state:
        st.session_state[_k] = _v


# ══════════════════════════════════════════════════════════════
#  SIDEBAR
# ══════════════════════════════════════════════════════════════
with st.sidebar:
    # Brand
    st.markdown("""
    <div style="display:flex;align-items:center;gap:0.7rem;padding:0.25rem 0 1rem">
        <div style="font-size:2rem;line-height:1">🏢</div>
        <div>
            <div style="font-size:1.05rem;font-weight:700;color:#c8daea">Zyro Dynamics</div>
            <div style="font-size:0.65rem;letter-spacing:0.15em;color:#274a65;font-weight:600">
                HR HELP DESK · AI
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    # API keys
    st.markdown("<div style='font-size:0.72rem;font-weight:700;letter-spacing:0.12em;"
                "color:#274a65;margin-bottom:0.5rem'>⚙️ CONFIGURATION</div>",
                unsafe_allow_html=True)

    groq_key = st.text_input(
        "Groq API Key",
        type="password",
        value=os.environ.get("GROQ_API_KEY", ""),
        help="Free key at https://console.groq.com",
        placeholder="gsk_••••••••••••••••",
        label_visibility="visible",
    )
    langchain_key = st.text_input(
        "LangChain API Key (optional)",
        type="password",
        value=os.environ.get("LANGCHAIN_API_KEY", ""),
        help="Enables LangSmith tracing",
        placeholder="ls__••••••••••••••••",
        label_visibility="visible",
    )

    st.divider()

    # Sample questions
    st.markdown("<div style='font-size:0.72rem;font-weight:700;letter-spacing:0.12em;"
                "color:#274a65;margin-bottom:0.5rem'>💡 SAMPLE QUERIES</div>",
                unsafe_allow_html=True)

    SAMPLE_QS = [
        "How many earned leave days per year?",
        "When is salary credited each month?",
        "What is the WFH policy for L3 employees?",
        "What health insurance do employees receive?",
        "How long does a PIP last?",
        "Explain the Annual Performance Review process.",
        "What is the payroll cut-off date?",
        "What are the POSH policy guidelines?",
        "What are travel expense reimbursement limits?",
        "How many days notice for resignation?",
    ]
    for q in SAMPLE_QS:
        if st.button(q, use_container_width=True, key=f"sq_{hash(q)}"):
            st.session_state.pending_question = q

    st.divider()

    # Session stats + clear
    c1, c2 = st.columns(2)
    c1.metric("Queries", st.session_state.queries_answered)
    c2.metric("Turns", len(st.session_state.chat_history))

    st.markdown('<div class="clear-btn">', unsafe_allow_html=True)
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.chat_history     = []
        st.session_state.queries_answered = 0
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    st.divider()
    st.markdown("""
    <div style="font-size:0.7rem;color:#274a65;line-height:1.8">
        <b style="color:#2d7fc1">v3.0 · Enterprise</b><br>
        NIAT × Kaggle RAG Challenge<br>
        LangChain · FAISS · BM25 · Groq<br>
        BAAI/bge-large-en-v1.5
    </div>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
#  APPLY ENV VARS FROM SIDEBAR
# ══════════════════════════════════════════════════════════════
if groq_key:
    os.environ["GROQ_API_KEY"] = groq_key
if langchain_key:
    os.environ["LANGCHAIN_API_KEY"]    = langchain_key
    os.environ["LANGCHAIN_TRACING_V2"] = "true"
    os.environ["LANGCHAIN_PROJECT"]    = "zyro-rag-challenge"


# ══════════════════════════════════════════════════════════════
#  HR CATEGORY TAGGER
# ══════════════════════════════════════════════════════════════
_HR_CATS = {
    "Leave":         ["leave", "earned leave", "sick leave", "maternity", "paternity",
                      "casual leave", " cl ", " el ", " sl ", "annual leave"],
    "Compensation":  ["salary", "payroll", "ctc", "bonus", "increment", "compensation",
                      "pay slip", "deduction", "tax", "wages"],
    "WFH / Remote":  ["work from home", "wfh", "hybrid", "remote", "work location",
                      "flexible work"],
    "Performance":   ["performance", "pip", "apr", "kra", "kpi", "review", "rating",
                      "promotion", "appraisal", "pmp"],
    "Benefits":      ["insurance", "health", "medical", "dental", "vision", "benefit",
                      "provident fund", " pf ", "gratuity", "esic"],
    "IT / Security": ["it policy", "cybersecurity", "data protection", "password",
                      "device", "laptop", "software", "gdpr"],
    "POSH":          ["posh", "harassment", "sexual", "iqc", "complaint", "misconduct"],
    "Onboarding":    ["onboarding", "probation", "joining", "induction", "background check"],
    "Separation":    ["separation", "resignation", "notice period", "fnf",
                      "full and final", "termination", "exit interview"],
    "Travel":        ["travel", "expense", "reimbursement", "per diem", "ticket", "hotel"],
    "Conduct":       ["code of conduct", "ethics", "discipline", "nda", "confidentiality"],
}

def _tag_category(text: str) -> str:
    tl = text.lower()
    tags = [cat for cat, kws in _HR_CATS.items() if any(kw in tl for kw in kws)]
    return ", ".join(tags) if tags else "General"


# ══════════════════════════════════════════════════════════════
#  RAG PIPELINE  (cached — builds once per server session)
# ══════════════════════════════════════════════════════════════
@st.cache_resource(show_spinner="📚 Initialising HR knowledge base…")
def build_pipeline(_groq_key: str):
    """
    PDF load → chunk → BAAI/bge-large embed → FAISS index
    BM25 retriever → Ensemble 70/30 → LLaMA-3.3-70B (Groq)
    Returns (ask_bot fn, vectorstore, n_docs, n_chunks)
    """

    # ── 1. Locate corpus ──────────────────────────────────────
    SEARCH_PATHS = [
        "/kaggle/input/niat-masterclass-rag-challenge/",
        "/kaggle/input/zyro-dynamics-hr-corpus/",
        "/kaggle/input/",
        os.path.join(os.path.dirname(__file__), "data"),
        os.path.dirname(os.path.abspath(__file__)),
        ".",
    ]
    pdf_files: list[str] = []
    for base in SEARCH_PATHS:
        found = sorted(glob.glob(os.path.join(base, "**/*.pdf"), recursive=True))
        if found:
            pdf_files = found
            break

    if not pdf_files:
        st.error(
            "**No PDF files found.** Attach the HR corpus dataset in Kaggle, "
            "or place PDFs in a `data/` folder next to `app.py`.",
            icon="📂",
        )
        st.stop()

    # ── 2. Load PDFs ──────────────────────────────────────────
    documents = []
    for path in pdf_files:
        try:
            loader = PyPDFLoader(path)
            pages  = loader.load()
            stem   = os.path.splitext(os.path.basename(path))[0]
            for p in pages:
                p.metadata["source"] = stem
            documents.extend(pages)
        except Exception as exc:
            st.warning(f"Skipped {os.path.basename(path)}: {exc}")

    if not documents:
        st.error("All PDFs failed to load. Check corpus integrity.")
        st.stop()

    # ── 3. Chunk ──────────────────────────────────────────────
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    chunks = splitter.split_documents(documents)
    for c in chunks:
        c.metadata["hr_category"] = _tag_category(c.page_content)

    # ── 4. Embeddings — BAAI/bge-large-en-v1.5 ───────────────
    embeddings = HuggingFaceEmbeddings(
        model_name="BAAI/bge-large-en-v1.5",
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True},
    )

    # ── 5. FAISS vector store ─────────────────────────────────
    vectorstore = FAISS.from_documents(chunks, embeddings)
    faiss_ret   = vectorstore.as_retriever(
        search_type="mmr",
        search_kwargs={"k": 6, "fetch_k": 20, "lambda_mult": 0.65},
    )

    # ── 6. BM25 retriever ─────────────────────────────────────
    bm25_ret   = BM25Retriever.from_documents(chunks)
    bm25_ret.k = 10

    # ── 7. Ensemble retriever (FAISS 70% + BM25 30%) ─────────
    ensemble = EnsembleRetriever(
        retrievers=[faiss_ret, bm25_ret],
        weights=[0.7, 0.3],
    )

    # ── 8. LLM ───────────────────────────────────────────────
    llm = ChatGroq(
        model="llama-3.3-70b-versatile",
        temperature=0.1,
        max_tokens=768,
        api_key=_groq_key,
        streaming=False,        # keep False for simplicity; switch on for streaming UX
    )
    parser = StrOutputParser()

    # ── 9. Prompts ────────────────────────────────────────────
    RAG_PROMPT = ChatPromptTemplate.from_template(
        "You are an expert HR Help Desk assistant for Zyro Dynamics "
        "(also called Acrux Dynamics).\n\n"
        "Rules:\n"
        "- Answer using ONLY the HR Policy Context below.\n"
        "- Be precise: cite exact numbers, dates, percentages.\n"
        "- Use bullet points for multi-item answers.\n"
        "- If the context lacks enough detail, say:\n"
        '  "The HR policy documents do not contain sufficient detail to answer '
        'this question. Please contact HR directly."\n'
        "- Never fabricate information.\n\n"
        "HR Policy Context:\n{context}\n\n"
        "Employee Question: {question}\n\n"
        "Grounded Answer:"
    )

    OOS_PROMPT = ChatPromptTemplate.from_template(
        "You are a strict scope classifier for an HR policy chatbot.\n\n"
        "In-scope topics (HR policy documents ONLY):\n"
        "- Leave entitlements (earned, sick, maternity, paternity, casual)\n"
        "- WFH, hybrid, remote-work arrangements\n"
        "- Code of conduct and ethics\n"
        "- Performance reviews, PIP, APR, KRAs, promotions\n"
        "- Salary, compensation, payroll, bonuses\n"
        "- Health insurance and benefits (PF, gratuity)\n"
        "- IT and cybersecurity policies\n"
        "- POSH (Prevention of Sexual Harassment)\n"
        "- Onboarding, probation, induction\n"
        "- Separation, resignation, notice period, F&F settlement\n"
        "- Business travel and expense reimbursement\n"
        "- Company overview, grade structure, office policies\n\n"
        "Question: {question}\n\n"
        "Reply with EXACTLY one token: IN_SCOPE or OUT_OF_SCOPE"
    )

    REFUSAL = (
        "I can only answer HR-related questions grounded in Zyro Dynamics "
        "internal policy documents. Your question appears to be outside that "
        "scope. Please reach out to the relevant department or consult an "
        "external resource."
    )

    # ── 10. Document formatter ────────────────────────────────
    def _fmt(docs) -> str:
        parts = []
        for i, d in enumerate(docs, 1):
            src  = d.metadata.get("source", "Unknown")
            page = d.metadata.get("page", "?")
            cat  = d.metadata.get("hr_category", "")
            tag  = f"  [{cat}]" if cat else ""
            parts.append(f"[Source {i}: {src}, page {page}{tag}]\n{d.page_content}")
        return "\n\n---\n\n".join(parts)

    # ── 11. ask_bot ───────────────────────────────────────────
    def ask_bot(question: str) -> dict:
        # Layer 1 — scope guard
        try:
            verdict = parser.invoke(
                llm.invoke(OOS_PROMPT.invoke({"question": question}))
            ).strip().upper()
        except Exception:
            verdict = "IN_SCOPE"   # fail open; let retrieval decide

        if "OUT_OF_SCOPE" in verdict:
            return {"answer": REFUSAL, "sources": [], "in_scope": False}

        # Layer 2 — hybrid retrieval
        try:
            docs = ensemble.invoke(question)
        except Exception:
            docs = vectorstore.similarity_search(question, k=5)

        if not docs:
            return {"answer": REFUSAL, "sources": [], "in_scope": False}

        # Layer 3 — relevance floor
        try:
            scored = vectorstore.similarity_search_with_relevance_scores(question, k=3)
            if scored and scored[0][1] < 0.20:
                return {"answer": REFUSAL, "sources": [], "in_scope": False}
        except Exception:
            pass

        # Layer 4 — generate answer
        context = _fmt(docs)
        try:
            answer = parser.invoke(
                llm.invoke(RAG_PROMPT.invoke({"context": context, "question": question}))
            )
        except Exception as exc:
            return {"answer": f"⚠️ Generation error: {exc}", "sources": [], "in_scope": True}

        # Deduplicate sources
        seen, sources = set(), []
        for d in docs:
            key = (d.metadata.get("source", ""), d.metadata.get("page", "?"))
            if key not in seen:
                seen.add(key)
                sources.append({
                    "file"    : d.metadata.get("source", "Unknown"),
                    "page"    : d.metadata.get("page", "?"),
                    "category": d.metadata.get("hr_category", ""),
                })

        return {"answer": answer, "sources": sources, "in_scope": True}

    return ask_bot, vectorstore, len(pdf_files), len(chunks)


# ══════════════════════════════════════════════════════════════
#  GATE — require API key
# ══════════════════════════════════════════════════════════════
if not groq_key:
    st.markdown("""
    <div class="hero">
        <div class="hero-eyebrow">Zyro Dynamics — Internal HR Platform</div>
        <div class="hero-title">HR Help Desk <span>powered by AI</span></div>
        <div class="hero-sub">
            Ask any question about company policies — leave entitlements,
            compensation, performance reviews, WFH arrangements, POSH
            guidelines, and more. All answers are grounded in official
            Zyro Dynamics HR documents.
        </div>
        <div class="pill-row">
            <span class="pill pill-online">● Enter Groq key to begin</span>
            <span class="pill pill-model">LLaMA 3.3 · 70B via Groq</span>
            <span class="pill pill-search">FAISS + BM25 Hybrid</span>
            <span class="pill pill-docs">BAAI/bge-large-en-v1.5</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.info(
        "👈 **Enter your Groq API Key** in the sidebar to start.  \n"
        "Get a free key at [console.groq.com](https://console.groq.com).",
        icon="🔑",
    )
    st.stop()


# ══════════════════════════════════════════════════════════════
#  BUILD PIPELINE
# ══════════════════════════════════════════════════════════════
try:
    ask_bot, vectorstore, n_docs, n_chunks = build_pipeline(groq_key)
    n_vecs = vectorstore.index.ntotal
except Exception as exc:
    st.error(f"Pipeline initialisation failed: {exc}")
    with st.expander("Full traceback"):
        st.code(traceback.format_exc())
    st.stop()


# ══════════════════════════════════════════════════════════════
#  HERO BANNER  (shown after pipeline loads)
# ══════════════════════════════════════════════════════════════
st.markdown(f"""
<div class="hero">
    <div class="hero-eyebrow">Zyro Dynamics — Internal HR Platform</div>
    <div class="hero-title">HR Help Desk <span>powered by AI</span></div>
    <div class="hero-sub">
        Ask any question about company policies — leave entitlements,
        compensation, performance reviews, WFH arrangements, POSH
        guidelines, and more. Answers are grounded in official Zyro
        Dynamics HR documents.
    </div>
    <div class="pill-row">
        <span class="pill pill-online">● SYSTEM ONLINE</span>
        <span class="pill pill-model">LLAMA 3.3 · 70B VIA GROQ</span>
        <span class="pill pill-search">FAISS SEMANTIC SEARCH</span>
        <span class="pill pill-docs">{n_docs} POLICY DOCUMENTS · {n_vecs} CHUNKS</span>
    </div>
</div>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
#  STATS DASHBOARD
# ══════════════════════════════════════════════════════════════
st.markdown(f"""
<div class="stats">
    <div class="stat">
        <div class="stat-val">{n_docs}</div>
        <div class="stat-lbl">Policy Documents</div>
    </div>
    <div class="stat">
        <div class="stat-val">{n_vecs}</div>
        <div class="stat-lbl">Vector Chunks</div>
    </div>
    <div class="stat">
        <div class="stat-val">{st.session_state.queries_answered}</div>
        <div class="stat-lbl">Queries Answered</div>
    </div>
    <div class="stat">
        <div class="stat-val purple">LLaMA 3.3</div>
        <div class="stat-lbl">70B · Groq Inference</div>
    </div>
</div>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
#  RENDER CHAT HISTORY
# ══════════════════════════════════════════════════════════════
def _render_assistant_msg(msg: dict) -> None:
    if not msg.get("in_scope", True):
        st.markdown(f'<div class="oos-box">⚠️ {msg["content"]}</div>',
                    unsafe_allow_html=True)
    else:
        st.markdown(msg["content"])

    if msg.get("sources"):
        n = len(msg["sources"])
        with st.expander(f"📚 Source citations ({n} document{'s' if n != 1 else ''} referenced)",
                         expanded=False):
            badges = ""
            for s in msg["sources"]:
                cat = f'<span class="src-cat">{s["category"]}</span>' if s.get("category") else ""
                badges += (
                    f'<span class="src-badge">📑 {s["file"]}'
                    f'<span class="src-page">page {s["page"]}</span>'
                    f'{cat}</span>'
                )
            st.markdown(f'<div class="src-wrap">{badges}</div>', unsafe_allow_html=True)

    if msg.get("elapsed"):
        st.markdown(f'<div class="rt-chip">⏱️ Response time: {msg["elapsed"]:.2f}s</div>',
                    unsafe_allow_html=True)


for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]):
        if msg["role"] == "assistant":
            _render_assistant_msg(msg)
        else:
            st.markdown(msg["content"])


# ══════════════════════════════════════════════════════════════
#  QUESTION HANDLER
# ══════════════════════════════════════════════════════════════
def handle_question(prompt: str) -> None:
    st.session_state.chat_history.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("🔍 Searching HR policy documents…"):
            t0 = time.perf_counter()
            try:
                result = ask_bot(prompt)
            except Exception as exc:
                result = {
                    "answer"  : f"⚠️ Unexpected error: {exc}. Please try again.",
                    "sources" : [],
                    "in_scope": True,
                }
            elapsed = time.perf_counter() - t0

        msg = {
            "role"    : "assistant",
            "content" : result["answer"],
            "sources" : result.get("sources", []),
            "in_scope": result.get("in_scope", True),
            "elapsed" : elapsed,
        }
        _render_assistant_msg(msg)

    st.session_state.chat_history.append(msg)
    st.session_state.queries_answered += 1


# ── sidebar sample click ──────────────────────────────────────
if st.session_state.pending_question:
    q = st.session_state.pending_question
    st.session_state.pending_question = None
    handle_question(q)

# ── live chat input ───────────────────────────────────────────
if prompt := st.chat_input("Ask a question about Zyro Dynamics HR policies…"):
    handle_question(prompt)


# ══════════════════════════════════════════════════════════════
#  INFO FOOTER
# ══════════════════════════════════════════════════════════════
st.markdown("""
<div class="info-bar">
    🔍 Retrieval: <b>FAISS cosine similarity + BM25 keyword (70 / 30 ensemble)</b> ·
    Model: <b>LLaMA-3.3-70B-Versatile via Groq</b> ·
    Embeddings: <b>BAAI/bge-large-en-v1.5</b> ·
    Answers are grounded in policy documents only — hallucinations are actively suppressed.
</div>
""", unsafe_allow_html=True)
