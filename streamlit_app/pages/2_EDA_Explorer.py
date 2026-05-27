import streamlit as st
import pandas as pd
import sys
import os
import plotly.express as px

# Set page config
st.set_page_config(page_title="EDA Explorer", page_icon="📈", layout="wide")

# Add utils to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils.db import cached_query

st.title("Exploratory Data Analysis (EDA) Explorer")
st.markdown("Analyze demographic and behavioral distribution metrics for the customer database.")

# Selectable features list
FEATURE_LABELS = {
    "age": "Age",
    "annual_income": "Annual Income",
    "total_spend": "Total Spend",
    "avg_order_value": "Average Order Value",
    "purchase_frequency": "Purchase Frequency",
    "days_since_last_purchase": "Recency (Days)",
    "cart_abandonment_rate": "Cart Abandonment Rate",
    "email_open_rate": "Email Open Rate",
    "app_usage_score": "App Usage Score",
    "loyalty_points": "Loyalty Points",
    "return_rate": "Return Rate",
    "referral_count": "Referral Count",
    "clv_estimate": "CLV Estimate",
    "engagement_index": "Engagement Index",
    "rfm_score": "RFM Score"
}

# Sidebar configuration
feature_key = st.sidebar.selectbox(
    "Select Feature to Analyze:",
    options=list(FEATURE_LABELS.keys()),
    format_func=lambda x: FEATURE_LABELS[x]
)

# Fetch customer details with segment details
df_cust = cached_query("""
    SELECT 
        c.*, 
        s.name as segment_name 
    FROM customers c
    LEFT JOIN segments s ON c.segment_id = s.id
""")

if df_cust.empty:
    st.warning("No customer data available in database.")
else:
    # Cast Decimal columns to float in Pandas
    if feature_key in df_cust.columns:
        df_cust[feature_key] = df_cust[feature_key].astype(float)
        
    df_clean = df_cust.dropna(subset=[feature_key])
    
    # Overview metrics row
    c1, c2, c3, c4 = st.columns(4)
    
    c1.metric(f"Mean {FEATURE_LABELS[feature_key]}", f"{df_clean[feature_key].mean():,.2f}")
    c2.metric(f"Median {FEATURE_LABELS[feature_key]}", f"{df_clean[feature_key].median():,.2f}")
    c3.metric(f"Std Dev", f"{df_clean[feature_key].std():,.2f}")
    
    # Missing count
    missing_count = len(df_cust) - len(df_clean)
    missing_pct = (missing_count / len(df_cust)) * 100
    c4.metric("Missing Values", f"{missing_count:,} ({missing_pct:.1f}%)")
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader(f"Overall Distribution Histogram")
        fig_hist = px.histogram(
            df_clean,
            x=feature_key,
            nbins=30,
            color_discrete_sequence=['#3B82F6'],
            labels={feature_key: FEATURE_LABELS[feature_key]}
        )
        fig_hist.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            yaxis_title="Customer Count"
        )
        st.plotly_chart(fig_hist, use_container_width=True)
        
    with col2:
        st.subheader(f"Grouped by Segment Boxplot")
        fig_box = px.box(
            df_clean,
            x="segment_name",
            y=feature_key,
            color="segment_name",
            color_discrete_sequence=px.colors.qualitative.Safe,
            labels={"segment_name": "Segment", feature_key: FEATURE_LABELS[feature_key]}
        )
        fig_box.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            showlegend=False
        )
        st.plotly_chart(fig_box, use_container_width=True)
        
    st.markdown("---")
    
    # Descriptive Statistics table
    st.subheader("Segment descriptive metrics summary table")
    summary_stats = df_clean.groupby("segment_name")[feature_key].describe()
    st.dataframe(summary_stats.rename(columns={
        "count": "Count",
        "mean": "Mean",
        "std": "Std Dev",
        "min": "Minimum",
        "25%": "25th Percentile",
        "50%": "Median",
        "75%": "75th Percentile",
        "max": "Maximum"
    }), use_container_width=True)
