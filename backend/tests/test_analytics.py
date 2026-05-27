import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.customers import Customer
from app.models.transactions import Transaction
from app.models.segments import Segment
from decimal import Decimal
import uuid
from datetime import datetime

@pytest.mark.asyncio
async def test_analytics_endpoints(client: AsyncClient, auth_headers: dict, db: AsyncSession):
    # Seed a segment, a customer and a transaction
    seg = Segment(
        id=1,
        name="Premium Loyalists",
        slug="premium-loyalists",
        description="VIP Customers",
        color_hex="#00FF00",
        icon="star",
        avg_clv=Decimal("250000.00"),
        avg_order_value=Decimal("5000.00"),
        churn_rate=Decimal("0.02"),
        size=10,
        revenue_share=Decimal("0.45"),
        marketing_strategy="Keep VIP happy",
        priority_score=10
    )
    db.add(seg)
    await db.flush()

    cust_id = uuid.uuid4()
    cust = Customer(
        id=cust_id,
        external_id="CUST_ANALYTICS_01",
        age=30,
        region="Karnataka",
        total_spend=Decimal("5000.00"),
        clv_estimate=Decimal("15000.00"),
        churn_probability=Decimal("0.10"),
        segment_id=1
    )
    db.add(cust)
    await db.flush()

    tx = Transaction(
        id=uuid.uuid4(),
        customer_id=cust_id,
        order_id="ORD_ANALYTICS_01",
        transaction_date=datetime.now(),
        amount=Decimal("5000.00"),
        category="Electronics",
        status="completed"
    )
    db.add(tx)
    await db.commit()

    # Test /overview
    response = await client.get("/api/v1/analytics/overview", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "total_customers" in data
    assert "total_revenue" in data

    # Test /revenue
    response = await client.get("/api/v1/analytics/revenue?group_by=day", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["group_by"] == "day"
    assert len(data["data"]) > 0

    # Test /churn
    response = await client.get("/api/v1/analytics/churn", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "data" in data

    # Test /cohort
    response = await client.get("/api/v1/analytics/cohort", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "cohorts" in data

    # Test /rfm
    response = await client.get("/api/v1/analytics/rfm", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "rfm_points" in data

    # Test /geographic
    response = await client.get("/api/v1/analytics/geographic", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0

    # Test /trends
    response = await client.get("/api/v1/analytics/trends", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "trends" in data
