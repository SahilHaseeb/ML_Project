"""
pages/09_skill_gap.py — Skill Gap Analyzer (Placeholder)
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st

st.set_page_config(page_title="Skill Gap Analyzer | Pakistan AI Jobs", page_icon="🎯", layout="wide")
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.stApp { background: linear-gradient(135deg, #0A0E1A, #0D1421); }
[data-testid="stSidebar"] { background: linear-gradient(180deg, #111827, #0D1421); }
.placeholder-card {
    background: linear-gradient(135deg, #111827, #1E293B);
    border: 2px dashed #334155;
    border-radius: 16px;
    padding: 3rem 2rem;
    text-align: center;
    margin: 2rem 0;
}
</style>
""", unsafe_allow_html=True)

st.title("🎯 Skill Gap Analyzer")

st.markdown("""
<div class="placeholder-card">
    <div style='font-size:4rem; margin-bottom:1rem;'>🚧</div>
    <h2 style='color:#94A3B8; margin-bottom:0.5rem;'>Coming in Phase 6</h2>
    <p style='color:#64748B; font-size:1rem; max-width:600px; margin:0 auto;'>
        Enter your current skills and your target job role.
        The Skill Gap Analyzer will compare your profile against real job requirements
        and tell you exactly which skills to learn next.
    </p>
</div>
""", unsafe_allow_html=True)

st.markdown("### 📋 How it will work")
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("""
    **Step 1 — Your Profile**
    Enter the skills you currently have from a searchable checklist.
    """)
with col2:
    st.markdown("""
    **Step 2 — Your Target Role**
    Select a job category or a specific job title you are aiming for.
    """)
with col3:
    st.markdown("""
    **Step 3 — Your Gap Report**
    See which skills appear in job listings for your target role that you currently lack.
    """)

st.markdown("### 🎭 Preview (UI prototype only)")
with st.form("gap_demo"):
    st.multiselect("Your current skills:", ["Python", "SQL", "Excel", "Power BI"], disabled=True)
    st.selectbox("Target job category:", ["Data Science", "Machine Learning", "DevOps"], disabled=True)
    st.form_submit_button("🔍 Analyze My Skill Gap", disabled=True)
st.caption("This form is disabled. It will become functional once real job data is available.")

st.info("**Why not now?** The skill gap report needs to be based on real, verified job requirements. Using synthetic sample data would give misleading advice to students and job seekers.")
