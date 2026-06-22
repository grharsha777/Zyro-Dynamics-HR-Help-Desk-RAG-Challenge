import streamlit as st
import os
import glob
import re

# ─── Page configuration ───────────────────────────────────────────────────────
st.set_page_config(
    page_title="Zyro Dynamics HR Help Desk",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Premium UI / UX / Motion / Security Layer ───────────────────────────────
st.markdown("""
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>
:root{
  --bg-0:#070b18;--bg-1:#0b1124;--bg-2:#101a36;
  --glass-bg:rgba(18,26,51,0.55);--glass-brd:rgba(125,159,255,0.18);
  --glass-brd-hi:rgba(146,197,255,0.45);
  --neon-cyan:#22d3ee;--neon-violet:#a855f7;--neon-magenta:#f472b6;--neon-blue:#60a5fa;
  --text-0:#eef2ff;--text-1:#c7d2fe;--text-2:#8b9bc7;
  --danger:#fca5a5;--danger-bg:rgba(252,165,165,0.08);
}
#AppViewContainer,.stApp,.main,section[data-testid="stAppViewContainer"]{
  background:radial-gradient(1200px 800px at 10% -10%,rgba(168,85,247,.18),transparent 60%),
  radial-gradient(1000px 700px at 100% 0%,rgba(34,211,238,.16),transparent 55%),
  radial-gradient(900px 600px at 50% 120%,rgba(96,165,250,.14),transparent 60%),
  linear-gradient(160deg,var(--bg-0) 0%,var(--bg-1) 50%,var(--bg-2) 100%)!important;
  background-attachment:fixed!important;color:var(--text-0)!important;
}
.zyro-aurora{position:fixed;inset:0;z-index:0;pointer-events:none;overflow:hidden}
.zyro-aurora::before,.zyro-aurora::after{content:"";position:absolute;width:60vw;height:60vw;border-radius:50%;filter:blur(120px);opacity:.35;mix-blend-mode:screen}
.zyro-aurora::before{top:-15%;left:-10%;background:conic-gradient(from 0deg,#22d3ee,#a855f7,#f472b6,#22d3ee);animation:zyro-spin 28s linear infinite}
.zyro-aurora::after{bottom:-20%;right:-15%;background:conic-gradient(from 180deg,#60a5fa,#22d3ee,#a855f7,#60a5fa);animation:zyro-spin 36s linear infinite reverse}
@keyframes zyro-spin{0%{transform:rotate(0) scale(1)}50%{transform:rotate(180deg) scale(1.08)}100%{transform:rotate(360deg) scale(1)}}
*::-webkit-scrollbar{width:10px;height:10px}
*::-webkit-scrollbar-track{background:rgba(255,255,255,.02)}
*::-webkit-scrollbar-thumb{background:linear-gradient(180deg,var(--neon-cyan),var(--neon-violet));border-radius:10px;border:2px solid transparent;background-clip:padding-box}
html{scrollbar-color:var(--neon-violet) transparent}
.stApp,.stApp p,.stApp span,.stApp li,.stApp label,.stApp div{font-family:'Inter','Segoe UI',system-ui,-apple-system,sans-serif!important}
.zyro-glass{position:relative;background:var(--glass-bg);backdrop-filter:blur(22px) saturate(150%);-webkit-backdrop-filter:blur(22px) saturate(150%);border:1px solid var(--glass-brd);border-radius:18px;box-shadow:0 10px 40px rgba(0,0,0,.35),inset 0 1px 0 rgba(255,255,255,.06);overflow:hidden}
.zyro-glass::before{content:"";position:absolute;inset:0;background:linear-gradient(120deg,transparent 30%,rgba(255,255,255,.06) 50%,transparent 70%);background-size:250% 250%;animation:zyro-shimmer 9s linear infinite;pointer-events:none}
@keyframes zyro-shimmer{0%{background-position:200% 0}100%{background-position:-200% 0}}
.zyro-hero{position:relative;z-index:2;padding:2.4rem 2.2rem;margin-bottom:1.6rem;text-align:center;animation:zyro-fadeUp .9s cubic-bezier(.2,.7,.2,1) both}
.zyro-hero h1{margin:0;font-size:clamp(1.6rem,3vw,2.4rem);font-weight:800;letter-spacing:-.02em;background:linear-gradient(90deg,#22d3ee,#a855f7,#f472b6,#60a5fa,#22d3ee);background-size:300% 100%;-webkit-background-clip:text;background-clip:text;color:transparent;animation:zyro-gradient 8s ease infinite;display:inline-block}
.zyro-hero .glyph{font-size:2.2rem;vertical-align:middle;display:inline-block;margin-right:.4rem;animation:zyro-float 4s ease-in-out infinite;filter:drop-shadow(0 0 14px rgba(168,85,247,.55))}
.zyro-hero p{margin:.7rem 0 0;color:var(--text-1);font-size:1rem;opacity:.92;letter-spacing:.01em}
.zyro-hero .zyro-divider{width:70%;margin:1.1rem auto 0;height:2px;background:linear-gradient(90deg,transparent,var(--neon-cyan),var(--neon-violet),transparent);border-radius:2px;opacity:.7}
@keyframes zyro-gradient{0%{background-position:0% 50%}50%{background-position:100% 50%}100%{background-position:0% 50%}}
@keyframes zyro-float{0%,100%{transform:translateY(0)}50%{transform:translateY(-6px)}}
@keyframes zyro-fadeUp{from{opacity:0;transform:translateY(18px)}to{opacity:1;transform:translateY(0)}}
section[data-testid="stSidebar"]{background:linear-gradient(180deg,rgba(11,17,36,.92),rgba(7,11,24,.96))!important;border-right:1px solid var(--glass-brd)!important;backdrop-filter:blur(18px)}
section[data-testid="stSidebar"] .stMarkdown h1,section[data-testid="stSidebar"] .stMarkdown h2,section[data-testid="stSidebar"] .stMarkdown h3{color:var(--text-0)!important;letter-spacing:-.01em}
section[data-testid="stSidebar"] hr{border-color:var(--glass-brd)!important;margin:1.1rem 0!important}
section[data-testid="stSidebar"] .stCaption,section[data-testid="stSidebar"] .stMarkdown p{color:var(--text-2)!important}
.stTextInput>div>div>input,.stTextArea textarea{background:rgba(10,16,36,.7)!important;border:1px solid var(--glass-brd)!important;border-radius:12px!important;color:var(--text-0)!important;transition:all .25s ease}
.stTextInput>div>div>input:focus,.stTextArea textarea:focus{border-color:var(--glass-brd-hi)!important;box-shadow:0 0 0 3px rgba(168,85,247,.18)!important;background:rgba(10,16,36,.9)!important}
.stButton>button{background:linear-gradient(135deg,rgba(34,211,238,.12),rgba(168,85,247,.16))!important;color:var(--text-0)!important;border:1px solid var(--glass-brd)!important;border-radius:12px!important;font-weight:600!important;letter-spacing:.01em;transition:all .28s cubic-bezier(.2,.7,.2,1)!important;position:relative;overflow:hidden}
.stButton>button::after{content:"";position:absolute;top:0;left:-120%;width:60%;height:100%;background:linear-gradient(120deg,transparent,rgba(255,255,255,.18),transparent);transform:skewX(-20deg);transition:left .6s ease}
.stButton>button:hover{transform:translateY(-2px);border-color:var(--glass-brd-hi)!important;box-shadow:0 8px 24px rgba(168,85,247,.28),0 0 0 1px rgba(34,211,238,.25) inset!important;background:linear-gradient(135deg,rgba(34,211,238,.22),rgba(168,85,247,.30))!important}
.stButton>button:hover::after{left:130%}
.stButton>button:active{transform:translateY(0)}
.stChatMessage{background:var(--glass-bg)!important;border:1px solid var(--glass-brd)!important;border-radius:16px!important;backdrop-filter:blur(14px);animation:zyro-fadeUp .55s cubic-bezier(.2,.7,.2,1) both;box-shadow:0 6px 24px rgba(0,0,0,.30)!important}
[data-testid="stChatMessageAvatarUser"]{background:linear-gradient(135deg,var(--neon-cyan),var(--neon-blue))!important}
[data-testid="stChatMessageAvatarAssistant"]{background:linear-gradient(135deg,var(--neon-violet),var(--neon-magenta))!important}
[data-testid="stChatInput"] textarea,[data-testid="stChatInputTextArea"]{background:rgba(10,16,36,.85)!important;border:1px solid var(--glass-brd)!important;border-radius:16px!important;color:var(--text-0)!important}
[data-testid="stChatInput"] textarea:focus{border-color:var(--glass-brd-hi)!important;box-shadow:0 0 0 3px rgba(34,211,238,.18)!important}
.source-badge{display:inline-flex;align-items:center;gap:.35rem;background:linear-gradient(135deg,rgba(34,211,238,.14),rgba(96,165,250,.14));border:1px solid rgba(96,165,250,.35);border-radius:999px;padding:4px 12px;font-size:.78rem;color:var(--text-1);margin:3px;transition:all .25s ease;backdrop-filter:blur(6px)}
.source-badge:hover{border-color:var(--neon-cyan);color:#fff;box-shadow:0 0 14px rgba(34,211,238,.45);transform:translateY(-1px)}
.oos-box{background:var(--danger-bg);border:1px solid rgba(252,165,165,.35);border-left:4px solid var(--danger);padding:.9rem 1.1rem;border-radius:12px;font-size:.92rem;color:#fecaca;backdrop-filter:blur(8px);animation:zyro-fadeUp .45s ease both}
details{background:rgba(10,16,36,.55)!important;border:1px solid var(--glass-brd)!important;border-radius:12px!important;backdrop-filter:blur(10px);transition:all .25s ease}
details:hover{border-color:var(--glass-brd-hi)!important}
details summary{color:var(--text-1)!important;font-weight:600}
.stSpinner>div{border-top-color:var(--neon-cyan)!important}
.stAlert{background:var(--glass-bg)!important;border:1px solid var(--glass-brd)!important;border-radius:14px!important;backdrop-filter:blur(14px);color:var(--text-1)!important}
.zyro-tagline{display:inline-block;margin-top:1rem;padding:6px 16px;font-size:.72rem;letter-spacing:.18em;text-transform:uppercase;color:var(--text-2);background:rgba(255,255,255,.04);border:1px solid var(--glass-brd);border-radius:999px;backdrop-filter:blur(6px)}
.zyro-foot{text-align:center;padding:1.2rem;color:var(--text-2);font-size:.78rem;letter-spacing:.08em;opacity:.8}
.dep-box{background:rgba(252,165,165,.06);border:1px solid rgba(252,165,165,.3);border-left:4px solid #f87171;padding:1.2rem 1.4rem;border-radius:14px;backdrop-filter:blur(8px)}
.dep-box code{background:rgba(0,0,0,.4);padding:2px 8px;border-radius:6px;font-size:.88rem;color:#fde68a}
</style>
</head>
<body>
<div class="zyro-aurora"></div>
<script>
(function(){
  document.addEventListener('contextmenu',function(e){e.preventDefault();return false},true);
  document.addEventListener('keydown',function(e){
    var k=e.key||e.keyCode;
    if(e.keyCode===123){e.preventDefault();return false}
    if(e.ctrlKey&&e.shiftKey&&('IJCijc'.indexOf(k)>-1)){e.preventDefault();return false}
    if(e.ctrlKey&&(k==='U'||k==='u')){e.preventDefault();return false}
  },true);
  var B=["%c⚠️  ZYRO DYNAMICS — ENTERPRISE SECURITY NOTICE  ⚠️","color:#fff;background:linear-gradient(90deg,#a855f7,#22d3ee);font-size:18px;font-weight:bold;padding:8px 16px;border-radius:6px;"];
  console.log.apply(console,B);
  console.log("%cThis console is monitored.","color:#fca5a5;font-size:12px;");
  setInterval(function(){console.clear();console.log.apply(console,B);console.log("%cThis console is monitored.","color:#fca5a5;font-size:12px;");},4000);
})();
</script>
</body>
</html>
""", unsafe_allow_html=True)

# ─── Header ───────────────────────────────────────────────────────────────────
st.markdown("""
<div class="zyro-hero zyro-glass">
    <h1><span class="glyph">🏢</span>Zyro Dynamics HR Help Desk</h1>
    <p>Ask any question about our HR policies — leave, compensation, WFH, POSH, and more.</p>
    <div class="zyro-divider"></div>
    <span class="zyro-tagline">AI-Powered · Retrieval-Augmented · Enterprise-Grade</span>
</div>
""", unsafe_allow_html=True)

# ─── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("⚙️ Configuration")
    groq_key = st.text_input(
        "Groq API Key",
        type="password",
        value=os.environ.get("GROQ_API_KEY", ""),
        help="Get a free key at https://console.groq.com",
    )
    langchain_key = st.text_input(
        "LangChain API Key (optional)",
        type="password",
        value=os.environ.get("LANGCHAIN_API_KEY", ""),
        help="Enables LangSmith tracing",
    )

    st.divider()
    st.header("💡 Sample Questions")
    sample_qs = [
        "How many days of earned leave do I get per year?",
        "When is salary credited each month?",
        "What is the WFH policy for L3 employees?",
        "What health insurance coverage do I get?",
        "What happens if I get a rating of 1 in my review?",
        "How long is the PIP duration?",
        "When is the Annual Performance Review?",
        "What is the payroll cut-off date?",
    ]
    for sq in sample_qs:
        if st.button(sq, use_container_width=True, key=f"sq_{sq[:20]}"):
            st.session_state.pending_question = sq

    st.divider()
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []

    st.divider()
    st.caption(
        "**Zyro Dynamics HR Help Desk**  \n"
        "Powered by LangChain · FAISS · Groq · Streamlit  \n"
        "Built for the NIAT × Kaggle RAG Challenge"
    )

# ═══════════════════════════════════════════════════════════════════════════════
# DEPENDENCY VALIDATOR — checks EVERYTHING upfront, reports ALL missing at once
# ═══════════════════════════════════════════════════════════════════════════════
def _check_all_dependencies() -> list[str]:
    """Return a list of missing pip package names (empty = all good)."""
    missing = []

    # (import_module_name, pip_package_name)
    hard_deps = [
        ("langchain_core",        "langchain-core"),
        ("langchain_groq",        "langchain-groq"),
        ("sentence_transformers", "sentence-transformers"),
        ("faiss",                 "faiss-cpu"),
    ]
    for mod, pkg in hard_deps:
        try:
            __import__(mod)
        except ImportError:
            missing.append(pkg)

    # PDF library — need at least one
    has_pdf = False
    for mod in ("pypdf", "fitz"):
        try:
            __import__(mod)
            has_pdf = True
            break
        except ImportError:
            pass
    if not has_pdf:
        missing.append("pypdf")

    return missing


_MISSING = _check_all_dependencies()
if _MISSING:
    st.markdown(
        '<div class="dep-box">'
        f'<p style="font-size:1.05rem;font-weight:700;color:#fca5a5;margin:0 0 .6rem;">'
        f'❌ Missing {len(_MISSING)} required package{"s" if len(_MISSING)>1 else ""}</p>'
        f'<p style="color:#e2e8f0;margin:0 0 .8rem;">'
        f'Add the following to your <strong>requirements.txt</strong> and redeploy:</p>'
        f'<code>{" ".join(_MISSING)}</code>'
        '</div>',
        unsafe_allow_html=True,
    )
    st.stop()


# ═══════════════════════════════════════════════════════════════════════════════
# PURE-PYTHON TEXT SPLITTER (eliminates langchain-text-splitters dependency)
# ═══════════════════════════════════════════════════════════════════════════════
class _SimpleDocument:
    """Minimal document container — avoids importing langchain_core at module level."""
    __slots__ = ("page_content", "metadata")

    def __init__(self, page_content: str, metadata: dict | None = None):
        self.page_content = page_content
        self.metadata = metadata or {}


def _split_text_recursive(
    text: str,
    chunk_size: int = 800,
    chunk_overlap: int = 120,
    separators: list[str] | None = None,
) -> list[str]:
    """Recursive character text splitter — pure Python, no dependencies."""
    if separators is None:
        separators = ["\n\n", "\n", ". ", " ", ""]

    final_chunks: list[str] = []

    def _split(current_text: str, sep_index: int) -> list[str]:
        if len(current_text) <= chunk_size:
            return [current_text] if current_text.strip() else []

        sep = separators[min(sep_index, len(separators) - 1)]

        if sep == "":
            # Last resort: hard slice
            return [
                current_text[i : i + chunk_size]
                for i in range(0, len(current_text), chunk_size - chunk_overlap)
                if current_text[i : i + chunk_size].strip()
            ]

        parts = current_text.split(sep)
        chunks: list[str] = []
        current = ""

        for part in parts:
            candidate = (current + sep + part) if current else part
            if len(candidate) <= chunk_size:
                current = candidate
            else:
                if current:
                    chunks.append(current)
                # If a single part is bigger than chunk_size, recurse with next separator
                if len(part) > chunk_size:
                    chunks.extend(_split(part, sep_index + 1))
                    current = ""
                else:
                    current = part

        if current.strip():
            chunks.append(current)

        return chunks

    raw = _split(text, 0)

    # Apply overlap by merging adjacent chunks
    if chunk_overlap > 0 and len(raw) > 1:
        merged = [raw[0]]
        for chunk in raw[1:]:
            overlap_text = merged[-1][-chunk_overlap:] if len(merged[-1]) > chunk_overlap else merged[-1]
            combined = overlap_text + chunk
            # If combined fits, use it; otherwise keep separate
            if len(combined) <= chunk_size * 1.3:
                merged[-1] = combined
            else:
                merged.append(chunk)
        final_chunks = merged
    else:
        final_chunks = raw

    return [c for c in final_chunks if c.strip()]


def _split_documents(
    documents: list[_SimpleDocument],
    chunk_size: int = 800,
    chunk_overlap: int = 120,
) -> list[_SimpleDocument]:
    """Split a list of documents into chunks."""
    chunks = []
    for doc in documents:
        texts = _split_text_recursive(doc.page_content, chunk_size, chunk_overlap)
        for t in texts:
            chunks.append(_SimpleDocument(page_content=t, metadata=dict(doc.metadata)))
    return chunks


# ═══════════════════════════════════════════════════════════════════════════════
# PDF LOADER — 4-strategy fallback (no langchain-community needed)
# ═══════════════════════════════════════════════════════════════════════════════
def _load_pdf(pdf_path: str) -> list[_SimpleDocument]:
    """Load PDF with cascading fallback strategies."""

    # Strategy 1: pypdf
    try:
        from pypdf import PdfReader
        reader = PdfReader(pdf_path)
        docs = []
        for i, page in enumerate(reader.pages):
            text = page.extract_text() or ""
            if text.strip():
                docs.append(_SimpleDocument(page_content=text, metadata={"source": pdf_path, "page": i}))
        return docs
    except Exception:
        pass

    # Strategy 2: PyMuPDF (fitz)
    try:
        import fitz
        doc = fitz.open(pdf_path)
        docs = []
        for i, page in enumerate(doc):
            text = page.get_text()
            if text.strip():
                docs.append(_SimpleDocument(page_content=text, metadata={"source": pdf_path, "page": i}))
        doc.close()
        return docs
    except Exception:
        pass

    raise ImportError(
        f"Cannot read `{pdf_path}`. Install a PDF library:\n"
        "  pip install pypdf\n"
        "  # OR\n"
        "  pip install PyMuPDF"
    )


# ═══════════════════════════════════════════════════════════════════════════════
# MINIMAL EMBEDDINGS WRAPPER — uses sentence-transformers directly
# ═══════════════════════════════════════════════════════════════════════════════
class _Embedder:
    """Thin wrapper around sentence-transformers — no langchain-huggingface needed."""

    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        from sentence_transformers import SentenceTransformer
        self._model = SentenceTransformer(model_name)

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        embs = self._model.encode(texts, normalize_embeddings=True, show_progress_bar=False)
        return [e.tolist() for e in embs]

    def embed_query(self, text: str) -> list[float]:
        emb = self._model.encode([text], normalize_embeddings=True, show_progress_bar=False)
        return emb[0].tolist()


# ═══════════════════════════════════════════════════════════════════════════════
# MINIMAL FAISS WRAPPER — uses faiss-cpu directly, no langchain-community
# ═══════════════════════════════════════════════════════════════════════════════
import numpy as np
import faiss


class _FaissStore:
    """Lightweight FAISS index with relevance scores — no langchain-community needed."""

    def __init__(self, documents: list[_SimpleDocument], embeddings: _Embedder):
        texts = [d.page_content for d in documents]
        vectors = np.array(embeddings.embed_documents(texts), dtype=np.float32)
        dim = vectors.shape[1]
        self._index = faiss.IndexFlatIP(dim)  # Inner product (= cosine on normalized vectors)
        self._index.add(vectors)
        self._documents = documents

    def similarity_search_with_relevance_scores(
        self, query: str, k: int = 5
    ) -> list[tuple[_SimpleDocument, float]]:
        q_vec = np.array([self._embedder.embed_query(query)], dtype=np.float32)
        scores, indices = self._index.search(q_vec, min(k, len(self._documents)))
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx >= 0:
                # FAISS InnerProduct on normalized vectors → score in [-1, 1]
                # Map to [0, 1] range for consistency with langchain's L2-based scoring
                relevance = float((score + 1) / 2)
                results.append((self._documents[idx], relevance))
        results.sort(key=lambda x: x[1], reverse=True)
        return results


# ═══════════════════════════════════════════════════════════════════════════════
# RAG PIPELINE (cached — builds only once per session)
# ═══════════════════════════════════════════════════════════════════════════════
@st.cache_resource(show_spinner="📚 Building HR knowledge base…")
def build_pipeline(_groq_key: str):

    # Now safe to import langchain packages we validated above
    from langchain_groq import ChatGroq
    from langchain_core.prompts import ChatPromptTemplate
    from langchain_core.output_parsers import StrOutputParser

    # ── Find corpus ───────────────────────────────────────────────────────────
    kaggle_path = "/kaggle/input/competitions/niat-masterclass-rag-challenge/zyro-dynamics-hr-corpus"
    local_path  = os.path.dirname(os.path.abspath(__file__))
    corpus_path = kaggle_path if os.path.exists(kaggle_path) else local_path

    pdf_files = sorted(glob.glob(os.path.join(corpus_path, "*.pdf")))
    if not pdf_files:
        st.error(f"No PDF files found in `{corpus_path}`. Make sure the HR corpus dataset is attached.")
        st.stop()

    # ── Load → chunk → embed → index ─────────────────────────────────────────
    documents: list[_SimpleDocument] = []
    for pdf_path in pdf_files:
        try:
            documents.extend(_load_pdf(pdf_path))
        except Exception as e:
            st.warning(f"Skipped `{os.path.basename(pdf_path)}`: {e}")

    if not documents:
        st.error("Failed to extract text from any PDF. See warnings above.")
        st.stop()

    chunks = _split_documents(documents, chunk_size=800, chunk_overlap=120)

    embedder = _Embedder(model_name="sentence-transformers/all-MiniLM-L6-v2")

    # Build FAISS store (pass embedder so it can embed queries later)
    store = _FaissStore(chunks, embedder)
    store._embedder = embedder  # attach for query-time use

    # ── LLM ──────────────────────────────────────────────────────────────────
    llm = ChatGroq(
        model="llama-3.3-70b-versatile",
        temperature=0.1,
        max_tokens=512,
        api_key=_groq_key,
    )
    parser = StrOutputParser()

    # ── Prompts ───────────────────────────────────────────────────────────────
    RAG_PROMPT = ChatPromptTemplate.from_template("""
You are an HR Help Desk assistant for Zyro Dynamics (also known as Acrux Dynamics).
Answer the employee's question using ONLY the information in the HR policy context below.
Be specific: include exact numbers, dates, limits, and percentages when they appear in the context.
Do NOT add information not found in the context.
If the context does not contain enough information, say:
"I don't have enough information in the HR policy documents to answer this question."

HR Policy Context:
{context}

Employee Question: {question}

Answer:
""")

    OOS_PROMPT = ChatPromptTemplate.from_template("""
You are a strict classifier. Decide if the question can be answered using
Zyro Dynamics internal HR policy documents.

HR policy documents cover ONLY:
- Leave policies (earned, sick, maternity, paternity, etc.)
- Work from home / hybrid / remote arrangements
- Code of conduct and ethics
- Performance reviews, PIP, APR, promotions
- Compensation, salary bands, bonuses, payroll dates
- Health insurance and employee benefits
- IT and data security policies
- Prevention of sexual harassment (POSH)
- Onboarding, probation, separation, full & final settlement
- Business travel and expense reimbursement
- Company overview, grade structure, office policies

Question: {question}

Reply with exactly one word — IN_SCOPE or OUT_OF_SCOPE. No explanation.
""")

    REFUSAL = (
        "I'm sorry, but I can only answer HR-related questions based on "
        "Zyro Dynamics internal policy documents. Your question falls outside "
        "the scope of what I can help with here. Please reach out to the relevant "
        "department or consult an external resource."
    )

    def format_docs(docs: list[_SimpleDocument]) -> str:
        parts = []
        for i, doc in enumerate(docs, 1):
            src  = doc.metadata.get("source", "").split("/")[-1]
            page = doc.metadata.get("page", "?")
            parts.append(f"[Source {i}: {src}, p.{page}]\n{doc.page_content}")
        return "\n\n---\n\n".join(parts)

    def ask_bot(question: str) -> dict:
        # Layer 1 — LLM scope classifier
        verdict = parser.invoke(
            llm.invoke(OOS_PROMPT.invoke({"question": question}))
        ).strip().upper()
        if "OUT_OF_SCOPE" in verdict:
            return {"answer": REFUSAL, "sources": [], "in_scope": False}

        # Layer 2 — similarity score floor
        docs_scores = store.similarity_search_with_relevance_scores(question, k=5)
        if docs_scores and docs_scores[0][1] < 0.60:
            return {"answer": REFUSAL, "sources": [], "in_scope": False}

        docs    = [d for d, _ in docs_scores]
        context = format_docs(docs)
        answer  = parser.invoke(
            llm.invoke(RAG_PROMPT.invoke({"context": context, "question": question}))
        )
        sources = [
            {"file": d.metadata.get("source", "").split("/")[-1],
             "page": d.metadata.get("page", "?")}
            for d in docs
        ]
        return {"answer": answer, "sources": sources, "in_scope": True}

    return ask_bot


# ─── Apply env vars from sidebar ─────────────────────────────────────────────
if groq_key:
    os.environ["GROQ_API_KEY"] = groq_key
if langchain_key:
    os.environ["LANGCHAIN_API_KEY"]    = langchain_key
    os.environ["LANGCHAIN_TRACING_V2"] = "true"
    os.environ["LANGCHAIN_PROJECT"]    = "zyro-rag-challenge"

# ─── Guard: require API key ───────────────────────────────────────────────────
if not groq_key:
    st.info(
        "👈 **Enter your Groq API Key** in the sidebar to start.  \n"
        "Get a free key at [console.groq.com](https://console.groq.com).",
        icon="🔑",
    )
    st.stop()

# ─── Build pipeline ───────────────────────────────────────────────────────────
ask_bot = build_pipeline(groq_key)

# ─── Session state init ───────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []

# ─── Render chat history ─────────────────────────────────────────────────────
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        if not msg.get("in_scope", True):
            st.markdown(
                f'<div class="oos-box">⚠️ {msg["content"]}</div>',
                unsafe_allow_html=True,
            )
        else:
            st.write(msg["content"])
        if msg.get("sources"):
            with st.expander("📄 Policy sources", expanded=False):
                for s in msg["sources"]:
                    st.markdown(
                        f'<span class="source-badge">📑 {s["file"]} — page {s["page"]}</span>',
                        unsafe_allow_html=True,
                    )

# ─── Common handler for any question ─────────────────────────────────────────
def handle_question(prompt: str):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)
    with st.chat_message("assistant"):
        with st.spinner("🔍 Searching HR policies…"):
            result   = ask_bot(prompt)
        answer   = result["answer"]
        sources  = result.get("sources", [])
        in_scope = result.get("in_scope", True)
        if not in_scope:
            st.markdown(
                f'<div class="oos-box">⚠️ {answer}</div>',
                unsafe_allow_html=True,
            )
        else:
            st.write(answer)
        if sources:
            with st.expander("📄 Policy sources", expanded=False):
                for s in sources:
                    st.markdown(
                        f'<span class="source-badge">📑 {s["file"]} — page {s["page"]}</span>',
                        unsafe_allow_html=True,
                    )
    st.session_state.messages.append({
        "role": "assistant",
        "content": answer,
        "sources": sources,
        "in_scope": in_scope,
    })

# ─── Handle sidebar sample click ─────────────────────────────────────────────
if "pending_question" in st.session_state:
    handle_question(st.session_state.pop("pending_question"))

# ─── Live chat input ─────────────────────────────────────────────────────────
if prompt := st.chat_input("Ask an HR question…"):
    handle_question(prompt)

# ─── Footer ───────────────────────────────────────────────────────────────────
st.markdown('<div class="zyro-foot">Zyro Dynamics © Confidential — Internal HR Help Desk</div>', unsafe_allow_html=True)
