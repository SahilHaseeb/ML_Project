"""
pages/08_ai_classifier.py — AI Job Classifier (Placeholder)
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st

st.set_page_config(page_title="AI Classifier | Pakistan AI Jobs", page_icon="🧠", layout="wide")
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

st.title("🧠 AI Job Classifier")

st.markdown("""
<div class="placeholder-card">
    <div style='font-size:4rem; margin-bottom:1rem;'>🚧</div>
    <h2 style='color:#94A3B8; margin-bottom:0.5rem;'>Coming in Phase 6</h2>
    <p style='color:#64748B; font-size:1rem; max-width:600px; margin:0 auto;'>
        The AI Job Classifier will automatically categorize a job title or description
        into the correct technology category (e.g., "Data Science", "DevOps", "Mobile Development").
    </p>
</div>
""", unsafe_allow_html=True)

st.markdown("### 📋 What this feature will do")
col1, col2 = st.columns(2)
with col1:
    st.markdown("""
    **Input (what you provide):**
    - Job title
    - Job description text
    - Required skills list
    """)
with col2:
    st.markdown("""
    **Output (what the model predicts):**
    - Predicted job category
    - Confidence score
    - Similar job listings from the dataset
    """)

st.markdown("### 🛠️ Technical Plan")
st.markdown("""
| Step | What we'll do |
|------|--------------|
| 1 | Collect enough labeled job listings (Phase 4) |
| 2 | Vectorize job descriptions using TF-IDF (Scikit-learn) |
| 3 | Train a classification model (Logistic Regression / SVM) |
| 4 | Evaluate with precision, recall, F1 score |
| 5 | Only deploy if accuracy meets our threshold |
| 6 | Optionally upgrade to BERT embeddings (Phase 7) |
""")

st.info("**Why is this not built yet?** Training a classifier on made-up sample data would produce meaningless results. We need real job listings first (Phase 4) before we can train and evaluate a model honestly.")

st.markdown("### 🎭 Preview (UI prototype only — no real model)")
with st.form("classifier_demo"):
    st.text_input("Job Title", placeholder="e.g. Senior Python Developer", disabled=True)
    st.text_area("Job Description", placeholder="Paste a job description here…", disabled=True)
    st.form_submit_button("🔮 Classify Job", disabled=True)
st.caption("This form is disabled. It will become functional in Phase 6.")
