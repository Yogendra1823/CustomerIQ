from pydantic import BaseModel, ConfigDict
from typing import Optional, Dict, Any
from uuid import UUID
from datetime import datetime
from decimal import Decimal

class MLRunBase(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    run_name: Optional[str] = None
    algorithm: Optional[str] = None
    n_clusters: Optional[int] = None
    silhouette_score: Optional[Decimal] = None
    davies_bouldin_score: Optional[Decimal] = None
    inertia: Optional[Decimal] = None
    training_samples: Optional[int] = None
    feature_count: Optional[int] = None
    runtime_seconds: Optional[Decimal] = None
    model_path: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None
    metrics: Optional[Dict[str, Any]] = None
    is_active: bool = False

class MLRunResponse(MLRunBase):
    id: UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True, protected_namespaces=())

class MLTrainResponse(BaseModel):
    run_id: UUID
    status: str

class MLTrainRequest(BaseModel):
    algorithm: Optional[str] = "kmeans"
    n_clusters: Optional[int] = 5
    run_name: Optional[str] = None
