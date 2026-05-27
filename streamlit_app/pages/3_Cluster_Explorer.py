import streamlit as st
import pandas as pd
import numpy as np
import sys
import os

# Set page config
st.set_page_config(page_title="Cluster Explorer", page_icon="🔮", layout="wide")

# Add utils to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils.db import cached_query
from utils.ml import load_ml_pipeline, FEATURE_COLUMNS
from utils.charts import plot_pca_scatter_2d, plot_pca_scatter_3d

st.title("Cluster Explorer (PCA Projection)")
st.markdown("Visualize customer segments projected into lower-dimensional PCA space to evaluate cluster separation.")

# Load pipeline
pipeline = load_ml_pipeline()

if not pipeline:
    st.warning("No active ML model found. Please train a clustering model in Model Studio first.")
else:
    # Fetch customers
    st.markdown("### Interactive Cluster Projections")
    
    # Get customers dataframe
    df_cust = cached_query("""
        SELECT 
            c.*, 
            s.name as segment_name 
        FROM customers c
        LEFT JOIN segments s ON c.segment_id = s.id
    """)
    
    if df_cust.empty or len(df_cust) < 10:
        st.warning("Insufficient data in database.")
    else:
        # Impute, scale, and run PCA
        X = df_cust[FEATURE_COLUMNS].copy()
        
        # Cast to float
        for col in FEATURE_COLUMNS:
            X[col] = X[col].astype(float)
            
        # Standard scaling and PCA projection
        try:
            X_imputed = pipeline["imputer"].transform(X)
            X_scaled = pipeline["scaler"].transform(X_imputed)
            X_pca = pipeline["pca"].transform(X_scaled)
            
            # Build PCA DataFrame
            df_pca = pd.DataFrame(X_pca[:, :3], columns=["PC1", "PC2", "PC3"])
            df_pca["Segment"] = df_cust["segment_name"].fillna("Unassigned")
            df_pca["ID"] = df_cust["external_id"]
            
            # Select 2D or 3D
            dimension = st.sidebar.radio("Select View Dimension:", ["2D Scatter Plot", "3D Scatter Plot"])
            
            # Sample for rendering performance (limit to 1,500 points)
            df_pca_sample = df_pca.sample(n=min(1500, len(df_pca)), random_state=42)
            
            if dimension == "2D Scatter Plot":
                fig = plot_pca_scatter_2d(df_pca_sample)
                st.plotly_chart(fig, use_container_width=True)
            else:
                fig = plot_pca_scatter_3d(df_pca_sample)
                st.plotly_chart(fig, use_container_width=True)
                
            # Explain variance ratio
            exp_var = pipeline["pca"].explained_variance_ratio_
            total_var = sum(exp_var) * 100
            st.markdown(f"""
            **Explained Variance Ratio:**
            - Principal Component 1 (PC1): **{exp_var[0]*100:.2f}%**
            - Principal Component 2 (PC2): **{exp_var[1]*100:.2f}%**
            - Principal Component 3 (PC3): **{exp_var[2]*100:.2f}%** if available.
            - Total Explained Variance: **{total_var:.2f}%**
            """)
            
        except Exception as e:
            st.error(f"Error computing PCA components: {str(e)}")
