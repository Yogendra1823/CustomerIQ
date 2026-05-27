from sqlalchemy import Column, Integer, String, Numeric, DateTime, func, ForeignKey, Uuid
from sqlalchemy.orm import relationship
import uuid
from .base import Base

class Customer(Base):
    __tablename__ = "customers"
    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    external_id = Column(String(100), unique=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    # Demographics
    age = Column(Integer)
    gender = Column(String(20))
    region = Column(String(100), index=True)
    country = Column(String(100), default="India")
    membership_status = Column(String(20), default="standard")
    # Financial
    annual_income = Column(Numeric(12, 2))
    total_spend = Column(Numeric(12, 2), default=0)
    avg_order_value = Column(Numeric(10, 2), default=0)
    clv_estimate = Column(Numeric(12, 2))
    # Behavioral
    purchase_frequency = Column(Integer, default=0)
    days_since_last_purchase = Column(Integer)
    cart_abandonment_rate = Column(Numeric(5, 4))
    return_rate = Column(Numeric(5, 4))
    # Engagement
    email_open_rate = Column(Numeric(5, 4))
    app_usage_score = Column(Numeric(5, 2))
    loyalty_points = Column(Integer, default=0)
    referral_count = Column(Integer, default=0)
    # ML Outputs
    rfm_score = Column(Numeric(5, 2))
    engagement_index = Column(Numeric(5, 2))
    churn_probability = Column(Numeric(5, 4))
    value_tier = Column(String(20), index=True)
    predicted_clv_90d = Column(Numeric(12, 2))
    preferred_category = Column(String(100))
    
    segment_id = Column(Integer, ForeignKey("segments.id"), index=True)
    segment = relationship("Segment", back_populates="customers")
    transactions = relationship("Transaction", back_populates="customer")
