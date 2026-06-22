import streamlit as st
import os
import glob

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
/* ============================================================
   ZYRO DYNAMICS — ENTERPRISE PREMIUM UI
   Single-file inline stylesheet (no external assets)
   ============================================================ */

/* ── Global tokens ─────────────────────────────────────────── */
:root{
  --bg-0:#070b18;
  --bg-1:#0b1124;
  --bg-2:#101a36;
  --glass-bg:rgba(18, 26, 51, 0.55);
  --glass-brd:rgba(125, 159, 255, 0.18);
  --glass-brd-hi:rgba(146, 197, 255, 0.45);
  --neon-cyan:#22d3ee;
  --neon-violet:#a855f7;
  --neon-magenta:#f472b6;
  --neon-blue:#60a5fa;
  --text-0:#eef2ff;
  --text-1:#c7d2fe;
  --text-2:#8b9bc7;
  --danger:#fca5a5;
  --danger-bg:rgba(252, 165, 165, 0.08);
  --ok:#86efac;
}

/* ── App background: deep corporate gradient w/ moving aurora ── */
#AppViewContainer, .stApp, .main, section[data-testid="stAppViewContainer"]{
  background: radial-gradient(1200px 800px at 10% -10%, rgba(168,85,247,0.18), transparent 60%),
              radial-gradient(1000px 700px at 100% 0%, rgba(34,211,238,0.16), transparent 55%),
              radial-gradient(900px 600px at 50% 120%, rgba(96,165,250,0.14), transparent 60%),
              linear-gradient(160deg, var(--bg-0) 0%, var(--bg-1) 50%, var(--bg-2) 100%) !important;
  background-attachment: fixed !important;
  color: var(--text-0) !important;
}

/* Animated aurora ribbons behind everything */
.zyro-aurora{
  position: fixed;
  inset: 0;
  z-index: 0;
  pointer-events: none;
  overflow: hidden;
}
.zyro-aurora::before,
.zyro-aurora::after{
  content:"";
  position:absolute;
  width: 60vw;
  height: 60vw;
  border-radius: 50%;
  filter: blur(120px);
  opacity: 0.35;
  mix-blend-mode: screen;
}
.zyro-aurora::before{
  top:-15%; left:-10%;
  background: conic-gradient(from 0deg, #22d3ee, #a855f7, #f472b6, #22d3ee);
  animation: zyro-spin 28s linear infinite;
}
.zyro-aurora::after{
  bottom:-20%; right:-15%;
  background: conic-gradient(from 180deg, #60a5fa, #22d3ee, #a855f7, #60a5fa);
  animation: zyro-spin 36s linear infinite reverse;
}
@keyframes zyro-spin{
  0%{transform: rotate(0deg) scale(1);}
  50%{transform: rotate(180deg) scale(1.08);}
  100%{transform: rotate(360deg) scale(1);}
}

/* ── Custom scrollbar ──────────────────────────────────────── */
*::-webkit-scrollbar{width:10px; height:10px;}
*::-webkit-scrollbar-track{background: rgba(255,255,255,0.02);}
*::-webkit-scrollbar-thumb{
  background: linear-gradient(180deg, var(--neon-cyan), var(--neon-violet));
  border-radius: 10px;
  border: 2px solid transparent;
  background-clip: padding-box;
}
*::-webkit-scrollbar-thumb:hover{
  background: linear-gradient(180deg, var(--neon-violet), var(--neon-magenta));
  background-clip: padding-box;
}
html{scrollbar-color: var(--neon-violet) transparent;}

/* ── Typography ────────────────────────────────────────────── */
.stApp, .stApp p, .stApp span, .stApp li, .stApp label, .stApp div{
  font-family: 'Inter', 'Segoe UI', system-ui, -apple-system, sans-serif !important;
}

/* ── Glass panel primitive ─────────────────────────────────── */
.zyro-glass{
  position: relative;
  background: var(--glass-bg);
  backdrop-filter: blur(22px) saturate(150%);
  -webkit-backdrop-filter: blur(22px) saturate(150%);
  border: 1px solid var(--glass-brd);
  border-radius: 18px;
  box-shadow:
    0 10px 40px rgba(0,0,0,0.35),
    inset 0 1px 0 rgba(255,255,255,0.06);
  overflow: hidden;
}
.zyro-glass::before{
  content:"";
  position:absolute;
  inset:0;
  background: linear-gradient(120deg, transparent 30%, rgba(255,255,255,0.06) 50%, transparent 70%);
  background-size: 250% 250%;
  animation: zyro-shimmer 9s linear infinite;
  pointer-events:none;
}
@keyframes zyro-shimmer{
  0%{background-position: 200% 0;}
  100%{background-position: -200% 0;}
}

/* ── Hero header ───────────────────────────────────────────── */
.zyro-hero{
  position: relative;
  z-index: 2;
  padding: 2.4rem 2.2rem;
  margin-bottom: 1.6rem;
  text-align: center;
  animation: zyro-fadeUp 0.9s cubic-bezier(.2,.7,.2,1) both;
}
.zyro-hero h1{
  margin:0;
  font-size: clamp(1.6rem, 3vw, 2.4rem);
  font-weight: 800;
  letter-spacing: -0.02em;
  background: linear-gradient(90deg, #22d3ee, #a855f7, #f472b6, #60a5fa, #22d3ee);
  background-size: 300% 100%;
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
  animation: zyro-gradient 8s ease infinite;
  display:inline-block;
}
.zyro-hero .glyph{
  font-size: 2.2rem;
  vertical-align: middle;
  display:inline-block;
  margin-right:.4rem;
  animation: zyro-float 4s ease-in-out infinite;
  filter: drop-shadow(0 0 14px rgba(168,85,247,0.55));
}
.zyro-hero p{
  margin: 0.7rem 0 0;
  color: var(--text-1);
  font-size: 1rem;
  opacity: 0.92;
  letter-spacing: 0.01em;
}
.zyro-hero .zyro-divider{
  width: 70%;
  margin: 1.1rem auto 0;
  height: 2px;
  background: linear-gradient(90deg, transparent, var(--neon-cyan), var(--neon-violet), transparent);
  border-radius: 2px;
  opacity:.7;
}
@keyframes zyro-gradient{
  0%{background-position: 0% 50%;}
  50%{background-position: 100% 50%;}
  100%{background-position: 0% 50%;}
}
@keyframes zyro-float{
  0%,100%{transform: translateY(0);}
  50%{transform: translateY(-6px);}
}
@keyframes zyro-fadeUp{
  from{opacity:0; transform: translateY(18px);}
  to{opacity:1; transform: translateY(0);}
}

/* ── Sidebar polish ────────────────────────────────────────── */
section[data-testid="stSidebar"]{
  background: linear-gradient(180deg, rgba(11,17,36,0.92), rgba(7,11,24,0.96)) !important;
  border-right: 1px solid var(--glass-brd) !important;
  backdrop-filter: blur(18px);
}
section[data-testid="stSidebar"] .stMarkdown h1,
section[data-testid="stSidebar"] .stMarkdown h2,
section[data-testid="stSidebar"] .stMarkdown h3{
  color: var(--text-0) !important;
  letter-spacing: -0.01em;
}
section[data-testid="stSidebar"] hr{
  border-color: var(--glass-brd) !important;
  margin: 1.1rem 0 !important;
}
section[data-testid="stSidebar"] .stCaption, section[data-testid="stSidebar"] .stMarkdown p{
  color: var(--text-2) !important;
}

/* ── Inputs ────────────────────────────────────────────────── */
.stTextInput > div > div > input,
.stTextArea textarea{
  background: rgba(10, 16, 36, 0.7) !important;
  border: 1px solid var(--glass-brd) !important;
  border-radius: 12px !important;
  color: var(--text-0) !important;
  transition: all .25s ease;
}
.stTextInput > div > div > input:focus,
.stTextArea textarea:focus{
  border-color: var(--glass-brd-hi) !important;
  box-shadow: 0 0 0 3px rgba(168,85,247,0.18) !important;
  background: rgba(10, 16, 36, 0.9) !important;
}

/* ── Buttons: kinetic hover ────────────────────────────────── */
.stButton > button{
  background: linear-gradient(135deg, rgba(34,211,238,0.12), rgba(168,85,247,0.16)) !important;
  color: var(--text-0) !important;
  border: 1px solid var(--glass-brd) !important;
  border-radius: 12px !important;
  font-weight: 600 !important;
  letter-spacing: 0.01em;
  transition: all .28s cubic-bezier(.2,.7,.2,1) !important;
  position: relative;
  overflow: hidden;
}
.stButton > button::after{
  content:"";
  position:absolute;
  top:0; left:-120%;
  width:60%; height:100%;
  background: linear-gradient(120deg, transparent, rgba(255,255,255,0.18), transparent);
  transform: skewX(-20deg);
  transition: left .6s ease;
}
.stButton > button:hover{
  transform: translateY(-2px);
  border-color: var(--glass-brd-hi) !important;
  box-shadow: 0 8px 24px rgba(168,85,247,0.28), 0 0 0 1px rgba(34,211,238,0.25) inset !important;
  background: linear-gradient(135deg, rgba(34,211,238,0.22), rgba(168,85,247,0.30)) !important;
}
.stButton > button:hover::after{ left: 130%; }
.stButton > button:active{ transform: translateY(0); }

/* ── Chat bubbles ──────────────────────────────────────────── */
.stChatMessage{
  background: var(--glass-bg) !important;
  border: 1px solid var(--glass-brd) !important;
  border-radius: 16px !important;
  backdrop-filter: blur(14px);
  animation: zyro-fadeUp .55s cubic-bezier(.2,.7,.2,1) both;
  box-shadow: 0 6px 24px rgba(0,0,0,0.30) !important;
}
[data-testid="stChatMessageAvatarUser"]{
  background: linear-gradient(135deg, var(--neon-cyan), var(--neon-blue)) !important;
}
[data-testid="stChatMessageAvatarAssistant"]{
  background: linear-gradient(135deg, var(--neon-violet), var(--neon-magenta)) !important;
}

/* ── Chat input ────────────────────────────────────────────── */
[data-testid="stChatInput"] textarea,
[data-testid="stChatInputTextArea"]{
  background: rgba(10, 16, 36, 0.85) !important;
  border: 1px solid var(--glass-brd) !important;
  border-radius: 16px !important;
  color: var(--text-0) !important;
}
[data-testid="stChatInput"] textarea:focus{
  border-color: var(--glass-brd-hi) !important;
  box-shadow: 0 0 0 3px rgba(34,211,238,0.18) !important;
}

/* ── Source badge (glassy pill) ────────────────────────────── */
.source-badge{
  display:inline-flex;
  align-items:center;
  gap:.35rem;
  background: linear-gradient(135deg, rgba(34,211,238,0.14), rgba(96,165,250,0.14));
  border: 1px solid rgba(96,165,250,0.35);
  border-radius: 999px;
  padding: 4px 12px;
  font-size: 0.78rem;
  color: var(--text-1);
  margin: 3px;
  transition: all .25s ease;
  backdrop-filter: blur(6px);
}
.source-badge:hover{
  border-color: var(--neon-cyan);
  color: #fff;
  box-shadow: 0 0 14px rgba(34,211,238,0.45);
  transform: translateY(-1px);
}

/* ── Out-of-scope box ──────────────────────────────────────── */
.oos-box{
  background: var(--danger-bg);
  border: 1px solid rgba(252,165,165,0.35);
  border-left: 4px solid var(--danger);
  padding: 0.9rem 1.1rem;
  border-radius: 12px;
  font-size: 0.92rem;
  color: #fecaca;
  backdrop-filter: blur(8px);
  animation: zyro-fadeUp .45s ease both;
}

/* ── Expanders (policy sources) ────────────────────────────── */
details{
  background: rgba(10,16,36,0.55) !important;
  border: 1px solid var(--glass-brd) !important;
  border-radius: 12px !important;
  backdrop-filter: blur(10px);
  transition: all .25s ease;
}
details:hover{ border-color: var(--glass-brd-hi) !important; }
details summary{
  color: var(--text-1) !important;
  font-weight: 600;
}

/* ── Spinner & info alerts ─────────────────────────────────── */
.stSpinner > div{ border-top-color: var(--neon-cyan) !important; }
.stAlert{
  background: var(--glass-bg) !important;
  border: 1px solid var(--glass-brd) !important;
  border-radius: 14px !important;
  backdrop-filter: blur(14px);
  color: var(--text-1) !important;
}

/* ── Header tagline pill ───────────────────────────────────── */
.zyro-tagline{
  display:inline-block;
  margin-top: 1rem;
  padding: 6px 16px;
  font-size: 0.72rem;
  letter-spacing: 0.18em;
  text-transform: uppercase;
  color: var(--text-2);
  background: rgba(255,255,255,0.04);
  border: 1px solid var(--glass-brd);
  border-radius: 999px;
  backdrop-filter: blur(6px);
}

/* ── Footer brand ──────────────────────────────────────────── */
.zyro-foot{
  text-align:center;
  padding: 1.2rem;
  color: var(--text-2);
  font-size: .78rem;
  letter-spacing: .08em;
  opacity: .8;
}
</style>
</head>
<body>
<div class="zyro-aurora"></div>

<script>
/* ============================================================
   FRONTEND SECURITY & DETECT-PREVENTION LAYER
   ============================================================ */
(function(){
  document.addEventListener('contextmenu', function(e){ e.preventDefault(); return false; }, true);

  document.addEventListener('keydown', function(e){
    var k = e.key || e.keyCode;
    if (e.keyCode === 123){ e.preventDefault(); return false; }
    if (e.ctrlKey && e.shiftKey && (k === 'I' || k === 'J' || k === 'C' || k === 'i' || k === 'j' || k === 'c')){
      e.preventDefault(); return false;
    }
    if (e.ctrlKey && (k === 'U' || k === 'u')){
      e.preventDefault(); return false;
    }
  }, true);

  var BANNER = [
    "%c⚠️  ZYRO DYNAMICS — ENTERPRISE SECURITY NOTICE  ⚠️",
    "color:#fff; background:linear-gradient(90deg,#a855f7,#22d3ee); font-size:18px; font-weight:bold; padding:8px 16px; border-radius:6px;"
  ];
  console.log.apply(console, BANNER);
  console.log("%cThis console is monitored. Unauthorized inspection of network traffic, source code, or application internals is strictly prohibited. All activity is logged and may be reviewed by the Zyro Dynamics Security Operations Center.",
    "color:#fca5a5; font-size:12px;");

  setInterval(function(){
    console.clear();
    console.log.apply(console, BANNER);
    console.log("%cThis console is monitored. Unauthorized inspection of network traffic, source code, or application internals is strictly prohibited. All activity is logged and may be reviewed by the Zyro Dynamics Security Operations Center.",
      "color:#fca5a5; font-size:12px;");
  }, 4000);
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

# ─── Robust PDF loading with multiple fallback strategies ─────────────────────
def _load_pdf_documents(pdf_path: str):
    """Load a single PDF file using the first available strategy.

    Tries in order:
      1. langchain_community.document_loaders.PyPDFLoader
      2. langchain_community.document_loaders.pdf.PyPDFLoader
      3. pypdf.PdfReader  (raw, wrapped into LangChain Document objects)
      4. PyMuPDF / fitz   (raw, wrapped into LangChain Document objects)
    Raises ImportError with clear instructions if nothing works.
    """
    # --- Strategy 1: standard langchain import --------------------------------
    try:
        from langchain_community.document_loaders import PyPDFLoader
        loader = PyPDFLoader(pdf_path)
        return loader.load()
    except (ModuleNotFoundError, ImportError, Exception):
        pass

    # --- Strategy 2: newer langchain sub-module path --------------------------
    try:
        from langchain_community.document_loaders.pdf import PyPDFLoader
        loader = PyPDFLoader(pdf_path)
        return loader.load()
    except (ModuleNotFoundError, ImportError, Exception):
        pass

    # --- Strategy 3: pypdf directly ------------------------------------------
    try:
        from pypdf import PdfReader
        from langchain_core.documents import Document
        reader = PdfReader(pdf_path)
        docs = []
        for i, page in enumerate(reader.pages):
            text = page.extract_text() or ""
            if text.strip():
                docs.append(Document(
                    page_content=text,
                    metadata={"source": pdf_path, "page": i},
                ))
        return docs
    except (ModuleNotFoundError, ImportError):
        pass

    # --- Strategy 4: PyMuPDF (fitz) directly ----------------------------------
    try:
        import fitz  # PyMuPDF
        from langchain_core.documents import Document
        doc = fitz.open(pdf_path)
        docs = []
        for i, page in enumerate(doc):
            text = page.get_text()
            if text.strip():
                docs.append(Document(
                    page_content=text,
                    metadata={"source": pdf_path, "page": i},
                ))
        doc.close()
        return docs
    except (ModuleNotFoundError, ImportError):
        pass

    # --- Nothing worked — tell the user exactly what to install ----------------
    raise ImportError(
        "No PDF parsing library found. Please install at least one of:\n\n"
        "  pip install pypdf\n"
        "  pip install PyMuPDF\n"
        "  pip install 'langchain-community[pdf]'\n\n"
        "Then restart the app."
    )


# ─── RAG pipeline (cached — builds only once per session) ────────────────────
@st.cache_resource(show_spinner="📚 Building HR knowledge base…")
def build_pipeline(_groq_key: str):
    from langchain_text_splitters import RecursiveCharacterTextSplitter
    from langchain_huggingface import HuggingFaceEmbeddings
    from langchain_community.vectorstores import FAISS
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
    documents = []
    for pdf_path in pdf_files:
        try:
            documents.extend(_load_pdf_documents(pdf_path))
        except Exception as e:
            st.warning(f"Skipped `{os.path.basename(pdf_path)}`: {e}")

    if not documents:
        st.error("Failed to extract text from any PDF. See warnings above.")
        st.stop()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=120,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    chunks = splitter.split_documents(documents)

    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True},
    )
    vectorstore = FAISS.from_documents(chunks, embeddings)

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

    def format_docs(docs):
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
        docs_scores = vectorstore.similarity_search_with_relevance_scores(question, k=5)
        if docs_scores and docs_scores[0][1] < 0.25:
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
