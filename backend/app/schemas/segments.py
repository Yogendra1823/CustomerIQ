from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Optional, List, Any
from uuid import UUID
from datetime import datetime
from decimal import Decimal

class SegmentBase(BaseModel):
    name: str
    slug: str
    description: Optional[str] = None
    color_hex: Optional[str] = None
    icon: Optional[str] = None
    avg_clv: Optional[Decimal] = None
    avg_order_value: Optional[Decimal] = None
    churn_rate: Optional[Decimal] = None
    size: Optional[int] = None
    revenue_share: Optional[Decimal] = None
    marketing_strategy: Optional[str] = None
    priority_score: Optional[int] = None

class SegmentCreate(SegmentBase):
    pass

class SegmentResponse(SegmentBase):
    id: int
    created_at: datetime

    @field_validator("priority_score", mode="before")
    @classmethod
    def coerce_priority_score(cls, value: Any) -> Optional[int]:
        """SQLite may return INTEGER columns as bytes in some rows."""
        if value is None:
            return None
        if isinstance(value, int):
            return value
        if isinstance(value, bytes):
            return int.from_bytes(value[:4], byteorder="little", signed=False)
        try:
            return int(value)
        except (TypeError, ValueError):
            return None

    @field_validator("avg_clv", "avg_order_value", "churn_rate", "revenue_share", mode="before")
    @classmethod
    def coerce_decimal(cls, value: Any) -> Optional[Decimal]:
        if value is None:
            return None
        if isinstance(value, Decimal):
            return value
        return Decimal(str(value))

    model_config = ConfigDict(from_attributes=True)
