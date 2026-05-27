from sqlalchemy import Column, Integer, String, Text, Numeric, DateTime, func
from sqlalchemy.orm import relationship
from .base import Base

class Segment(Base):
    __tablename__ = "segments"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False)
    slug = Column(String(100), unique=True, nullable=False)
    description = Column(Text)
    color_hex = Column(String(7))
    icon = Column(String(50))
    avg_clv = Column(Numeric(12, 2))
    avg_order_value = Column(Numeric(10, 2))
    churn_rate = Column(Numeric(5, 4))
    size = Column(Integer)
    revenue_share = Column(Numeric(5, 4))
    marketing_strategy = Column(Text)
    priority_score = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    customers = relationship("Customer", back_populates="segment")
