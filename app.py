"""
app.py — Pakistan AI Job Market Intelligence Platform
=======================================================
This is the main entry point for the Streamlit application.
It sets up the page configuration, loads the data once (cached),
and provides a styled sidebar that links to all pages.

How Streamlit multi-page apps work:
  - app.py is the "home shell" (landing page + shared config)
  - Files inside pages/ are automatically detected as extra pages
  - Users navigate between pages via the sidebar
"""

import sys
import os

# Make sure Python can find the src/ modules from any directory
sys.path.insert(0, os.path.dirname(__file__))

import logging
import streamlit as st
import pandas as pd

from src.data_processing.cleaner import clean_pipeline

# ── Logging setup ──────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

# ── Page configuration (must be the FIRST Streamlit call) ─────────────────────
st.set_page_config(
    page_title="Pakistan AI Job Market Intelligence",
    page_icon="🇵🇰",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "About": "Pakistan AI Job Market Intelligence Platform — Phase 1 (Sample Data)",
    },
)

# ── Custom CSS — dark tech dashboard theme ─────────────────────────────────────
st.markdown("""
<style>
    /* Google Font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* Main background */
    .stApp {
        background: linear-gradient(135deg, #0A0E1A 0%, #0D1421 50%, #0A0E1A 100%);
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #111827 0%, #0D1421 100%);
        border-right: 1px solid #1E293B;
    }

    /* KPI metric cards */
    [data-testid="stMetric"] {
        background: linear-gradient(135deg, #111827, #1E293B);
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 1rem 1.2rem;
        box-shadow: 0 4px 20px rgba(0, 212, 255, 0.05);
    }
    [data-testid="stMetricValue"] {
        font-size: 2rem !important;
        font-weight: 700 !important;
        color: #00D4FF !important;
    }
    [data-testid="stMetricLabel"] {
        font-size: 0.8rem !important;
        color: #94A3B8 !important;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    /* Section headers */
    h1 { color: #F1F5F9 !important; font-weight: 700 !important; }
    h2 { color: #E2E8F0 !important; font-weight: 600 !important; }
    h3 { color: #CBD5E1 !important; font-weight: 600 !important; }

    /* Data table */
    [data-testid="stDataFrame"] {
        border: 1px solid #1E293B;
        border-radius: 8px;
    }

    /* Info / warning banners */
    .stAlert {
        border-radius: 8px !important;
    }

    /* Dividers */
    hr { border-color: #1E293B !important; }

    /* Tabs */
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        color: #94A3B8;
    }
    .stTabs [aria-selected="true"] {
        color: #00D4FF !important;
        border-bottom: 2px solid #00D4FF !important;
    }

    /* Sample data banner */
    .sample-banner {
        background: linear-gradient(90deg, #1E3A5F, #1B2D4F);
        border: 1px solid #2563EB;
        border-radius: 8px;
        padding: 0.75rem 1rem;
        font-size: 0.85rem;
        color: #93C5FD;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)


# ── Cached data loader — only runs once per session ────────────────────────────
@st.cache_data(ttl=300, show_spinner="Loading job data …")
def _load_dataset_cached(dataset_choice: str) -> tuple[pd.DataFrame, dict]:
    """
    Load and clean the requested job dataset.
    Caches results for 300 seconds per dataset choice.
    """
    root = os.path.dirname(__file__)
    if dataset_choice == "real":
        real_path = os.path.join(root, "data", "processed", "cleaned_jobs.csv")
        if os.path.exists(real_path) and os.path.getsize(real_path) > 0:
            df = pd.read_csv(real_path, low_memory=False)
            df["posting_date"] = pd.to_datetime(df["posting_date"], errors="coerce")
            df["scraped_at"] = pd.to_datetime(df["scraped_at"], errors="coerce")
            from src.data_processing.validators import generate_quality_report
            report = generate_quality_report(df)
            return df, report

    # Default to Phase 1 sample data
    sample_path = os.path.join(root, "data", "sample", "sample_jobs.csv")
    raw_df = pd.read_csv(sample_path, low_memory=False)
    clean_df, report = clean_pipeline(raw_df)
    return clean_df, report


def load_data(dataset_choice: str | None = None) -> tuple[pd.DataFrame, dict]:
    """
    Main data loader interface used by all dashboard pages.
    Detects dataset from session_state or parameter.
    """
    if dataset_choice is None:
        dataset_choice = st.session_state.get("selected_dataset", "real")
    return _load_dataset_cached(dataset_choice)


# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='text-align:center; padding: 1rem 0 0.5rem 0;'>
        <div style='font-size:2rem'>🇵🇰</div>
        <div style='font-size:1rem; font-weight:700; color:#00D4FF; letter-spacing:0.03em;'>
            Pakistan AI Jobs
        </div>
        <div style='font-size:0.7rem; color:#64748B; margin-top:2px;'>
            Market Intelligence Platform
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.divider()

    # ── Dataset Selector (Phase 2 requirement: keep sample and real data separate)
    real_csv = os.path.join(os.path.dirname(__file__), "data", "processed", "cleaned_jobs.csv")
    has_real = os.path.exists(real_csv) and os.path.getsize(real_csv) > 0

    st.markdown("**📁 Data Source**")
    options = []
    if has_real:
        options.append("🌐 Real Cleaned Jobs (Phase 2)")
    options.append("🔬 Phase 1 Sample (50 jobs)")

    curr_choice = st.session_state.get("selected_dataset", "real" if has_real else "sample")
    default_idx = 0 if (has_real and curr_choice == "real") else (len(options) - 1)

    chosen_label = st.selectbox(
        "Select Active Dataset",
        options,
        index=default_idx,
        label_visibility="collapsed",
        key="dataset_selector_dropdown",
    )
    st.session_state["selected_dataset"] = "real" if "Real" in chosen_label else "sample"
    st.divider()

    st.markdown("**📊 Navigation**")
    st.page_link("app.py",                          label="🏠  Home / Overview",       icon=None)
    st.page_link("pages/02_job_listings.py",         label="💼  Job Listings",           icon=None)
    st.page_link("pages/03_skills_analysis.py",      label="🔧  Skills Analysis",        icon=None)
    st.page_link("pages/04_location_analysis.py",    label="📍  Location Analysis",      icon=None)
    st.page_link("pages/05_salary_analysis.py",      label="💰  Salary Analysis",        icon=None)
    st.page_link("pages/06_experience_analysis.py",  label="📈  Experience Analysis",    icon=None)
    st.page_link("pages/07_historical_trends.py",    label="📅  Historical Trends",      icon=None)

    st.divider()
    st.markdown("**🤖 AI Features (Planned)**")
    st.page_link("pages/08_ai_classifier.py",        label="🧠  AI Job Classifier",      icon=None)
    st.page_link("pages/09_skill_gap.py",            label="🎯  Skill Gap Analyzer",     icon=None)

    st.divider()
    st.page_link("pages/10_about.py",                label="ℹ️  About / Data Sources",   icon=None)

    st.divider()
    if st.session_state["selected_dataset"] == "real":
        st.markdown(
            "<div style='font-size:0.7rem; color:#10B981; text-align:center;'>"
            "✅ Phase 2 Active — Real Data<br>"
            "Permitted APIs (Remotive / Arbeitnow)"
            "</div>",
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            "<div style='font-size:0.7rem; color:#F59E0B; text-align:center;'>"
            "🔬 Phase 1 — Sample Demo Data<br>"
            "50 synthetic demonstration listings."
            "</div>",
            unsafe_allow_html=True,
        )


# ── Home page content ──────────────────────────────────────────────────────────
def render_home():
    # Load data
    df, quality_report = load_data()

    # Dynamic banner based on active dataset
    if st.session_state.get("selected_dataset") == "real":
        st.markdown("""
        <div style="background: linear-gradient(90deg, #064E3B, #065F46); border: 1px solid #10B981; border-radius: 8px; padding: 0.75rem 1rem; font-size: 0.85rem; color: #A7F3D0; margin-bottom: 1rem;">
            ✅ <strong>REAL COLLECTED DATA (Phase 2):</strong> Viewing cleaned listings from permitted public APIs
            (Remotive API & Arbeitnow API). Pakistan-eligible worldwide remote and domestic roles are strictly categorized.
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="sample-banner">
            🔬 <strong>SAMPLE DATA NOTICE:</strong> Currently viewing <strong>50 synthetic demonstration job listings</strong>.
            Switch to <strong>Real Cleaned Jobs</strong> in the sidebar to view live collected data.
        </div>
        """, unsafe_allow_html=True)

    # Hero header
    st.markdown("""
    <div style='margin-bottom: 2rem;'>
        <h1 style='font-size:2.2rem; margin-bottom:0.3rem;'>
            🇵🇰 Pakistan AI Job Market Intelligence
        </h1>
        <p style='color:#94A3B8; font-size:1rem; margin:0;'>
            Analyzing technology job listings to help students, job seekers,
            and researchers understand the tech hiring landscape.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # ── KPI Cards ──────────────────────────────────────────────────────────────
    from src.analytics.overview import get_summary_stats
    stats = get_summary_stats(df)

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("📋 Total Listings",    stats["total_jobs"])
    c2.metric("🏢 Companies",          stats["unique_companies"])
    c3.metric("📍 Cities",             stats["unique_cities"])
    c4.metric("🗂️  Categories",        stats["unique_categories"])
    c5.metric("💰 Salary Disclosed",   f"{stats['salary_disclosure_rate']}%")

    st.divider()

    # ── Charts row ─────────────────────────────────────────────────────────────
    import plotly.express as px

    col_left, col_right = st.columns([1, 1], gap="large")

    with col_left:
        st.subheader("🗂️ Jobs by Category")
        from src.analytics.overview import get_top_categories
        cat_df = get_top_categories(df, n=10)
        if not cat_df.empty:
            fig = px.bar(
                cat_df,
                x="count", y="category",
                orientation="h",
                color="count",
                color_continuous_scale=["#1E3A5F", "#00D4FF"],
                labels={"count": "Job Listings", "category": ""},
                template="plotly_dark",
            )
            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                coloraxis_showscale=False,
                margin=dict(l=0, r=0, t=10, b=0),
                height=380,
            )
            fig.update_traces(marker_line_width=0)
            st.plotly_chart(fig, use_container_width=True)

    with col_right:
        st.subheader("📍 Jobs by City")
        from src.analytics.location import get_jobs_by_city
        city_df = get_jobs_by_city(df)
        if not city_df.empty:
            fig2 = px.pie(
                city_df.head(8),
                names="location",
                values="count",
                color_discrete_sequence=px.colors.sequential.Blues_r,
                template="plotly_dark",
                hole=0.45,
            )
            fig2.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                legend=dict(font=dict(size=11), bgcolor="rgba(0,0,0,0)"),
                margin=dict(l=0, r=0, t=10, b=0),
                height=380,
            )
            fig2.update_traces(textfont_size=11)
            st.plotly_chart(fig2, use_container_width=True)

    st.divider()

    # ── Top skills bar ─────────────────────────────────────────────────────────
    st.subheader("🔧 Top In-Demand Skills")
    from src.analytics.skills import get_top_skills
    skill_df = get_top_skills(df, n=15)
    if not skill_df.empty:
        fig3 = px.bar(
            skill_df,
            x="skill", y="count",
            color="count",
            color_continuous_scale=["#1E3A5F", "#00D4FF", "#38BDF8"],
            labels={"count": "# Job Listings", "skill": "Skill"},
            template="plotly_dark",
        )
        fig3.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            coloraxis_showscale=False,
            margin=dict(l=0, r=0, t=10, b=0),
            height=330,
            xaxis_tickangle=-35,
        )
        fig3.update_traces(marker_line_width=0)
        st.plotly_chart(fig3, use_container_width=True)

    st.divider()

    # ── Data quality summary ───────────────────────────────────────────────────
    with st.expander("📊 Data Quality Report — click to expand"):
        st.markdown(f"""
        **Total rows after cleaning:** {quality_report['total_rows']}

        Below is the completeness (non-null percentage) of each field.
        Fields with low completeness are normal — for example, salary is optional
        in many job postings.
        """)
        qr_df = pd.DataFrame({
            "Field": list(quality_report["completeness_pct"].keys()),
            "Completeness %": list(quality_report["completeness_pct"].values()),
            "Missing Count": list(quality_report["missing_values"].values()),
        })
        st.dataframe(qr_df, use_container_width=True, hide_index=True)

    # ── Date range footer ──────────────────────────────────────────────────────
    if stats["date_range_start"] and stats["date_range_end"]:
        st.caption(
            f"📅 Data covers: **{stats['date_range_start']}** → **{stats['date_range_end']}**  |  "
            f"Source: Sample CSV  |  Phase 1 of 9"
        )


if __name__ == "__main__" or True:
    render_home()
