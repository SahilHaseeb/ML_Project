"""
pages/05_salary_analysis.py — Salary Analysis Dashboard
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
import plotly.express as px
from app import load_data
from src.analytics.salary import get_salary_coverage, get_salary_stats_by_category, get_salary_distribution, get_salary_by_experience

st.set_page_config(page_title="Salary Analysis | Pakistan AI Jobs", page_icon="💰", layout="wide")
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

st.markdown('<div class="sample-banner">⚠️ <strong>SAMPLE DATA</strong> — Salary figures are synthetic. Do not use for real financial decisions.</div>', unsafe_allow_html=True)
st.title("💰 Salary Analysis")
st.markdown("Explore salary ranges across job categories and experience levels (PKR unless noted).")

df, _ = load_data()

# ── Salary coverage warning ────────────────────────────────────────────────────
coverage = get_salary_coverage(df)
st.info(
    f"ℹ️ **Salary data coverage:** {coverage['disclosed']} of {coverage['total']} listings "
    f"({coverage['rate_pct']}%) disclose a salary range. "
    f"Statistics below are based only on listings where salary was provided."
)

# ── KPIs ───────────────────────────────────────────────────────────────────────
dist = get_salary_distribution(df)
if not dist.empty:
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("📉 Min Salary (PKR)", f"{int(dist.min()):,}")
    c2.metric("📈 Max Salary (PKR)", f"{int(dist.max()):,}")
    c3.metric("📊 Median Salary (PKR)", f"{int(dist.median()):,}")
    c4.metric("💰 Listings with Salary", coverage["disclosed"])
else:
    st.warning("No PKR salary data available.")

st.divider()

tab1, tab2, tab3 = st.tabs(["📊 By Category", "📈 Distribution", "🔗 Experience vs Salary"])

with tab1:
    cat_salary = get_salary_stats_by_category(df)
    if not cat_salary.empty:
        fig = px.bar(
            cat_salary.sort_values("median_salary"),
            x="median_salary", y="category",
            orientation="h",
            color="median_salary",
            color_continuous_scale=["#1B2D4F", "#16A34A", "#4ADE80"],
            text=cat_salary.sort_values("median_salary")["median_salary"].apply(lambda x: f"PKR {x:,.0f}"),
            labels={"median_salary": "Median Salary (PKR)", "category": ""},
            template="plotly_dark",
        )
        fig.update_traces(textposition="outside", marker_line_width=0)
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            coloraxis_showscale=False, height=420,
            margin=dict(l=0, r=160, t=10, b=0),
        )
        st.plotly_chart(fig, use_container_width=True)
        
        st.dataframe(
            cat_salary.rename(columns={
                "category": "Category",
                "median_salary": "Median Salary",
                "min_salary": "Min Salary",
                "max_salary": "Max Salary",
                "job_count": "# Listings",
            }),
            use_container_width=True, hide_index=True,
        )
    else:
        st.info("No salary data by category available.")

with tab2:
    if not dist.empty:
        fig2 = px.histogram(
            dist,
            nbins=15,
            labels={"value": "Salary (PKR)", "count": "# Listings"},
            template="plotly_dark",
            color_discrete_sequence=["#00D4FF"],
        )
        fig2.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            height=380, margin=dict(l=0, r=0, t=10, b=0),
            bargap=0.05,
        )
        st.plotly_chart(fig2, use_container_width=True)
        
        st.markdown(
            f"**Distribution of disclosed minimum salaries (PKR).** "
            f"Only {coverage['disclosed']} listings included."
        )
    else:
        st.info("Not enough salary data for a distribution chart.")

with tab3:
    from src.analytics.salary import get_salary_by_experience
    exp_sal = get_salary_by_experience(df)
    if not exp_sal.empty:
        fig3 = px.bar(
            exp_sal,
            x="exp_bucket", y="median_salary",
            color="median_salary",
            color_continuous_scale=["#1B2D4F", "#16A34A", "#4ADE80"],
            text=exp_sal["median_salary"].apply(lambda x: f"PKR {x:,.0f}"),
            labels={"exp_bucket": "Experience Level", "median_salary": "Median Salary (PKR)"},
            template="plotly_dark",
        )
        fig3.update_traces(textposition="outside", marker_line_width=0)
        fig3.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            coloraxis_showscale=False, height=380,
            margin=dict(l=0, r=0, t=10, b=80),
        )
        st.plotly_chart(fig3, use_container_width=True)
    else:
        st.info("Not enough data to show the salary-experience relationship.")
