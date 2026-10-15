"""
pages/07_historical_trends.py — Historical Trends
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
import plotly.express as px
from app import load_data
from src.analytics.trends import get_monthly_posting_trend, get_category_trend, get_skill_growth

st.set_page_config(page_title="Historical Trends | Pakistan AI Jobs", page_icon="📅", layout="wide")
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.stApp { background: linear-gradient(135deg, #0A0E1A, #0D1421); }
[data-testid="stSidebar"] { background: linear-gradient(180deg, #111827, #0D1421); }
.sample-banner { background:linear-gradient(90deg,#1E3A5F,#1B2D4F); border:1px solid #2563EB;
    border-radius:8px; padding:0.75rem 1rem; font-size:0.85rem; color:#93C5FD; margin-bottom:1rem; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="sample-banner">⚠️ <strong>SAMPLE DATA</strong> — Trends shown are from synthetic data and do not represent real market changes.</div>', unsafe_allow_html=True)
st.title("📅 Historical Trends")
st.markdown("Track how job postings and skill demand change over time.")

df, _ = load_data()

# ── Monthly posting trend ──────────────────────────────────────────────────────
st.subheader("📈 Monthly Job Posting Volume")
monthly = get_monthly_posting_trend(df)
if not monthly.empty:
    fig = px.area(
        monthly,
        x="month", y="count",
        labels={"month": "Month", "count": "# Listings"},
        template="plotly_dark",
        color_discrete_sequence=["#00D4FF"],
    )
    fig.update_traces(
        fill="tozeroy",
        fillcolor="rgba(0, 212, 255, 0.15)",
        line=dict(color="#00D4FF", width=2.5),
    )
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(17,24,39,0.6)",
        height=320, margin=dict(l=0, r=0, t=10, b=0),
        xaxis_tickangle=-30,
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No posting date data available.")

st.divider()

# ── Category trend ─────────────────────────────────────────────────────────────
st.subheader("🗂️ Job Postings by Category Over Time")
cat_trend = get_category_trend(df)
if not cat_trend.empty:
    # Let user filter to avoid overcrowding
    all_cats = sorted(cat_trend["category"].unique().tolist())
    selected_cats = st.multiselect(
        "Select categories to display:",
        all_cats,
        default=all_cats[:5],
    )
    filtered_trend = cat_trend[cat_trend["category"].isin(selected_cats)]
    if not filtered_trend.empty:
        fig2 = px.line(
            filtered_trend,
            x="month", y="count",
            color="category",
            markers=True,
            labels={"month": "Month", "count": "# Listings", "category": "Category"},
            template="plotly_dark",
        )
        fig2.update_traces(line=dict(width=2), marker=dict(size=7))
        fig2.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(17,24,39,0.6)",
            height=380, margin=dict(l=0, r=0, t=10, b=0),
            legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(size=10)),
            xaxis_tickangle=-30,
        )
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("Select at least one category above.")

st.divider()

# ── Skill growth tracker ───────────────────────────────────────────────────────
st.subheader("🔧 Track a Skill's Demand Over Time")
from src.analytics.skills import get_top_skills
top_skills = get_top_skills(df, n=30)["skill"].tolist()
selected_skill = st.selectbox("Select a skill to track:", top_skills)

if selected_skill:
    skill_trend = get_skill_growth(df, selected_skill)
    if not skill_trend.empty:
        fig3 = px.bar(
            skill_trend,
            x="month", y="count",
            color="count",
            color_continuous_scale=["#1B2D4F", "#0EA5E9", "#00D4FF"],
            labels={"month": "Month", "count": f"# Jobs mentioning {selected_skill}"},
            template="plotly_dark",
            title=f"Monthly demand for: {selected_skill}",
        )
        fig3.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(17,24,39,0.6)",
            coloraxis_showscale=False, height=320,
            margin=dict(l=0, r=0, t=40, b=0),
        )
        st.plotly_chart(fig3, use_container_width=True)
    else:
        st.info(f"No listings found mentioning '{selected_skill}' in the current dataset.")

st.caption("Tip: With real data over multiple months, these charts will show genuine market trends.")
