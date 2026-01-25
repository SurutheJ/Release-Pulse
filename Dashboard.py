# ============================
# Imports & Page Config
# ============================
import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="ReleasePulse",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================
# Load Data
# ============================
reviews = pd.read_csv("spotify_reviews_multilabel.csv")
priority = pd.read_csv("priority_backlog.csv")

# Canonical reference
df = reviews.copy()

# ============================
# Sidebar Navigation (LOCKED)
# ============================
st.sidebar.title("Navigation")

page = st.sidebar.radio(
    "Select a Section",
    [
        "Home",
        "About the Dashboard",
        "Executive Summary",
        "Release Health",
        "Priority Roadmap",
        "Theme Deep Dive"
    ]
)

st.sidebar.markdown("---")
st.sidebar.caption("ReleasePulse — Internal PM Tool")
st.sidebar.caption("Created by Suruthe Jayachandran")

# ============================
# 1. HOME
# ============================
if page == "Home":
    st.title("ReleasePulse")

    st.markdown("""
    **AI-Assisted Feedback Intelligence for Product Roadmaps**

    An internal Product Management tool designed to turn noisy user reviews
    into **release health insights** and **prioritized roadmap decisions**.
    """)

    st.markdown("""
    This dashboard is intended for **Product Managers** working with
    imperfect, real-world user feedback and limited engineering bandwidth.
    """)

# ============================
# 2. ABOUT THE DASHBOARD
# ============================
elif page == "About the Dashboard":
    st.title("About the Dashboard")

    st.markdown("""
    **ReleasePulse** helps Product Managers answer three core questions:

    1. *Where is user pain coming from?*  
    2. *Is this a new regression or persistent product debt?*  
    3. *What should we fix next given limited resources?*
    """)

    st.subheader("How to Use This Dashboard")

    st.markdown("""
    - **Executive Summary** — High-level snapshot of the latest release  
    - **Release Health** — Diagnostic view showing where pain is concentrated by version  
    - **Priority Roadmap** — Ranked fix order using severity, confidence, and effort tradeoffs  
    - **Theme Deep Dive** — Raw user feedback to validate decisions
    """)

    st.markdown("""
    **Design principle:**  
    *Context first, diagnosis next, decisions last.*
    """)

# ============================
# 3. EXECUTIVE SUMMARY
# ============================
elif page == "Executive Summary":
    st.title("Executive Summary — Latest Release")

    latest_version = sorted(df["RC_ver"].dropna().unique())[-1]

    st.markdown(f"""
    This page summarizes **overall user pain in the latest release ({latest_version})**.
    It is intended for quick alignment before deeper investigation.
    """)

    summary_pain = (
        df[df["RC_ver"] == latest_version]
        .groupby("theme_label")["final_weight"]
        .sum()
        .sort_values(ascending=False)
        .reset_index()
    )

    fig = px.bar(
        summary_pain,
        x="theme_label",
        y="final_weight",
        title=f"User Pain by Product Area — Version {latest_version}",
        labels={
            "theme_label": "Product Area",
            "final_weight": "Total Weighted User Pain"
        }
    )

    fig.update_layout(xaxis_tickangle=-45, height=450)
    st.plotly_chart(fig, use_container_width=True)

# ============================
# 4. RELEASE HEALTH (HERO PAGE)
# ============================
elif page == "Release Health":
    st.title("Release Health — Diagnostic View")

    st.markdown("""
    This view shows **where user pain is concentrated** for a selected release.
    It uses **raw weighted user feedback** (severity × validation).
    """)

    versions = sorted(df["RC_ver"].dropna().unique(), reverse=True)

    selected_version = st.selectbox(
        "Select App Version",
        versions,
        index=0
    )

    health_pain = (
        df[df["RC_ver"] == selected_version]
        .groupby("theme_label")["final_weight"]
        .sum()
        .sort_values(ascending=False)
        .reset_index()
    )

    fig = px.bar(
        health_pain,
        x="theme_label",
        y="final_weight",
        title=f"Release Health — Version {selected_version}",
        labels={
            "theme_label": "Product Area",
            "final_weight": "Total Weighted User Pain"
        }
    )

    fig.update_layout(xaxis_tickangle=-45, height=450)
    st.plotly_chart(fig, use_container_width=True)

    st.caption(
        "Higher values indicate more concentrated user frustration in this release."
    )

# ============================
# 5. PRIORITY ROADMAP (DECISION PAGE)
# ============================
elif page == "Priority Roadmap":
    st.title("Priority Roadmap")

    st.markdown("""
    This page converts release insights into a **ranked fix order** using a
    RICE-style prioritization framework.
    """)

    display_cols = [
        "theme",
        "Priority_Score",
        "Effort",
        "Is_Persistent",
        "Is_Regression"
    ]

    st.dataframe(
        priority[display_cols]
        .sort_values("Priority_Score", ascending=False),
        use_container_width=True
    )

    st.markdown("""
    **How to interpret this table:**
    - Higher score → higher priority
    - Low effort + persistent pain → fastest wins
    - Regression flags indicate release risk
    """)

# ============================
# 6. THEME DEEP DIVE (EVIDENCE)
# ============================
elif page == "Theme Deep Dive":
    st.title("Theme Deep Dive — User Evidence")

    st.markdown("""
    This view provides **raw user feedback** to validate and contextualize
    the signals shown elsewhere in the dashboard.
    """)

    THEMES = sorted(df["theme_label"].dropna().unique())
    VERSIONS = sorted(df["RC_ver"].dropna().unique(), reverse=True)

    selected_theme = st.selectbox("Select Theme", THEMES)
    selected_version = st.selectbox("Select Version", VERSIONS)

    deep_dive = (
        df[
            (df["theme_label"] == selected_theme) &
            (df["RC_ver"] == selected_version)
        ]
        .sort_values("final_weight", ascending=False)
        .head(5)
    )

    st.subheader("Top High-Impact Reviews")
    st.table(deep_dive[["score", "content"]])
