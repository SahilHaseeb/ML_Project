"""
pages/06_experience_analysis.py — Experience Level Analysis
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
import plotly.express as px
from app import load_data
from src.analytics.experience import get_experience_distribution, get_avg_experience_by_category, get_experience_vs_salary

st.set_page_config(page_title="Experience Analysis | Pakistan AI Jobs", page_icon="📈", layout="wide")
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

st.markdown('<div class="sample-banner">⚠️ <strong>SAMPLE DATA</strong> — Experience levels are illustrative only.</div>', unsafe_allow_html=True)
st.title("📈 Experience Analysis")
st.markdown("Understand how much experience employers typically require, broken down by job category.")

df, _ = load_data()

col1, col2 = st.columns(2, gap="large")

with col1:
    st.subheader("🎓 Experience Level Distribution")
    exp_df = get_experience_distribution(df)
    if not exp_df.empty:
        fig = px.pie(
            exp_df,
            names="level", values="count",
            color_discrete_sequence=["#00D4FF", "#0EA5E9", "#2563EB", "#1D4ED8", "#1E3A5F", "#475569"],
            template="plotly_dark", hole=0.4,
        )
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(size=11)),
            height=380, margin=dict(l=0, r=0, t=10, b=0),
        )
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(exp_df.rename(columns={"level": "Experience Level", "count": "# Listings"}),
                     use_container_width=True, hide_index=True)

with col2:
    st.subheader("🏆 Avg Experience Required by Category")
    avg_exp = get_avg_experience_by_category(df)
    if not avg_exp.empty:
        fig2 = px.bar(
            avg_exp.sort_values("avg_experience_years"),
            x="avg_experience_years", y="category",
            orientation="h",
            color="avg_experience_years",
            color_continuous_scale=["#1B2D4F", "#7C3AED", "#A78BFA"],
            text=avg_exp.sort_values("avg_experience_years")["avg_experience_years"].apply(lambda x: f"{x} yrs"),
            labels={"avg_experience_years": "Avg Years Required", "category": ""},
            template="plotly_dark",
        )
        fig2.update_traces(textposition="outside", marker_line_width=0)
        fig2.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            coloraxis_showscale=False, height=420,
            margin=dict(l=0, r=60, t=10, b=0),
        )
        st.plotly_chart(fig2, use_container_width=True)

st.divider()

st.subheader("🔗 Experience vs Salary (Scatter)")
st.markdown("Each dot is one job listing. Hover to see the title and company.")
scatter_df = get_experience_vs_salary(df)
if not scatter_df.empty:
    fig3 = px.scatter(
        scatter_df,
        x="experience_min",
        y="salary_min",
        color="category",
        hover_data=["title", "company"],
        labels={"experience_min": "Min Experience (yrs)", "salary_min": "Min Salary (PKR)"},
        template="plotly_dark",
        size_max=12,
    )
    fig3.update_traces(marker=dict(size=10, opacity=0.85, line=dict(width=0)))
    fig3.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(17,24,39,0.6)",
        height=420, margin=dict(l=0, r=0, t=10, b=0),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(size=10)),
    )
    st.plotly_chart(fig3, use_container_width=True)
    st.caption("Note: Only listings where both experience and salary are disclosed are shown.")
else:
    st.info("Not enough data to draw a scatter chart (requires both experience and salary).")
