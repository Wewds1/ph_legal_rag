import streamlit as st
import requests

st.set_page_config(
    page_title="LexPH — Philippine Jurisprudence Search",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;600;700&family=DM+Sans:wght@300;400;500;600&display=swap');

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

:root {
    --ink:        #0f0f0f;
    --ink-muted:  #5a5a5a;
    --ink-faint:  #9a9a9a;
    --surface:    #fafaf8;
    --panel:      #f3f2ef;
    --border:     #e2e0da;
    --accent:     #b5292a;
    --accent-dim: #f5e6e6;
    --accent-mid: #d94545;
    --white:      #ffffff;
    --radius-sm:  6px;
    --radius-md:  12px;
    --radius-lg:  20px;
    --shadow-sm:  0 1px 4px rgba(0,0,0,.06);
    --shadow-md:  0 4px 20px rgba(0,0,0,.08);
    --shadow-lg:  0 12px 48px rgba(0,0,0,.12);
    --serif:      'Playfair Display', Georgia, serif;
    --sans:       'DM Sans', system-ui, sans-serif;
}

html, body,
[data-testid="stAppViewContainer"],
[data-testid="stMain"],
[data-testid="stMainBlockContainer"],
section[data-testid="stMain"] > div { 
    background-color: var(--surface) !important;
    font-family: var(--sans) !important;
    color: var(--ink) !important;
}

/* ── Hide Streamlit chrome ── */
#MainMenu, footer, header,
[data-testid="stToolbar"],
[data-testid="stDecoration"] { display: none !important; }

/* ── Global block wrapper ── */
[data-testid="stMainBlockContainer"] {
    max-width: 1100px !important;
    padding: 0 32px 80px !important;
    margin: 0 auto !important;
}

/* ────────────────────────────
   HERO
──────────────────────────── */
.lex-hero {
    padding: 80px 0 56px;
    border-bottom: 1px solid var(--border);
    margin-bottom: 48px;
}
.lex-eyebrow {
    font-family: var(--sans);
    font-size: 11px;
    font-weight: 600;
    letter-spacing: .18em;
    text-transform: uppercase;
    color: var(--accent);
    margin-bottom: 20px;
}
.lex-title {
    font-family: var(--serif);
    font-size: clamp(2.4rem, 5vw, 4rem);
    font-weight: 700;
    line-height: 1.12;
    color: var(--ink);
    margin-bottom: 18px;
}
.lex-title span { color: var(--accent); }
.lex-sub {
    font-size: 1.05rem;
    color: var(--ink-muted);
    line-height: 1.65;
    max-width: 520px;
    font-weight: 300;
}
.lex-rule {
    width: 48px;
    height: 3px;
    background: var(--accent);
    margin: 28px 0;
    border-radius: 2px;
}

/* ────────────────────────────
   SEARCH AREA
──────────────────────────── */
.search-label {
    font-size: 0.78rem;
    font-weight: 600;
    letter-spacing: .08em;
    text-transform: uppercase;
    color: var(--ink-muted);
    margin-bottom: 10px;
    display: block;
}

/* Input override */
.stTextInput > label { display: none !important; }
.stTextInput > div > div > input {
    background-color: var(--white) !important;
    color: var(--ink) !important;
    border: 1.5px solid var(--border) !important;
    border-radius: var(--radius-sm) !important;
    font-family: var(--sans) !important;
    font-size: 1rem !important;
    font-weight: 400 !important;
    padding: 14px 18px !important;
    box-shadow: var(--shadow-sm) !important;
    transition: border-color .2s, box-shadow .2s !important;
    height: auto !important;
}
.stTextInput > div > div > input:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 3px rgba(181,41,42,.1) !important;
    outline: none !important;
}
.stTextInput > div > div > input::placeholder { color: var(--ink-faint) !important; }

/* Primary button */
.stButton > button {
    background-color: var(--accent) !important;
    color: var(--white) !important;
    border: none !important;
    border-radius: var(--radius-sm) !important;
    font-family: var(--sans) !important;
    font-size: 0.9rem !important;
    font-weight: 600 !important;
    letter-spacing: .04em !important;
    padding: 14px 28px !important;
    height: 52px !important;
    cursor: pointer !important;
    transition: background-color .18s, transform .12s, box-shadow .18s !important;
    box-shadow: 0 2px 8px rgba(181,41,42,.25) !important;
    white-space: nowrap !important;
    width: 100% !important;
}
.stButton > button:hover {
    background-color: var(--accent-mid) !important;
    box-shadow: 0 4px 16px rgba(181,41,42,.35) !important;
    transform: translateY(-1px) !important;
}
.stButton > button:active {
    transform: translateY(0) !important;
}

/* Secondary / ghost button for Close */
button[kind="secondary"],
.btn-ghost > button {
    background-color: transparent !important;
    color: var(--ink-muted) !important;
    border: 1.5px solid var(--border) !important;
    box-shadow: none !important;
}
.btn-ghost > button:hover {
    background-color: var(--panel) !important;
    box-shadow: none !important;
    transform: none !important;
}

/* ────────────────────────────
   RESULT SECTION HEADER
──────────────────────────── */
.result-header {
    display: flex;
    align-items: baseline;
    gap: 12px;
    margin-bottom: 24px;
    padding-bottom: 16px;
    border-bottom: 1px solid var(--border);
}
.result-heading {
    font-family: var(--serif);
    font-size: 1.4rem;
    font-weight: 600;
    color: var(--ink);
}
.result-count {
    font-size: 0.8rem;
    color: var(--ink-faint);
    font-weight: 500;
    background: var(--panel);
    padding: 3px 10px;
    border-radius: 20px;
}

/* ────────────────────────────
   CASE CARD
──────────────────────────── */
.case-card {
    background: var(--white);
    border: 1px solid var(--border);
    border-radius: var(--radius-md);
    padding: 28px 32px;
    margin-bottom: 16px;
    position: relative;
    box-shadow: var(--shadow-sm);
    transition: box-shadow .2s, transform .2s;
}
.case-card:hover {
    box-shadow: var(--shadow-md);
    transform: translateY(-2px);
}
.case-card::before {
    content: '';
    position: absolute;
    left: 0; top: 20%; bottom: 20%;
    width: 3px;
    background: var(--accent);
    border-radius: 0 2px 2px 0;
}
.case-meta {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 10px;
}
.case-gr {
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: .1em;
    text-transform: uppercase;
    color: var(--accent);
    background: var(--accent-dim);
    padding: 3px 10px;
    border-radius: 4px;
}
.case-title-text {
    font-family: var(--serif);
    font-size: 1.1rem;
    font-weight: 600;
    color: var(--ink);
    margin-bottom: 10px;
    line-height: 1.4;
}
.case-snippet {
    font-size: 0.9rem;
    color: var(--ink-muted);
    line-height: 1.7;
    margin-bottom: 18px;
}
.case-link {
    font-size: 0.82rem;
    font-weight: 600;
    color: var(--accent);
    text-decoration: none;
    letter-spacing: .03em;
    border-bottom: 1px solid transparent;
    transition: border-color .15s;
}
.case-link:hover { border-bottom-color: var(--accent); }

/* ────────────────────────────
   ANSWER BOX
──────────────────────────── */
.answer-box {
    background: var(--white);
    border: 1px solid var(--border);
    border-radius: var(--radius-md);
    padding: 28px 32px;
    margin: 20px 0;
    line-height: 1.8;
    color: var(--ink);
    font-size: 0.97rem;
    box-shadow: var(--shadow-sm);
}
.disclaimer-box {
    background: var(--accent-dim);
    border: 1px solid #e8c5c5;
    border-radius: var(--radius-sm);
    padding: 14px 18px;
    color: #7a1a1a;
    font-size: 0.82rem;
    line-height: 1.6;
    margin-top: 20px;
}

/* ────────────────────────────
   EMPTY STATE
──────────────────────────── */
.empty-state {
    text-align: center;
    padding: 64px 24px;
    color: var(--ink-faint);
}
.empty-icon {
    font-size: 2.5rem;
    margin-bottom: 16px;
    opacity: .4;
}
.empty-title {
    font-family: var(--serif);
    font-size: 1.2rem;
    color: var(--ink-muted);
    margin-bottom: 8px;
}
.empty-sub { font-size: 0.88rem; }

/* ────────────────────────────
   CHAT PANEL
──────────────────────────── */
.chat-divider {
    border: none;
    border-top: 1px solid var(--border);
    margin: 40px 0 32px;
}
.chat-section-label {
    font-family: var(--serif);
    font-size: 1.4rem;
    font-weight: 600;
    color: var(--ink);
    margin-bottom: 6px;
}
.chat-section-sub {
    font-size: 0.88rem;
    color: var(--ink-muted);
    margin-bottom: 24px;
}

/* Textarea */
.stTextArea > label { display: none !important; }
.stTextArea > div > div > textarea {
    background-color: var(--white) !important;
    color: var(--ink) !important;
    border: 1.5px solid var(--border) !important;
    border-radius: var(--radius-sm) !important;
    font-family: var(--sans) !important;
    font-size: 0.95rem !important;
    padding: 14px 18px !important;
    resize: none !important;
    box-shadow: var(--shadow-sm) !important;
    transition: border-color .2s !important;
}
.stTextArea > div > div > textarea:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 3px rgba(181,41,42,.1) !important;
    outline: none !important;
}

/* ────────────────────────────
   SPINNER OVERRIDE
──────────────────────────── */
[data-testid="stSpinner"] > div {
    border-top-color: var(--accent) !important;
}

/* ────────────────────────────
   STAT STRIP
──────────────────────────── */
.stat-strip {
    display: flex;
    gap: 40px;
    padding: 20px 0;
    border-top: 1px solid var(--border);
    border-bottom: 1px solid var(--border);
    margin: 32px 0 48px;
}
.stat-item { text-align: left; }
.stat-num {
    font-family: var(--serif);
    font-size: 1.6rem;
    font-weight: 700;
    color: var(--ink);
    line-height: 1;
}
.stat-label {
    font-size: 0.75rem;
    color: var(--ink-faint);
    margin-top: 4px;
    font-weight: 500;
    letter-spacing: .04em;
    text-transform: uppercase;
}

/* Streamlit column gap fix */
[data-testid="column"] { gap: 0 !important; }

/* Error / info overrides */
[data-testid="stAlert"] {
    border-radius: var(--radius-sm) !important;
    font-family: var(--sans) !important;
}
</style>
""", unsafe_allow_html=True)

API_URL = "http://localhost:8000"

# ── Session state ──────────────────────────────────────────────────────────────
if "show_chat" not in st.session_state:
    st.session_state.show_chat = False
if "chat_response" not in st.session_state:
    st.session_state.chat_response = None
if "search_results" not in st.session_state:
    st.session_state.search_results = None
if "last_query" not in st.session_state:
    st.session_state.last_query = ""

# ── Hero ───────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="lex-hero">
    <div class="lex-eyebrow">Philippine Jurisprudence Database</div>
    <h1 class="lex-title">⚖️ Lex<span>PH</span></h1>
    <div class="lex-rule"></div>
    <p class="lex-sub">
        Search Supreme Court decisions, G.R. numbers, and legal precedents
        from the Philippine jurisprudence corpus — instantly.
    </p>
</div>
""", unsafe_allow_html=True)

# ── Stat strip ────────────────────────────────────────────────────────────────
st.markdown("""
<div class="stat-strip">
    <div class="stat-item">
        <div class="stat-num">80K+</div>
        <div class="stat-label">Decisions indexed</div>
    </div>
    <div class="stat-item">
        <div class="stat-num">1901</div>
        <div class="stat-label">Coverage from</div>
    </div>
    <div class="stat-item">
        <div class="stat-num">RAG</div>
        <div class="stat-label">AI-assisted answers</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Search bar ────────────────────────────────────────────────────────────────
st.markdown('<span class="search-label">Search jurisprudence</span>', unsafe_allow_html=True)

col_input, col_btn = st.columns([5, 1])
with col_input:
    query = st.text_input(
        "query",
        placeholder="G.R. No. 242353  ·  defamation  ·  estafa  ·  labor rights",
        label_visibility="collapsed"
    )
with col_btn:
    st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
    search_clicked = st.button("Search", use_container_width=True)

# ── Search logic ──────────────────────────────────────────────────────────────
if search_clicked and query.strip():
    st.session_state.last_query = query.strip()
    try:
        with st.spinner("Searching..."):
            r = requests.post(f"{API_URL}/search", json={"query": query.strip()}, timeout=30)
        if r.status_code == 200:
            st.session_state.search_results = r.json()
        else:
            st.error(f"Server returned {r.status_code}. Please try again.")
            st.session_state.search_results = None
    except requests.exceptions.ConnectionError:
        st.error("Could not reach the backend. Make sure the API is running on port 8000.")
        st.session_state.search_results = None
    except Exception as e:
        st.error(f"Unexpected error: {e}")
        st.session_state.search_results = None

# ── Results ───────────────────────────────────────────────────────────────────
if st.session_state.search_results is not None:
    data = st.session_state.search_results
    results = data.get("results", [])

    if results:
        st.markdown(f"""
        <div class="result-header">
            <span class="result-heading">Results</span>
            <span class="result-count">{len(results)} case{'s' if len(results) != 1 else ''} found</span>
        </div>
        """, unsafe_allow_html=True)

        for case in results:
            st.markdown(f"""
            <div class="case-card">
                <div class="case-meta">
                    <span class="case-gr">G.R. No. {case['gr_no']}</span>
                </div>
                <div class="case-title-text">{case['case_title']}</div>
                <div class="case-snippet">{case['snippet']}</div>
                <a href="{case['source_url']}" target="_blank" class="case-link">Read full decision &rarr;</a>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="empty-state">
            <div class="empty-icon">⚖</div>
            <div class="empty-title">No cases found</div>
            <div class="empty-sub">Try a different keyword, G.R. number, or legal concept.</div>
        </div>
        """, unsafe_allow_html=True)

# ── AI Chat section ────────────────────────────────────────────────────────────
st.markdown('<hr class="chat-divider">', unsafe_allow_html=True)

col_chat_hdr, col_chat_toggle = st.columns([4, 1])
with col_chat_hdr:
    st.markdown("""
    <div class="chat-section-label">Ask a legal question</div>
    <div class="chat-section-sub">Get an AI-assisted answer grounded in Philippine jurisprudence.</div>
    """, unsafe_allow_html=True)
with col_chat_toggle:
    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
    toggle_label = "Hide" if st.session_state.show_chat else "Open"
    if st.button(toggle_label, key="toggle_chat"):
        st.session_state.show_chat = not st.session_state.show_chat
        if not st.session_state.show_chat:
            st.session_state.chat_response = None
        st.rerun()

if st.session_state.show_chat:
    chat_query = st.text_area(
        "chat_input",
        placeholder="e.g., What constitutes grave abuse of discretion under Philippine law?",
        height=110,
        label_visibility="collapsed"
    )

    col_send, col_clear, _ = st.columns([1, 1, 3])
    with col_send:
        send_clicked = st.button("Get answer", key="send_chat", use_container_width=True)
    with col_clear:
        if st.button("Clear", key="clear_chat", use_container_width=True):
            st.session_state.chat_response = None
            st.rerun()

    if send_clicked and chat_query.strip():
        try:
            with st.spinner("Analyzing jurisprudence..."):
                r = requests.post(f"{API_URL}/chat", json={"query": chat_query.strip()}, timeout=30)
            if r.status_code == 200:
                st.session_state.chat_response = r.json()
            else:
                st.error(f"Server returned {r.status_code}.")
        except Exception as e:
            st.error(f"Error: {e}")

    if st.session_state.chat_response:
        resp = st.session_state.chat_response

        st.markdown(f'<div class="answer-box">{resp["answer"]}</div>', unsafe_allow_html=True)

        if resp.get("precedents"):
            st.markdown("""
            <div style="font-size:.78rem;font-weight:700;letter-spacing:.1em;
                        text-transform:uppercase;color:var(--ink-faint);
                        margin:28px 0 14px;">
                Cases cited
            </div>
            """, unsafe_allow_html=True)

            for case in resp["precedents"]:
                st.markdown(f"""
                <div class="case-card">
                    <div class="case-meta">
                        <span class="case-gr">G.R. No. {case['gr_no']}</span>
                    </div>
                    <div class="case-title-text">{case['title']}</div>
                    <div class="case-snippet">{case['snippet']}</div>
                    <a href="{case['source_url']}" target="_blank" class="case-link">Read full decision &rarr;</a>
                </div>
                """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="disclaimer-box">
            <strong>Legal disclaimer:</strong> {resp["disclaimer"]}
        </div>
        """, unsafe_allow_html=True)

# ── Footer ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="margin-top:64px;padding-top:24px;border-top:1px solid var(--border);
            display:flex;justify-content:space-between;align-items:center;
            font-size:0.78rem;color:var(--ink-faint);">
    <span>LexPH &mdash; Philippine Jurisprudence Search</span>
    <span>For research purposes only. Not a substitute for legal counsel.</span>
</div>
""", unsafe_allow_html=True)