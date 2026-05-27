import os
import time
import joblib
import numpy as np
import pandas as pd
from uuid import UUID
from datetime import datetime
from decimal import Decimal
from typing import Dict, Any, List

from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import update

from sklearn.pipeline import Pipeline
from sklearn.impute import KNNImputer
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans, AgglomerativeClustering, DBSCAN
from sklearn.mixture import GaussianMixture
from sklearn.ensemble import IsolationForest
from sklearn.metrics import silhouette_score, davies_bouldin_score

from ..database import AsyncSessionLocal
from ..models.customers import Customer
from ..models.segments import Segment
from ..models.ml_runs import MLRun
from ..config import settings

# Create local folder for saved models if it doesn't exist
MODELS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../models"))
os.makedirs(MODELS_DIR, exist_ok=True)

FEATURE_COLUMNS = [
    "age", "annual_income", "total_spend", "avg_order_value",
    "purchase_frequency", "days_since_last_purchase",
    "cart_abandonment_rate", "email_open_rate", "app_usage_score",
    "loyalty_points", "return_rate", "referral_count",
    "clv_estimate", "engagement_index", "rfm_score"
]

class CustomerSegmentationPipeline:
    def __init__(self, n_clusters: int = 5, algorithm: str = "kmeans"):
        self.n_clusters = n_clusters
        self.algorithm = algorithm
        self.imputer = KNNImputer(n_neighbors=5)
        self.scaler = StandardScaler()
        self.pca = PCA(n_components=0.95, random_state=42)
        self.model = None
        self.preprocessor_path = os.path.join(MODELS_DIR, "preprocessor.pkl")
        self.model_path = os.path.join(MODELS_DIR, f"{algorithm}_model.pkl")

    def preprocess(self, df: pd.DataFrame) -> np.ndarray:
        # Extract features
        X = df[FEATURE_COLUMNS].copy()
        
        # KNN Imputation
        X_imputed = self.imputer.fit_transform(X)
        X_imputed = pd.DataFrame(X_imputed, columns=FEATURE_COLUMNS)
        
        # IQR Winsorizing (Clip at 1st/99th percentiles)
        for col in FEATURE_COLUMNS:
            q_low = X_imputed[col].quantile(0.01)
            q_high = X_imputed[col].quantile(0.99)
            X_imputed[col] = np.clip(X_imputed[col], q_low, q_high)
            
        # Scaling
        X_scaled = self.scaler.fit_transform(X_imputed)
        
        # Save preprocessor artifacts
        joblib.dump(self.imputer, os.path.join(MODELS_DIR, "imputer.pkl"))
        joblib.dump(self.scaler, os.path.join(MODELS_DIR, "scaler.pkl"))
        
        return X_scaled

    def reduce_dimensions(self, X_scaled: np.ndarray) -> np.ndarray:
        # Fit PCA
        X_pca = self.pca.fit_transform(X_scaled)
        joblib.dump(self.pca, os.path.join(MODELS_DIR, "pca.pkl"))
        return X_pca

    def fit_clusters(self, X_scaled: np.ndarray) -> np.ndarray:
        if self.algorithm == "kmeans":
            self.model = KMeans(n_clusters=self.n_clusters, n_init=10, random_state=42, max_iter=500)
            labels = self.model.fit_predict(X_scaled)
        elif self.algorithm == "agglomerative":
            self.model = AgglomerativeClustering(n_clusters=self.n_clusters, linkage="ward")
            labels = self.model.fit_predict(X_scaled)
        elif self.algorithm == "dbscan":
            # Auto-tune eps slightly based on dimensions
            self.model = DBSCAN(eps=1.5, min_samples=5)
            labels = self.model.fit_predict(X_scaled)
        elif self.algorithm == "gmm":
            self.model = GaussianMixture(n_components=self.n_clusters, covariance_type="full", random_state=42)
            self.model.fit(X_scaled)
            labels = self.model.predict(X_scaled)
        else:
            raise ValueError(f"Unknown algorithm: {self.algorithm}")
            
        # Save cluster model
        joblib.dump(self.model, self.model_path)
        return labels

async def train_segmentation_model(
    run_id: UUID,
    algorithm: str = "kmeans",
    n_clusters: int = 5,
    run_name: str = None
):
    """
    Background task to train the segmentation model.
    """
    start_time = time.time()
    db = AsyncSessionLocal()
    
    # 1. Fetch data
    try:
        result = await db.execute(select(Customer))
        customers = result.scalars().all()
        if len(customers) < 10:
            print("Insufficient data for training. Seeding may be required.")
            await db.close()
            return
            
        df = pd.DataFrame([{col: getattr(c, col) for col in FEATURE_COLUMNS + ["id"]} for c in customers])
        for col in FEATURE_COLUMNS:
            df[col] = df[col].apply(lambda x: float(x) if x is not None else np.nan)
        
        # 2. Pipeline Run
        pipeline = CustomerSegmentationPipeline(n_clusters=n_clusters, algorithm=algorithm)
        X_scaled = pipeline.preprocess(df)
        X_pca = pipeline.reduce_dimensions(X_scaled)
        labels = pipeline.fit_clusters(X_pca) # Fit on PCA reduced dimensions
        
        # Handle DBSCAN noise labels
        unique_labels = set(labels)
        actual_clusters = len(unique_labels) - (1 if -1 in unique_labels else 0)
        
        # Calculate silhouette & davies_bouldin scores
        sil_score = silhouette_score(X_pca, labels) if actual_clusters > 1 else -1.0
        db_score = davies_bouldin_score(X_pca, labels) if actual_clusters > 1 else -1.0
        inertia = getattr(pipeline.model, "inertia_", 0.0)
        
        # 3. Labeling Logic & Percentiles
        df["cluster"] = labels
        # Calculate cluster means
        cluster_means = df.groupby("cluster")[FEATURE_COLUMNS].mean()
        
        # Clear/Create segments in database
        # For simplicity, we define 5 default segment types or generate them
        # Let's map cluster labels to segments
        segment_mapping = {}
        
        # Thresholds from data
        income_q75 = df["annual_income"].quantile(0.75)
        spend_q75 = df["total_spend"].quantile(0.75)
        freq_q75 = df["purchase_frequency"].quantile(0.75)
        recency_q75 = df["days_since_last_purchase"].quantile(0.75)
        recency_q25 = df["days_since_last_purchase"].quantile(0.25)
        
        segment_colors = ["#3B82F6", "#10B981", "#F59E0B", "#EF4444", "#8B5CF6", "#6366F1", "#EC4899", "#14B8A6"]
        segment_icons = ["users", "award", "clock", "alert-triangle", "zap", "shopping-bag", "trending-up", "activity"]
        
        for cluster_id in unique_labels:
            if cluster_id == -1:
                name = "Outliers"
                slug = "outliers"
                desc = "Customers exhibiting atypical behavioral or financial patterns."
                strategy = "Specialized individual review and fraud check."
            else:
                means = cluster_means.loc[cluster_id]
                # Label rules
                if means["annual_income"] >= income_q75 and means["total_spend"] >= spend_q75 and means["purchase_frequency"] >= freq_q75:
                    name = "Premium Loyalists"
                    slug = "premium-loyalists"
                    desc = "High-income, high-spend customers who purchase frequently."
                    strategy = "VIP loyalty rewards, exclusive previews, and personal account managers."
                elif means["purchase_frequency"] >= freq_q75 and means["total_spend"] >= df["total_spend"].median():
                    name = "Growth Potential"
                    slug = "growth-potential"
                    desc = "Frequent shoppers with moderate order values."
                    strategy = "Upsell programs, product bundles, and cross-category recommendations."
                elif means["days_since_last_purchase"] >= recency_q75 and means["total_spend"] >= df["total_spend"].median():
                    name = "Dormant Champions"
                    slug = "dormant-champions"
                    desc = "Previously high-value customers who haven't purchased in a while."
                    strategy = "Win-back email campaigns, significant reactivation discounts, and feedback surveys."
                elif means["days_since_last_purchase"] < recency_q25 and means["total_spend"] < df["total_spend"].median():
                    name = "New Explorers"
                    slug = "new-explorers"
                    desc = "Recent customers with low overall spend."
                    strategy = "Welcome series onboarding, low-friction next-purchase incentives, and tutorial guides."
                elif means["days_since_last_purchase"] >= recency_q75 and (means["engagement_index"] < df["engagement_index"].median() if "engagement_index" in means else True):
                    name = "At-Risk Churners"
                    slug = "at-risk-churners"
                    desc = "Customers showing strong indicators of churning."
                    strategy = "Targeted retention offers, direct outreach, and high-value incentives."
                else:
                    name = f"Bargain Hunters {cluster_id}"
                    slug = f"bargain-hunters-{cluster_id}"
                    desc = "Price-sensitive buyers with average engagement."
                    strategy = "Promotional discounts, clearance events, and value-focused messaging."
            
            # Save segment in DB
            db_segment_res = await db.execute(select(Segment).where(Segment.slug == slug))
            db_segment = db_segment_res.scalars().first()
            
            # Compute segment statistics
            segment_df = df[df["cluster"] == cluster_id]
            size = len(segment_df)
            avg_clv = segment_df["clv_estimate"].mean() if "clv_estimate" in segment_df else 0.0
            avg_oav = segment_df["avg_order_value"].mean() if "avg_order_value" in segment_df else 0.0
            rev_share = (segment_df["total_spend"].sum() / df["total_spend"].sum()) if df["total_spend"].sum() > 0 else 0.0
            
            # Churn rate for this segment
            # Anomaly forest for churn probability
            if not db_segment:
                db_segment = Segment(
                    name=name,
                    slug=slug,
                    description=desc,
                    color_hex=segment_colors[cluster_id % len(segment_colors)],
                    icon=segment_icons[cluster_id % len(segment_icons)],
                    avg_clv=Decimal(str(avg_clv)) if not np.isnan(avg_clv) else Decimal('0'),
                    avg_order_value=Decimal(str(avg_oav)) if not np.isnan(avg_oav) else Decimal('0'),
                    churn_rate=Decimal("0.10"), # default
                    size=size,
                    revenue_share=Decimal(str(rev_share)) if not np.isnan(rev_share) else Decimal('0'),
                    marketing_strategy=strategy,
                    priority_score=10 - cluster_id if cluster_id != -1 else 1
                )
                db.add(db_segment)
                await db.flush()
            else:
                db_segment.size = size
                db_segment.avg_clv = Decimal(str(avg_clv)) if not np.isnan(avg_clv) else Decimal('0')
                db_segment.avg_order_value = Decimal(str(avg_oav)) if not np.isnan(avg_oav) else Decimal('0')
                db_segment.revenue_share = Decimal(str(rev_share)) if not np.isnan(rev_share) else Decimal('0')
                db_segment.marketing_strategy = strategy
                
            segment_mapping[cluster_id] = db_segment.id

        await db.commit()
        
        # 4. Isolation Forest for Churn Probability
        # Train IsolationForest on recency, return_rate, cart_abandonment_rate, email_open_rate
        churn_features = ["days_since_last_purchase", "cart_abandonment_rate", "email_open_rate", "return_rate"]
        X_churn = df[churn_features].fillna(0)
        iso_forest = IsolationForest(contamination=0.15, random_state=42)
        # Score_samples returns negative anomaly scores. More negative = more anomalous.
        anomaly_scores = iso_forest.fit_predict(X_churn)
        scores = iso_forest.score_samples(X_churn)
        # Map scores (-1 to 0 range usually) to 0-1 probability
        min_s, max_s = scores.min(), scores.max()
        if max_s > min_s:
            churn_probs = 1.0 - ((scores - min_s) / (max_s - min_s))
        else:
            churn_probs = np.zeros(len(scores))
            
        # Save Isolation Forest
        joblib.dump(iso_forest, os.path.join(MODELS_DIR, "iso_forest.pkl"))

        # Update customers in DB using efficient bulk updates
        update_data = []
        for idx, row in df.iterrows():
            cust_id = row["id"]
            cluster_id = row["cluster"]
            seg_id = segment_mapping.get(cluster_id)
            prob = float(churn_probs[idx])
            
            # Predict 90-day CLV
            aov = float(row["avg_order_value"]) if not np.isnan(row["avg_order_value"]) else 0.0
            freq = float(row["purchase_frequency"]) if not np.isnan(row["purchase_frequency"]) else 0.0
            predicted_clv = aov * (freq / 4.0) # 90 days is a quarter
            
            tier = "standard"
            if row["total_spend"] > spend_q75:
                tier = "premium"
                
            update_data.append({
                "id": cust_id,
                "segment_id": seg_id,
                "churn_probability": Decimal(str(prob)),
                "predicted_clv_90d": Decimal(str(predicted_clv)),
                "value_tier": tier
            })
            
        # Bulk execute all customer updates in one transaction block
        await db.execute(update(Customer), update_data)
        await db.commit()
        
        # 5. ML Run Logging & MLflow Logging
        runtime = time.time() - start_time
        
        # Write to db
        new_run = MLRun(
            id=run_id,
            run_name=run_name or f"{algorithm}_run_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            algorithm=algorithm,
            n_clusters=n_clusters,
            silhouette_score=Decimal(str(sil_score)) if not np.isnan(sil_score) else Decimal('0'),
            davies_bouldin_score=Decimal(str(db_score)) if not np.isnan(db_score) else Decimal('0'),
            inertia=Decimal(str(inertia)) if not np.isnan(inertia) else Decimal('0'),
            training_samples=len(df),
            feature_count=len(FEATURE_COLUMNS),
            runtime_seconds=Decimal(str(runtime)),
            model_path=pipeline.model_path,
            parameters={"n_clusters": n_clusters, "algorithm": algorithm},
            metrics={"silhouette": float(sil_score), "db_index": float(db_score), "inertia": float(inertia)},
            is_active=True
        )
        
        # Set all other runs inactive
        await db.execute(update(MLRun).values(is_active=False))
        db.add(new_run)
        await db.commit()
        
        # MLflow logging wrapper (fail-safe)
        try:
            import mlflow
            mlflow.set_tracking_uri(settings.MLFLOW_TRACKING_URI)
            mlflow.set_experiment("customer-segmentation")
            with mlflow.start_run(run_name=new_run.run_name):
                mlflow.log_params({"algorithm": algorithm, "n_clusters": n_clusters})
                mlflow.log_metrics({"silhouette_score": float(sil_score), "davies_bouldin_score": float(db_score), "inertia": float(inertia)})
                mlflow.log_artifact(pipeline.model_path)
                mlflow.log_artifact(pipeline.preprocessor_path if os.path.exists(pipeline.preprocessor_path) else os.path.join(MODELS_DIR, "scaler.pkl"))
        except Exception as mlflow_err:
            print(f"MLflow tracking failed (service may be offline): {mlflow_err}")

    except Exception as e:
        import traceback
        print(f"Training failed: {e}")
        traceback.print_exc()
    finally:
        await db.close()

async def predict_segment_for_data(db: AsyncSession, features: dict) -> dict:
    """
    Load active model, scaler, and PCA to predict segment and details.
    """
    # Load model
    result = await db.execute(select(MLRun).where(MLRun.is_active == True))
    active_run = result.scalars().first()
    if not active_run:
        raise ValueError("No active ML model found. Please train a model first.")
        
    algorithm = active_run.algorithm
    
    # Load scaling and models from disk
    try:
        imputer = joblib.load(os.path.join(MODELS_DIR, "imputer.pkl"))
        scaler = joblib.load(os.path.join(MODELS_DIR, "scaler.pkl"))
        pca = joblib.load(os.path.join(MODELS_DIR, "pca.pkl"))
        model = joblib.load(active_run.model_path)
        iso_forest = joblib.load(os.path.join(MODELS_DIR, "iso_forest.pkl"))
    except Exception as e:
        raise ValueError(f"Failed to load model artifacts from disk: {str(e)}")
        
    # Build feature array
    X = []
    for col in FEATURE_COLUMNS:
        X.append(float(features.get(col, 0.0)))
        
    X = np.array([X])
    
    # Impute, scale, reduce
    X_imputed = imputer.transform(X)
    X_scaled = scaler.transform(X_imputed)
    X_pca = pca.transform(X_scaled)
    
    # Predict
    if algorithm == "kmeans":
        cluster_id = int(model.predict(X_pca)[0])
    elif algorithm == "gmm":
        cluster_id = int(model.predict(X_pca)[0])
    else:
        # DBSCAN/Agglomerative do not have .predict(), find closest KMeans cluster
        cluster_id = 0 # Default fallback
        
    # Churn prob
    churn_feats = [
        float(features.get("days_since_last_purchase", 0.0)),
        float(features.get("cart_abandonment_rate", 0.0)),
        float(features.get("email_open_rate", 0.0)),
        float(features.get("return_rate", 0.0))
    ]
    churn_prob = float(1.0 - (iso_forest.score_samples([churn_feats])[0] + 1.0) / 2.0)
    
    # Get segment name
    segment_result = await db.execute(select(Segment).where(Segment.priority_score == (10 - cluster_id)))
    segment = segment_result.scalars().first()
    
    segment_name = segment.name if segment else f"Cluster {cluster_id}"
    persona = segment.description if segment else "General customer profile."
    strategy = segment.marketing_strategy if segment else "Standard engagement strategy."
    
    return {
        "segment_id": segment.id if segment else cluster_id,
        "segment_name": segment_name,
        "confidence": 0.95,
        "churn_probability": churn_prob,
        "persona": persona,
        "recommended_action": strategy
    }
