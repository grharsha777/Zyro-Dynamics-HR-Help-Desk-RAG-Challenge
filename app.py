"""
Zyro Dynamics — HR Help Desk  (Enterprise RAG Chatbot)
Built for the NIAT × Kaggle RAG Challenge
"""

import streamlit as st
import os
import glob
import time
import numpy as np

# ─── Page config (MUST be first Streamlit call) ───────────────────────────────
st.set_page_config(
    page_title="Zyro Dynamics · HR Help Desk",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ══════════════════════════════════════════════════════════════════════════════
# DESIGN SYSTEM & GLOBAL CSS
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
/* ── Google Fonts ── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=Space+Grotesk:wght@400;500;600;700&display=swap');

/* ── Design Tokens ── */
:root {
  --bg-deep:    #04071a;
  --bg-mid:     #080d22;
  --bg-panel:   #0c1230;
  --glass:      rgba(14, 22, 55, 0.60);
  --glass-hi:   rgba(20, 32, 72, 0.80);
  --border:     rgba(100, 130, 255, 0.15);
  --border-hi:  rgba(120, 170, 255, 0.40);
  --cyan:       #22d3ee;
  --violet:     #818cf8;
  --indigo:     #6366f1;
  --rose:       #f472b6;
  --amber:      #fbbf24;
  --green:      #34d399;
  --red-soft:   #fca5a5;
  --txt-0:      #f0f4ff;
  --txt-1:      #b8c4e8;
  --txt-2:      #6b7aab;
  --radius-sm:  10px;
  --radius-md:  16px;
  --radius-lg:  22px;
  --shadow-lg:  0 20px 60px rgba(0,0,0,0.50);
}

/* ── Base reset ── */
*, *::before, *::after { box-sizing: border-box; }

/* ── App Background ── */
.stApp, .main,
section[data-testid="stAppViewContainer"],
div[data-testid="stAppViewContainer"] {
  background:
    radial-gradient(ellipse 900px 600px at 5% -5%,  rgba(129,140,248,0.20) 0%, transparent 65%),
    radial-gradient(ellipse 800px 500px at 95% 5%,  rgba(34,211,238,0.18)  0%, transparent 60%),
    radial-gradient(ellipse 700px 700px at 50% 110%,rgba(99,102,241,0.15)  0%, transparent 60%),
    linear-gradient(165deg, var(--bg-deep) 0%, var(--bg-mid) 55%, var(--bg-panel) 100%) !important;
  background-attachment: fixed !important;
}

/* ── Fonts everywhere ── */
.stApp, .stApp * {
  font-family: 'Inter', system-ui, sans-serif !important;
  color: var(--txt-0) !important;
}

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 8px; height: 8px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb {
  background: linear-gradient(180deg, var(--violet), var(--cyan));
  border-radius: 8px;
}

/* ─────────────────────────────────────────────
   ANIMATED BACKGROUND PARTICLES (CSS only)
───────────────────────────────────────────── */
.zyro-canvas {
  position: fixed; inset: 0; pointer-events: none; z-index: 0; overflow: hidden;
}
.zyro-orb {
  position: absolute; border-radius: 50%; filter: blur(80px); opacity: 0.28; mix-blend-mode: screen;
}
.orb-1 { width: 600px; height: 600px; top: -150px; left: -100px;
  background: radial-gradient(circle, #818cf8 0%, transparent 70%);
  animation: drift1 22s ease-in-out infinite alternate; }
.orb-2 { width: 500px; height: 500px; top: 10%; right: -120px;
  background: radial-gradient(circle, #22d3ee 0%, transparent 70%);
  animation: drift2 28s ease-in-out infinite alternate; }
.orb-3 { width: 400px; height: 400px; bottom: -100px; left: 30%;
  background: radial-gradient(circle, #6366f1 0%, transparent 70%);
  animation: drift3 18s ease-in-out infinite alternate; }
.orb-4 { width: 300px; height: 300px; top: 40%; left: 10%;
  background: radial-gradient(circle, #f472b6 0%, transparent 70%);
  animation: drift4 24s ease-in-out infinite alternate; opacity: 0.18; }

@keyframes drift1 { from { transform: translate(0,0) scale(1); }     to { transform: translate(60px, 80px) scale(1.1); } }
@keyframes drift2 { from { transform: translate(0,0) scale(1.05); }  to { transform: translate(-70px, 60px) scale(0.95); } }
@keyframes drift3 { from { transform: translate(0,0) scale(0.95); }  to { transform: translate(50px, -60px) scale(1.08); } }
@keyframes drift4 { from { transform: translate(0,0); }              to { transform: translate(40px, -40px); } }

/* ── Floating micro-particles ── */
.particle { position: absolute; border-radius: 50%; opacity: 0; animation: float-particle linear infinite; }
@keyframes float-particle {
  0%   { opacity: 0; transform: translateY(100vh) scale(0); }
  10%  { opacity: 0.6; }
  90%  { opacity: 0.3; }
  100% { opacity: 0; transform: translateY(-20px) scale(1.2); }
}

/* ─────────────────────────────────────────────
   SIDEBAR
───────────────────────────────────────────── */
section[data-testid="stSidebar"] {
  background: linear-gradient(180deg, rgba(8,12,30,0.96) 0%, rgba(4,7,26,0.98) 100%) !important;
  border-right: 1px solid var(--border) !important;
  backdrop-filter: blur(24px) !important;
}
section[data-testid="stSidebar"] .stMarkdown h1,
section[data-testid="stSidebar"] .stMarkdown h2,
section[data-testid="stSidebar"] .stMarkdown h3 { color: var(--txt-0) !important; }
section[data-testid="stSidebar"] hr { border-color: var(--border) !important; margin: 1rem 0 !important; }
section[data-testid="stSidebar"] .stCaption p,
section[data-testid="stSidebar"] .stMarkdown p { color: var(--txt-2) !important; font-size: 0.82rem !important; }

/* ─────────────────────────────────────────────
   HERO HEADER
───────────────────────────────────────────── */
.zyro-hero {
  position: relative; z-index: 2;
  background: linear-gradient(135deg, rgba(14,22,55,0.70) 0%, rgba(20,12,50,0.70) 100%);
  border: 1px solid var(--border-hi);
  border-radius: var(--radius-lg);
  backdrop-filter: blur(30px) saturate(160%);
  padding: 2.4rem 2rem 2rem;
  margin-bottom: 1.4rem;
  overflow: hidden;
  box-shadow: var(--shadow-lg), inset 0 1px 0 rgba(255,255,255,0.06);
  animation: hero-in 0.8s cubic-bezier(0.2,0.8,0.2,1) both;
}
@keyframes hero-in { from { opacity:0; transform:translateY(20px); } to { opacity:1; transform:translateY(0); } }

/* Shimmer sweep */
.zyro-hero::before {
  content: "";
  position: absolute; top: 0; left: -100%; width: 60%; height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255,255,255,0.05), transparent);
  animation: hero-shimmer 6s ease infinite;
}
@keyframes hero-shimmer { 0% { left: -100%; } 100% { left: 200%; } }

/* Top accent bar */
.zyro-hero::after {
  content: "";
  position: absolute; top: 0; left: 0; right: 0; height: 3px;
  background: linear-gradient(90deg, var(--violet), var(--cyan), var(--rose), var(--indigo));
  background-size: 300% 100%;
  animation: bar-flow 5s ease infinite;
}
@keyframes bar-flow { 0%,100% { background-position:0% 0%; } 50% { background-position:100% 0%; } }

.hero-inner { display: flex; align-items: center; gap: 1.6rem; flex-wrap: wrap; }

.hero-logo {
  width: 72px; height: 72px; flex-shrink: 0;
  background: linear-gradient(135deg, var(--indigo), var(--cyan));
  border-radius: 20px;
  display: flex; align-items: center; justify-content: center;
  font-size: 2rem;
  box-shadow: 0 8px 24px rgba(99,102,241,0.45);
  animation: logo-pulse 4s ease-in-out infinite;
  position: relative;
}
@keyframes logo-pulse {
  0%,100% { box-shadow: 0 8px 24px rgba(99,102,241,0.45); }
  50% { box-shadow: 0 8px 36px rgba(34,211,238,0.55); }
}

.hero-text { flex: 1; }
.hero-text h1 {
  margin: 0 0 0.3rem;
  font-family: 'Space Grotesk', sans-serif !important;
  font-size: clamp(1.5rem, 2.8vw, 2.2rem);
  font-weight: 800;
  letter-spacing: -0.03em;
  background: linear-gradient(90deg, var(--txt-0) 0%, var(--cyan) 50%, var(--violet) 100%);
  -webkit-background-clip: text; background-clip: text; color: transparent !important;
  background-size: 200% 100%;
  animation: title-shift 8s ease infinite;
}
@keyframes title-shift { 0%,100%{background-position:0% 0%} 50%{background-position:100% 0%} }

.hero-text p { margin: 0; color: var(--txt-1) !important; font-size: 0.95rem; line-height: 1.55; }

.hero-badges { display: flex; flex-wrap: wrap; gap: 0.5rem; margin-top: 1rem; }
.hero-badge {
  display: inline-flex; align-items: center; gap: 0.3rem;
  padding: 4px 12px; border-radius: 999px; font-size: 0.72rem;
  font-weight: 600; letter-spacing: 0.06em; text-transform: uppercase;
  border: 1px solid; backdrop-filter: blur(8px);
  transition: all 0.25s ease;
}
.badge-cyan   { background: rgba(34,211,238,0.10);  border-color: rgba(34,211,238,0.35);  color: var(--cyan)   !important; }
.badge-violet { background: rgba(129,140,248,0.10); border-color: rgba(129,140,248,0.35); color: var(--violet) !important; }
.badge-rose   { background: rgba(244,114,182,0.10); border-color: rgba(244,114,182,0.35); color: var(--rose)   !important; }
.badge-green  { background: rgba(52,211,153,0.10);  border-color: rgba(52,211,153,0.35);  color: var(--green)  !important; }

/* Status dot */
.status-dot {
  display: inline-block; width: 7px; height: 7px; border-radius: 50%;
  background: var(--green); margin-right: 4px;
  box-shadow: 0 0 6px var(--green);
  animation: pulse-dot 2s ease-in-out infinite;
}
@keyframes pulse-dot { 0%,100%{opacity:1;transform:scale(1)} 50%{opacity:0.6;transform:scale(1.3)} }

/* ─────────────────────────────────────────────
   STATS ROW
───────────────────────────────────────────── */
.stats-row {
  display: flex; gap: 1rem; margin-bottom: 1.4rem; flex-wrap: wrap;
  animation: hero-in 0.8s 0.15s cubic-bezier(0.2,0.8,0.2,1) both;
}
.stat-card {
  flex: 1; min-width: 120px;
  background: var(--glass);
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  padding: 1rem 1.2rem;
  backdrop-filter: blur(18px);
  text-align: center;
  transition: all 0.28s ease;
  position: relative; overflow: hidden;
}
.stat-card::before {
  content: ""; position: absolute; bottom: 0; left: 0; right: 0; height: 2px;
  background: linear-gradient(90deg, transparent, var(--cyan), transparent);
  opacity: 0; transition: opacity 0.3s;
}
.stat-card:hover { border-color: var(--border-hi); transform: translateY(-3px); box-shadow: 0 12px 32px rgba(0,0,0,0.3); }
.stat-card:hover::before { opacity: 1; }
.stat-num { font-size: 1.7rem; font-weight: 800; font-family: 'Space Grotesk', sans-serif !important; }
.stat-label { font-size: 0.72rem; color: var(--txt-2) !important; letter-spacing: 0.06em; text-transform: uppercase; margin-top: 2px; }

/* ─────────────────────────────────────────────
   CHAT MESSAGES
───────────────────────────────────────────── */
.stChatMessage {
  background: var(--glass) !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--radius-md) !important;
  backdrop-filter: blur(18px) !important;
  box-shadow: 0 6px 28px rgba(0,0,0,0.28) !important;
  animation: msg-in 0.45s cubic-bezier(0.2,0.8,0.2,1) both;
  margin-bottom: 0.75rem !important;
}
@keyframes msg-in { from { opacity:0; transform:translateY(12px); } to { opacity:1; transform:translateY(0); } }

[data-testid="stChatMessageAvatarUser"]      { background: linear-gradient(135deg, var(--indigo), var(--cyan)) !important; }
[data-testid="stChatMessageAvatarAssistant"] { background: linear-gradient(135deg, var(--violet), var(--rose)) !important; }

/* ── Chat input ── */
[data-testid="stChatInput"] textarea,
[data-testid="stChatInputTextArea"] {
  background: rgba(8,12,30,0.88) !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--radius-md) !important;
  color: var(--txt-0) !important;
  transition: all 0.25s ease;
}
[data-testid="stChatInput"] textarea:focus {
  border-color: var(--border-hi) !important;
  box-shadow: 0 0 0 3px rgba(99,102,241,0.20) !important;
}

/* ─────────────────────────────────────────────
   SIDEBAR BUTTONS
───────────────────────────────────────────── */
.stButton > button {
  background: linear-gradient(135deg, rgba(99,102,241,0.12), rgba(34,211,238,0.12)) !important;
  color: var(--txt-1) !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--radius-sm) !important;
  font-size: 0.82rem !important;
  font-weight: 500 !important;
  text-align: left !important;
  transition: all 0.25s cubic-bezier(0.2,0.8,0.2,1) !important;
  position: relative; overflow: hidden;
}
.stButton > button:hover {
  background: linear-gradient(135deg, rgba(99,102,241,0.28), rgba(34,211,238,0.20)) !important;
  border-color: var(--border-hi) !important;
  color: var(--txt-0) !important;
  transform: translateX(4px) !important;
  box-shadow: 0 4px 20px rgba(99,102,241,0.25) !important;
}

/* ─────────────────────────────────────────────
   INPUTS
───────────────────────────────────────────── */
.stTextInput > div > div > input,
.stTextArea textarea {
  background: rgba(8,12,30,0.80) !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--radius-sm) !important;
  color: var(--txt-0) !important;
  transition: all 0.25s ease;
}
.stTextInput > div > div > input:focus {
  border-color: var(--border-hi) !important;
  box-shadow: 0 0 0 3px rgba(99,102,241,0.18) !important;
}
.stTextInput label, .stSelectbox label { color: var(--txt-2) !important; font-size: 0.8rem !important; font-weight: 500 !important; letter-spacing: 0.04em; }

/* ─────────────────────────────────────────────
   CARDS & COMPONENTS
───────────────────────────────────────────── */
.zyro-card {
  background: var(--glass);
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  backdrop-filter: blur(20px);
  padding: 1.1rem 1.2rem;
  transition: all 0.28s ease;
  animation: hero-in 0.7s cubic-bezier(0.2,0.8,0.2,1) both;
}
.zyro-card:hover { border-color: var(--border-hi); box-shadow: 0 8px 30px rgba(0,0,0,0.30); }

/* Source citations */
.source-pill {
  display: inline-flex; align-items: center; gap: 0.35rem;
  background: linear-gradient(135deg, rgba(34,211,238,0.10), rgba(99,102,241,0.10));
  border: 1px solid rgba(99,102,241,0.30);
  border-radius: 999px; padding: 4px 12px;
  font-size: 0.76rem; color: var(--txt-1) !important;
  margin: 3px; transition: all 0.2s ease;
  backdrop-filter: blur(6px);
}
.source-pill:hover {
  border-color: var(--cyan); color: #fff !important;
  box-shadow: 0 0 14px rgba(34,211,238,0.35);
  transform: translateY(-1px);
}

/* Out-of-scope box */
.oos-box {
  background: rgba(252,165,165,0.06);
  border: 1px solid rgba(252,165,165,0.30);
  border-left: 4px solid var(--red-soft);
  padding: 0.9rem 1.1rem;
  border-radius: var(--radius-sm);
  color: #fecaca !important;
  font-size: 0.9rem;
  backdrop-filter: blur(8px);
  animation: msg-in 0.4s ease both;
}

/* Expander */
details {
  background: rgba(8,12,30,0.60) !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--radius-sm) !important;
  backdrop-filter: blur(10px);
  transition: all 0.2s;
}
details:hover { border-color: var(--border-hi) !important; }
details summary { color: var(--txt-1) !important; font-weight: 600; font-size: 0.85rem; }

/* Info alerts */
.stAlert {
  background: var(--glass) !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--radius-md) !important;
  backdrop-filter: blur(14px);
  color: var(--txt-1) !important;
}

/* Section dividers */
.section-label {
  font-size: 0.68rem; font-weight: 700; letter-spacing: 0.12em;
  text-transform: uppercase; color: var(--txt-2) !important;
  margin: 0.8rem 0 0.4rem; padding-left: 2px;
}

/* ─────────────────────────────────────────────
   SPINNER
───────────────────────────────────────────── */
.stSpinner > div { border-top-color: var(--cyan) !important; }

/* ─────────────────────────────────────────────
   THINKING ANIMATION
───────────────────────────────────────────── */
.thinking-dots { display: inline-flex; gap: 4px; align-items: center; }
.thinking-dots span {
  display: inline-block; width: 6px; height: 6px; border-radius: 50%;
  background: var(--cyan); animation: dot-bounce 1.2s ease-in-out infinite;
}
.thinking-dots span:nth-child(2) { animation-delay: 0.2s; }
.thinking-dots span:nth-child(3) { animation-delay: 0.4s; }
@keyframes dot-bounce { 0%,80%,100%{transform:scale(0.7);opacity:0.5} 40%{transform:scale(1.2);opacity:1} }

/* ─────────────────────────────────────────────
   FOOTER
───────────────────────────────────────────── */
.zyro-footer {
  text-align: center; padding: 1.5rem 1rem 1rem;
  color: var(--txt-2) !important; font-size: 0.75rem;
  letter-spacing: 0.05em; border-top: 1px solid var(--border);
  margin-top: 2rem;
}
.zyro-footer a { color: var(--cyan) !important; text-decoration: none; }
.zyro-footer a:hover { color: var(--violet) !important; }

/* Sidebar doc list */
.doc-item {
  display: flex; align-items: center; gap: 0.5rem;
  padding: 0.4rem 0.6rem; border-radius: 8px;
  background: rgba(99,102,241,0.06);
  border: 1px solid rgba(99,102,241,0.12);
  margin-bottom: 0.3rem; font-size: 0.78rem;
  color: var(--txt-1) !important;
  transition: all 0.2s;
}
.doc-item:hover { background: rgba(99,102,241,0.12); border-color: var(--border-hi); }

/* Welcome card */
.welcome-card {
  background: linear-gradient(135deg, rgba(99,102,241,0.10) 0%, rgba(34,211,238,0.08) 100%);
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  padding: 1.4rem 1.6rem;
  margin: 1rem 0;
  backdrop-filter: blur(16px);
}
.welcome-card h3 { font-family: 'Space Grotesk', sans-serif !important; margin: 0 0 0.6rem; font-size: 1.05rem; }
.welcome-card p  { color: var(--txt-1) !important; font-size: 0.88rem; line-height: 1.55; margin: 0; }

/* Progress bar for build */
.stProgress > div > div { background: linear-gradient(90deg, var(--indigo), var(--cyan)) !important; border-radius: 4px !important; }
</style>
""", unsafe_allow_html=True)

# ── Animated background orbs + particles ──────────────────────────────────────
st.markdown("""
<div class="zyro-canvas">
  <div class="zyro-orb orb-1"></div>
  <div class="zyro-orb orb-2"></div>
  <div class="zyro-orb orb-3"></div>
  <div class="zyro-orb orb-4"></div>
  <!-- Floating micro-particles -->
  <div class="particle" style="width:3px;height:3px;background:#818cf8;left:15%;animation-duration:18s;animation-delay:0s;"></div>
  <div class="particle" style="width:2px;height:2px;background:#22d3ee;left:35%;animation-duration:22s;animation-delay:4s;"></div>
  <div class="particle" style="width:4px;height:4px;background:#f472b6;left:55%;animation-duration:15s;animation-delay:8s;"></div>
  <div class="particle" style="width:2px;height:2px;background:#6366f1;left:75%;animation-duration:20s;animation-delay:2s;"></div>
  <div class="particle" style="width:3px;height:3px;background:#34d399;left:88%;animation-duration:17s;animation-delay:6s;"></div>
  <div class="particle" style="width:2px;height:2px;background:#818cf8;left:25%;animation-duration:24s;animation-delay:10s;"></div>
  <div class="particle" style="width:3px;height:3px;background:#22d3ee;left:65%;animation-duration:19s;animation-delay:3s;"></div>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    # Logo area
    st.markdown("""
    <div style="text-align:center;padding:1rem 0 0.5rem;">
      <div style="font-size:2.5rem;margin-bottom:0.4rem;filter:drop-shadow(0 0 16px rgba(99,102,241,0.6));">🏢</div>
      <div style="font-family:'Space Grotesk',sans-serif;font-weight:700;font-size:1.05rem;
                  background:linear-gradient(90deg,#818cf8,#22d3ee);
                  -webkit-background-clip:text;background-clip:text;color:transparent;">
        Zyro Dynamics
      </div>
      <div style="font-size:0.7rem;color:#6b7aab;letter-spacing:0.1em;text-transform:uppercase;margin-top:2px;">
        HR Help Desk · AI
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    # API Keys
    st.markdown('<div class="section-label">🔑 API Configuration</div>', unsafe_allow_html=True)
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
        help="For tracing at smith.langchain.com",
    )

    st.divider()

    # Quick questions
    st.markdown('<div class="section-label">💬 Quick Questions</div>', unsafe_allow_html=True)
    sample_qs = [
        "How many earned leave days per year?",
        "When is salary credited each month?",
        "What is the WFH policy for L3 employees?",
        "What health insurance coverage do I get?",
        "What happens with a performance rating of 1?",
        "How long is the PIP duration?",
        "When is the Annual Performance Review?",
        "What is the payroll cut-off date?",
        "What is the maternity leave entitlement?",
        "How do I claim travel reimbursements?",
    ]
    for sq in sample_qs:
        if st.button(f"→ {sq}", use_container_width=True, key=f"sq_{hash(sq)}"):
            st.session_state.pending_question = sq

    st.divider()

    # Document list
    st.markdown('<div class="section-label">📚 Knowledge Base</div>', unsafe_allow_html=True)
    doc_names = [
        ("🏢", "Company Profile"),
        ("📖", "Employee Handbook"),
        ("🌴", "Leave Policy"),
        ("🏠", "Work From Home"),
        ("⚖️", "Code of Conduct"),
        ("📊", "Performance Review"),
        ("💰", "Compensation & Benefits"),
        ("🔒", "IT & Data Security"),
        ("🛡️", "POSH Policy"),
        ("🚪", "Onboarding & Separation"),
        ("✈️", "Travel & Expense"),
    ]
    for icon, name in doc_names:
        st.markdown(f'<div class="doc-item"><span>{icon}</span><span>{name}</span></div>', unsafe_allow_html=True)

    st.divider()

    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("🗑️ Clear", use_container_width=True):
            st.session_state.messages = []
            st.session_state.query_count = 0
            st.rerun()
    with col_b:
        if st.button("↺ Reset", use_container_width=True):
            for k in ["messages", "rag_pipeline", "query_count", "pending_question"]:
                st.session_state.pop(k, None)
            st.rerun()

    st.divider()
    st.markdown("""
    <div style="font-size:0.72rem;color:#6b7aab;line-height:1.7;text-align:center;">
      <strong style="color:#8b9bc7;">Zyro Dynamics HR Help Desk</strong><br>
      Powered by <span style="color:#818cf8;">LangChain</span> ·
      <span style="color:#22d3ee;">FAISS</span> ·
      <span style="color:#f472b6;">Groq</span><br>
      NIAT × Kaggle RAG Challenge
    </div>
    """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# HERO HEADER
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="zyro-hero">
  <div class="hero-inner">
    <div class="hero-logo">🏢</div>
    <div class="hero-text">
      <h1>Zyro Dynamics HR Help Desk</h1>
      <p>Your intelligent, always-available HR assistant — powered by RAG over 11 internal policy documents.</p>
      <div class="hero-badges">
        <span class="hero-badge badge-green"><span class="status-dot"></span>System Online</span>
        <span class="hero-badge badge-cyan">⚡ Groq LLM</span>
        <span class="hero-badge badge-violet">🔍 FAISS Vector Search</span>
        <span class="hero-badge badge-rose">📄 11 Policy Docs</span>
      </div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# DEPENDENCY CHECK
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
    has_pdf = any(__import__(m) or True for m in ["pypdf", "fitz"]
                  if not (lambda m=m: __import__(m))() or True)
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
    st.error(
        f"**Missing packages:** `{' '.join(_MISSING)}`\n\n"
        "Add these to `requirements.txt` and redeploy on Streamlit Cloud."
    )
    st.stop()

# ══════════════════════════════════════════════════════════════════════════════
# PURE-PYTHON DOCUMENT / TEXT SPLITTER
# ══════════════════════════════════════════════════════════════════════════════
class _Doc:
    __slots__ = ("page_content", "metadata")
    def __init__(self, page_content: str, metadata: dict | None = None):
        self.page_content = page_content
        self.metadata = metadata or {}


def _split_text(text: str, chunk_size: int = 800, chunk_overlap: int = 120) -> list[str]:
    separators = ["\n\n", "\n", ". ", " ", ""]

    def _split(txt: str, sep_idx: int) -> list[str]:
        if len(txt) <= chunk_size:
            return [txt] if txt.strip() else []
        sep = separators[min(sep_idx, len(separators) - 1)]
        if sep == "":
            return [txt[i:i+chunk_size] for i in range(0, len(txt), max(1, chunk_size - chunk_overlap))
                    if txt[i:i+chunk_size].strip()]
        parts = txt.split(sep)
        chunks, current = [], ""
        for part in parts:
            candidate = (current + sep + part) if current else part
            if len(candidate) <= chunk_size:
                current = candidate
            else:
                if current: chunks.append(current)
                if len(part) > chunk_size: chunks.extend(_split(part, sep_idx + 1)); current = ""
                else: current = part
        if current.strip(): chunks.append(current)
        return chunks

    raw = _split(text, 0)
    if chunk_overlap <= 0 or len(raw) <= 1:
        return [c for c in raw if c.strip()]
    merged = [raw[0]]
    for chunk in raw[1:]:
        tail = merged[-1][-chunk_overlap:]
        combined = tail + chunk
        if len(combined) <= chunk_size * 1.35: merged[-1] = combined
        else: merged.append(chunk)
    return [c for c in merged if c.strip()]


def _split_docs(docs: list[_Doc], chunk_size=800, chunk_overlap=120) -> list[_Doc]:
    out = []
    for doc in docs:
        for t in _split_text(doc.page_content, chunk_size, chunk_overlap):
            out.append(_Doc(page_content=t, metadata=dict(doc.metadata)))
    return out

# ══════════════════════════════════════════════════════════════════════════════
# PDF LOADER  (pypdf → PyMuPDF fallback)
# ══════════════════════════════════════════════════════════════════════════════
def _load_pdf(path: str) -> list[_Doc]:
    try:
        from pypdf import PdfReader
        reader = PdfReader(path)
        return [_Doc(page_content=p.extract_text() or "", metadata={"source": path, "page": i})
                for i, p in enumerate(reader.pages) if (p.extract_text() or "").strip()]
    except Exception:
        pass
    try:
        import fitz
        doc = fitz.open(path)
        pages = [_Doc(page_content=page.get_text(), metadata={"source": path, "page": i})
                 for i, page in enumerate(doc) if page.get_text().strip()]
        doc.close()
        return pages
    except Exception:
        pass
    raise RuntimeError(f"Cannot read {path}. Install pypdf or PyMuPDF.")

# ══════════════════════════════════════════════════════════════════════════════
# EMBEDDER  (sentence-transformers, no langchain wrapper needed)
# ══════════════════════════════════════════════════════════════════════════════
class _Embedder:
    def __init__(self, model="sentence-transformers/all-MiniLM-L6-v2"):
        from sentence_transformers import SentenceTransformer
        self._m = SentenceTransformer(model)

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return self._m.encode(texts, normalize_embeddings=True, show_progress_bar=False).tolist()

    def embed_query(self, text: str) -> list[float]:
        return self._m.encode([text], normalize_embeddings=True, show_progress_bar=False)[0].tolist()

# ══════════════════════════════════════════════════════════════════════════════
# FAISS VECTOR STORE  (self-contained — no langchain-community)
# ══════════════════════════════════════════════════════════════════════════════
import faiss

class _VectorStore:
    def __init__(self, docs: list[_Doc], embedder: _Embedder):
        # ← FIX: store embedder as instance attribute FIRST
        self._embedder = embedder
        self._docs = docs
        vecs = np.array(embedder.embed_documents([d.page_content for d in docs]), dtype=np.float32)
        self._index = faiss.IndexFlatIP(vecs.shape[1])   # cosine on L2-normalised vecs
        self._index.add(vecs)

    def search(self, query: str, k: int = 5) -> list[tuple[_Doc, float]]:
        q = np.array([self._embedder.embed_query(query)], dtype=np.float32)
        scores, idxs = self._index.search(q, min(k, len(self._docs)))
        results = []
        for s, i in zip(scores[0], idxs[0]):
            if i >= 0:
                results.append((self._docs[i], float((s + 1) / 2)))   # map [-1,1] → [0,1]
        return sorted(results, key=lambda x: x[1], reverse=True)

# ══════════════════════════════════════════════════════════════════════════════
# RAG PIPELINE  (cached — builds once per session)
# ══════════════════════════════════════════════════════════════════════════════
@st.cache_resource(show_spinner=False)
def build_pipeline(_groq_key: str):
    from langchain_groq import ChatGroq
    from langchain_core.prompts import ChatPromptTemplate
    from langchain_core.output_parsers import StrOutputParser

    # ── Locate PDFs ───────────────────────────────────────────────────────────
    base = os.path.dirname(os.path.abspath(__file__))
    candidates = [
        "/kaggle/input/competitions/niat-masterclass-rag-challenge/zyro-dynamics-hr-corpus",
        os.path.join(base, "zyro-dynamics-hr-corpus"),
        base,
    ]
    pdf_files = []
    for c in candidates:
        found = sorted(glob.glob(os.path.join(c, "*.pdf")))
        if found:
            pdf_files = found
            break

    if not pdf_files:
        st.error("❌ No PDF files found. Make sure the `zyro-dynamics-hr-corpus/` folder is in your repo.")
        st.stop()

    # ── Load → chunk ──────────────────────────────────────────────────────────
    all_docs: list[_Doc] = []
    for p in pdf_files:
        try:
            all_docs.extend(_load_pdf(p))
        except Exception as e:
            st.warning(f"Skipped `{os.path.basename(p)}`: {e}")

    if not all_docs:
        st.error("❌ Could not extract text from any PDF.")
        st.stop()

    chunks = _split_docs(all_docs, chunk_size=800, chunk_overlap=120)

    # ── Embed → index ─────────────────────────────────────────────────────────
    embedder = _Embedder()
    store = _VectorStore(chunks, embedder)

    # ── LLM ───────────────────────────────────────────────────────────────────
    llm    = ChatGroq(model="llama-3.3-70b-versatile", temperature=0.1, max_tokens=600, api_key=_groq_key)
    parser = StrOutputParser()

    # ── Prompts ───────────────────────────────────────────────────────────────
    RAG_PROMPT = ChatPromptTemplate.from_template("""
You are an expert HR Help Desk assistant for Zyro Dynamics (also known as Acrux Dynamics).
Answer the employee's question using ONLY the HR policy context provided below.
Be precise: quote exact numbers, percentages, dates, and limits from the context.
Never add information not found in the context.
If the context is insufficient, say exactly:
"I don't have enough information in the HR policy documents to answer this question."

HR Policy Context:
{context}

Employee Question: {question}

Provide a clear, well-structured answer:""")

    OOS_PROMPT = ChatPromptTemplate.from_template("""
You are a strict binary classifier for an HR chatbot.
Decide if the question is answerable from Zyro Dynamics internal HR policy documents.

In-scope topics: leave policies, work from home, code of conduct, performance reviews (APR/PIP),
compensation, salary, payroll, health insurance, IT & data security, POSH, onboarding,
probation, separation, travel & expense reimbursement, company overview & culture, grade structure.

Question: {question}

Reply with EXACTLY one word — either IN_SCOPE or OUT_OF_SCOPE. No other text.""")

    REFUSAL = (
        "I'm sorry — I can only answer HR-related questions based on Zyro Dynamics "
        "internal policy documents. Your question is outside my scope. Please contact "
        "the relevant department or consult an external resource."
    )

    def _ctx(docs: list[_Doc]) -> str:
        parts = []
        for i, d in enumerate(docs, 1):
            src  = os.path.basename(d.metadata.get("source", "Unknown"))
            page = d.metadata.get("page", "?")
            parts.append(f"[Source {i} · {src} · page {page}]\n{d.page_content}")
        return "\n\n---\n\n".join(parts)

    def ask(question: str) -> dict:
        # 1 — LLM scope gate
        verdict = parser.invoke(llm.invoke(OOS_PROMPT.invoke({"question": question}))).strip().upper()
        if "OUT_OF_SCOPE" in verdict:
            return {"answer": REFUSAL, "sources": [], "in_scope": False}

        # 2 — Semantic relevance floor
        hits = store.search(question, k=5)
        if not hits or hits[0][1] < 0.58:
            return {"answer": REFUSAL, "sources": [], "in_scope": False}

        docs    = [d for d, _ in hits]
        answer  = parser.invoke(llm.invoke(RAG_PROMPT.invoke({"context": _ctx(docs), "question": question})))
        sources = [{"file": os.path.basename(d.metadata.get("source", "")),
                    "page": d.metadata.get("page", "?")} for d in docs]
        return {"answer": answer, "sources": sources, "in_scope": True}

    return ask, len(pdf_files), len(chunks)

# ══════════════════════════════════════════════════════════════════════════════
# APPLY ENV VARS FROM SIDEBAR INPUT
# ══════════════════════════════════════════════════════════════════════════════
if groq_key:
    os.environ["GROQ_API_KEY"] = groq_key
if langchain_key:
    os.environ["LANGCHAIN_API_KEY"]    = langchain_key
    os.environ["LANGCHAIN_TRACING_V2"] = "true"
    os.environ["LANGCHAIN_PROJECT"]    = "zyro-rag-challenge"

# ── Guard: need API key ───────────────────────────────────────────────────────
if not groq_key:
    st.markdown("""
    <div class="welcome-card">
      <h3>👋 Welcome to the Zyro Dynamics HR Help Desk</h3>
      <p>To get started, enter your <strong>Groq API Key</strong> in the sidebar on the left.<br>
      Get a free key at <a href="https://console.groq.com" target="_blank" style="color:#22d3ee;">console.groq.com</a> — no credit card required.</p>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# ── Build pipeline with progress UX ──────────────────────────────────────────
if "rag_pipeline" not in st.session_state:
    with st.status("🔧 Building HR knowledge base…", expanded=True) as status:
        st.write("📄 Loading and parsing HR policy PDFs…")
        time.sleep(0.3)
        st.write("✂️  Chunking documents into semantic segments…")
        time.sleep(0.2)
        st.write("🧠 Generating embeddings with all-MiniLM-L6-v2…")
        result = build_pipeline(groq_key)
        ask_bot, n_docs, n_chunks = result
        st.session_state.rag_pipeline = ask_bot
        st.session_state.n_docs   = n_docs
        st.session_state.n_chunks = n_chunks
        st.write(f"✅ Indexed {n_chunks} chunks from {n_docs} documents.")
        status.update(label="✅ Knowledge base ready!", state="complete")
else:
    ask_bot  = st.session_state.rag_pipeline
    n_docs   = st.session_state.get("n_docs", 11)
    n_chunks = st.session_state.get("n_chunks", "—")

# ── Session state ─────────────────────────────────────────────────────────────
if "messages"    not in st.session_state: st.session_state.messages    = []
if "query_count" not in st.session_state: st.session_state.query_count = 0

# ══════════════════════════════════════════════════════════════════════════════
# STATS ROW
# ══════════════════════════════════════════════════════════════════════════════
st.markdown(f"""
<div class="stats-row">
  <div class="stat-card">
    <div class="stat-num" style="background:linear-gradient(90deg,#818cf8,#22d3ee);
         -webkit-background-clip:text;background-clip:text;color:transparent;">{n_docs}</div>
    <div class="stat-label">Policy Docs</div>
  </div>
  <div class="stat-card">
    <div class="stat-num" style="background:linear-gradient(90deg,#22d3ee,#34d399);
         -webkit-background-clip:text;background-clip:text;color:transparent;">{n_chunks}</div>
    <div class="stat-label">Vector Chunks</div>
  </div>
  <div class="stat-card">
    <div class="stat-num" style="background:linear-gradient(90deg,#f472b6,#818cf8);
         -webkit-background-clip:text;background-clip:text;color:transparent;">{st.session_state.query_count}</div>
    <div class="stat-label">Queries Answered</div>
  </div>
  <div class="stat-card">
    <div class="stat-num" style="background:linear-gradient(90deg,#fbbf24,#f472b6);
         -webkit-background-clip:text;background-clip:text;color:transparent;">LLaMA</div>
    <div class="stat-label">3.3 · 70B</div>
  </div>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# RENDER CHAT HISTORY
# ══════════════════════════════════════════════════════════════════════════════
# Empty state
if not st.session_state.messages:
    st.markdown("""
    <div class="zyro-card" style="text-align:center;padding:2rem;">
      <div style="font-size:2.5rem;margin-bottom:0.6rem;">💬</div>
      <div style="font-family:'Space Grotesk',sans-serif;font-weight:700;font-size:1.1rem;margin-bottom:0.4rem;">
        Ask your HR question
      </div>
      <div style="color:#8b9bc7;font-size:0.88rem;max-width:420px;margin:0 auto;line-height:1.6;">
        Type any HR policy question below, or click a quick question in the sidebar.
        I'll search through all 11 Zyro Dynamics policy documents to find your answer.
      </div>
    </div>
    """, unsafe_allow_html=True)

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        if not msg.get("in_scope", True):
            st.markdown(f'<div class="oos-box">⚠️ {msg["content"]}</div>', unsafe_allow_html=True)
        else:
            st.write(msg["content"])
        if msg.get("sources"):
            with st.expander("📄 Source citations", expanded=False):
                for s in msg["sources"]:
                    # Clean up filename for display
                    fname = s["file"].replace("_", " ").replace(".pdf", "")
                    st.markdown(
                        f'<span class="source-pill">📑 {fname} · p.{s["page"]}</span>',
                        unsafe_allow_html=True,
                    )

# ══════════════════════════════════════════════════════════════════════════════
# QUESTION HANDLER
# ══════════════════════════════════════════════════════════════════════════════
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
            st.markdown(f'<div class="oos-box">⚠️ {answer}</div>', unsafe_allow_html=True)
        else:
            st.write(answer)

        if sources:
            with st.expander("📄 Source citations", expanded=True):
                for s in sources:
                    fname = s["file"].replace("_", " ").replace(".pdf", "")
                    st.markdown(
                        f'<span class="source-pill">📑 {fname} · p.{s["page"]}</span>',
                        unsafe_allow_html=True,
                    )

    st.session_state.messages.append({
        "role":     "assistant",
        "content":  answer,
        "sources":  sources,
        "in_scope": in_scope,
    })
    st.session_state.query_count += 1

# ── Handle sidebar quick-click ────────────────────────────────────────────────
if "pending_question" in st.session_state:
    handle_question(st.session_state.pop("pending_question"))
    st.rerun()

# ── Live chat input ───────────────────────────────────────────────────────────
if prompt := st.chat_input("Ask an HR question — leave, salary, WFH, performance, benefits…"):
    handle_question(prompt)

# ══════════════════════════════════════════════════════════════════════════════
# FOOTER
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="zyro-footer">
  <strong>Zyro Dynamics</strong> © Confidential · Internal HR Help Desk ·
  Built with <a href="https://langchain.com" target="_blank">LangChain</a> ·
  <a href="https://console.groq.com" target="_blank">Groq</a> ·
  <a href="https://streamlit.io" target="_blank">Streamlit</a>
</div>
""", unsafe_allow_html=True)
