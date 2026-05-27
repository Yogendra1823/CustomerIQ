from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy import func
from typing import List, Optional
from uuid import UUID

from ..dependencies import get_db, get_current_user
from ..models.users import User
from ..models.customers import Customer
from ..schemas.customers import CustomerResponse, CustomerDetailResponse, CustomerCreate, CustomerUpdate, PaginatedCustomersResponse

router = APIRouter(prefix="/customers", tags=["Customers"])

@router.get("", response_model=PaginatedCustomersResponse)
async def get_customers(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    segment_id: Optional[int] = None,
    region: Optional[str] = None,
    value_tier: Optional[str] = None,
    search: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    offset = (page - 1) * limit
    
    query = select(Customer)
    if segment_id:
        query = query.where(Customer.segment_id == segment_id)
    if region:
        query = query.where(Customer.region == region)
    if value_tier:
        query = query.where(Customer.value_tier == value_tier)
    if search:
        query = query.where(Customer.external_id.ilike(f"%{search}%"))
        
    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    total = await db.scalar(count_query)
    
    # Get paginated results
    query = query.offset(offset).limit(limit)
    result = await db.execute(query)
    customers = result.scalars().all()
    
    return PaginatedCustomersResponse(
        items=customers,
        total=total,
        page=page,
        limit=limit,
        pages=(total + limit - 1) // limit
    )

@router.get("/{id}", response_model=CustomerDetailResponse)
async def get_customer(id: UUID, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = await db.execute(
        select(Customer)
        .options(selectinload(Customer.transactions), selectinload(Customer.segment))
        .where(Customer.id == id)
    )
    customer = result.scalars().first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer

@router.post("", response_model=CustomerResponse, status_code=201)
async def create_customer(customer_in: CustomerCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    new_customer = Customer(**customer_in.model_dump())
    db.add(new_customer)
    await db.commit()
    await db.refresh(new_customer)
    return new_customer

@router.put("/{id}", response_model=CustomerResponse)
async def update_customer(id: UUID, customer_in: CustomerUpdate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = await db.execute(select(Customer).where(Customer.id == id))
    customer = result.scalars().first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
        
    update_data = customer_in.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(customer, key, value)
        
    await db.commit()
    await db.refresh(customer)
    return customer

@router.post("/upload")
async def bulk_upload_customers(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Bulk upload customer data from a CSV file.
    Parses headers, validates rows, saves records, and returns upload summary.
    """
    import csv
    import io
    import time
    from decimal import Decimal
    
    try:
        contents = await file.read()
        buffer = io.StringIO(contents.decode("utf-8"))
        reader = csv.DictReader(buffer)
        
        imported_count = 0
        
        for row in reader:
            external_id = row.get("external_id") or row.get("Customer ID") or f"CUST_{imported_count}_{int(time.time())}"
            
            # Create Customer model
            customer = Customer(
                external_id=external_id,
                age=int(row["age"]) if row.get("age") else None,
                gender=row.get("gender") or "Unknown",
                region=row.get("region") or "India",
                membership_status=row.get("membership_status") or "standard",
                annual_income=Decimal(row["annual_income"]) if row.get("annual_income") else Decimal("0"),
                total_spend=Decimal(row["total_spend"]) if row.get("total_spend") else Decimal("0"),
                avg_order_value=Decimal(row["avg_order_value"]) if row.get("avg_order_value") else Decimal("0"),
                clv_estimate=Decimal(row["clv_estimate"]) if row.get("clv_estimate") else Decimal("0"),
                purchase_frequency=int(row["purchase_frequency"]) if row.get("purchase_frequency") else 0,
                days_since_last_purchase=int(row["days_since_last_purchase"]) if row.get("days_since_last_purchase") else None,
                cart_abandonment_rate=Decimal(row["cart_abandonment_rate"]) if row.get("cart_abandonment_rate") else Decimal("0"),
                return_rate=Decimal(row["return_rate"]) if row.get("return_rate") else Decimal("0"),
                email_open_rate=Decimal(row["email_open_rate"]) if row.get("email_open_rate") else Decimal("0"),
                app_usage_score=Decimal(row["app_usage_score"]) if row.get("app_usage_score") else Decimal("0"),
                loyalty_points=int(row["loyalty_points"]) if row.get("loyalty_points") else 0,
                referral_count=int(row["referral_count"]) if row.get("referral_count") else 0,
                rfm_score=Decimal(row["rfm_score"]) if row.get("rfm_score") else Decimal("0"),
                engagement_index=Decimal(row["engagement_index"]) if row.get("engagement_index") else Decimal("0"),
                churn_probability=Decimal(row["churn_probability"]) if row.get("churn_probability") else Decimal("0"),
                value_tier=row.get("value_tier") or "standard",
                preferred_category=row.get("preferred_category") or "General"
            )
            
            db.add(customer)
            imported_count += 1
            
        await db.commit()
        return {"filename": file.filename, "rows_imported": imported_count, "message": "Upload successful"}
        
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=f"Failed to process CSV file: {str(e)}")

@router.get("/{id}/predict")
async def predict_customer_segment(
    id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Predict the segment for a single customer using their existing features.
    Saves the prediction results to the customer record.
    """
    customer = await db.get(Customer, id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
        
    # Build feature dict
    features = {
        "age": customer.age or 34,
        "annual_income": float(customer.annual_income or 0.0),
        "total_spend": float(customer.total_spend or 0.0),
        "avg_order_value": float(customer.avg_order_value or 0.0),
        "purchase_frequency": customer.purchase_frequency,
        "days_since_last_purchase": customer.days_since_last_purchase or 45,
        "cart_abandonment_rate": float(customer.cart_abandonment_rate or 0.0),
        "email_open_rate": float(customer.email_open_rate or 0.0),
        "app_usage_score": float(customer.app_usage_score or 0.0),
        "loyalty_points": customer.loyalty_points,
        "return_rate": float(customer.return_rate or 0.0),
        "referral_count": customer.referral_count,
        "clv_estimate": float(customer.clv_estimate or 0.0),
        "engagement_index": float(customer.engagement_index or 0.0),
        "rfm_score": float(customer.rfm_score or 0.0)
    }
    
    from ..services.ml_service import predict_segment_for_data
    from decimal import Decimal
    
    try:
        prediction = await predict_segment_for_data(db, features)
        
        # Save to DB
        customer.segment_id = prediction["segment_id"]
        customer.churn_probability = Decimal(str(prediction["churn_probability"]))
        customer.value_tier = "premium" if prediction["segment_name"] == "Premium Loyalists" else "standard"
        await db.commit()
        await db.refresh(customer)
        
        return prediction
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")
