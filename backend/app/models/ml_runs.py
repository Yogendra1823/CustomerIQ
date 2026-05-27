from sqlalchemy import Column, Integer, String, Numeric, Boolean, DateTime, func, JSON, Uuid
import uuid
from .base import Base

class MLRun(Base):
    __tablename__ = "ml_runs"
    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    run_name = Column(String(200))
    algorithm = Column(String(50))
    n_clusters = Column(Integer)
    silhouette_score = Column(Numeric(6, 4))
    davies_bouldin_score = Column(Numeric(6, 4))
    inertia = Column(Numeric(12, 2))
    training_samples = Column(Integer)
    feature_count = Column(Integer)
    runtime_seconds = Column(Numeric(6, 2))
    model_path = Column(String(500))
    parameters = Column(JSON)
    metrics = Column(JSON)
    is_active = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
