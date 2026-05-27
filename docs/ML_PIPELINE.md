# CustomerIQ Machine Learning Pipeline

This document explains the algorithms, data preprocessing details, model validation metrics, and business interpretations used in the CustomerIQ clustering pipeline.

## 1. Feature Engineering
The pipeline processes 15 financial, demographic, and behavioral features to build a multi-dimensional customer behavioral vector:
* **Demographics**: `age`
* **Financial metrics**: `annual_income`, `total_spend`, `avg_order_value`, `clv_estimate`
* **Behavioral indicators**: `purchase_frequency`, `days_since_last_purchase` (recency), `cart_abandonment_rate`, `return_rate`
* **Engagement metrics**: `email_open_rate`, `app_usage_score`, `loyalty_points`, `referral_count`, `engagement_index`, `rfm_score`

## 2. Preprocessing Steps
* **KNN Imputation**: Replaces missing values using KNNImputer (k=5) to maintain statistical properties of sparse columns.
* **IQR Winsorization**: Clips high-skew features at the 1st and 99th percentiles. This limits the impact of extreme outliers without discarding vital data.
* **Normalization**: Utilizes `StandardScaler` to ensure zero mean and unit variance.

## 3. Dimensionality Reduction
* **PCA (Principal Component Analysis)**: Retains components explaining 95% of the variance. Reducing coordinates helps avoid the "curse of dimensionality" during distance measurements and enables interactive 2D/3D plotting of clusters in Streamlit.

## 4. Clustering & Optimal K Estimation
* The pipeline supports four algorithms:
  * **K-Means**: Configured as the primary clustering method. Runs 10 iterations to prevent local minima.
  * **Agglomerative Hierarchical**: Grouping based on Ward link metrics.
  * **DBSCAN**: Noise clustering. Useful for detecting sparse transaction densities.
  * **Gaussian Mixture Models (GMM)**: Soft-assignment density clustering.
* **Optimal K Selection**: Evaluates silhouette and Davies-Bouldin metrics for cluster limits (K = 2 to 10). Detects the elbow using KneeLocator logic.

## 5. Segment Personas and Business Logic

Auto-labels are applied to clusters according to specific rules:
* **Premium Loyalists**: High annual income and spend. Recommended strategy: VIP event invites and personal account managers.
* **Growth Potential**: Frequent purchasers with average spending. Strategy: Bundle upsells and cross-category recommendations.
* **Dormant Champions**: Historically high-value buyers who haven't ordered recently. Strategy: High-value reactivation discounts.
* **New Explorers**: Recent buyers with low overall spend. Strategy: Low-friction welcome coupons and tutorial onboarding series.
* **At-Risk Churners**: Long elapsed time since purchase and low engagement levels. Strategy: Immediate direct retention campaigns.
* **Bargain Hunters**: Value-oriented customers. Strategy: Promotional discounts and seasonal sales.

## 6. Churn Risk & LTV Estimation
* **Churn Probability**: Isolation Forest model trained on recency, return rates, and cart abandonments to generate anomaly scores mapped to a 0-1 probability indicator.
* **90-Day LTV**: Estimated using the customer's average order value and purchase frequency.
