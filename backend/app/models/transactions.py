from sqlalchemy import Column, Integer, String, Numeric, DateTime, func, ForeignKey, Uuid
from sqlalchemy.orm import relationship
import uuid
from .base import Base

class Transaction(Base):
    __tablename__ = "transactions"
    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    customer_id = Column(Uuid, ForeignKey("customers.id", ondelete="CASCADE"), index=True)
    order_id = Column(String(100), unique=True, nullable=False)
    transaction_date = Column(DateTime(timezone=True), nullable=False, index=True)
    amount = Column(Numeric(10, 2), nullable=False)
    category = Column(String(100), index=True)
    items_count = Column(Integer)
    status = Column(String(20))
    channel = Column(String(50))
    discount_applied = Column(Numeric(5, 4), default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    customer = relationship("Customer", back_populates="transactions")
