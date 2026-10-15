"""
pages/04_location_analysis.py — Location / City Analysis Dashboard
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
import plotly.express as px
from app import load_data
from src.analytics.location import get_jobs_by_city, get_remote_vs_onsite, get_top_cities, get_categories_by_city

st.set_page_config(page_title="Location Analysis | Pakistan AI Jobs", page_icon="📍", layout="wide")
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

st.markdown('<div class="sample-banner">⚠️ <strong>SAMPLE DATA</strong> — Geographic distribution is illustrative only.</div>', unsafe_allow_html=True)
st.title("📍 Location Analysis")
st.markdown("Understand how job listings are distributed across Pakistani cities and work modes.")

df, _ = load_data()

# ── KPIs ───────────────────────────────────────────────────────────────────────
city_df = get_jobs_by_city(df)
top_city = city_df.iloc[0]["location"] if not city_df.empty else "N/A"
top_city_count = city_df.iloc[0]["count"] if not city_df.empty else 0
remote_jobs = df[df["location"] == "Remote"].shape[0]

c1, c2, c3 = st.columns(3)
c1.metric("🏙️ Top City", top_city, f"{top_city_count} listings")
c2.metric("📍 Cities Represented", city_df[~city_df["location"].isin(["Remote","Hybrid"])]["location"].nunique())
c3.metric("🏠 Remote Listings", remote_jobs)

st.divider()

col1, col2 = st.columns([1.2, 1], gap="large")

with col1:
    st.subheader("🏙️ Job Listings by City")
    top_cities = get_top_cities(df, n=10)
    if not top_cities.empty:
        fig = px.bar(
            top_cities.sort_values("count"),
            x="count", y="location",
            orientation="h",
            color="count",
            color_continuous_scale=["#1B2D4F", "#0EA5E9", "#00D4FF"],
            text="count",
            labels={"count": "# Listings", "location": ""},
            template="plotly_dark",
        )
        fig.update_traces(textposition="outside", marker_line_width=0)
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            coloraxis_showscale=False, height=380,
            margin=dict(l=0, r=60, t=10, b=0),
        )
        st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("🏠 Remote vs On-site vs Hybrid")
    mode_df = get_remote_vs_onsite(df)
    if not mode_df.empty:
        fig2 = px.pie(
            mode_df,
            names="work_mode",
            values="count",
            color_discrete_map={
                "On-site": "#0EA5E9",
                "Remote": "#00D4FF",
                "Hybrid": "#2563EB",
                "Unknown": "#475569",
            },
            template="plotly_dark",
            hole=0.5,
        )
        fig2.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            legend=dict(bgcolor="rgba(0,0,0,0)"),
            height=380,
            margin=dict(l=0, r=0, t=10, b=0),
        )
        st.plotly_chart(fig2, use_container_width=True)

st.divider()

# ── Per-city category breakdown ────────────────────────────────────────────────
st.subheader("🗂️ Job Categories by City")
all_cities = sorted(df["location"].dropna().unique().tolist())
selected_city = st.selectbox("Select a city:", all_cities)
cat_for_city = get_categories_by_city(df, selected_city)
if not cat_for_city.empty:
    fig3 = px.bar(
        cat_for_city,
        x="category", y="count",
        color="count",
        color_continuous_scale=["#1B2D4F", "#00D4FF"],
        labels={"count": "# Listings", "category": "Category"},
        template="plotly_dark",
        title=f"Categories in {selected_city}",
    )
    fig3.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        coloraxis_showscale=False, height=350,
        margin=dict(l=0, r=0, t=40, b=0), xaxis_tickangle=-30,
    )
    st.plotly_chart(fig3, use_container_width=True)
else:
    st.info(f"No category data available for {selected_city}.")

# ── Full city table ────────────────────────────────────────────────────────────
with st.expander("📋 Full City Distribution Table"):
    st.dataframe(
        city_df.rename(columns={"location": "Location", "count": "Listings", "percentage": "% Share"}),
        use_container_width=True, hide_index=True,
    )
