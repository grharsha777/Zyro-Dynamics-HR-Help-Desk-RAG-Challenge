"""
Zyro Dynamics — HR Help Desk  |  Enterprise RAG Chatbot
NIAT × Kaggle RAG Challenge
"""

import streamlit as st
import os
import glob
import time
import numpy as np

# ─── Page config  (must be first Streamlit call) ─────────────────────────────
st.set_page_config(
    page_title="Zyro Dynamics · HR Help Desk",
    page_icon="https://img.icons8.com/fluency/48/company.png",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ══════════════════════════════════════════════════════════════════════════════
#  DESIGN SYSTEM  —  Professional Enterprise HR  (no emoji in UI chrome)
# ══════════════════════════════════════════════════════════════════════════════
STYLES = """
<style>
/* ── Fonts ─────────────────────────────────────────────────────────────────── */
@import url('https://fonts.googleapis.com/css2?family=Inter:ital,wght@0,300;0,400;0,500;0,600;0,700;0,800&family=DM+Serif+Display:ital@0;1&display=swap');

/* ── Tokens ─────────────────────────────────────────────────────────────────── */
:root {
  --navy-950: #05091e;
  --navy-900: #090f28;
  --navy-800: #0e1535;
  --navy-700: #131c42;
  --navy-600: #1a254f;
  --panel:    rgba(13, 20, 52, 0.72);
  --panel-hi: rgba(18, 28, 65, 0.88);
  --stroke:   rgba(110, 140, 255, 0.13);
  --stroke-hi:rgba(140, 170, 255, 0.38);
  --accent:   #4f6ef7;
  --accent-lt:#7b93f9;
  --teal:     #14b8a6;
  --gold:     #d4a017;
  --gold-lt:  #f0c040;
  --danger:   #e05c6a;
  --success:  #22c27a;
  --txt-0:    #edf0ff;
  --txt-1:    #9aa5cc;
  --txt-2:    #5a6690;
  --r-sm: 8px;
  --r-md: 12px;
  --r-lg: 18px;
  --shadow: 0 8px 32px rgba(0,0,0,0.45);
}

/* ── Reset ──────────────────────────────────────────────────────────────────── */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

/* ── Background ─────────────────────────────────────────────────────────────── */
.stApp, .main,
section[data-testid="stAppViewContainer"],
div[data-testid="stAppViewContainer"] {
  background:
    radial-gradient(ellipse 1100px 700px at 0% 0%,   rgba(79,110,247,.18) 0%, transparent 60%),
    radial-gradient(ellipse 900px  600px at 100% 0%,  rgba(20,184,166,.13) 0%, transparent 55%),
    radial-gradient(ellipse 800px  800px at 50%  110%,rgba(79,110,247,.12) 0%, transparent 55%),
    linear-gradient(170deg, var(--navy-950) 0%, var(--navy-900) 45%, var(--navy-800) 100%) !important;
  background-attachment: fixed !important;
}

/* ── Global font ────────────────────────────────────────────────────────────── */
.stApp, .stApp * {
  font-family: 'Inter', system-ui, -apple-system, sans-serif !important;
}

/* ── Scrollbar ───────────────────────────────────────────────────────────────── */
::-webkit-scrollbar              { width: 6px; height: 6px; }
::-webkit-scrollbar-track        { background: transparent; }
::-webkit-scrollbar-thumb        { background: var(--accent); border-radius: 6px; opacity: .6; }

/* ══════════════════════════════════════════════════════════════════════════════
   SIDEBAR
══════════════════════════════════════════════════════════════════════════════ */
section[data-testid="stSidebar"] {
  background: linear-gradient(180deg, rgba(9,15,40,.98) 0%, rgba(5,9,30,.99) 100%) !important;
  border-right: 1px solid var(--stroke) !important;
}
section[data-testid="stSidebar"] > div { padding-top: 0 !important; }

/* Sidebar text */
section[data-testid="stSidebar"] .stMarkdown p,
section[data-testid="stSidebar"] .stMarkdown span,
section[data-testid="stSidebar"] .stCaption p { color: var(--txt-1) !important; font-size: .80rem !important; }
section[data-testid="stSidebar"] hr { border-color: var(--stroke) !important; margin: .8rem 0 !important; }

/* ══════════════════════════════════════════════════════════════════════════════
   ANIMATED BACKGROUND ORBS
══════════════════════════════════════════════════════════════════════════════ */
.bg-orbs { position: fixed; inset: 0; pointer-events: none; z-index: 0; overflow: hidden; }
.orb {
  position: absolute; border-radius: 50%;
  filter: blur(100px); opacity: .20; mix-blend-mode: screen;
}
.orb-1 { width:700px; height:700px; top:-200px; left:-150px;
  background: radial-gradient(circle, #4f6ef7, transparent 70%);
  animation: orb-float 26s ease-in-out infinite alternate; }
.orb-2 { width:550px; height:550px; top:5%; right:-100px;
  background: radial-gradient(circle, #14b8a6, transparent 70%);
  animation: orb-float 32s ease-in-out infinite alternate-reverse; }
.orb-3 { width:450px; height:450px; bottom:-100px; left:25%;
  background: radial-gradient(circle, #4f6ef7, transparent 70%);
  animation: orb-float 20s ease-in-out infinite alternate; opacity: .15; }
@keyframes orb-float {
  from { transform: translate(0, 0) scale(1); }
  to   { transform: translate(50px, 60px) scale(1.08); }
}

/* ══════════════════════════════════════════════════════════════════════════════
   HERO BANNER
══════════════════════════════════════════════════════════════════════════════ */
.hero-wrap {
  position: relative; z-index: 2;
  display: flex; align-items: center; gap: 2rem;
  background: var(--panel);
  border: 1px solid var(--stroke-hi);
  border-radius: var(--r-lg);
  backdrop-filter: blur(28px) saturate(150%);
  padding: 1.8rem 2rem;
  margin-bottom: 1.2rem;
  overflow: hidden;
  box-shadow: var(--shadow), inset 0 1px 0 rgba(255,255,255,.05);
  animation: fade-up .7s cubic-bezier(.2,.8,.2,1) both;
}
/* Top gradient border */
.hero-wrap::before {
  content: "";
  position: absolute; top: 0; left: 0; right: 0; height: 2px;
  background: linear-gradient(90deg, var(--accent), var(--teal), var(--accent));
  background-size: 200% 100%;
  animation: border-slide 5s linear infinite;
}
@keyframes border-slide { 0%{background-position:0%} 100%{background-position:200%} }

/* Subtle shimmer sweep */
.hero-wrap::after {
  content: "";
  position: absolute; top: 0; left: -80%; width: 40%; height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255,255,255,.04), transparent);
  animation: hero-sweep 9s linear infinite;
  pointer-events: none;
}
@keyframes hero-sweep { 0%{left:-80%} 100%{left:160%} }

.hero-img {
  width: 90px; height: 90px; flex-shrink: 0; border-radius: var(--r-md);
  object-fit: cover;
  box-shadow: 0 8px 28px rgba(79,110,247,.35);
  border: 1px solid var(--stroke-hi);
}

.hero-body { flex: 1; }
.hero-eyebrow {
  font-size: .68rem; font-weight: 600; letter-spacing: .14em;
  text-transform: uppercase; color: var(--accent-lt) !important;
  margin-bottom: .4rem;
}
.hero-title {
  font-family: 'DM Serif Display', Georgia, serif !important;
  font-size: clamp(1.4rem, 2.6vw, 2rem);
  font-weight: 400;
  color: var(--txt-0) !important;
  letter-spacing: -.01em;
  line-height: 1.2;
  margin-bottom: .4rem;
}
.hero-title em { font-style: italic; color: var(--accent-lt) !important; }
.hero-sub {
  font-size: .88rem; color: var(--txt-1) !important; line-height: 1.55;
  max-width: 560px;
}
.hero-pills { display: flex; flex-wrap: wrap; gap: .5rem; margin-top: .9rem; }
.pill {
  display: inline-flex; align-items: center; gap: .3rem;
  padding: 3px 11px; border-radius: 999px;
  font-size: .70rem; font-weight: 600; letter-spacing: .06em; text-transform: uppercase;
  border: 1px solid; backdrop-filter: blur(6px);
}
.pill-blue  { background: rgba(79,110,247,.10); border-color: rgba(79,110,247,.35); color: var(--accent-lt) !important; }
.pill-teal  { background: rgba(20,184,166,.10); border-color: rgba(20,184,166,.35); color: #2dd4bf !important; }
.pill-gold  { background: rgba(212,160,23,.10);  border-color: rgba(212,160,23,.35);  color: var(--gold-lt) !important; }
.pill-green { background: rgba(34,194,122,.10); border-color: rgba(34,194,122,.35); color: var(--success) !important; }
.dot-live {
  display: inline-block; width: 6px; height: 6px; border-radius: 50%;
  background: var(--success); margin-right: 3px;
  box-shadow: 0 0 5px var(--success);
  animation: blink 2s ease-in-out infinite;
}
@keyframes blink { 0%,100%{opacity:1} 50%{opacity:.4} }

/* ══════════════════════════════════════════════════════════════════════════════
   STATS ROW
══════════════════════════════════════════════════════════════════════════════ */
.stats-row {
  display: grid; grid-template-columns: repeat(4, 1fr); gap: .9rem;
  margin-bottom: 1.2rem;
  animation: fade-up .7s .1s cubic-bezier(.2,.8,.2,1) both;
}
.stat-card {
  background: var(--panel);
  border: 1px solid var(--stroke);
  border-radius: var(--r-md);
  padding: 1rem 1.2rem;
  backdrop-filter: blur(18px);
  text-align: center;
  transition: border-color .25s, transform .25s, box-shadow .25s;
  cursor: default;
}
.stat-card:hover {
  border-color: var(--stroke-hi);
  transform: translateY(-2px);
  box-shadow: 0 10px 28px rgba(0,0,0,.35);
}
.stat-num {
  font-family: 'DM Serif Display', serif !important;
  font-size: 1.8rem; font-weight: 400; color: var(--txt-0) !important;
  display: block; line-height: 1;
}
.stat-num-accent { color: var(--accent-lt) !important; }
.stat-num-teal   { color: #2dd4bf !important; }
.stat-num-gold   { color: var(--gold-lt) !important; }
.stat-num-green  { color: var(--success) !important; }
.stat-label {
  font-size: .68rem; color: var(--txt-2) !important;
  letter-spacing: .08em; text-transform: uppercase;
  margin-top: .35rem; display: block;
}

/* ══════════════════════════════════════════════════════════════════════════════
   CHAT MESSAGES  —  TEXT OVERFLOW FIX
══════════════════════════════════════════════════════════════════════════════ */

/* Kill Streamlit's default avatar icon text rendering */
[data-testid="stChatMessageAvatarUser"] *,
[data-testid="stChatMessageAvatarAssistant"] * {
  font-size: 0 !important;
  line-height: 0 !important;
}

.stChatMessage {
  background: var(--panel) !important;
  border: 1px solid var(--stroke) !important;
  border-radius: var(--r-md) !important;
  backdrop-filter: blur(18px) !important;
  box-shadow: 0 4px 20px rgba(0,0,0,.28) !important;
  animation: fade-up .4s cubic-bezier(.2,.8,.2,1) both;
  margin-bottom: .7rem !important;
  /* OVERFLOW FIX */
  overflow: hidden !important;
  min-width: 0 !important;
}

/* Ensure message content text wraps and never overflows */
.stChatMessage p,
.stChatMessage span,
.stChatMessage div,
.stChatMessage li {
  color: var(--txt-0) !important;
  word-wrap: break-word !important;
  overflow-wrap: break-word !important;
  word-break: break-word !important;
  white-space: pre-wrap !important;
  max-width: 100% !important;
  line-height: 1.65 !important;
}
.stChatMessage p { font-size: .9rem !important; }

/* Message content container */
[data-testid="stChatMessageContent"] {
  overflow: hidden !important;
  min-width: 0 !important;
  max-width: 100% !important;
}

/* Avatar styling — replace icon text with initials via pseudo */
[data-testid="stChatMessageAvatarUser"] {
  background: linear-gradient(135deg, var(--accent), #7b93f9) !important;
  border: none !important;
  flex-shrink: 0 !important;
}
[data-testid="stChatMessageAvatarAssistant"] {
  background: linear-gradient(135deg, #0d2a4a, #1a3a6a) !important;
  border: 1px solid var(--stroke-hi) !important;
  flex-shrink: 0 !important;
}

/* ── Chat input ─────────────────────────────────────────────────────────────── */
[data-testid="stChatInput"] textarea,
[data-testid="stChatInputTextArea"] {
  background: rgba(9,15,40,.85) !important;
  border: 1px solid var(--stroke-hi) !important;
  border-radius: var(--r-md) !important;
  color: var(--txt-0) !important;
  font-size: .9rem !important;
  transition: box-shadow .25s, border-color .25s;
}
[data-testid="stChatInput"] textarea:focus {
  border-color: var(--accent) !important;
  box-shadow: 0 0 0 3px rgba(79,110,247,.20) !important;
}

/* ══════════════════════════════════════════════════════════════════════════════
   SIDEBAR ELEMENTS
══════════════════════════════════════════════════════════════════════════════ */
.stButton > button {
  background: rgba(79,110,247,.08) !important;
  color: var(--txt-1) !important;
  border: 1px solid var(--stroke) !important;
  border-radius: var(--r-sm) !important;
  font-size: .80rem !important;
  font-weight: 500 !important;
  text-align: left !important;
  transition: all .22s ease !important;
  padding: .4rem .7rem !important;
}
.stButton > button:hover {
  background: rgba(79,110,247,.18) !important;
  border-color: var(--stroke-hi) !important;
  color: var(--txt-0) !important;
  transform: translateX(3px) !important;
}

.stTextInput > div > div > input {
  background: rgba(9,15,40,.80) !important;
  border: 1px solid var(--stroke) !important;
  border-radius: var(--r-sm) !important;
  color: var(--txt-0) !important;
  font-size: .85rem !important;
  transition: border-color .25s, box-shadow .25s;
}
.stTextInput > div > div > input:focus {
  border-color: var(--accent) !important;
  box-shadow: 0 0 0 2px rgba(79,110,247,.20) !important;
}
.stTextInput label { color: var(--txt-2) !important; font-size: .75rem !important;
  letter-spacing: .05em; text-transform: uppercase; font-weight: 600 !important; }

/* ══════════════════════════════════════════════════════════════════════════════
   CUSTOM COMPONENTS
══════════════════════════════════════════════════════════════════════════════ */

/* Section label */
.section-label {
  font-size: .66rem; font-weight: 700; letter-spacing: .12em;
  text-transform: uppercase; color: var(--txt-2) !important;
  padding: .6rem 0 .3rem;
}

/* Quick-question buttons in sidebar */
.qq-btn {
  display: block; width: 100%;
  padding: .45rem .7rem;
  background: rgba(79,110,247,.07);
  border: 1px solid var(--stroke);
  border-radius: var(--r-sm);
  color: var(--txt-1) !important;
  font-size: .78rem; font-weight: 400; text-align: left;
  margin-bottom: .3rem; cursor: pointer;
  transition: all .2s ease;
}
.qq-btn:hover { background: rgba(79,110,247,.16); border-color: var(--stroke-hi); color: var(--txt-0) !important; }

/* Doc list in sidebar */
.doc-row {
  display: flex; align-items: center; gap: .6rem;
  padding: .35rem .6rem; border-radius: var(--r-sm);
  margin-bottom: .25rem;
  background: rgba(255,255,255,.025);
  border: 1px solid var(--stroke);
  font-size: .75rem; color: var(--txt-1) !important;
  transition: all .2s;
}
.doc-row:hover { background: rgba(79,110,247,.10); border-color: var(--stroke-hi); }
.doc-icon { width: 6px; height: 6px; border-radius: 50%; background: var(--accent); flex-shrink: 0; }

/* Source citation pills */
.cite-pill {
  display: inline-flex; align-items: center; gap: .3rem;
  background: rgba(79,110,247,.09);
  border: 1px solid rgba(79,110,247,.28);
  border-radius: 6px; padding: 4px 10px;
  font-size: .74rem; color: var(--txt-1) !important;
  margin: 3px; transition: all .2s ease;
}
.cite-pill:hover {
  border-color: var(--accent); color: var(--txt-0) !important;
  box-shadow: 0 0 10px rgba(79,110,247,.25);
}
.cite-dot { width: 5px; height: 5px; border-radius: 50%; background: var(--accent); display: inline-block; }

/* Out-of-scope response */
.oos-card {
  background: rgba(224,92,106,.06);
  border: 1px solid rgba(224,92,106,.25);
  border-left: 3px solid var(--danger);
  border-radius: var(--r-sm);
  padding: .85rem 1rem;
  font-size: .88rem; color: #fca5a5 !important;
  line-height: 1.6;
}

/* Welcome empty state */
.empty-state {
  background: var(--panel);
  border: 1px solid var(--stroke);
  border-radius: var(--r-md);
  padding: 2.5rem 2rem;
  text-align: center;
  backdrop-filter: blur(18px);
  animation: fade-up .6s .2s both;
}
.empty-state-icon {
  width: 56px; height: 56px; margin: 0 auto .9rem;
  background: linear-gradient(135deg, var(--accent), var(--teal));
  border-radius: 14px;
  display: flex; align-items: center; justify-content: center;
}
.empty-state h3 {
  font-family: 'DM Serif Display', serif !important;
  font-size: 1.2rem; color: var(--txt-0) !important;
  margin-bottom: .4rem; font-weight: 400;
}
.empty-state p { font-size: .85rem; color: var(--txt-1) !important; line-height: 1.6; max-width: 380px; margin: 0 auto; }

/* Expander */
details {
  background: rgba(9,15,40,.60) !important;
  border: 1px solid var(--stroke) !important;
  border-radius: var(--r-sm) !important;
  transition: border-color .2s;
}
details:hover { border-color: var(--stroke-hi) !important; }
details summary { color: var(--txt-1) !important; font-size: .80rem !important; font-weight: 600; }

/* Alerts */
.stAlert {
  background: var(--panel) !important;
  border: 1px solid var(--stroke) !important;
  border-radius: var(--r-md) !important;
  color: var(--txt-1) !important;
}

/* Progress */
.stProgress > div > div {
  background: linear-gradient(90deg, var(--accent), var(--teal)) !important;
  border-radius: 4px !important;
}

/* Footer */
.hr-footer {
  text-align: center; padding: 1.2rem;
  color: var(--txt-2) !important; font-size: .72rem;
  letter-spacing: .05em; border-top: 1px solid var(--stroke); margin-top: 1.5rem;
}
.hr-footer a { color: var(--accent-lt) !important; text-decoration: none; }

/* Animations */
@keyframes fade-up {
  from { opacity: 0; transform: translateY(14px); }
  to   { opacity: 1; transform: translateY(0); }
}

/* Divider */
.stDivider { border-color: var(--stroke) !important; }

/* Status widget */
.stStatus { background: var(--panel) !important; border: 1px solid var(--stroke) !important;
  border-radius: var(--r-md) !important; }

/* Info message */
.rag-info-bar {
  background: rgba(79,110,247,.08);
  border: 1px solid rgba(79,110,247,.22);
  border-radius: var(--r-sm);
  padding: .55rem .85rem;
  font-size: .78rem; color: var(--txt-1) !important;
  margin-bottom: .7rem;
  display: flex; align-items: center; gap: .5rem;
}
.rag-info-bar b { color: var(--accent-lt) !important; }
</style>
"""

st.markdown(STYLES, unsafe_allow_html=True)

# ── Animated background ───────────────────────────────────────────────────────
st.markdown("""
<div class="bg-orbs">
  <div class="orb orb-1"></div>
  <div class="orb orb-2"></div>
  <div class="orb orb-3"></div>
</div>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:

    # Brand
    st.markdown("""
    <div style="padding:1.4rem 0 .6rem;text-align:center;">
      <img src="https://img.icons8.com/fluency/80/company.png"
           style="width:52px;height:52px;border-radius:12px;
                  box-shadow:0 6px 20px rgba(79,110,247,.35);margin-bottom:.6rem;display:block;margin-left:auto;margin-right:auto;">
      <div style="font-family:'DM Serif Display',serif;font-size:1.05rem;color:#edf0ff;letter-spacing:-.01em;">
        Zyro Dynamics
      </div>
      <div style="font-size:.66rem;color:#5a6690;letter-spacing:.12em;text-transform:uppercase;margin-top:2px;">
        HR Help Desk &middot; AI
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    # API keys
    st.markdown('<div class="section-label">API Configuration</div>', unsafe_allow_html=True)
    groq_key = st.text_input(
        "Groq API Key",
        type="password",
        value=os.environ.get("GROQ_API_KEY", ""),
        placeholder="gsk_...",
        help="Free key at console.groq.com",
    )
    langchain_key = st.text_input(
        "LangSmith Key (optional)",
        type="password",
        value=os.environ.get("LANGCHAIN_API_KEY", ""),
        placeholder="ls__...",
        help="Enables LangSmith tracing",
    )

    st.divider()

    # Quick questions
    st.markdown('<div class="section-label">Quick Questions</div>', unsafe_allow_html=True)
    SAMPLE_QS = [
        "How many earned leave days per year?",
        "When is salary credited each month?",
        "What is the WFH policy for L3 employees?",
        "What health insurance coverage do employees get?",
        "What happens with a performance rating of 1?",
        "How long is the PIP duration?",
        "When is the Annual Performance Review?",
        "What is the payroll cut-off date?",
        "What is the maternity leave entitlement?",
        "How do I claim travel reimbursements?",
        "What is the notice period for resignation?",
        "How does the performance bonus work?",
    ]
    for q in SAMPLE_QS:
        if st.button(q, use_container_width=True, key=f"sq_{hash(q)}"):
            st.session_state.pending_question = q

    st.divider()

    # Knowledge base docs
    st.markdown('<div class="section-label">Knowledge Base</div>', unsafe_allow_html=True)
    DOCS = [
        "Company Profile",
        "Employee Handbook",
        "Leave Policy",
        "Work From Home Policy",
        "Code of Conduct",
        "Performance Review Policy",
        "Compensation & Benefits",
        "IT & Data Security",
        "Prevention of Sexual Harassment",
        "Onboarding & Separation",
        "Travel & Expense Policy",
    ]
    for d in DOCS:
        st.markdown(f'<div class="doc-row"><span class="doc-icon"></span>{d}</div>',
                    unsafe_allow_html=True)

    st.divider()

    c1, c2 = st.columns(2)
    with c1:
        if st.button("Clear Chat", use_container_width=True):
            st.session_state.messages     = []
            st.session_state.query_count  = 0
            st.rerun()
    with c2:
        if st.button("Reset App", use_container_width=True):
            for k in ["messages", "rag_pipeline", "query_count", "pending_question",
                      "n_docs", "n_chunks"]:
                st.session_state.pop(k, None)
            st.rerun()

    st.divider()
    st.markdown("""
    <div style="font-size:.70rem;color:#5a6690;line-height:1.8;text-align:center;">
      Powered by <span style="color:#9aa5cc;">LangChain</span> &middot;
      <span style="color:#9aa5cc;">FAISS</span> &middot;
      <span style="color:#9aa5cc;">Groq LLaMA&nbsp;3.3&nbsp;70B</span><br>
      NIAT &times; Kaggle RAG Challenge
    </div>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  DEPENDENCY CHECK
# ══════════════════════════════════════════════════════════════════════════════
def _check_deps() -> list[str]:
    missing = []
    for mod, pkg in [
        ("langchain_core",        "langchain-core"),
        ("langchain_groq",        "langchain-groq"),
        ("sentence_transformers", "sentence-transformers"),
        ("faiss",                 "faiss-cpu"),
    ]:
        try:
            __import__(mod)
        except ImportError:
            missing.append(pkg)
    try:
        __import__("pypdf")
    except ImportError:
        try:
            __import__("fitz")
        except ImportError:
            missing.append("pypdf")
    return missing

_MISSING = _check_deps()
if _MISSING:
    st.error(f"**Missing packages:** `{' '.join(_MISSING)}` — add to `requirements.txt` and redeploy.")
    st.stop()


# ══════════════════════════════════════════════════════════════════════════════
#  PURE-PYTHON DOCUMENT TYPES & SPLITTER
# ══════════════════════════════════════════════════════════════════════════════
class _Doc:
    __slots__ = ("page_content", "metadata")
    def __init__(self, page_content: str, metadata: dict | None = None):
        self.page_content = page_content
        self.metadata     = metadata or {}


def _split_text(text: str, chunk_size: int = 600, chunk_overlap: int = 100) -> list[str]:
    """
    Recursive splitter.  Smaller chunk_size (600) gives more, richer chunks
    from compact PDFs — fixes the '39 chunks' problem.
    """
    seps = ["\n\n", "\n", ". ", " ", ""]

    def _rec(txt: str, si: int) -> list[str]:
        if len(txt) <= chunk_size:
            return [txt] if txt.strip() else []
        sep = seps[min(si, len(seps) - 1)]
        if not sep:
            return [txt[i:i+chunk_size]
                    for i in range(0, len(txt), max(1, chunk_size - chunk_overlap))
                    if txt[i:i+chunk_size].strip()]
        parts, chunks, cur = txt.split(sep), [], ""
        for part in parts:
            cand = (cur + sep + part) if cur else part
            if len(cand) <= chunk_size:
                cur = cand
            else:
                if cur: chunks.append(cur)
                if len(part) > chunk_size:
                    chunks.extend(_rec(part, si + 1)); cur = ""
                else:
                    cur = part
        if cur.strip(): chunks.append(cur)
        return chunks

    raw = _rec(text, 0)
    if chunk_overlap <= 0 or len(raw) <= 1:
        return [c for c in raw if c.strip()]
    merged = [raw[0]]
    for chunk in raw[1:]:
        tail = merged[-1][-chunk_overlap:]
        if len(tail + chunk) <= int(chunk_size * 1.3):
            merged[-1] = tail + chunk
        else:
            merged.append(chunk)
    return [c for c in merged if c.strip()]


def _split_docs(docs: list[_Doc], chunk_size=600, chunk_overlap=100) -> list[_Doc]:
    out = []
    for doc in docs:
        for t in _split_text(doc.page_content, chunk_size, chunk_overlap):
            out.append(_Doc(page_content=t, metadata=dict(doc.metadata)))
    return out


# ══════════════════════════════════════════════════════════════════════════════
#  PDF LOADER
# ══════════════════════════════════════════════════════════════════════════════
def _load_pdf(path: str) -> list[_Doc]:
    # Strategy 1 — pypdf
    try:
        from pypdf import PdfReader
        reader = PdfReader(path)
        pages  = []
        for i, page in enumerate(reader.pages):
            txt = (page.extract_text() or "").strip()
            if txt:
                pages.append(_Doc(page_content=txt, metadata={"source": path, "page": i}))
        if pages:
            return pages
    except Exception:
        pass
    # Strategy 2 — PyMuPDF
    try:
        import fitz
        doc   = fitz.open(path)
        pages = []
        for i, page in enumerate(doc):
            txt = page.get_text().strip()
            if txt:
                pages.append(_Doc(page_content=txt, metadata={"source": path, "page": i}))
        doc.close()
        return pages
    except Exception:
        pass
    raise RuntimeError(f"Cannot read {path}. Install pypdf or PyMuPDF.")


# ══════════════════════════════════════════════════════════════════════════════
#  EMBEDDER  (sentence-transformers direct)
# ══════════════════════════════════════════════════════════════════════════════
class _Embedder:
    def __init__(self, model: str = "sentence-transformers/all-MiniLM-L6-v2"):
        from sentence_transformers import SentenceTransformer
        self._m = SentenceTransformer(model)

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return self._m.encode(texts, normalize_embeddings=True,
                              show_progress_bar=False, batch_size=64).tolist()

    def embed_query(self, text: str) -> list[float]:
        return self._m.encode([text], normalize_embeddings=True,
                              show_progress_bar=False)[0].tolist()


# ══════════════════════════════════════════════════════════════════════════════
#  FAISS VECTOR STORE  (self-contained — no langchain-community)
# ══════════════════════════════════════════════════════════════════════════════
import faiss

class _VectorStore:
    def __init__(self, docs: list[_Doc], embedder: _Embedder):
        self._embedder = embedder          # ← CRITICAL BUG FIX: store first
        self._docs     = docs
        vecs = np.array(
            embedder.embed_documents([d.page_content for d in docs]),
            dtype=np.float32
        )
        dim          = vecs.shape[1]
        self._index  = faiss.IndexFlatIP(dim)   # inner-product = cosine on L2-norm vecs
        self._index.add(vecs)

    def search(self, query: str, k: int = 6) -> list[tuple[_Doc, float]]:
        q      = np.array([self._embedder.embed_query(query)], dtype=np.float32)
        scores, idxs = self._index.search(q, min(k, len(self._docs)))
        result = []
        for s, i in zip(scores[0], idxs[0]):
            if i >= 0:
                result.append((self._docs[i], float((s + 1) / 2)))   # [-1,1] → [0,1]
        return sorted(result, key=lambda x: x[1], reverse=True)


# ══════════════════════════════════════════════════════════════════════════════
#  RAG PIPELINE  (cached — builds once per session)
# ══════════════════════════════════════════════════════════════════════════════
@st.cache_resource(show_spinner=False)
def build_pipeline(_groq_key: str):
    from langchain_groq import ChatGroq
    from langchain_core.prompts import ChatPromptTemplate
    from langchain_core.output_parsers import StrOutputParser

    # ── Locate PDFs ──────────────────────────────────────────────────────────
    base = os.path.dirname(os.path.abspath(__file__))
    search_dirs = [
        "/kaggle/input/competitions/niat-masterclass-rag-challenge/zyro-dynamics-hr-corpus",
        os.path.join(base, "zyro-dynamics-hr-corpus"),
        base,
    ]
    pdf_files = []
    for d in search_dirs:
        found = sorted(glob.glob(os.path.join(d, "*.pdf")))
        if found:
            pdf_files = found
            break

    if not pdf_files:
        st.error("No PDF files found. Ensure `zyro-dynamics-hr-corpus/` is in your repository.")
        st.stop()

    # ── Load pages ───────────────────────────────────────────────────────────
    raw_docs: list[_Doc] = []
    for p in pdf_files:
        try:
            raw_docs.extend(_load_pdf(p))
        except Exception as e:
            st.warning(f"Skipped {os.path.basename(p)}: {e}")

    if not raw_docs:
        st.error("Could not extract text from any PDF.")
        st.stop()

    # ── Chunk (smaller = more chunks = better recall) ────────────────────────
    chunks = _split_docs(raw_docs, chunk_size=600, chunk_overlap=100)

    # ── Embed & index ────────────────────────────────────────────────────────
    embedder = _Embedder()
    store    = _VectorStore(chunks, embedder)

    # ── LLM ──────────────────────────────────────────────────────────────────
    llm    = ChatGroq(
        model="llama-3.3-70b-versatile",
        temperature=0.05,
        max_tokens=700,
        api_key=_groq_key,
    )
    parser = StrOutputParser()

    # ── Prompts ───────────────────────────────────────────────────────────────
    RAG_PROMPT = ChatPromptTemplate.from_template("""
You are a precise, professional HR Help Desk assistant for Zyro Dynamics (also called Acrux Dynamics).

STRICT RULES:
1. Answer ONLY using the HR Policy Context below.
2. Be specific — include exact numbers, dates, durations, percentages, and conditions.
3. Structure longer answers with clear, concise paragraphs or bullet points.
4. Never fabricate information not found in the context.
5. If context is insufficient, say: "The HR policy documents do not contain sufficient detail to answer this question. Please contact HR directly."
6. Write in a professional, neutral HR tone. No greetings, no filler phrases.

HR Policy Context:
{context}

Employee Question:
{question}

Answer:""")

    OOS_PROMPT = ChatPromptTemplate.from_template("""
You are a strict binary classifier for an HR chatbot.
Determine if the following question can be answered from Zyro Dynamics internal HR policy documents.

In-scope: leave policies, WFH/remote, code of conduct, performance reviews (APR, PIP, ratings),
compensation, salary, payroll, bonuses, health insurance, benefits, IT/data security, POSH/ICC,
onboarding, probation, separation, full & final settlement, travel & expense reimbursement,
company overview, culture, grade structure, office policies.

Question: {question}

Reply with EXACTLY one word — IN_SCOPE or OUT_OF_SCOPE. Nothing else.""")

    REFUSAL = (
        "This question falls outside the scope of Zyro Dynamics HR policy documents. "
        "I can only assist with HR-related queries such as leave, compensation, performance, "
        "WFH policy, benefits, IT security, POSH, or onboarding. "
        "For other matters, please contact the appropriate department."
    )

    def _format_context(docs: list[_Doc]) -> str:
        parts = []
        for i, d in enumerate(docs, 1):
            fname = os.path.basename(d.metadata.get("source", "Unknown"))
            page  = d.metadata.get("page", "?")
            parts.append(f"[Document {i} — {fname}, page {page}]\n{d.page_content}")
        return "\n\n" + "─" * 60 + "\n\n".join(parts)

    def ask(question: str) -> dict:
        # Gate 1 — LLM scope classifier
        verdict = parser.invoke(
            llm.invoke(OOS_PROMPT.invoke({"question": question}))
        ).strip().upper()
        if "OUT_OF_SCOPE" in verdict:
            return {"answer": REFUSAL, "sources": [], "in_scope": False, "score": 0.0}

        # Gate 2 — semantic relevance floor (lower = more lenient = better recall)
        hits = store.search(question, k=6)
        if not hits or hits[0][1] < 0.52:
            return {"answer": REFUSAL, "sources": [], "in_scope": False, "score": 0.0}

        docs   = [d for d, _ in hits]
        top_sc = hits[0][1]
        answer = parser.invoke(
            llm.invoke(RAG_PROMPT.invoke({
                "context":  _format_context(docs),
                "question": question,
            }))
        )
        sources = [
            {"file": os.path.basename(d.metadata.get("source", "")),
             "page": d.metadata.get("page", "?")}
            for d in docs
        ]
        return {"answer": answer, "sources": sources, "in_scope": True, "score": round(top_sc, 3)}

    return ask, len(pdf_files), len(chunks)


# ══════════════════════════════════════════════════════════════════════════════
#  APPLY ENV VARS
# ══════════════════════════════════════════════════════════════════════════════
if groq_key:
    os.environ["GROQ_API_KEY"] = groq_key
if langchain_key:
    os.environ["LANGCHAIN_API_KEY"]    = langchain_key
    os.environ["LANGCHAIN_TRACING_V2"] = "true"
    os.environ["LANGCHAIN_PROJECT"]    = "zyro-rag-challenge"

# ══════════════════════════════════════════════════════════════════════════════
#  API KEY GUARD
# ══════════════════════════════════════════════════════════════════════════════
if not groq_key:
    # Hero still visible but with welcome message
    st.markdown("""
    <div class="hero-wrap">
      <img class="hero-img"
           src="https://img.icons8.com/fluency/200/office-building.png"
           alt="Zyro Dynamics HR">
      <div class="hero-body">
        <div class="hero-eyebrow">Zyro Dynamics &mdash; Internal Platform</div>
        <div class="hero-title">HR Help Desk <em>powered by AI</em></div>
        <div class="hero-sub">
          Intelligent, retrieval-augmented answers from 11 internal HR policy documents —
          leave, compensation, performance, WFH, benefits, POSH, and more.
        </div>
        <div class="hero-pills">
          <span class="pill pill-green"><span class="dot-live"></span>System Ready</span>
          <span class="pill pill-blue">LLaMA 3.3 &middot; 70B</span>
          <span class="pill pill-teal">FAISS Vector Search</span>
          <span class="pill pill-gold">11 Policy Documents</span>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.info(
        "**Enter your Groq API Key** in the sidebar to activate the assistant.  \n"
        "Get a free key at [console.groq.com](https://console.groq.com) — no credit card needed.",
    )
    st.stop()

# ══════════════════════════════════════════════════════════════════════════════
#  BUILD PIPELINE (with progress UX)
# ══════════════════════════════════════════════════════════════════════════════
if "rag_pipeline" not in st.session_state:
    with st.status("Initialising HR knowledge base...", expanded=True) as status:
        st.write("Loading and parsing HR policy PDFs...")
        time.sleep(0.2)
        st.write("Chunking documents into semantic segments...")
        time.sleep(0.1)
        st.write("Generating vector embeddings...")
        result = build_pipeline(groq_key)
        ask_bot, n_docs, n_chunks = result
        st.session_state.rag_pipeline = ask_bot
        st.session_state.n_docs       = n_docs
        st.session_state.n_chunks     = n_chunks
        st.write(f"Indexed {n_chunks} chunks from {n_docs} documents.")
        status.update(label="Knowledge base ready.", state="complete")
else:
    ask_bot  = st.session_state.rag_pipeline
    n_docs   = st.session_state.get("n_docs",   11)
    n_chunks = st.session_state.get("n_chunks", "—")

# session defaults
if "messages"    not in st.session_state: st.session_state.messages    = []
if "query_count" not in st.session_state: st.session_state.query_count = 0

# ══════════════════════════════════════════════════════════════════════════════
#  HERO BANNER  (only shown when ready)
# ══════════════════════════════════════════════════════════════════════════════
st.markdown(f"""
<div class="hero-wrap">
  <img class="hero-img"
       src="https://img.icons8.com/fluency/200/office-building.png"
       alt="Zyro Dynamics HR">
  <div class="hero-body">
    <div class="hero-eyebrow">Zyro Dynamics &mdash; Internal HR Platform</div>
    <div class="hero-title">HR Help Desk <em>powered by AI</em></div>
    <div class="hero-sub">
      Ask any question about company policies — leave entitlements, compensation,
      performance reviews, WFH arrangements, POSH guidelines, and more.
      Answers are grounded in official Zyro Dynamics HR documents.
    </div>
    <div class="hero-pills">
      <span class="pill pill-green"><span class="dot-live"></span>System Online</span>
      <span class="pill pill-blue">LLaMA 3.3 &middot; 70B via Groq</span>
      <span class="pill pill-teal">FAISS Semantic Search</span>
      <span class="pill pill-gold">{n_docs} Policy Documents &middot; {n_chunks} Chunks</span>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
#  STATS ROW
# ══════════════════════════════════════════════════════════════════════════════
st.markdown(f"""
<div class="stats-row">
  <div class="stat-card">
    <span class="stat-num stat-num-accent">{n_docs}</span>
    <span class="stat-label">Policy Documents</span>
  </div>
  <div class="stat-card">
    <span class="stat-num stat-num-teal">{n_chunks}</span>
    <span class="stat-label">Vector Chunks</span>
  </div>
  <div class="stat-card">
    <span class="stat-num stat-num-green">{st.session_state.query_count}</span>
    <span class="stat-label">Queries Answered</span>
  </div>
  <div class="stat-card">
    <span class="stat-num stat-num-gold" style="font-size:1.2rem;padding-top:.3rem;">LLaMA 3.3</span>
    <span class="stat-label">70B &middot; Groq Inference</span>
  </div>
</div>
""", unsafe_allow_html=True)

# ── RAG info bar ──────────────────────────────────────────────────────────────
st.markdown("""
<div class="rag-info-bar">
  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#7b93f9" stroke-width="2">
    <circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>
  </svg>
  <span>
    Retrieval method: <b>FAISS cosine similarity</b> &middot;
    Model: <b>LLaMA-3.3-70B-Versatile</b> &middot;
    Answers are grounded in policy documents only &mdash; hallucinations are actively suppressed.
  </span>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
#  CHAT HISTORY
# ══════════════════════════════════════════════════════════════════════════════
if not st.session_state.messages:
    st.markdown("""
    <div class="empty-state">
      <div class="empty-state-icon">
        <svg width="26" height="26" viewBox="0 0 24 24" fill="none"
             stroke="white" stroke-width="1.8" stroke-linecap="round">
          <path d="M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2z"/>
        </svg>
      </div>
      <h3>How can we help you today?</h3>
      <p>
        Type your HR policy question below or select a topic from the sidebar.
        This assistant searches all 11 Zyro Dynamics policy documents to provide
        accurate, policy-grounded responses.
      </p>
    </div>
    """, unsafe_allow_html=True)

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        if not msg.get("in_scope", True):
            st.markdown(f'<div class="oos-card">{msg["content"]}</div>',
                        unsafe_allow_html=True)
        else:
            st.markdown(msg["content"])

        if msg.get("sources"):
            with st.expander(f"Source citations ({len(msg['sources'])} documents referenced)",
                             expanded=False):
                for s in msg["sources"]:
                    fname = (s["file"]
                             .replace("_", " ")
                             .replace(".pdf", "")
                             .title())
                    st.markdown(
                        f'<span class="cite-pill">'
                        f'<span class="cite-dot"></span>'
                        f'{fname} &nbsp;&middot;&nbsp; page&nbsp;{s["page"]}'
                        f'</span>',
                        unsafe_allow_html=True,
                    )

        if msg.get("score") and msg.get("in_scope"):
            st.caption(f"Relevance score: {msg['score']:.3f}")


# ══════════════════════════════════════════════════════════════════════════════
#  QUESTION HANDLER
# ══════════════════════════════════════════════════════════════════════════════
def handle_question(prompt: str) -> None:
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Searching HR policies..."):
            result = ask_bot(prompt)

        answer   = result["answer"]
        sources  = result.get("sources", [])
        in_scope = result.get("in_scope", True)
        score    = result.get("score", 0.0)

        if not in_scope:
            st.markdown(f'<div class="oos-card">{answer}</div>', unsafe_allow_html=True)
        else:
            st.markdown(answer)

        if sources:
            with st.expander(f"Source citations ({len(sources)} documents referenced)",
                             expanded=True):
                for s in sources:
                    fname = (s["file"]
                             .replace("_", " ")
                             .replace(".pdf", "")
                             .title())
                    st.markdown(
                        f'<span class="cite-pill">'
                        f'<span class="cite-dot"></span>'
                        f'{fname} &nbsp;&middot;&nbsp; page&nbsp;{s["page"]}'
                        f'</span>',
                        unsafe_allow_html=True,
                    )

        if in_scope and score:
            st.caption(f"Relevance score: {score:.3f}")

    st.session_state.messages.append({
        "role":     "assistant",
        "content":  answer,
        "sources":  sources,
        "in_scope": in_scope,
        "score":    score,
    })
    st.session_state.query_count += 1


# ── Sidebar quick-click handler ───────────────────────────────────────────────
if "pending_question" in st.session_state:
    handle_question(st.session_state.pop("pending_question"))
    st.rerun()

# ── Live chat input ───────────────────────────────────────────────────────────
if prompt := st.chat_input("Ask a question about Zyro Dynamics HR policies..."):
    handle_question(prompt)

# ══════════════════════════════════════════════════════════════════════════════
#  FOOTER
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="hr-footer">
  Zyro Dynamics &copy; Confidential &mdash; Internal HR Help Desk &mdash;
  Built with <a href="https://langchain.com" target="_blank">LangChain</a>,
  <a href="https://console.groq.com" target="_blank">Groq</a> &amp;
  <a href="https://streamlit.io" target="_blank">Streamlit</a>
</div>
""", unsafe_allow_html=True)
