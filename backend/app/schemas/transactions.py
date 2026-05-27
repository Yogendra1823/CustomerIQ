from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from uuid import UUID
from datetime import datetime
from decimal import Decimal

class TransactionBase(BaseModel):
    order_id: str
    transaction_date: datetime
    amount: Decimal
    category: Optional[str] = None
    items_count: Optional[int] = None
    status: Optional[str] = None
    channel: Optional[str] = None
    discount_applied: Optional[Decimal] = None

class TransactionCreate(TransactionBase):
    customer_id: UUID

class TransactionResponse(TransactionBase):
    id: UUID
    customer_id: UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
