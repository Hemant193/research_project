import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import streamlit as st

st.set_page_config(
    page_title="TUHH Course Advisor",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────
st.markdown("""
<style>
/* ── Font & base ─────────────────────────────────────────── */
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&family=DM+Mono:wght@400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

/* ── Header strip ────────────────────────────────────────── */
.hero {
    background: linear-gradient(135deg, #0f2942 0%, #1a4a7a 60%, #0d6efd 100%);
    border-radius: 12px;
    padding: 28px 36px;
    margin-bottom: 24px;
    color: white;
}
.hero h1 {
    font-size: 2rem;
    font-weight: 600;
    margin: 0 0 6px 0;
    letter-spacing: -0.5px;
}
.hero p {
    font-size: 0.95rem;
    opacity: 0.82;
    margin: 0;
}

/* ── Answer card ─────────────────────────────────────────── */
.answer-card {
    background: #f0f7ff;
    border-left: 4px solid #0d6efd;
    border-radius: 8px;
    padding: 18px 22px;
    margin: 16px 0;
    line-height: 1.7;
}

/* ── Chunk card ──────────────────────────────────────────── */
.chunk-card {
    background: #fafafa;
    border: 1px solid #e5e7eb;
    border-radius: 8px;
    padding: 14px 18px;
    margin-bottom: 12px;
    font-family: 'DM Mono', monospace;
    font-size: 0.82rem;
    line-height: 1.6;
    color: #374151;
    white-space: pre-wrap;
}

/* ── Strategy badge ──────────────────────────────────────── */
.badge {
    display: inline-block;
    padding: 3px 12px;
    border-radius: 20px;
    font-size: 0.78rem;
    font-weight: 600;
    margin-right: 8px;
}
.badge-bm25   { background: #dbeafe; color: #1d4ed8; }
.badge-dense  { background: #dcfce7; color: #166534; }
.badge-rerank { background: #fef3c7; color: #92400e; }
.badge-hyde   { background: #fce7f3; color: #9d174d; }

/* ── Metric pill ─────────────────────────────────────────── */
.metric-row {
    display: flex;
    gap: 16px;
    margin: 10px 0 4px 0;
    flex-wrap: wrap;
}
.metric-pill {
    background: white;
    border: 1px solid #e5e7eb;
    border-radius: 8px;
    padding: 6px 14px;
    font-size: 0.82rem;
    color: #374151;
}
.metric-pill b { color: #0d6efd; }

/* ── Example button row ──────────────────────────────────── */
div[data-testid="column"] button {
    border-radius: 8px !important;
    font-size: 0.82rem !important;
    background: #f8fafc !important;
    border: 1px solid #e2e8f0 !important;
    color: #334155 !important;
    text-align: left !important;
    padding: 8px 12px !important;
    width: 100% !important;
    white-space: normal !important;
    height: auto !important;
    min-height: 52px !important;
}
div[data-testid="column"] button:hover {
    background: #eff6ff !important;
    border-color: #0d6efd !important;
}

/* ── Sidebar ─────────────────────────────────────────────── */
section[data-testid="stSidebar"] {
    background: #0f2942;
}
section[data-testid="stSidebar"] * {
    color: #e2e8f0 !important;
}
section[data-testid="stSidebar"] .stSelectbox label,
section[data-testid="stSidebar"] .stSlider label {
    color: #94a3b8 !important;
    font-size: 0.82rem !important;
    text-transform: uppercase;
    letter-spacing: 0.8px;
}
</style>
""", unsafe_allow_html=True)

from src.database     import get_vector_store
from src.retrievers import get_retriever
from src.rag_chain  import get_qa_chain

# ── Constants ─────────────────────────────────────────────────
STRATEGY_META = {
    "Sparse (BM25)": {
        "badge": "badge-bm25",
        "emoji": "🔤",
        "desc":  "Keyword frequency matching. Fast, no embeddings needed. Best for exact term lookups.",
        "speed": "⚡ Very fast",
    },
    "Dense (Vector)": {
        "badge": "badge-dense",
        "emoji": "🧠",
        "desc":  "Semantic cosine similarity over embeddings. Understands meaning, not just keywords.",
        "speed": "🔵 Medium",
    },
    "Hybrid + Rerank": {
        "badge": "badge-rerank",
        "emoji": "🎯",
        "desc":  "Dense top-20 → CrossEncoder reranks → top-5. Highest accuracy, slower.",
        "speed": "🔴 Slower",
    },
    "HyDE": {
        "badge": "badge-hyde",
        "emoji": "💡",
        "desc":  "Generates a hypothetical answer, embeds it, then retrieves. Best for open questions.",
        "speed": "🔴 Slower",
    },
}

EXAMPLES = [
    "I love mathematics and programming. What should I study at TUHH?",
    "What is the Advanced Machine Learning module about?",
    "Which programs are taught in English?",
    "I want to work in AI research — what do you recommend?",
    "How many credit points is Advanced Machine Learning worth?",
    "What topics are covered in the AML lecture?",
]

# ── Load vector store (cached across reruns) ──────────────────
@st.cache_resource(show_spinner="Loading ChromaDB vector store…")
def _load_vs():
    return get_vector_store()


# ── Helper: run one query ─────────────────────────────────────
def run_query(query: str, strategy: str, top_k: int):
    vs        = _load_vs()
    retriever = get_retriever(strategy, vs, top_k=top_k)
    chain     = get_qa_chain(retriever)
    t0        = time.time()
    resp      = chain.invoke({"input": query})
    elapsed   = round(time.time() - t0, 2)
    return resp["answer"], resp["context"], elapsed


# ─────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🎓 TUHH Course Advisor")
    st.markdown("---")

    app_mode = st.radio(
        "MODE",
        ["💬 Ask a Question", "⚔️ Compare Strategies", "📊 Results Dashboard"],
        label_visibility="collapsed",
    )

    st.markdown("---")
    st.markdown("**⚙️ RETRIEVAL SETTINGS**")

    strategy = st.selectbox(
        "STRATEGY",
        list(STRATEGY_META.keys()),
        help="Select the retrieval strategy to use.",
    )
    top_k = st.slider("TOP-K CHUNKS", 2, 10, 5)

    meta = STRATEGY_META[strategy]
    st.markdown(f"""
    <div style='background:#1a3a5c;border-radius:8px;padding:12px;margin-top:8px;'>
        <div style='font-size:1.1rem;margin-bottom:4px;'>{meta['emoji']} {strategy}</div>
        <div style='font-size:0.78rem;opacity:0.8;'>{meta['desc']}</div>
        <div style='font-size:0.75rem;margin-top:6px;opacity:0.65;'>{meta['speed']}</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("""
    <div style='font-size:0.75rem;opacity:0.5;'>
    Make sure <code>ollama serve</code> is running.<br><br>
    M.Sc. Data Science Project · TUHH
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────
# HERO HEADER
# ─────────────────────────────────────────────────────────────
st.markdown("""
<div class='hero'>
    <h1>🎓 TUHH Course Advisor</h1>
    <p>Ask anything about TUHH master programs and modules — powered by your local Ollama LLM + ChromaDB.</p>
</div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────
# MODE 1: ASK A QUESTION
# ─────────────────────────────────────────────────────────────
if app_mode == "💬 Ask a Question":

    # Example buttons
    st.markdown("##### 💡 Try an example")
    cols = st.columns(3)
    chosen = None
    for i, ex in enumerate(EXAMPLES):
        if cols[i % 3].button(ex, key=f"ex_{i}"):
            chosen = ex

    st.markdown("")

    # Query input
    query = st.text_input(
        "Your question:",
        value=chosen or "",
        placeholder="e.g. What should I study if I love machine learning?",
    )

    if st.button("🔍  Search", type="primary", disabled=not query.strip()):
        with st.spinner(f"Running **{strategy}** retrieval…"):
            answer, docs, elapsed = run_query(query, strategy, top_k)

        # ── Answer ────────────────────────────────────────────
        badge_cls = STRATEGY_META[strategy]["badge"]
        st.markdown(f"""
        <div class='metric-row'>
            <div class='metric-pill'>
                <span class='badge {badge_cls}'>{strategy}</span>
            </div>
            <div class='metric-pill'>⏱ <b>{elapsed}s</b></div>
            <div class='metric-pill'>📄 <b>{len(docs)}</b> chunks retrieved</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"<div class='answer-card'>{answer}</div>", unsafe_allow_html=True)

        # ── Source chunks ──────────────────────────────────────
        with st.expander(f"📂  View {len(docs)} retrieved source chunks", expanded=False):
            for i, doc in enumerate(docs):
                m = doc.metadata
                prog  = m.get("program_name", "unknown")
                src   = m.get("source_file", "unknown")
                cidx  = m.get("chunk_index", "?")
                total = m.get("total_chunks", "?")
                lang  = m.get("language", "")
                deg   = m.get("degree", "")

                st.markdown(f"""
                **Chunk {i+1}** — `{src}`
                | Program: *{prog}* {f'({deg})' if deg else ''} {f'· {lang}' if lang else ''}
                | Chunk #{cidx}/{total}
                """)
                st.markdown(
                    f"<div class='chunk-card'>{doc.page_content[:600]}</div>",
                    unsafe_allow_html=True,
                )



elif app_mode == "⚔️ Compare Strategies":

    st.markdown("### ⚔️ Compare All 4 Strategies Side-by-Side")
    st.caption("Enter a query and see how each strategy responds simultaneously.")

    compare_strategies = st.multiselect(
        "Strategies to compare:",
        list(STRATEGY_META.keys()),
        default=["Sparse (BM25)", "Dense (Vector)"],
    )
    compare_k = st.slider("Top-K", 2, 8, 5, key="compare_k")

    query_c = st.text_area(
        "Your question:",
        placeholder="e.g. I love maths and programming — what should I study?",
        height=80,
    )

    if st.button("⚔️  Compare", type="primary",
                 disabled=not query_c.strip() or not compare_strategies):

        cols = st.columns(len(compare_strategies))

        for col, strat in zip(cols, compare_strategies):
            with col:
                meta = STRATEGY_META[strat]
                st.markdown(f"#### {meta['emoji']} {strat}")
                with st.spinner("Running…"):
                    try:
                        ans, docs, lat = run_query(query_c, strat, compare_k)
                        st.markdown(
                            f"<div class='answer-card' style='font-size:0.9rem;'>{ans}</div>",
                            unsafe_allow_html=True,
                        )
                        st.caption(f"⏱ {lat}s · {len(docs)} chunks")
                    except Exception as e:
                        st.error(f"Error: {e}")


elif app_mode == "📊 Results Dashboard":

    st.markdown("### 📊 Evaluation Results Dashboard")
    st.caption("Run the evaluation notebook first to populate these results.")

    results_dir = Path(__file__).parent / "results"
    summary_csv = results_dir / "summary.csv"
    full_csv    = results_dir / "full_results.csv"

    if not summary_csv.exists():
        st.warning(
            "No results found yet. "
            "Run `notebooks/evaluation.ipynb` to generate them."
        )
        st.code("jupyter notebook notebooks/evaluation.ipynb", language="bash")

    else:
        import pandas as pd

        summary = pd.read_csv(summary_csv)
        full    = pd.read_csv(full_csv) if full_csv.exists() else None

        # ── Top-level metrics ──────────────────────────────────
        st.markdown("#### Summary Table")
        display_cols = {
            "strategy":   "Strategy",
            "Hit_Rate":   "Hit Rate @5",
            "MRR":        "MRR",
            "KW_Coverage":"KW Coverage",
            "Latency_s":  "Avg Latency (s)",
        }
        cols_present = [c for c in display_cols if c in summary.columns]
        st.dataframe(
            summary[cols_present]
            .rename(columns={c: display_cols[c] for c in cols_present})
            .sort_values("Hit Rate @5" if "Hit Rate @5" in
                         [display_cols[c] for c in cols_present] else cols_present[1],
                         ascending=False)
            .reset_index(drop=True),
            use_container_width=True,
            hide_index=True,
        )

        # ── Saved figures ──────────────────────────────────────
        st.markdown("#### Charts")
        fig_cols = st.columns(2)
        for fig_path, col in [
            (results_dir / "fig1_bars.png",    fig_cols[0]),
            (results_dir / "fig2_heatmaps.png", fig_cols[1]),
        ]:
            if fig_path.exists():
                col.image(str(fig_path), use_container_width=True)
            else:
                col.info(f"{fig_path.name} not found — run the notebook.")

        if (results_dir / "fig3_radar.png").exists():
            radar_col = st.columns([1, 2, 1])[1]
            radar_col.image(
                str(results_dir / "fig3_radar.png"), use_container_width=True
            )

        # ── Full results table ──────────────────────────────────
        if full is not None:
            st.markdown("#### Full Results")
            filter_strat = st.multiselect(
                "Filter by strategy:",
                full["strategy"].unique().tolist(),
                default=full["strategy"].unique().tolist(),
            )
            filtered = full[full["strategy"].isin(filter_strat)]
            show_cols = ["strategy", "query_id", "category", "difficulty",
                         "query", "hit_at_5", "kw_cov", "mrr", "latency_s"]
            show_cols = [c for c in show_cols if c in filtered.columns]
            st.dataframe(
                filtered[show_cols].reset_index(drop=True),
                use_container_width=True,
                hide_index=True,
            )

        # ── Download buttons ───────────────────────────────────
        st.markdown("#### Download")
        dl_cols = st.columns(2)
        with open(summary_csv, "rb") as f:
            dl_cols[0].download_button(
                "⬇️  Download summary.csv", f,
                file_name="summary.csv", mime="text/csv",
            )
        if full_csv.exists():
            with open(full_csv, "rb") as f:
                dl_cols[1].download_button(
                    "⬇️  Download full_results.csv", f,
                    file_name="full_results.csv", mime="text/csv",
                )