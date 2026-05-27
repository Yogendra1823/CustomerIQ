# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- **Authentication**: Added support for Google Login ("Continue with Google") in the frontend and backend.

### Changed
- **Database**: Migrated local SQLite default to Neon serverless PostgreSQL.
- **Documentation**: Completely overhauled `README.md` with new sleek badging, Mermaid diagrams, and professional formatting. 
- **Documentation**: Updated `DEPLOYMENT.md` to reflect the Vercel, Render, Upstash, and Neon serverless architecture stack.
- **Security**: Scrubbed repository of temporary development scripts (`add_google_auth.py`, etc.) and scrubbed database URL examples for strict production security compliance.
- **Frontend**: Fixed strict TypeScript compilation errors across React components to allow flawless Vercel production builds.

## [1.0.0] - 2026-05-25

### Added
- **Backend API**:
  - Engineered with FastAPI for async operations.
  - Implemented async database session handling with SQLAlchemy for Neon/Supabase cloud databases and local SQLite.
  - Formulated JWT authentication (Access & Refresh tokens).
  - Setup Redis cache mechanism with 300s expiration decorator.
  - Structured structured-logging (JSON format) and request rate limiting.
- **Machine Learning Pipeline**:
  - Implemented data pre-processing using KNN imputer, Winsorizer, and StandardScaler.
  - Added feature selection based on Pearson correlation and VIF metrics.
  - Added PCA dimensionality reduction for 2D/3D visualizations.
  - Built Elbow-method clustering comparing K-Means, DBSCAN, Agglomerative, and GMM.
  - Embedded Isolation Forest anomaly detector to estimate customer churn risk indices.
  - Hooked up MLflow for experiment tracking and logging model artifacts.
- **Frontend Dashboard**:
  - Built SPA using React 18, TypeScript, and Vite.
  - Styled with Tailwind CSS for glassmorphic elements and dark mode.
  - Implemented React Query (TanStack Query) for auto-refetching/caching.
  - Configured Zustand store for token authentication persistence.
  - Rendered charts using Recharts (Donut, Bar, Line, Radar) and Plotly (3D RFM scatter).
- **Streamlit Analytics Workspace**:
  - Designed interactive sidebar showing database connectivity metrics and ML models.
  - Built EDA pages with boxplots/histograms, PCA projection visualizers, and cohort matrices.
  - Automated report compiler outputting ReportLab PDF summaries.
- **DevOps/Deployment**:
  - Wrote `docker-compose.yml` defining services: `backend`, `frontend`, `streamlit`, `redis`, `mlflow`, and `nginx`.
  - Configured Nginx reverse-proxy setup.
