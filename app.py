"""
Zyro Dynamics - HR Help Desk (AI Policy Assistant)
NIAT x Kaggle RAG Challenge

Stack: Groq LLaMA-3.3-70B | FAISS + BM25 Ensemble | BAAI/bge-large-en-v1.5

requirements.txt should include:
    streamlit
    langchain
    langchain-community
    langchain-text-splitters
    langchain-huggingface
    langchain-groq
    langchain-core
    faiss-cpu
    pypdf
    sentence-transformers
    rank_bm25
"""

# ──────────────────────────────────────────────────────────────
#  TOP-LEVEL IMPORTS  (must stay outside any cached function)
# ──────────────────────────────────────────────────────────────
import os
import glob
import time
import traceback

import streamlit as st

from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

try:
    from langchain_community.retrievers import BM25Retriever
    from langchain.retrievers import EnsembleRetriever
    BM25_AVAILABLE = True
except ImportError:
    # BM25Retriever needs the "rank_bm25" package. If it isn't installed,
    # the app still works with FAISS-only retrieval instead of crashing.
    BM25_AVAILABLE = False


# ──────────────────────────────────────────────────────────────
#  PAGE CONFIG  — must be the first Streamlit call
# ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Zyro Dynamics | HR Help Desk",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "Get Help": "https://github.com/grharsha777/Zyro-Dynamics-HR-Help-Desk-RAG-Challenge",
        "About": "Zyro Dynamics HR Help Desk - LangChain + Groq + FAISS. NIAT x Kaggle RAG Challenge.",
    },
)

# ──────────────────────────────────────────────────────────────
#  STYLE  — minimal, professional, light-on-color theme
# ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
html, body, [class*="css"] {
    font-family: 'Segoe UI', system-ui, sans-serif;
}
#MainMenu, footer, header { visibility: hidden; }

.hero {
    background: #f7f8fa;
    border: 1px solid #e3e6ea;
    border-radius: 10px;
    padding: 1.75rem 2rem;
    margin-bottom: 1.25rem;
}
.hero-title {
    font-size: 1.6rem;
    font-weight: 700;
    color: #1a1a1a;
    margin: 0 0 0.4rem;
}
.hero-sub {
    font-size: 0.92rem;
    color: #5a5f66;
    max-width: 700px;
    line-height: 1.6;
    margin-bottom: 0.9rem;
}
.badge-row { display: flex; flex-wrap: wrap; gap: 0.5rem; }
.badge {
    display: inline-block;
    padding: 0.25rem 0.75rem;
    border-radius: 5px;
    font-size: 0.72rem;
    font-weight: 600;
    background: #ffffff;
    border: 1px solid #d8dbe0;
    color: #44484f;
}

.stats {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 0.75rem;
    margin-bottom: 1.25rem;
}
.stat {
    background: #ffffff;
    border: 1px solid #e3e6ea;
    border-radius: 8px;
    padding: 0.9rem 1rem;
    text-align: center;
}
.stat-val { font-size: 1.4rem; font-weight: 700; color: #1f4e8c; }
.stat-lbl {
    font-size: 0.68rem;
    font-weight: 600;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    color: #8a8f96;
    margin-top: 0.3rem;
}

.src-wrap { display: flex; flex-wrap: wrap; gap: 0.4rem; margin-top: 0.5rem; }
.src-badge {
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    background: #f4f6f8;
    border: 1px solid #dde1e6;
    border-radius: 6px;
    padding: 0.3rem 0.7rem;
    font-size: 0.76rem;
    color: #3a3f45;
}
.src-page {
    background: #e4e9f0;
    border-radius: 4px;
    padding: 1px 6px;
    font-size: 0.68rem;
    color: #1f4e8c;
    font-weight: 600;
}
.src-cat { font-size: 0.68rem; color: #8a8f96; font-style: italic; }

.oos-box {
    background: #fdf3f3;
    border-left: 3px solid #c0392b;
    border-radius: 0 6px 6px 0;
    padding: 0.8rem 1rem;
    color: #6b2424;
    font-size: 0.88rem;
    line-height: 1.6;
}

.rt-chip {
    display: inline-block;
    background: #f4f6f8;
    border: 1px solid #dde1e6;
    border-radius: 100px;
    padding: 2px 10px;
    font-size: 0.7rem;
    color: #5a5f66;
    margin-top: 0.5rem;
}

.info-bar {
    background: #f7f8fa;
    border: 1px solid #e3e6ea;
    border-radius: 8px;
    padding: 0.75rem 1.1rem;
    font-size: 0.76rem;
    color: #5a5f66;
    margin-top: 1.5rem;
    line-height: 1.7;
}
.info-bar b { color: #1f4e8c; }
</style>
""", unsafe_allow_html=True)


# ──────────────────────────────────────────────────────────────
#  SESSION STATE
# ──────────────────────────────────────────────────────────────
for _k, _v in {
    "chat_history": [],
    "queries_answered": 0,
    "pending_question": None,
}.items():
    if _k not in st.session_state:
        st.session_state[_k] = _v


# ──────────────────────────────────────────────────────────────
#  SIDEBAR
# ──────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### Zyro Dynamics")
    st.caption("HR Help Desk")
    st.divider()

    st.markdown("**Configuration**")
    groq_key = st.text_input(
        "Groq API Key",
        type="password",
        value=os.environ.get("GROQ_API_KEY", ""),
        help="Free key at https://console.groq.com",
        placeholder="gsk_...",
    )

    st.divider()
    st.markdown("**Sample Queries**")

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
    c1, c2 = st.columns(2)
    c1.metric("Queries", st.session_state.queries_answered)
    c2.metric("Turns", len(st.session_state.chat_history))

    if st.button("Clear Chat", use_container_width=True):
        st.session_state.chat_history = []
        st.session_state.queries_answered = 0
        st.rerun()

    st.divider()
    st.caption("v3.0 - NIAT x Kaggle RAG Challenge")
    st.caption("LangChain - FAISS - BM25 - Groq")


# ──────────────────────────────────────────────────────────────
#  APPLY ENV VARS FROM SIDEBAR
# ──────────────────────────────────────────────────────────────
if groq_key:
    os.environ["GROQ_API_KEY"] = groq_key


# ──────────────────────────────────────────────────────────────
#  HR CATEGORY TAGGER
# ──────────────────────────────────────────────────────────────
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


# ──────────────────────────────────────────────────────────────
#  CORPUS DISCOVERY
#  The app is deployed on Streamlit Community Cloud, so the
#  Kaggle "/kaggle/input/..." paths from the notebook do not exist
#  there. We search a set of locations that cover both Kaggle and
#  a normal git-based Streamlit deployment.
# ──────────────────────────────────────────────────────────────
def _discover_pdfs() -> list[str]:
    try:
        app_dir = os.path.dirname(os.path.abspath(__file__))
    except NameError:
        app_dir = os.getcwd()

    search_paths = [
        os.path.join(app_dir, "data"),
        os.path.join(app_dir, "corpus"),
        os.path.join(app_dir, "docs"),
        app_dir,
        "/kaggle/input/niat-masterclass-rag-challenge/",
        "/kaggle/input/zyro-dynamics-hr-corpus/",
        "/kaggle/input/",
        ".",
    ]

    for base in search_paths:
        if not os.path.isdir(base):
            continue
        found = sorted(glob.glob(os.path.join(base, "**/*.pdf"), recursive=True))
        if found:
            return found

    return []


# ──────────────────────────────────────────────────────────────
#  RAG PIPELINE  (cached — builds once per server session)
# ──────────────────────────────────────────────────────────────
@st.cache_resource(show_spinner="Initialising HR knowledge base...")
def build_pipeline(_groq_key: str):
    pdf_files = _discover_pdfs()

    if not pdf_files:
        st.error(
            "No PDF files found. Add the HR policy PDFs to a `data/` folder "
            "in the project repository (next to app.py), or attach the "
            "corpus dataset if running on Kaggle."
        )
        st.stop()

    # Load PDFs
    documents = []
    for path in pdf_files:
        try:
            loader = PyPDFLoader(path)
            pages = loader.load()
            stem = os.path.splitext(os.path.basename(path))[0]
            for p in pages:
                p.metadata["source"] = stem
            documents.extend(pages)
        except Exception as exc:
            st.warning(f"Skipped {os.path.basename(path)}: {exc}")

    if not documents:
        st.error("All PDFs failed to load. Check corpus integrity.")
        st.stop()

    # Chunk
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    chunks = splitter.split_documents(documents)
    for c in chunks:
        c.metadata["hr_category"] = _tag_category(c.page_content)

    # Embeddings
    try:
        embeddings = HuggingFaceEmbeddings(
            model_name="BAAI/bge-large-en-v1.5",
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True},
        )
    except Exception as exc:
        st.error(f"Failed to load embedding model: {exc}")
        st.stop()

    # FAISS vector store
    vectorstore = FAISS.from_documents(chunks, embeddings)
    faiss_ret = vectorstore.as_retriever(
        search_type="mmr",
        search_kwargs={"k": 6, "fetch_k": 20, "lambda_mult": 0.65},
    )

    # Hybrid retriever (FAISS + BM25), with a safe fallback to FAISS only
    if BM25_AVAILABLE:
        bm25_ret = BM25Retriever.from_documents(chunks)
        bm25_ret.k = 10
        retriever = EnsembleRetriever(
            retrievers=[faiss_ret, bm25_ret],
            weights=[0.7, 0.3],
        )
    else:
        retriever = faiss_ret

    # LLM
    llm = ChatGroq(
        model="llama-3.3-70b-versatile",
        temperature=0.1,
        max_tokens=768,
        api_key=_groq_key,
        streaming=False,
    )
    parser = StrOutputParser()

    # Prompts
    RAG_PROMPT = ChatPromptTemplate.from_template(
        "You are an HR Help Desk assistant for Zyro Dynamics "
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

    def _fmt(docs) -> str:
        parts = []
        for i, d in enumerate(docs, 1):
            src = d.metadata.get("source", "Unknown")
            page = d.metadata.get("page", "?")
            cat = d.metadata.get("hr_category", "")
            tag = f"  [{cat}]" if cat else ""
            parts.append(f"[Source {i}: {src}, page {page}{tag}]\n{d.page_content}")
        return "\n\n---\n\n".join(parts)

    def ask_bot(question: str) -> dict:
        # Layer 1 — scope guard
        try:
            verdict = parser.invoke(
                llm.invoke(OOS_PROMPT.invoke({"question": question}))
            ).strip().upper()
        except Exception:
            verdict = "IN_SCOPE"  # fail open; let retrieval decide

        if "OUT_OF_SCOPE" in verdict:
            return {"answer": REFUSAL, "sources": [], "in_scope": False}

        # Layer 2 — hybrid retrieval
        try:
            docs = retriever.invoke(question)
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
            return {"answer": f"Generation error: {exc}", "sources": [], "in_scope": True}

        # Deduplicate sources
        seen, sources = set(), []
        for d in docs:
            key = (d.metadata.get("source", ""), d.metadata.get("page", "?"))
            if key not in seen:
                seen.add(key)
                sources.append({
                    "file": d.metadata.get("source", "Unknown"),
                    "page": d.metadata.get("page", "?"),
                    "category": d.metadata.get("hr_category", ""),
                })

        return {"answer": answer, "sources": sources, "in_scope": True}

    return ask_bot, vectorstore, len(pdf_files), len(chunks)


# ──────────────────────────────────────────────────────────────
#  GATE — require API key
# ──────────────────────────────────────────────────────────────
if not groq_key:
    st.markdown("""
    <div class="hero">
        <div class="hero-title">HR Help Desk</div>
        <div class="hero-sub">
            Ask any question about company policies - leave entitlements,
            compensation, performance reviews, WFH arrangements, POSH
            guidelines, and more. All answers are grounded in official
            Zyro Dynamics HR documents.
        </div>
        <div class="badge-row">
            <span class="badge">LLaMA 3.3 70B via Groq</span>
            <span class="badge">FAISS + BM25 Hybrid Retrieval</span>
            <span class="badge">BAAI/bge-large-en-v1.5</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.info("Enter your Groq API key in the sidebar to start. "
            "Get a free key at console.groq.com.")
    st.stop()


# ──────────────────────────────────────────────────────────────
#  BUILD PIPELINE
# ──────────────────────────────────────────────────────────────
try:
    ask_bot, vectorstore, n_docs, n_chunks = build_pipeline(groq_key)
    n_vecs = vectorstore.index.ntotal
except Exception as exc:
    st.error(f"Pipeline initialisation failed: {exc}")
    with st.expander("Full traceback"):
        st.code(traceback.format_exc())
    st.stop()


# ──────────────────────────────────────────────────────────────
#  HERO BANNER
# ──────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="hero">
    <div class="hero-title">HR Help Desk</div>
    <div class="hero-sub">
        Ask any question about company policies - leave entitlements,
        compensation, performance reviews, WFH arrangements, POSH
        guidelines, and more. Answers are grounded in official Zyro
        Dynamics HR documents.
    </div>
    <div class="badge-row">
        <span class="badge">System Online</span>
        <span class="badge">LLaMA 3.3 70B via Groq</span>
        <span class="badge">{n_docs} Policy Documents</span>
        <span class="badge">{n_vecs} Indexed Chunks</span>
    </div>
</div>
""", unsafe_allow_html=True)


# ──────────────────────────────────────────────────────────────
#  STATS DASHBOARD
# ──────────────────────────────────────────────────────────────
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
        <div class="stat-val">LLaMA 3.3</div>
        <div class="stat-lbl">70B via Groq</div>
    </div>
</div>
""", unsafe_allow_html=True)


# ──────────────────────────────────────────────────────────────
#  RENDER CHAT HISTORY
# ──────────────────────────────────────────────────────────────
def _render_assistant_msg(msg: dict) -> None:
    if not msg.get("in_scope", True):
        st.markdown(f'<div class="oos-box">{msg["content"]}</div>', unsafe_allow_html=True)
    else:
        st.markdown(msg["content"])

    if msg.get("sources"):
        n = len(msg["sources"])
        with st.expander(f"Source citations ({n} document{'s' if n != 1 else ''} referenced)",
                          expanded=False):
            badges = ""
            for s in msg["sources"]:
                cat = f'<span class="src-cat">{s["category"]}</span>' if s.get("category") else ""
                badges += (
                    f'<span class="src-badge">{s["file"]}'
                    f'<span class="src-page">page {s["page"]}</span>'
                    f'{cat}</span>'
                )
            st.markdown(f'<div class="src-wrap">{badges}</div>', unsafe_allow_html=True)

    if msg.get("elapsed"):
        st.markdown(f'<div class="rt-chip">Response time: {msg["elapsed"]:.2f}s</div>',
                     unsafe_allow_html=True)


for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]):
        if msg["role"] == "assistant":
            _render_assistant_msg(msg)
        else:
            st.markdown(msg["content"])


# ──────────────────────────────────────────────────────────────
#  QUESTION HANDLER
# ──────────────────────────────────────────────────────────────
def handle_question(prompt: str) -> None:
    st.session_state.chat_history.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Searching HR policy documents..."):
            t0 = time.perf_counter()
            try:
                result = ask_bot(prompt)
            except Exception as exc:
                result = {
                    "answer": f"Unexpected error: {exc}. Please try again.",
                    "sources": [],
                    "in_scope": True,
                }
            elapsed = time.perf_counter() - t0

        msg = {
            "role": "assistant",
            "content": result["answer"],
            "sources": result.get("sources", []),
            "in_scope": result.get("in_scope", True),
            "elapsed": elapsed,
        }
        _render_assistant_msg(msg)

    st.session_state.chat_history.append(msg)
    st.session_state.queries_answered += 1


if st.session_state.pending_question:
    q = st.session_state.pending_question
    st.session_state.pending_question = None
    handle_question(q)

if prompt := st.chat_input("Ask a question about Zyro Dynamics HR policies..."):
    handle_question(prompt)


# ──────────────────────────────────────────────────────────────
#  INFO FOOTER
# ──────────────────────────────────────────────────────────────
retrieval_label = "FAISS cosine similarity + BM25 keyword (70 / 30 ensemble)" if BM25_AVAILABLE \
    else "FAISS cosine similarity (MMR)"

st.markdown(f"""
<div class="info-bar">
    Retrieval: <b>{retrieval_label}</b> &middot;
    Model: <b>LLaMA-3.3-70B-Versatile via Groq</b> &middot;
    Embeddings: <b>BAAI/bge-large-en-v1.5</b><br>
    Answers are grounded in policy documents only.
</div>
""", unsafe_allow_html=True)
