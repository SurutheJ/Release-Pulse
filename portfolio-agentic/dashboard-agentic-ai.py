# ============================
# ReleasePulse — Portfolio (AI & Agentic)
# ============================
# Same as Dashboard v2, plus:
# - Agentic AI Assistant (LLM + tool-calling in a decide–act loop)
# - "Built with — AI & ML" section for portfolio
# Run from project root: streamlit run portfolio-agentic/dashboard-agentic-ai.py
# ============================

import os
import sys
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from agentic_assistant import run_agent

st.set_page_config(
    page_title="ReleasePulse — Spotify Review Intelligence",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================
# Custom CSS Styling
# ============================
st.markdown("""
<style>
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .metric-value {
        font-size: 2.5rem;
        font-weight: bold;
    }
    .metric-label {
        font-size: 0.9rem;
        opacity: 0.9;
    }
    .stMetric {
        background-color: #f0f2f6;
        padding: 15px;
        border-radius: 10px;
    }
    div[data-testid="stMetricValue"] {
        font-size: 1.8rem;
    }
    .highlight-box {
        background-color: #e8f4f8;
        padding: 15px;
        border-radius: 8px;
        border-left: 4px solid #1f77b4;
        margin: 10px 0;
    }
    .warning-box {
        background-color: #fff3cd;
        padding: 15px;
        border-radius: 8px;
        border-left: 4px solid #ffc107;
        margin: 10px 0;
    }
    .success-box {
        background-color: #d4edda;
        padding: 15px;
        border-radius: 8px;
        border-left: 4px solid #28a745;
        margin: 10px 0;
    }
    .methodology-card {
        background: #f8f9fa;
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #dee2e6;
        margin: 10px 0;
    }
    .formula-box {
        background: #2d2d2d;
        color: #f8f8f2;
        padding: 15px;
        border-radius: 8px;
        font-family: 'Courier New', monospace;
        margin: 10px 0;
    }
    /* Fixed sidebar with compact spacing */
    [data-testid="stSidebar"] {
        position: fixed;
        height: 100vh;
    }
    [data-testid="stSidebar"] [data-testid="stVerticalBlock"] {
        gap: 0.5rem;
    }
    [data-testid="stSidebar"] [data-testid="stMetric"] {
        padding: 8px;
    }
    [data-testid="stSidebar"] [data-testid="stMetricValue"] {
        font-size: 1.2rem;
    }
    [data-testid="stSidebar"] [data-testid="stMetricLabel"] {
        font-size: 0.75rem;
    }
    [data-testid="stSidebar"] .stRadio > div {
        gap: 0.25rem;
    }
    [data-testid="stSidebar"] h1 {
        font-size: 1.3rem;
        margin-bottom: 0;
    }
    [data-testid="stSidebar"] img {
        max-width: 40px;
    }
    /* Chat messages: hide avatar so content uses full width, viewer-friendly */
    [data-testid="stSidebar"] [data-testid="stChatMessage"] {
        padding: 0.5rem 0;
        max-width: 100%;
    }
    [data-testid="stSidebar"] [data-testid="stChatMessage"] > div:first-child {
        display: none;
    }
    [data-testid="stSidebar"] [data-testid="stChatMessage"] [data-testid="stMarkdown"] {
        max-width: 100%;
        word-wrap: break-word;
    }
    /* Home page: hero and cards */
    .hero-subtitle { font-size: 1.1rem; color: #555; margin-bottom: 1.5rem; line-height: 1.5; }
    .agentic-badge { display: inline-block; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 0.25rem 0.75rem; border-radius: 20px; font-size: 0.85rem; font-weight: 600; margin-bottom: 0.5rem; }
    .home-card { border-radius: 12px; padding: 1.25rem 1.5rem; box-shadow: 0 2px 8px rgba(0,0,0,0.06); border: 1px solid #eee; margin: 0.5rem 0; }
    .cta-box { background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%); border-radius: 12px; padding: 1.5rem; text-align: center; border-left: 4px solid #667eea; margin-top: 1.5rem; }
</style>
""", unsafe_allow_html=True)

# ============================
# Load Data (paths relative to project root)
# ============================
_DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")

@st.cache_data
def load_data():
    reviews = pd.read_csv(os.path.join(_DATA_DIR, "spotify_reviews_multilabel.csv"))
    priority = pd.read_csv(os.path.join(_DATA_DIR, "priority_backlog.csv"))
    persistence = pd.read_csv(os.path.join(_DATA_DIR, "theme_persistence.csv"))
    version_signal = pd.read_csv(os.path.join(_DATA_DIR, "theme_version_signal.csv"))
    return reviews, priority, persistence, version_signal

reviews, priority, persistence, version_signal = load_data()
df = reviews.copy()

if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = []

# ============================
# Sidebar Navigation
# ============================
st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/thumb/8/84/Spotify_icon.svg/232px-Spotify_icon.svg.png", width=60)
st.sidebar.caption("**Spotify app** · User review intelligence")
st.sidebar.title("ReleasePulse")
st.sidebar.markdown("Feedback insights & prioritization from **Spotify** app store reviews.")
st.sidebar.markdown("---")

page = st.sidebar.radio(
    "Navigation",
    [
        "Home",
        "Methodology",
        "Executive Summary",
        "Release Health",
        "Priority Roadmap",
        "Trend Analysis",
        "Theme Deep Dive"
    ]
)

st.sidebar.markdown("---")
st.sidebar.markdown("### 💬 AI Assistant")
st.sidebar.caption("Ask about Spotify priorities, themes, regressions.")
st.sidebar.markdown("**Sample questions:**")
st.sidebar.markdown("- What should we fix first?  \n- Which themes regressed?  \n- Show me Playback Reliability reviews  \n- What are the persistent issues?")
st.sidebar.markdown("")
with st.sidebar.expander("**Open chat**", expanded=True):
    for msg in st.session_state.chat_messages[-8:]:
        with st.chat_message(msg["role"], avatar=None):
            st.markdown(msg["content"])
    chat_prompt = st.text_input("Ask about Spotify reviews...", key="sidebar_chat_input", placeholder="e.g. What should we fix first?")
    if st.button("Send", key="sidebar_chat_send"):
        if chat_prompt and chat_prompt.strip():
            # Streamlit Cloud stores secrets in st.secrets; local uses OPENAI_API_KEY env var
            try:
                api_key = st.secrets["OPENAI_API_KEY"]
            except (KeyError, AttributeError, TypeError):
                api_key = os.environ.get("OPENAI_API_KEY")
            ctx = {"reviews": reviews, "priority": priority, "persistence": persistence, "version_signal": version_signal}
            with st.spinner("Thinking..."):
                reply = run_agent(chat_prompt.strip(), ctx, api_key=api_key)
            st.session_state.chat_messages.append({"role": "user", "content": chat_prompt.strip()})
            st.session_state.chat_messages.append({"role": "assistant", "content": reply})
            if "sidebar_chat_input" in st.session_state:
                del st.session_state["sidebar_chat_input"]
            st.rerun()
st.sidebar.markdown("---")
st.sidebar.caption("Portfolio edition — Suruthe Jayachandran")

# ============================
# 1. HOME (no charts; agentic AI focus, visually appealing)
# ============================
if page == "Home":
    st.markdown("<span class='agentic-badge'>Agentic AI</span>", unsafe_allow_html=True)
    st.title("ReleasePulse — Spotify Review Intelligence")
    st.markdown(
        "<p class='hero-subtitle'>Turn <strong>Spotify app store reviews</strong> into actionable insights and prioritized decisions. "
        "Powered by <strong>agentic AI</strong>: ask in plain language, get answers from your data.</p>",
        unsafe_allow_html=True
    )
    
    st.markdown("""
    <div class="highlight-box">
    <strong>What this dashboard does:</strong> It analyzes <strong>Spotify mobile app user reviews</strong> from the store — 
    clusters them into themes, detects regressions and persistent issues, and ranks what to fix next (RICE). 
    The <strong>agentic AI assistant</strong> in the sidebar decides which data to fetch and answers your questions in context.
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("**ReleasePulse** helps Product Managers answer three core questions:")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 28px 20px; border-radius: 12px; color: white; text-align: center; min-height: 140px; box-shadow: 0 4px 12px rgba(102,126,234,0.3);">
            <p style="margin:0; font-size: 1.5rem; opacity: 0.9;">1</p>
            <p style="margin: 0.5rem 0 0 0; font-weight: 600;">Where is user pain coming from?</p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); padding: 28px 20px; border-radius: 12px; color: white; text-align: center; min-height: 140px; box-shadow: 0 4px 12px rgba(240,147,251,0.3);">
            <p style="margin:0; font-size: 1.5rem; opacity: 0.9;">2</p>
            <p style="margin: 0.5rem 0 0 0; font-weight: 600;">Is this a new regression or persistent debt?</p>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); padding: 28px 20px; border-radius: 12px; color: white; text-align: center; min-height: 140px; box-shadow: 0 4px 12px rgba(79,172,254,0.3);">
            <p style="margin:0; font-size: 1.5rem; opacity: 0.9;">3</p>
            <p style="margin: 0.5rem 0 0 0; font-weight: 600;">What should we fix next?</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.subheader("The Problem We Solve")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        <div class="warning-box">
        <strong>The Challenge:</strong> PMs spend <strong>4–8 hours per release</strong> manually reading 
        and categorizing app reviews — time-consuming, subjective, and reactive.
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="success-box">
        <strong>The Solution:</strong> ReleasePulse automates the pipeline to <strong>under 10 minutes</strong> 
        with consistent, data-driven prioritization and <strong>agentic AI</strong> for natural-language questions.
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.subheader("How to Use This Dashboard")
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["Methodology", "Executive Summary", "Release Health", "Priority Roadmap", "Theme Deep Dive"])
    with tab1:
        st.markdown("Technical approach: weighting, clustering, regression & persistence detection, RICE.")
    with tab2:
        st.markdown("High-level snapshot of the latest release: pain metrics, top theme, quick health check.")
    with tab3:
        st.markdown("Pain by version, theme breakdown, version-over-version comparison.")
    with tab4:
        st.markdown("RICE prioritization, effort vs impact, regression/persistence flags, CSV export.")
    with tab5:
        st.markdown("Raw user feedback and high-impact review samples per theme.")
    
    st.markdown("---")
    st.subheader("Built with — AI & ML")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        <div class="home-card">
        <strong>NLP & clustering</strong><br>
        <span style="color:#666; font-size:0.9rem;">sentence-transformers, weighted KMeans for theme discovery.</span>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="home-card">
        <strong>ML pipeline</strong><br>
        <span style="color:#666; font-size:0.9rem;">Regression & persistence detection, RICE prioritization.</span>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div class="home-card">
        <strong>Agentic AI</strong><br>
        <span style="color:#666; font-size:0.9rem;">LLM + tool-calling: decides which data to fetch, answers from backlog, reviews, regressions.</span>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="cta-box">
    <strong>Get started:</strong> Open the sidebar → <strong>Open chat</strong> and ask anything about Spotify priorities, themes, or regressions.
    </div>
    """, unsafe_allow_html=True)
    st.markdown("")
    st.caption("Design principle: context first, diagnosis next, decisions last.")

# ============================
# 2. METHODOLOGY
# ============================
elif page == "Methodology":
    st.title("Methodology")
    st.markdown("### How ReleasePulse Works")
    
    st.markdown("""
    This page explains the technical approach behind ReleasePulse so you can 
    **understand and trust** the insights it provides.
    """)
    
    st.markdown("---")
    
    # Pipeline Overview
    st.subheader("1. Data Pipeline Overview")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.markdown("""
        <div class="methodology-card" style="text-align: center;">
        <h4>Step 1</h4>
        <p><strong>Collect</strong></p>
        <p style="font-size: 0.8rem;">App store reviews with scores & metadata</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="methodology-card" style="text-align: center;">
        <h4>Step 2</h4>
        <p><strong>Weight</strong></p>
        <p style="font-size: 0.8rem;">Severity × Impact × Sample Size</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="methodology-card" style="text-align: center;">
        <h4>Step 3</h4>
        <p><strong>Cluster</strong></p>
        <p style="font-size: 0.8rem;">NLP embeddings + KMeans</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="methodology-card" style="text-align: center;">
        <h4>Step 4</h4>
        <p><strong>Analyze</strong></p>
        <p style="font-size: 0.8rem;">Regression & persistence detection</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col5:
        st.markdown("""
        <div class="methodology-card" style="text-align: center;">
        <h4>Step 5</h4>
        <p><strong>Prioritize</strong></p>
        <p style="font-size: 0.8rem;">RICE scoring</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Weighting System
    st.subheader("2. Review Weighting System")
    
    st.markdown("""
    Not all reviews are equal. A 1-star review with 50 thumbs-up from the latest version 
    carries more signal than a 3-star review with no engagement from an old release.
    """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **Weight Components:**
        
        | Component | Formula | Rationale |
        |-----------|---------|-----------|
        | Severity | `6 - score` | Low ratings = more pain |
        | Impact | `1 + (thumbs_up / max)` | Validated feedback matters more |
        | Version | `count / max_count` | Normalize for sample size |
        """)
    
    with col2:
        st.markdown("""
        <div class="formula-box">
        <strong>Final Weight =</strong><br>
        Severity × Impact × Version Weight
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        **Example:**  
        1-star review (severity=5) with 10 thumbs-up (impact=1.5) 
        from a well-sampled release (version=0.8) = **6.0 weight**
        """)
    
    st.markdown("---")
    
    # Theme Clustering
    st.subheader("3. Theme Clustering")
    
    st.markdown("""
    Reviews are automatically grouped into product themes using **semantic embeddings**.
    """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **How it works:**
        1. Each review is converted to a 384-dimensional vector using `sentence-transformers`
        2. Vectors are weighted by review importance
        3. KMeans clustering groups similar reviews
        4. Each cluster is labeled as a product theme
        
        **Why 6 clusters?**  
        Empirically tested 4, 6, 8, 10 — 6 provided the best balance of 
        interpretability and distinctiveness.
        """)
    
    with col2:
        st.markdown("**Current Themes:**")
        theme_descriptions = {
            "Playback Reliability": "Crashes, buffering, songs not playing",
            "Navigation & Home Feed": "UI navigation, homepage recommendations",
            "Library & Playlist Control": "Playlist management, library organization",
            "Free vs Premium Friction": "Ads, premium features, upgrade prompts",
            "UI & Content Surfaces": "Visual design, content discovery",
            "Performance & Media Issues": "App speed, downloads, offline mode"
        }
        
        for theme, desc in theme_descriptions.items():
            st.markdown(f"- **{theme}**: {desc}")
    
    st.markdown("---")
    
    # Regression & Persistence
    st.subheader("4. Regression & Persistence Detection")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="methodology-card">
        <h4>Regression Detection</h4>
        <p>A theme is flagged as a <strong>regression</strong> if its pain share 
        increases by more than <strong>5%</strong> vs. the previous release.</p>
        <p><em>Indicates: Something broke in the latest release</em></p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="methodology-card">
        <h4>Persistence Detection</h4>
        <p>A theme is flagged as <strong>persistent</strong> if it represents 
        more than <strong>15%</strong> of pain in <strong>3+ releases</strong>.</p>
        <p><em>Indicates: Long-standing tech debt</em></p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="highlight-box">
    <strong>How to interpret flags:</strong>
    <ul>
    <li><strong>Regression only</strong>: New issue — investigate recent changes</li>
    <li><strong>Persistent only</strong>: Tech debt — plan for larger investment</li>
    <li><strong>Both flags</strong>: Worsening chronic issue — high priority</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # RICE Prioritization
    st.subheader("5. RICE Prioritization")
    
    st.markdown("""
    Themes are ranked using a modified **RICE framework** (Reach, Impact, Confidence, Effort).
    """)
    
    st.markdown("""
    <div class="formula-box">
    <strong>Priority Score = (Reach × Impact × Confidence) / Effort</strong>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        | Component | Calculation |
        |-----------|-------------|
        | **Reach** | 60% signal + 40% volume |
        | **Impact** | Inverted rating × multipliers |
        | **Confidence** | 70% volume + 30% persistence |
        | **Effort** | Manual estimate (1-5) |
        """)
    
    with col2:
        st.markdown("""
        **Impact Multipliers:**
        - **+20%** if regression (release risk)
        - **+20%** if persistent (accumulated debt)
        
        **Effort Scale:**
        - 1 = Quick fix
        - 2 = Small feature
        - 3 = Medium feature
        - 4 = Large feature
        - 5 = Major initiative
        """)
    
    st.markdown("---")
    
    st.subheader("6. Limitations & Caveats")
    
    st.markdown("""
    <div class="warning-box">
    <strong>Important caveats to keep in mind:</strong>
    <ul>
    <li><strong>Effort is estimated</strong>: Treat as relative, not absolute</li>
    <li><strong>Correlation ≠ causation</strong>: Clusters show patterns, not root causes</li>
    <li><strong>English-focused</strong>: Embeddings optimized for English text</li>
    <li><strong>Batch analysis</strong>: Not real-time; reflects data at pipeline run time</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)
    
    st.info("For the full technical documentation, see [METHODOLOGY.md](https://github.com/yourusername/ReleasePulse/blob/main/docs/METHODOLOGY.md)")

# ============================
# 3. EXECUTIVE SUMMARY
# ============================
elif page == "Executive Summary":
    st.title("Executive Summary")
    
    st.markdown("""
    <div class="highlight-box">
    <strong>For PMs:</strong> This page is a one-page snapshot of the <strong>latest release</strong> — total reviews, 
    average rating, pain by product area, and top pain theme. Use it for a quick release health check, to share 
    with stakeholders, or to decide where to dig deeper (e.g. Theme Deep Dive or Release Health for version comparison).
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")
    
    latest_version = sorted(df["RC_ver"].dropna().unique())[-1]
    latest_df = df[df["RC_ver"] == latest_version]
    
    st.markdown(f"### Release: **{latest_version}**")
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_reviews = len(latest_df)
        st.metric("Total Reviews", f"{total_reviews:,}")
    
    with col2:
        avg_rating = latest_df["score"].mean()
        st.metric("Average Rating", f"{avg_rating:.2f}")
    
    with col3:
        total_pain = latest_df["final_weight"].sum()
        st.metric("Total Pain Score", f"{total_pain:.0f}")
    
    with col4:
        top_theme = latest_df.groupby("theme_label")["final_weight"].sum().idxmax()
        st.metric("Top Pain Area", top_theme[:15] + "..." if len(top_theme) > 15 else top_theme)
    
    st.markdown("---")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("User Pain by Product Area")
        
        summary_pain = (
            latest_df
            .groupby("theme_label")["final_weight"]
            .sum()
            .sort_values(ascending=True)
            .reset_index()
        )
        
        fig = px.bar(
            summary_pain,
            x="final_weight",
            y="theme_label",
            orientation="h",
            color="final_weight",
            color_continuous_scale="Reds"
        )
        
        fig.update_layout(
            height=400,
            xaxis_title="Total Weighted User Pain",
            yaxis_title="",
            showlegend=False
        )
        fig.update_coloraxes(showscale=False)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Rating Distribution")
        
        rating_dist = latest_df["score"].value_counts().sort_index().reset_index()
        rating_dist.columns = ["Rating", "Count"]
        
        fig = px.bar(
            rating_dist,
            x="Rating",
            y="Count",
            color="Rating",
            color_continuous_scale="RdYlGn"
        )
        fig.update_layout(height=400, showlegend=False)
        fig.update_coloraxes(showscale=False)
        st.plotly_chart(fig, use_container_width=True)
    
    # Insights box
    st.markdown("---")
    st.subheader("Key Insights")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"""
        **Highest Pain Area:** {summary_pain.iloc[-1]['theme_label']}  
        - Weight: {summary_pain.iloc[-1]['final_weight']:.1f}
        """)
    
    with col2:
        low_ratings = len(latest_df[latest_df["score"] <= 2])
        st.markdown(f"""
        **Critical Reviews (1-2 stars):** {low_ratings} ({100*low_ratings/len(latest_df):.1f}%)  
        - Requires immediate attention
        """)
    
    # How to interpret (NEW)
    with st.expander("How to Interpret This Data"):
        st.markdown("""
        - **Pain Score** is a weighted sum where low ratings, high engagement, and well-sampled releases contribute more
        - **Top Pain Area** shows where users are struggling most in this release
        - **Critical Reviews** (1-2 stars) often contain the most actionable feedback
        - Compare with previous releases in **Release Health** to see if issues are new or ongoing
        """)

# ============================
# 5. RELEASE HEALTH
# ============================
elif page == "Release Health":
    st.title("Release Health — Diagnostic View")
    
    st.markdown("""
    Analyze **where user pain is concentrated** for any selected release.
    Uses weighted user feedback (severity × validation).
    """)
    
    versions = sorted(df["RC_ver"].dropna().unique(), reverse=True)
    
    col1, col2 = st.columns([1, 3])
    
    with col1:
        selected_version = st.selectbox(
            "Select App Version",
            versions,
            index=0
        )
        
        # Version stats
        version_df = df[df["RC_ver"] == selected_version]
        st.markdown("---")
        st.markdown("**Version Stats:**")
        st.metric("Reviews", len(version_df))
        st.metric("Avg Rating", f"{version_df['score'].mean():.2f}")
        st.metric("Pain Score", f"{version_df['final_weight'].sum():.0f}")
    
    with col2:
        health_pain = (
            version_df
            .groupby("theme_label")["final_weight"]
            .sum()
            .sort_values(ascending=False)
            .reset_index()
        )
        
        # Add percentage
        health_pain["percentage"] = 100 * health_pain["final_weight"] / health_pain["final_weight"].sum()
        
        fig = px.bar(
            health_pain,
            x="theme_label",
            y="final_weight",
            color="percentage",
            color_continuous_scale="Viridis",
            text=health_pain["percentage"].apply(lambda x: f"{x:.1f}%")
        )
        
        fig.update_layout(
            title=f"Release Health — Version {selected_version}",
            xaxis_tickangle=-45,
            height=450,
            xaxis_title="Product Area",
            yaxis_title="Total Weighted User Pain"
        )
        fig.update_traces(textposition="outside")
        fig.update_coloraxes(showscale=False)
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # Comparison with previous version
    st.subheader("Version Comparison")
    
    if len(versions) > 1:
        prev_version = versions[1] if versions[0] == selected_version else versions[0]
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"**Current: {selected_version}**")
            current_pain = version_df.groupby("theme_label")["final_weight"].sum()
            st.dataframe(current_pain.reset_index().rename(columns={"final_weight": "Pain Score"}), hide_index=True)
        
        with col2:
            st.markdown(f"**Previous: {prev_version}**")
            prev_df = df[df["RC_ver"] == prev_version]
            prev_pain = prev_df.groupby("theme_label")["final_weight"].sum()
            st.dataframe(prev_pain.reset_index().rename(columns={"final_weight": "Pain Score"}), hide_index=True)
    
    # How to interpret (NEW)
    with st.expander("How to Interpret This Data"):
        st.markdown("""
        - **Percentage** shows each theme's share of total pain for this release
        - Compare percentages across versions to identify **regressions** (sudden increases)
        - A theme with >20% pain share is a major concern
        - Use **Theme Deep Dive** to see actual user quotes for any concerning theme
        """)

# ============================
# 6. PRIORITY ROADMAP
# ============================
elif page == "Priority Roadmap":
    st.title("Priority Roadmap")
    
    st.markdown("""
    Convert release insights into a **ranked fix order** using a RICE-style prioritization framework.
    """)
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Themes", len(priority))
    
    with col2:
        persistent_count = priority["Is_Persistent"].sum()
        st.metric("Persistent Issues", int(persistent_count))
    
    with col3:
        regression_count = priority["Is_Regression"].sum()
        st.metric("Regressions", int(regression_count))
    
    with col4:
        avg_effort = priority["Effort"].mean()
        st.metric("Avg Effort", f"{avg_effort:.1f}")
    
    st.markdown("---")
    
    # Priority visualization
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Priority Score Ranking")
        
        priority_sorted = priority.sort_values("Priority_Score", ascending=True)
        
        fig = px.bar(
            priority_sorted,
            x="Priority_Score",
            y="theme",
            orientation="h",
            color="Effort",
            color_continuous_scale="RdYlGn_r",
            hover_data=["Reach", "Impact", "Confidence", "Is_Persistent", "Is_Regression"]
        )
        
        fig.update_layout(
            height=400,
            xaxis_title="Priority Score",
            yaxis_title=""
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Effort Distribution")
        
        effort_dist = priority.groupby("Effort").size().reset_index(name="Count")
        
        fig = px.pie(
            effort_dist,
            values="Count",
            names="Effort",
            color="Effort",
            color_discrete_sequence=px.colors.sequential.RdBu
        )
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # Detailed table
    st.subheader("Detailed Priority Backlog")
    
    display_priority = priority.copy()
    display_priority["Priority_Score"] = display_priority["Priority_Score"].apply(lambda x: f"{x:.4f}")
    display_priority["Reach"] = display_priority["Reach"].apply(lambda x: f"{x:.2%}")
    display_priority["Impact"] = display_priority["Impact"].apply(lambda x: f"{x:.2f}")
    display_priority["Confidence"] = display_priority["Confidence"].apply(lambda x: f"{x:.2%}")
    
    st.dataframe(
        display_priority[["theme", "Priority_Score", "Reach", "Impact", "Confidence", "Effort", "Is_Persistent", "Is_Regression"]]
        .sort_values("Priority_Score", ascending=False),
        use_container_width=True,
        hide_index=True
    )
    
    # Export functionality (NEW)
    st.markdown("---")
    st.subheader("Export Backlog")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("Download the priority backlog as CSV to import into Jira, Asana, or other tools.")
    
    with col2:
        export_df = priority[["theme", "Priority_Score", "Reach", "Impact", "Confidence", "Effort", "Is_Persistent", "Is_Regression"]].copy()
        export_df = export_df.sort_values("Priority_Score", ascending=False)
        
        csv = export_df.to_csv(index=False)
        st.download_button(
            label="Download CSV",
            data=csv,
            file_name=f"priority_backlog_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
    
    st.markdown("""
    ---
    **How to interpret this table:**
    - **Higher score** → Higher priority
    - **Low effort + persistent pain** → Fastest wins
    - **Regression flags** indicate release risk requiring immediate attention
    """)
    
    # How to interpret (NEW)
    with st.expander("Understanding the RICE Components"):
        st.markdown("""
        | Component | What It Measures | Range |
        |-----------|------------------|-------|
        | **Reach** | % of users affected (signal + volume) | 0-1 |
        | **Impact** | Severity of pain (inverted rating + multipliers) | 0-1.44 |
        | **Confidence** | Reliability of the signal (volume + persistence) | 0-1 |
        | **Effort** | Estimated implementation complexity | 1-5 |
        
        **Flags:**
        - **Is_Regression = True**: Pain increased >5% from last release
        - **Is_Persistent = True**: Pain high in 3+ consecutive releases
        """)

# ============================
# 7. TREND ANALYSIS
# ============================
elif page == "Trend Analysis":
    st.title("Trend Analysis")
    
    st.markdown("Track **theme signals across releases** to identify patterns and regressions.")
    
    # Theme selector
    themes = sorted(version_signal["theme"].unique())
    selected_themes = st.multiselect(
        "Select Themes to Compare",
        themes,
        default=themes[:3]
    )
    
    if selected_themes:
        # Filter data
        trend_data = version_signal[version_signal["theme"].isin(selected_themes)]
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Normalized Signal Over Time")
            
            fig = px.line(
                trend_data,
                x="RC_ver",
                y="Normalized_Signal",
                color="theme",
                markers=True
            )
            fig.update_layout(
                height=400,
                xaxis_tickangle=-45,
                xaxis_title="App Version",
                yaxis_title="Normalized Signal"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("Review Count Trend")
            
            fig = px.line(
                trend_data,
                x="RC_ver",
                y="Review_Count",
                color="theme",
                markers=True
            )
            fig.update_layout(
                height=400,
                xaxis_tickangle=-45,
                xaxis_title="App Version",
                yaxis_title="Review Count"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("---")
        
        # Average rating trend
        st.subheader("Average Rating Trend by Theme")
        
        fig = px.line(
            trend_data,
            x="RC_ver",
            y="Avg_Rating",
            color="theme",
            markers=True
        )
        fig.update_layout(
            height=350,
            xaxis_tickangle=-45,
            xaxis_title="App Version",
            yaxis_title="Average Rating"
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Delta analysis
        st.markdown("---")
        st.subheader("Signal Delta (Version over Version)")
        
        delta_data = trend_data[trend_data["Delta"].notna()]
        
        if not delta_data.empty:
            fig = px.bar(
                delta_data,
                x="RC_ver",
                y="Delta",
                color="theme",
                barmode="group"
            )
            fig.update_layout(
                height=350,
                xaxis_tickangle=-45,
                xaxis_title="App Version",
                yaxis_title="Signal Change"
            )
            fig.add_hline(y=0, line_dash="dash", line_color="gray")
            st.plotly_chart(fig, use_container_width=True)
            
            st.caption("Positive delta = worsening signal | Negative delta = improving")
        
        # How to interpret (NEW)
        with st.expander("How to Interpret Trends"):
            st.markdown("""
            - **Normalized Signal** shows each theme's % share of total pain per release
            - **Upward trend** = worsening issue, may need prioritization
            - **Downward trend** = improving, possibly due to past fixes
            - **Delta > 0.05** triggers a regression flag
            - **Stable high signal** across 3+ releases = persistent issue
            """)
    else:
        st.warning("Please select at least one theme to view trends.")

# ============================
# 8. THEME DEEP DIVE
# ============================
elif page == "Theme Deep Dive":
    st.title("Theme Deep Dive — User Evidence")
    
    st.markdown("""
    Explore **raw user feedback** to validate and contextualize the signals shown elsewhere.
    """)
    
    col1, col2 = st.columns(2)
    
    THEMES = sorted(df["theme_label"].dropna().unique())
    VERSIONS = sorted(df["RC_ver"].dropna().unique(), reverse=True)
    
    with col1:
        selected_theme = st.selectbox("Select Theme", THEMES)
    
    with col2:
        selected_version = st.selectbox("Select Version", VERSIONS)
    
    # Filter data
    deep_dive = df[
        (df["theme_label"] == selected_theme) &
        (df["RC_ver"] == selected_version)
    ].sort_values("final_weight", ascending=False)
    
    st.markdown("---")
    
    # Stats for this selection
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Reviews", len(deep_dive))
    
    with col2:
        st.metric("Avg Rating", f"{deep_dive['score'].mean():.2f}" if len(deep_dive) > 0 else "N/A")
    
    with col3:
        st.metric("Total Pain", f"{deep_dive['final_weight'].sum():.1f}")
    
    with col4:
        # Check persistence
        is_persistent = persistence[persistence["theme"] == selected_theme]["Is_Persistent"].values
        st.metric("Persistent?", "Yes" if len(is_persistent) > 0 and is_persistent[0] else "No")
    
    st.markdown("---")
    
    # How to use this data (NEW)
    st.markdown("""
    <div class="highlight-box">
    <strong>How to use this data:</strong> Read through high-impact reviews to understand the 
    <em>why</em> behind the numbers. Look for patterns, specific complaints, and user suggestions. 
    Use direct quotes in your PRDs and stakeholder communications.
    </div>
    """, unsafe_allow_html=True)
    
    # Top reviews
    num_reviews = st.slider("Number of reviews to display", 5, 20, 10)
    
    st.subheader(f"Top {num_reviews} High-Impact Reviews")
    
    if len(deep_dive) > 0:
        for idx, row in deep_dive.head(num_reviews).iterrows():
            rating = int(row["score"])
            weight = row["final_weight"]
            
            # Color-code by rating
            if rating <= 2:
                icon = "[LOW]"
            elif rating == 3:
                icon = "[MED]"
            else:
                icon = "[HIGH]"
            
            with st.expander(f"{icon} Rating: {rating}/5 — Pain Weight: {weight:.2f}"):
                st.markdown(f"**Review:**")
                st.write(row["content"])
                st.markdown(f"**Score:** {row['score']} | **Weight:** {weight:.2f}")
    else:
        st.info("No reviews found for this combination.")
    
    st.markdown("---")
    
    # Word cloud or rating distribution
    st.subheader("Rating Distribution for Selection")
    
    if len(deep_dive) > 0:
        rating_counts = deep_dive["score"].value_counts().sort_index().reset_index()
        rating_counts.columns = ["Rating", "Count"]
        
        fig = px.bar(
            rating_counts,
            x="Rating",
            y="Count",
            color="Rating",
            color_continuous_scale="RdYlGn"
        )
        fig.update_layout(height=300, showlegend=False)
        fig.update_coloraxes(showscale=False)
        st.plotly_chart(fig, use_container_width=True)
