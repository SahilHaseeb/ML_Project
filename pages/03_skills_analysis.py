"""
pages/03_skills_analysis.py — Skills Analysis Dashboard
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from app import load_data
from src.analytics.skills import get_top_skills, get_skills_by_category, get_unique_skill_count, get_skill_category_matrix

st.set_page_config(page_title="Skills Analysis | Pakistan AI Jobs", page_icon="🔧", layout="wide")

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

st.markdown('<div class="sample-banner">⚠️ <strong>SAMPLE DATA</strong> — 50 synthetic listings. Skill frequencies are illustrative only.</div>', unsafe_allow_html=True)
st.title("🔧 Skills Analysis")
st.markdown("Discover which technical skills appear most frequently in job listings.")

df, _ = load_data()

# KPI row
c1, c2, c3 = st.columns(3)
top_skills_df = get_top_skills(df, n=1)
top_skill = top_skills_df["skill"].iloc[0] if not top_skills_df.empty else "N/A"
c1.metric("🏆 Most Demanded Skill", top_skill)
c2.metric("🔢 Unique Skills Found", get_unique_skill_count(df))
c3.metric("📋 Listings Analyzed", len(df))

st.divider()

tab1, tab2, tab3 = st.tabs(["📊 Top Skills", "🗂️ Skills by Category", "🔥 Skill Heatmap"])

with tab1:
    n = st.slider("Show top N skills", min_value=5, max_value=30, value=20, step=1)
    skill_df = get_top_skills(df, n=n)
    if not skill_df.empty:
        fig = px.bar(
            skill_df.sort_values("count"),
            x="count", y="skill",
            orientation="h",
            color="count",
            color_continuous_scale=["#1E3A5F", "#0EA5E9", "#00D4FF"],
            text="count",
            labels={"count": "Job Listings", "skill": ""},
            template="plotly_dark",
        )
        fig.update_traces(textposition="outside", marker_line_width=0)
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            coloraxis_showscale=False, height=max(400, n * 28),
            margin=dict(l=0, r=60, t=10, b=0),
        )
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("**Percentage of listings requiring each skill:**")
        st.dataframe(skill_df.rename(columns={"skill":"Skill","count":"# Listings","percentage":"% of Jobs"}),
                     use_container_width=True, hide_index=True)

with tab2:
    categories = sorted(df["category"].dropna().unique().tolist())
    selected_cat = st.selectbox("Select Category", categories)
    cat_skills = get_skills_by_category(df, selected_cat, n=15)
    if not cat_skills.empty:
        fig2 = px.bar(
            cat_skills.sort_values("count"),
            x="count", y="skill",
            orientation="h",
            color="count",
            color_continuous_scale=["#1B2D4F", "#2563EB", "#60A5FA"],
            text="count",
            labels={"count": "# Listings", "skill": ""},
            template="plotly_dark",
            title=f"Top Skills in: {selected_cat}",
        )
        fig2.update_traces(textposition="outside", marker_line_width=0)
        fig2.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            coloraxis_showscale=False, height=400,
            margin=dict(l=0, r=60, t=40, b=0),
        )
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("No skill data available for this category.")

with tab3:
    st.markdown("Each cell shows how many jobs in that **category** require a given **skill**.")
    matrix = get_skill_category_matrix(df, top_n_skills=15)
    if not matrix.empty:
        fig3 = go.Figure(data=go.Heatmap(
            z=matrix.values,
            x=matrix.columns.tolist(),
            y=matrix.index.tolist(),
            colorscale=[[0, "#0A0E1A"], [0.3, "#1E3A5F"], [0.7, "#0EA5E9"], [1.0, "#00D4FF"]],
            showscale=True,
            hovertemplate="Category: %{y}<br>Skill: %{x}<br>Count: %{z}<extra></extra>",
        ))
        fig3.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            height=500,
            margin=dict(l=0, r=0, t=10, b=0),
            xaxis=dict(tickangle=-40),
        )
        st.plotly_chart(fig3, use_container_width=True)
    else:
        st.info("Not enough data to generate the heatmap.")
