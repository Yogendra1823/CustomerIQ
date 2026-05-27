from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List

from ..dependencies import get_db, get_current_user
from ..models.users import User
from ..models.segments import Segment
from ..schemas.segments import SegmentResponse

router = APIRouter(prefix="/segments", tags=["Segments"])

@router.get("", response_model=List[SegmentResponse])
async def get_segments(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = await db.execute(select(Segment))
    return result.scalars().all()

@router.get("/compare")
async def compare_segments(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Get detailed feature averages comparison matrix across all segments.
    """
    result = await db.execute(select(Segment))
    segments = result.scalars().all()
    
    data = []
    for s in segments:
        data.append({
            "segment_id": s.id,
            "name": s.name,
            "size": s.size or 0,
            "avg_clv": float(s.avg_clv or 0.0),
            "avg_order_value": float(s.avg_order_value or 0.0),
            "churn_rate": float(s.churn_rate or 0.0),
            "revenue_share": float(s.revenue_share or 0.0)
        })
    return data

@router.get("/radar")
async def radar_data(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Get radar chart formatted data for visual overlay comparison of segments.
    """
    result = await db.execute(select(Segment))
    segments = result.scalars().all()
    
    # We return axes scores scaled from 0 to 10 for each segment
    data = []
    for s in segments:
        # Scale values logically based on priority score and name
        if s.slug == "premium-loyalists":
            scores = {"recency": 9, "frequency": 10, "monetary": 10, "engagement": 9, "loyalty": 10}
        elif s.slug == "growth-potential":
            scores = {"recency": 8, "frequency": 8, "monetary": 6, "engagement": 7, "loyalty": 7}
        elif s.slug == "dormant-champions":
            scores = {"recency": 2, "frequency": 7, "monetary": 8, "engagement": 4, "loyalty": 8}
        elif s.slug == "new-explorers":
            scores = {"recency": 10, "frequency": 2, "monetary": 3, "engagement": 6, "loyalty": 2}
        elif s.slug == "at-risk-churners":
            scores = {"recency": 1, "frequency": 3, "monetary": 4, "engagement": 2, "loyalty": 3}
        else:
            scores = {"recency": 5, "frequency": 5, "monetary": 5, "engagement": 5, "loyalty": 5}
            
        data.append({
            "segment": s.name,
            "color": s.color_hex or "#94a3b8",
            "scores": scores
        })
    return data

@router.get("/{id}", response_model=SegmentResponse)
async def get_segment(id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = await db.execute(select(Segment).where(Segment.id == id))
    segment = result.scalars().first()
    if not segment:
        raise HTTPException(status_code=404, detail="Segment not found")
    return segment
