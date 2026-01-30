# ============================
# Imports & Page Config
# ============================
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(
    page_title="ReleasePulse",
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
</style>
""", unsafe_allow_html=True)

# ============================
# Load Data
# ============================
@st.cache_data
def load_data():
    reviews = pd.read_csv("data/spotify_reviews_multilabel.csv")
    priority = pd.read_csv("data/priority_backlog.csv")
    persistence = pd.read_csv("data/theme_persistence.csv")
    version_signal = pd.read_csv("data/theme_version_signal.csv")
    return reviews, priority, persistence, version_signal

reviews, priority, persistence, version_signal = load_data()
df = reviews.copy()

# ============================
# Sidebar Navigation
# ============================
st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/thumb/8/84/Spotify_icon.svg/232px-Spotify_icon.svg.png", width=60)
st.sidebar.title("ReleasePulse")
st.sidebar.markdown("---")

page = st.sidebar.radio(
    "Navigation",
    [
        "Home",
        "About",
        "Executive Summary",
        "Release Health",
        "Priority Roadmap",
        "Trend Analysis",
        "Theme Deep Dive"
    ]
)

st.sidebar.markdown("---")
st.sidebar.markdown("### Quick Stats")
total_reviews = len(df)
total_versions = df["RC_ver"].nunique()
total_themes = df["theme_label"].nunique()

st.sidebar.metric("Total Reviews", f"{total_reviews:,}")
st.sidebar.metric("App Versions", total_versions)
st.sidebar.metric("Theme Categories", total_themes)

st.sidebar.markdown("---")
st.sidebar.caption("ReleasePulse — Internal PM Tool")
st.sidebar.caption("Created by Suruthe Jayachandran")

# ============================
# 1. HOME
# ============================
if page == "Home":
    st.title("ReleasePulse")
    st.markdown("### AI-Assisted Feedback Intelligence for Product Roadmaps")
    
    st.markdown("""
    <div class="highlight-box">
    <strong>Welcome to ReleasePulse</strong> — An internal Product Management tool designed to transform 
    noisy user reviews into <strong>actionable release insights</strong> and <strong>prioritized roadmap decisions</strong>.
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Key metrics row
    col1, col2, col3, col4 = st.columns(4)
    
    latest_version = sorted(df["RC_ver"].dropna().unique())[-1]
    latest_reviews = len(df[df["RC_ver"] == latest_version])
    avg_rating = df[df["RC_ver"] == latest_version]["score"].mean()
    persistent_issues = persistence[persistence["Is_Persistent"] == True].shape[0]
    
    with col1:
        st.metric(
            label="Latest Version",
            value=latest_version,
            delta="Current"
        )
    
    with col2:
        st.metric(
            label="Reviews (Latest)",
            value=f"{latest_reviews:,}",
            delta=None
        )
    
    with col3:
        st.metric(
            label="Avg Rating (Latest)",
            value=f"{avg_rating:.2f}",
            delta=f"{avg_rating - 2.5:.2f}" if avg_rating else None
        )
    
    with col4:
        st.metric(
            label="Persistent Issues",
            value=persistent_issues,
            delta="Tracked"
        )
    
    st.markdown("---")
    
    # Quick overview charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Reviews by Version")
        version_counts = df.groupby("RC_ver").size().reset_index(name="count")
        version_counts = version_counts.sort_values("RC_ver")
        
        fig = px.bar(
            version_counts,
            x="RC_ver",
            y="count",
            color="count",
            color_continuous_scale="Blues"
        )
        fig.update_layout(
            xaxis_tickangle=-45,
            height=350,
            showlegend=False,
            xaxis_title="App Version",
            yaxis_title="Number of Reviews"
        )
        fig.update_coloraxes(showscale=False)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Pain Distribution by Theme")
        theme_pain = df.groupby("theme_label")["final_weight"].sum().reset_index()
        theme_pain = theme_pain.sort_values("final_weight", ascending=True)
        
        fig = px.pie(
            theme_pain,
            values="final_weight",
            names="theme_label",
            hole=0.4,
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        fig.update_layout(height=350)
        st.plotly_chart(fig, use_container_width=True)
    
    st.info("Use the sidebar navigation to explore detailed insights")

# ============================
# 2. ABOUT
# ============================
elif page == "About":
    st.title("About ReleasePulse")
    
    st.markdown("""
    **ReleasePulse** helps Product Managers answer three core questions:
    """)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 25px; border-radius: 12px; color: white; text-align: center; height: 150px;">
            <h3>1</h3>
            <p><strong>Where is user pain coming from?</strong></p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); padding: 25px; border-radius: 12px; color: white; text-align: center; height: 150px;">
            <h3>2</h3>
            <p><strong>Is this a new regression or persistent debt?</strong></p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); padding: 25px; border-radius: 12px; color: white; text-align: center; height: 150px;">
            <h3>3</h3>
            <p><strong>What should we fix next?</strong></p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    st.subheader("How to Use This Dashboard")
    
    tab1, tab2, tab3, tab4 = st.tabs(["Executive Summary", "Release Health", "Priority Roadmap", "Theme Deep Dive"])
    
    with tab1:
        st.markdown("""
        **Executive Summary** provides a high-level snapshot of the latest release:
        - Overall user pain metrics
        - Key performance indicators
        - Quick health assessment
        """)
    
    with tab2:
        st.markdown("""
        **Release Health** offers diagnostic views:
        - Pain concentration by version
        - Theme-level breakdown
        - Version-over-version comparisons
        """)
    
    with tab3:
        st.markdown("""
        **Priority Roadmap** helps with decision-making:
        - RICE-style prioritization scoring
        - Effort vs. impact analysis
        - Regression and persistence flags
        """)
    
    with tab4:
        st.markdown("""
        **Theme Deep Dive** validates insights with evidence:
        - Raw user feedback samples
        - High-impact review exploration
        - Contextual user quotes
        """)
    
    st.markdown("---")
    st.markdown("""
    > **Design Principle:** *Context first, diagnosis next, decisions last.*
    """)

# ============================
# 3. EXECUTIVE SUMMARY
# ============================
elif page == "Executive Summary":
    st.title("Executive Summary")
    
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

# ============================
# 4. RELEASE HEALTH
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

# ============================
# 5. PRIORITY ROADMAP
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
    
    st.markdown("""
    ---
    **How to interpret this table:**
    - **Higher score** → Higher priority
    - **Low effort + persistent pain** → Fastest wins
    - **Regression flags** indicate release risk requiring immediate attention
    """)

# ============================
# 6. TREND ANALYSIS
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
    else:
        st.warning("Please select at least one theme to view trends.")

# ============================
# 7. THEME DEEP DIVE
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
    
    # Top reviews
    num_reviews = st.slider("Number of reviews to display", 5, 20, 10)
    
    st.subheader(f"Top {num_reviews} High-Impact Reviews")
    
    if len(deep_dive) > 0:
        for idx, row in deep_dive.head(num_reviews).iterrows():
            rating = int(row["score"])
            weight = row["final_weight"]
            
            with st.expander(f"Rating: {rating}/5 — Pain Weight: {weight:.2f}"):
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
