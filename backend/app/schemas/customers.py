from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from uuid import UUID
from datetime import datetime
from decimal import Decimal
from .transactions import TransactionResponse
from .segments import SegmentResponse

class CustomerBase(BaseModel):
    external_id: str
    age: Optional[int] = None
    gender: Optional[str] = None
    region: Optional[str] = None
    country: str = "India"
    membership_status: str = "standard"
    
    annual_income: Optional[Decimal] = None
    total_spend: Decimal = Decimal('0.0')
    avg_order_value: Decimal = Decimal('0.0')
    clv_estimate: Optional[Decimal] = None
    
    purchase_frequency: int = 0
    days_since_last_purchase: Optional[int] = None
    cart_abandonment_rate: Optional[Decimal] = None
    return_rate: Optional[Decimal] = None
    
    email_open_rate: Optional[Decimal] = None
    app_usage_score: Optional[Decimal] = None
    loyalty_points: int = 0
    referral_count: int = 0

class CustomerCreate(CustomerBase):
    pass

class CustomerUpdate(BaseModel):
    age: Optional[int] = None
    gender: Optional[str] = None
    region: Optional[str] = None
    annual_income: Optional[Decimal] = None
    membership_status: Optional[str] = None

class CustomerResponse(CustomerBase):
    id: UUID
    rfm_score: Optional[Decimal] = None
    engagement_index: Optional[Decimal] = None
    churn_probability: Optional[Decimal] = None
    value_tier: Optional[str] = None
    predicted_clv_90d: Optional[Decimal] = None
    preferred_category: Optional[str] = None
    segment_id: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class CustomerDetailResponse(CustomerResponse):
    transactions: List[TransactionResponse] = []
    segment: Optional[SegmentResponse] = None

class PaginatedCustomersResponse(BaseModel):
    items: List[CustomerResponse]
    total: int
    page: int
    limit: int
    pages: int
