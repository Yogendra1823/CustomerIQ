import streamlit as st
import pandas as pd
import sys
import os
import uuid
import asyncio

# Set page config
st.set_page_config(page_title="Model Studio", page_icon="⚙️", layout="wide")

# Add backend directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../backend")))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils.db import cached_query
from app.services.ml_service import train_segmentation_model

st.title("Model Studio")
st.markdown("Monitor historical clustering runs, inspect model silhouette scores, and train new models in real-time.")

# Fetch runs
df_runs = cached_query("SELECT * FROM ml_runs ORDER BY created_at DESC")

# Show active model card
df_active = df_runs[df_runs["is_active"] == 1] if not df_runs.empty else pd.DataFrame()

st.subheader("Active Segmentation Model")
if df_active.empty:
    st.warning("No model is currently active. Please train a new model below.")
else:
    active = df_active.iloc[0]
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Algorithm", str(active["algorithm"]).upper())
    c2.metric("Clusters (k)", int(active["n_clusters"]))
    c3.metric("Silhouette Score", f"{float(active['silhouette_score']):.4f}")
    c4.metric("Davies-Bouldin Index", f"{float(active['davies_bouldin_score']):.4f}")
    
st.markdown("---")

# Train new model section
st.subheader("Train New Model")
col1, col2 = st.columns(2)

with col1:
    alg = st.selectbox("Select Clustering Algorithm:", ["kmeans", "gmm"])
    k_clusters = st.slider("Select Number of Clusters (k):", min_value=2, max_value=10, value=5)
    model_name = st.text_input("Run Name (Optional):", placeholder="e.g. quarterly_segmentation_v1")
    
    if st.button("Trigger Training Pipeline"):
        st.info("Initializing scikit-learn pipeline...")
        run_id = uuid.uuid4()
        
        # Define helper to run async function
        async def run_training():
            await train_segmentation_model(
                run_id=run_id,
                algorithm=alg,
                n_clusters=k_clusters,
                run_name=model_name or None
            )
            
        with st.spinner("Running preprocessing, winsorization, scaling, PCA projection, and clustering..."):
            try:
                # Execute async function in streamlit loop
                # Streamlit might have its own loop running, so we check or get/create loop
                try:
                    loop = asyncio.get_running_loop()
                    # If running loop exists, schedule it
                    future = asyncio.run_coroutine_threadsafe(run_training(), loop)
                    future.result() # Wait for completion
                except RuntimeError:
                    # No running loop, run standard asyncio.run
                    asyncio.run(run_training())
                    
                st.success("Model trained successfully! Page will refresh.")
                st.rerun()
            except Exception as err:
                st.error(f"Pipeline error: {str(err)}")

# Show runs history
st.subheader("Training Run History")
if df_runs.empty:
    st.info("No training runs recorded yet.")
else:
    st.dataframe(
        df_runs,
        column_config={
            "id": "Run ID",
            "run_name": "Name",
            "algorithm": "Algorithm",
            "n_clusters": "Clusters",
            "silhouette_score": st.column_config.NumberColumn("Silhouette", format="%.4f"),
            "davies_bouldin_score": st.column_config.NumberColumn("DB Index", format="%.4f"),
            "inertia": st.column_config.NumberColumn("Inertia", format="%.2f"),
            "training_samples": "Samples",
            "runtime_seconds": st.column_config.NumberColumn("Runtime (s)", format="%.2f"),
            "is_active": "Active Status",
            "created_at": "Created At"
        },
        use_container_width=True
    )
