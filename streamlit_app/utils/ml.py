import os
import joblib
import numpy as np
import pandas as pd
import streamlit as st
from .db import cached_query

MODELS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../models"))

FEATURE_COLUMNS = [
    "age", "annual_income", "total_spend", "avg_order_value",
    "purchase_frequency", "days_since_last_purchase",
    "cart_abandonment_rate", "email_open_rate", "app_usage_score",
    "loyalty_points", "return_rate", "referral_count",
    "clv_estimate", "engagement_index", "rfm_score"
]

@st.cache_resource
def load_ml_pipeline():
    """
    Load active ML models, scalers, and dimensionality reduction tools from disk.
    """
    df_run = cached_query("SELECT * FROM ml_runs WHERE is_active = 1 LIMIT 1")
    if df_run.empty:
        return None
    
    run = df_run.iloc[0]
    algorithm = run["algorithm"]
    model_path = run["model_path"]
    
    try:
        imputer = joblib.load(os.path.join(MODELS_DIR, "imputer.pkl"))
        scaler = joblib.load(os.path.join(MODELS_DIR, "scaler.pkl"))
        pca = joblib.load(os.path.join(MODELS_DIR, "pca.pkl"))
        model = joblib.load(model_path)
        iso_forest = joblib.load(os.path.join(MODELS_DIR, "iso_forest.pkl"))
        return {
            "imputer": imputer,
            "scaler": scaler,
            "pca": pca,
            "model": model,
            "iso_forest": iso_forest,
            "algorithm": algorithm
        }
    except Exception as e:
        print(f"Error loading model pipeline: {e}")
        return None

def predict_customer(features: dict) -> dict:
    """
    Predict cluster segment, churn probability, and marketing strategy for a set of features.
    """
    pipeline = load_ml_pipeline()
    if not pipeline:
        return {
            "cluster_id": 0,
            "segment_name": "Unclassified",
            "churn_probability": 0.5,
            "persona": "No active model trained yet.",
            "recommended_action": "Train a model in Model Studio first."
        }
        
    X = [float(features.get(col, 0.0)) for col in FEATURE_COLUMNS]
    X = np.array([X])
    
    X_imputed = pipeline["imputer"].transform(X)
    X_scaled = pipeline["scaler"].transform(X_imputed)
    X_pca = pipeline["pca"].transform(X_scaled)
    
    # Run prediction
    algorithm = pipeline["algorithm"]
    if algorithm in ["kmeans", "gmm"]:
        cluster_id = int(pipeline["model"].predict(X_pca)[0])
    else:
        cluster_id = 0
    
    churn_feats = [
        float(features.get("days_since_last_purchase", 0.0)),
        float(features.get("cart_abandonment_rate", 0.0)),
        float(features.get("email_open_rate", 0.0)),
        float(features.get("return_rate", 0.0))
    ]
    churn_prob = float(1.0 - (pipeline["iso_forest"].score_samples([churn_feats])[0] + 1.0) / 2.0)
    
    # Retrieve segment info from database
    df_seg = cached_query(f"SELECT * FROM segments WHERE priority_score = {10 - cluster_id} LIMIT 1")
    if not df_seg.empty:
        segment_name = df_seg.iloc[0]["name"]
        persona = df_seg.iloc[0]["description"]
        strategy = df_seg.iloc[0]["marketing_strategy"]
    else:
        segment_name = f"Cluster {cluster_id}"
        persona = "General behavioral profile."
        strategy = "Standard target strategy."
        
    return {
        "cluster_id": cluster_id,
        "segment_name": segment_name,
        "churn_probability": churn_prob,
        "persona": persona,
        "recommended_action": strategy
    }
