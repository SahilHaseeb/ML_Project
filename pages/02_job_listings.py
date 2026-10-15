"""
pages/02_job_listings.py — Browsable Job Listings Table
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
import pandas as pd
from app import load_data

st.set_page_config(page_title="Job Listings | Pakistan AI Jobs", page_icon="💼", layout="wide")

# Re-apply base styles (imported from app via shared CSS in .streamlit/config.toml)
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

st.markdown('<div class="sample-banner">⚠️ <strong>SAMPLE DATA</strong> — 50 synthetic job listings for demonstration only.</div>', unsafe_allow_html=True)
st.title("💼 Job Listings")
st.markdown("Browse, search, and filter the collected job listings. Use the sidebar filters to narrow down results.")

df, _ = load_data()

# ── Sidebar filters ────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🔍 Filters")
    
    categories = ["All"] + sorted(df["category"].dropna().unique().tolist())
    selected_cat = st.selectbox("Category", categories)

    cities = ["All"] + sorted(df["location"].dropna().unique().tolist())
    selected_city = st.selectbox("City / Location", cities)

    job_types = ["All"] + sorted(df["job_type"].dropna().unique().tolist())
    selected_type = st.selectbox("Job Type", job_types)

    search_term = st.text_input("🔎 Search title or skills", placeholder="e.g. Python, ML, DevOps")

# ── Apply filters ──────────────────────────────────────────────────────────────
filtered = df.copy()

if selected_cat != "All":
    filtered = filtered[filtered["category"] == selected_cat]

if selected_city != "All":
    filtered = filtered[filtered["location"] == selected_city]

if selected_type != "All":
    filtered = filtered[filtered["job_type"] == selected_type]

if search_term:
    mask = (
        filtered["title"].str.contains(search_term, case=False, na=False) |
        filtered["skills"].str.contains(search_term, case=False, na=False) |
        filtered["description"].str.contains(search_term, case=False, na=False)
    )
    filtered = filtered[mask]

# ── Results count ──────────────────────────────────────────────────────────────
st.markdown(f"**{len(filtered)}** listing(s) match your filters.")

if filtered.empty:
    st.info("No jobs match the current filters. Try adjusting the sidebar options.")
else:
    # ── Display table ──────────────────────────────────────────────────────────
    display_cols = ["title", "company", "location", "category", "job_type",
                    "experience_min", "experience_max", "salary_min", "salary_max",
                    "salary_currency", "skills", "posting_date"]
    available_cols = [c for c in display_cols if c in filtered.columns]

    st.dataframe(
        filtered[available_cols].reset_index(drop=True),
        use_container_width=True,
        height=500,
        column_config={
            "title": st.column_config.TextColumn("Job Title", width="medium"),
            "company": st.column_config.TextColumn("Company", width="medium"),
            "location": st.column_config.TextColumn("Location"),
            "category": st.column_config.TextColumn("Category"),
            "job_type": st.column_config.TextColumn("Type"),
            "experience_min": st.column_config.NumberColumn("Exp Min (yrs)", format="%.0f"),
            "experience_max": st.column_config.NumberColumn("Exp Max (yrs)", format="%.0f"),
            "salary_min": st.column_config.NumberColumn("Salary Min", format="%,.0f"),
            "salary_max": st.column_config.NumberColumn("Salary Max", format="%,.0f"),
            "salary_currency": st.column_config.TextColumn("Currency"),
            "skills": st.column_config.TextColumn("Skills", width="large"),
            "posting_date": st.column_config.DateColumn("Posted"),
        },
    )

    # ── Selected row detail ────────────────────────────────────────────────────
    st.divider()
    st.markdown("### 📄 Job Detail")
    selected_title = st.selectbox(
        "Select a job to view full description:",
        filtered["title"].tolist(),
    )
    if selected_title:
        row = filtered[filtered["title"] == selected_title].iloc[0]
        c1, c2, c3 = st.columns(3)
        c1.markdown(f"**Company:** {row.get('company', 'N/A')}")
        c1.markdown(f"**Location:** {row.get('location', 'N/A')}")
        c2.markdown(f"**Category:** {row.get('category', 'N/A')}")
        c2.markdown(f"**Job Type:** {row.get('job_type', 'N/A')}")
        c3.markdown(f"**Experience:** {row.get('experience_min', '?')} – {row.get('experience_max', '?')} yrs")
        sal_min = row.get("salary_min")
        sal_max = row.get("salary_max")
        if pd.notna(sal_min):
            c3.markdown(f"**Salary:** {int(sal_min):,} – {int(sal_max):,} {row.get('salary_currency', '')}")
        else:
            c3.markdown("**Salary:** Not disclosed")
        
        st.markdown("**Skills Required:**")
        if pd.notna(row.get("skills")):
            for skill in str(row["skills"]).split("|"):
                st.badge(skill.strip(), color="blue")
        
        st.markdown("**Description:**")
        st.markdown(f"> {row.get('description', 'No description available.')}")
