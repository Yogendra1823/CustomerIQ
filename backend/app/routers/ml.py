from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List
from uuid import UUID

from ..dependencies import get_db, get_current_user, require_admin
from ..models.users import User
from ..models.ml_runs import MLRun
from ..schemas.ml_runs import MLRunResponse, MLTrainResponse, MLTrainRequest
from ..services.ml_service import train_segmentation_model, predict_segment_for_data

router = APIRouter(prefix="/ml", tags=["Machine Learning"])

@router.post("/train", response_model=MLTrainResponse, status_code=202)
async def train_model(
    request: MLTrainRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Trigger a background task to train a new segmentation model using scikit-learn.
    Requires admin privileges.
    """
    # Create an inactive MLRun record to return the ID immediately
    import uuid
    run_id = uuid.uuid4()
    
    # Add a background task to run the training pipeline
    background_tasks.add_task(
        train_segmentation_model,
        run_id=run_id,
        algorithm=request.algorithm,
        n_clusters=request.n_clusters,
        run_name=request.run_name
    )
    
    return MLTrainResponse(run_id=run_id, status="started")

@router.get("/runs", response_model=List[MLRunResponse])
async def get_runs(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all ML training runs, sorted by creation date descending.
    """
    result = await db.execute(select(MLRun).order_by(MLRun.created_at.desc()))
    return result.scalars().all()

@router.get("/models", response_model=List[MLRunResponse])
async def get_models(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all ML training runs, mapped for the models endpoint requested by the frontend.
    """
    result = await db.execute(select(MLRun).order_by(MLRun.created_at.desc()))
    return result.scalars().all()

@router.get("/runs/{id}", response_model=MLRunResponse)
async def get_run(
    id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get details of a specific ML run by its ID.
    """
    run = await db.get(MLRun, id)
    if not run:
        raise HTTPException(status_code=404, detail="ML Run not found")
    return run

@router.post("/activate/{id}", response_model=MLRunResponse)
async def activate_run(
    id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Activate a specific ML run to be used for customer segmentation and predictions.
    All other runs will be deactivated.
    """
    run = await db.get(MLRun, id)
    if not run:
        raise HTTPException(status_code=404, detail="ML Run not found")
    
    # Deactivate all other runs
    await db.execute(select(MLRun).where(MLRun.id != id))
    result = await db.execute(select(MLRun))
    for r in result.scalars().all():
        r.is_active = (r.id == id)
        
    await db.commit()
    await db.refresh(run)
    return run

@router.post("/predict")
async def predict_customer_segment(
    features: dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Predict the segment for a given set of customer features.
    """
    try:
        prediction = await predict_segment_for_data(db, features)
        return prediction
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")
