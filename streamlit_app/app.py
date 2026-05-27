import streamlit as st
import os
import sys

# Set page config
st.set_page_config(
    page_title="CustomerIQ Analytics Platform",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom branding CSS
st.markdown("""
<style>
    .reportview-container {
        background: #0f172a;
    }
    .stMetric {
        background-color: #1e293b;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #334155;
    }
    .db-status-green {
        color: #10b981;
        font-weight: bold;
    }
    .db-status-red {
        color: #ef4444;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Add current path to sys.path
sys.path.append(os.path.dirname(__file__))

from utils.db import cached_query, get_engine
from utils.ml import load_ml_pipeline

st.title("CustomerIQ — Intelligent Segmentation & Analytics Platform")
st.subheader("Data Scientist & Analyst Workspace")

st.markdown("""
Welcome to the **CustomerIQ Analytics Workspace**. This interface connects directly to your 
production PostgreSQL/SQLite database to explore customer demographics, analyze behavior, run 
clustering ML pipelines, and export business reports.
""")

# Sidebar status cards
st.sidebar.image("https://img.icons8.com/clouds/100/database.png", width=80)
st.sidebar.markdown("### System Architecture Status")

# Check DB Connection
try:
    engine = get_engine()
    with engine.connect() as conn:
        db_status = "<span class='db-status-green'>● Connected</span>"
except Exception as e:
    db_status = f"<span class='db-status-red'>● Disconnected</span> ({str(e)})"
    
st.sidebar.markdown(f"**Database:** {db_status}", unsafe_allow_html=True)

# Get Row Counts
customer_count = 0
transaction_count = 0
if "Connected" in db_status:
    try:
        df_cust_count = cached_query("SELECT COUNT(*) as count FROM customers")
        df_tx_count = cached_query("SELECT COUNT(*) as count FROM transactions")
        customer_count = df_cust_count.iloc[0]["count"]
        transaction_count = df_tx_count.iloc[0]["count"]
    except Exception:
        pass

st.sidebar.write(f"- Customers: **{customer_count:,}**")
st.sidebar.write(f"- Transactions: **{transaction_count:,}**")

# Get Active Model
pipeline = load_ml_pipeline()
if pipeline:
    st.sidebar.markdown(f"**Active Model:** `{pipeline['algorithm'].upper()}`")
    st.sidebar.markdown(f"**Model Path:** `models/{pipeline['algorithm']}_model.pkl`")
else:
    st.sidebar.markdown("**Active Model:** *None (Train model in Model Studio)*")

# Page Content: Overview of available tabs
st.markdown("---")
st.markdown("### Workspace Navigation Directory")

col1, col2 = st.columns(2)

with col1:
    st.info("👈 Use the **sidebar sidebar** to navigate between pages:")
    st.markdown("""
    - **1_Overview:** High-level dashboard showing total revenue, segments distribution, and KPIs.
    - **2_EDA_Explorer:** Feature selector to analyze distributions and stats for demographic characteristics.
    - **3_Cluster_Explorer:** Interactive 2D/3D Plotly PCA projections of customer behavior.
    - **4_RFM_Analysis:** Multi-dimensional scatter plot comparing Recency, Frequency, and Monetary parameters.
    """)
    
with col2:
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
    - **5_Cohort_Analysis:** Cohort matrix retention percentages showing lifecycle decay values.
    - **6_Upload_Predict:** Batch segment customer lists from CSV file uploads.
    - **7_Model_Studio:** Trigger clustering algorithms (KMeans, DBSCAN, GMM) and evaluate metrics.
    - **8_Executive_Report:** PDF document compilation with business highlights.
    """)

# Display KPIs
st.markdown("### Core Analytics Snapshot")
if customer_count > 0:
    c1, c2, c3 = st.columns(3)
    
    # Calculate Total Revenue
    df_rev = cached_query("SELECT SUM(total_spend) as spend, AVG(clv_estimate) as clv FROM customers")
    total_spend = df_rev.iloc[0]["spend"] or 0.0
    avg_clv = df_rev.iloc[0]["clv"] or 0.0
    
    c1.metric("Total Seeded Customers", f"{customer_count:,}")
    c2.metric("Total Enterprise Revenue", f"₹{total_spend:,.2f}")
    c3.metric("Average Customer CLV", f"₹{avg_clv:,.2f}")
else:
    st.warning("No database tables populated. Please seed the database first.")
