import streamlit as st
import pandas as pd
import sys
import os

# Set page config
st.set_page_config(page_title="Executive Overview", page_icon="📊", layout="wide")

# Add utils to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils.db import cached_query
from utils.charts import plot_segment_donut, plot_revenue_bar

st.title("Executive Overview")
st.markdown("High-level dashboard summarizing customer segmentation health and revenue share.")

# Fetch segments
df_segments = cached_query("SELECT * FROM segments WHERE size > 0")

if df_segments.empty:
    st.warning("No segments available. Please train a clustering model in Model Studio to group customers.")
else:
    # KPI metrics row
    c1, c2, c3, c4 = st.columns(4)
    
    # Compute total values from customers
    df_kpis = cached_query("""
        SELECT 
            COUNT(id) as total_customers,
            SUM(total_spend) as total_revenue,
            AVG(clv_estimate) as avg_clv,
            AVG(churn_probability) as churn_rate
        FROM customers
    """)
    
    total_customers = df_kpis.iloc[0]["total_customers"] or 0
    total_revenue = df_kpis.iloc[0]["total_revenue"] or 0.0
    avg_clv = df_kpis.iloc[0]["avg_clv"] or 0.0
    churn_rate = df_kpis.iloc[0]["churn_rate"] or 0.0
    
    c1.metric("Total Customers", f"{total_customers:,}")
    c2.metric("Total Revenue", f"₹{total_revenue:,.2f}")
    c3.metric("Average CLV", f"₹{avg_clv:,.2f}")
    c4.metric("Average Churn Risk", f"{churn_rate * 100:.2f}%")
    
    st.markdown("---")
    
    # Charts row
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Segment Customer Distribution")
        fig_donut = plot_segment_donut(df_segments)
        st.plotly_chart(fig_donut, use_container_width=True)
        
    with col2:
        st.subheader("Revenue Share by Segment")
        fig_revenue = plot_revenue_bar(df_segments)
        st.plotly_chart(fig_revenue, use_container_width=True)
        
    st.markdown("---")
    
    # Recent Transactions Table
    st.subheader("Recent Customer Activity")
    df_recent = cached_query("""
        SELECT 
            c.external_id as customer_id,
            t.order_id,
            t.transaction_date,
            t.amount,
            t.category,
            t.status
        FROM transactions t
        JOIN customers c ON t.customer_id = c.id
        ORDER BY t.transaction_date DESC
        LIMIT 10
    """)
    
    st.dataframe(
        df_recent,
        column_config={
            "customer_id": "Customer ID",
            "order_id": "Order ID",
            "transaction_date": "Date & Time",
            "amount": st.column_config.NumberColumn("Amount (INR)", format="₹%.2f"),
            "category": "Product Category",
            "status": "Order Status"
        },
        use_container_width=True
    )
