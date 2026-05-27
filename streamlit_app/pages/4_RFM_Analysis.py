import streamlit as st
import pandas as pd
import sys
import os

# Set page config
st.set_page_config(page_title="RFM Analysis", page_icon="🎯", layout="wide")

# Add utils to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils.db import cached_query
from utils.charts import plot_rfm_scatter_3d

st.title("RFM Analysis Dashboard")
st.markdown("Explore customer behavioral distributions across **Recency** (days since purchase), **Frequency** (total orders), and **Monetary** (total spend).")

# Fetch customer RFM data
df_cust = cached_query("""
    SELECT 
        c.external_id,
        c.days_since_last_purchase,
        c.purchase_frequency,
        c.total_spend,
        s.name as segment_name
    FROM customers c
    LEFT JOIN segments s ON c.segment_id = s.id
""")

if df_cust.empty:
    st.warning("No customer data available in database.")
else:
    # Cast decimals to float
    df_cust["days_since_last_purchase"] = df_cust["days_since_last_purchase"].astype(float)
    df_cust["purchase_frequency"] = df_cust["purchase_frequency"].astype(float)
    df_cust["total_spend"] = df_cust["total_spend"].astype(float)
    df_cust["segment_name"] = df_cust["segment_name"].fillna("Unassigned")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("3D RFM Behavior Space")
        fig_rfm = plot_rfm_scatter_3d(df_cust)
        st.plotly_chart(fig_rfm, use_container_width=True)
        
    with col2:
        st.subheader("Segment RFM Centroids")
        # Calculate centroids
        centroids = df_cust.groupby("segment_name").agg({
            "days_since_last_purchase": "mean",
            "purchase_frequency": "mean",
            "total_spend": "mean"
        }).rename(columns={
            "days_since_last_purchase": "Avg Recency (Days)",
            "purchase_frequency": "Avg Frequency (Orders)",
            "total_spend": "Avg Monetary (Spend)"
        })
        
        st.dataframe(
            centroids.style.format({
                "Avg Recency (Days)": "{:.1f}",
                "Avg Frequency (Orders)": "{:.1f}",
                "Avg Monetary (Spend)": "₹{:,.2f}"
            }),
            use_container_width=True
        )
        
        st.markdown("""
        **How to interpret RFM:**
        - **Recency (X-Axis):** Lower is better. Tells how active customers are.
        - **Frequency (Y-Axis):** Higher is better. Shows buying consistency.
        - **Monetary (Z-Axis):** Higher is better. Focuses on revenue contribution.
        """)
