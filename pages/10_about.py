"""
pages/10_about.py — About the Project / Data Sources
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st

st.set_page_config(page_title="About | Pakistan AI Jobs", page_icon="ℹ️", layout="wide")
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.stApp { background: linear-gradient(135deg, #0A0E1A, #0D1421); }
[data-testid="stSidebar"] { background: linear-gradient(180deg, #111827, #0D1421); }
.info-card {
    background: linear-gradient(135deg, #111827, #1E293B);
    border: 1px solid #334155;
    border-radius: 12px;
    padding: 1.5rem;
    margin-bottom: 1rem;
}
</style>
""", unsafe_allow_html=True)

st.title("ℹ️ About the Project")

st.markdown("""
## Pakistan AI Job Market Intelligence Platform

This project was built as a university data science capstone to help students,
job seekers, and researchers understand technology hiring trends in Pakistan.

> **This platform does NOT claim to represent the complete Pakistan job market.**
> It only analyzes the specific datasets it has collected, from the specific sources
> and time periods listed below.
""")

st.divider()

col1, col2 = st.columns(2)

with col1:
    st.markdown("### 🛠️ Technology Stack")
    st.markdown("""
    | Tool | Purpose |
    |------|---------|
    | **Python** | Core language |
    | **Streamlit** | Web dashboard |
    | **Pandas / NumPy** | Data processing |
    | **Plotly** | Interactive charts |
    | **Scikit-learn** | ML (Phase 6+) |
    | **PostgreSQL** | Database (Phase 5+) |
    | **SQLAlchemy** | ORM layer |
    | **Requests / BS4** | Web scraping (Phase 4+) |
    """)

with col2:
    st.markdown("### 📅 Project Phases")
    st.markdown("""
    | Phase | Description | Status |
    |-------|-------------|--------|
    | 1 | Structure + sample data + basic dashboard | ✅ Complete |
    | 2 | Data validation & cleaning | 🔜 Next |
    | 3 | EDA & visualizations | 🔜 Planned |
    | 4 | Real data collection | 🔜 Planned |
    | 5 | PostgreSQL integration | 🔜 Planned |
    | 6 | Machine Learning | 🔜 Planned |
    | 7 | NLP & Deep Learning | 🔜 Planned |
    | 8 | Full integration | 🔜 Planned |
    | 9 | Testing & deployment | 🔜 Planned |
    """)

st.divider()

st.markdown("### 📊 Current Data Sources")

st.markdown("""
<div class="info-card">
<strong>Phase 1 — Synthetic Sample Dataset</strong><br>
<ul>
<li><strong>File:</strong> <code>data/sample/sample_jobs.csv</code></li>
<li><strong>Rows:</strong> 50 synthetic job listings</li>
<li><strong>Purpose:</strong> Dashboard development and demonstration only</li>
<li><strong>Real market coverage:</strong> None — data is invented for testing</li>
<li><strong>Collection date:</strong> Not applicable</li>
</ul>
</div>
""", unsafe_allow_html=True)

st.markdown("### 🔮 Planned Data Sources (Phase 4)")
st.markdown("""
| Source | Type | Notes |
|--------|------|-------|
| **Rozee.pk** | Job portal | Must verify robots.txt and ToS before scraping |
| **Mustakbil.com** | Job portal | Must verify permissions |
| **LinkedIn** | Job portal | API rate limits apply; may require paid access |
| **Government / PSEB** | Official data | Open data where available |

> ⚠️ **No real scraping is performed until each source's terms of service and
> robots.txt have been reviewed and documented.**
""")

st.divider()

st.markdown("### ⚠️ Limitations")
st.markdown("""
- Phase 1 uses **synthetic data** — do not make career or business decisions based on it.
- Salary and experience data may be incomplete even in real-world sources.
- Job listings may not cover all sectors, cities, or experience levels equally.
- The dataset represents only what employers chose to post publicly on the included sources.
- Duplicate detection is best-effort and may not catch all duplicates.
""")

st.markdown("### 📜 License & Ethics")
st.markdown("""
- This project is built for **educational purposes**.
- Only publicly available data from permitted sources will be collected.
- **No personal data** (candidate profiles, contact information) is stored.
- All scraping will comply with applicable website terms and local laws.
""")

st.divider()
st.caption("Pakistan AI Job Market Intelligence Platform — Phase 1 | Built with Streamlit + Python")
