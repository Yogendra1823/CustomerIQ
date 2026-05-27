import pytest
from httpx import AsyncClient
from app.models.customers import Customer
from app.models.segments import Segment
from app.models.transactions import Transaction
from datetime import datetime, timedelta
from decimal import Decimal

@pytest.fixture
async def sample_data(db):
    # Add customers
    c1 = Customer(
        external_id="c1",
        total_spend=Decimal("1200.50"),
        clv_estimate=Decimal("1500.00"),
        churn_probability=0.25,
        region="North America",
        value_tier="High-Value"
    )
    c2 = Customer(
        external_id="c2",
        total_spend=Decimal("300.00"),
        clv_estimate=Decimal("400.00"),
        churn_probability=0.85, # High risk
        region="Europe",
        value_tier="Low-Value"
    )
    c3 = Customer(
        external_id="c3",
        total_spend=Decimal("0.00"),
        clv_estimate=Decimal("100.00"),
        churn_probability=0.95, # High risk
        region="Asia",
        value_tier="Low-Value"
    )
    db.add_all([c1, c2, c3])
    await db.commit()

    # Add transactions
    t1 = Transaction(
        customer_id=c1.id,
        amount=Decimal("500.00"),
        order_id="TX_1001",
        transaction_date=datetime.now() - timedelta(days=5)
    )
    t2 = Transaction(
        customer_id=c1.id,
        amount=Decimal("700.50"),
        order_id="TX_1002",
        transaction_date=datetime.now() - timedelta(days=15)
    )
    t3 = Transaction(
        customer_id=c2.id,
        amount=Decimal("300.00"),
        order_id="TX_1003",
        transaction_date=datetime.now() - timedelta(days=40)
    )
    db.add_all([t1, t2, t3])
    await db.commit()

    # Add segments
    s1 = Segment(
        name="VIP",
        slug="vip",
        size=1,
        revenue_share=80.0
    )
    s2 = Segment(
        name="Churn Risk",
        slug="churn-risk",
        size=2,
        revenue_share=20.0
    )
    db.add_all([s1, s2])
    await db.commit()

    return {"c1": c1, "c2": c2, "c3": c3, "s1": s1, "s2": s2}

@pytest.mark.asyncio
async def test_read_dashboard_stats_success(client: AsyncClient, auth_headers: dict, sample_data):
    response = await client.get("/api/v1/dashboard/stats", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total_customers"] == 3
    assert data["total_revenue"] == 1500.50
    assert data["avg_clv"] == 666.67 or round(data["avg_clv"], 2) == 666.67
    assert data["high_risk_count"] == 2
    assert data["segments_count"] == 2

@pytest.mark.asyncio
async def test_read_dashboard_stats_unauthorized(client: AsyncClient, sample_data):
    response = await client.get("/api/v1/dashboard/stats")
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_read_analytics_overview_success(client: AsyncClient, auth_headers: dict, sample_data):
    response = await client.get("/api/v1/analytics/overview", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total_customers"] == 3
    assert len(data["top_segments"]) == 2
    assert data["top_segments"][0]["name"] == "Churn Risk" # Order by size desc
    assert len(data["regional_breakdown"]) == 3

@pytest.mark.asyncio
async def test_read_revenue_analytics_success(client: AsyncClient, auth_headers: dict, sample_data):
    response = await client.get("/api/v1/analytics/revenue?group_by=month", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["group_by"] == "month"
    assert len(data["data"]) >= 1

@pytest.mark.asyncio
async def test_read_churn_analytics_success(client: AsyncClient, auth_headers: dict, sample_data):
    response = await client.get("/api/v1/analytics/churn", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "data" in data

@pytest.mark.asyncio
async def test_catch_all_route_redirect_or_json(client: AsyncClient, auth_headers: dict):
    # Missing API route should return JSON 404
    response = await client.get("/api/v1/nonexistent", headers=auth_headers)
    assert response.status_code == 404
    assert "detail" in response.json()
    assert "not found" in response.json()["detail"]

    # Non-API route should redirect to /docs
    response = await client.get("/non-api-path", follow_redirects=False)
    assert response.status_code == 307
    assert response.headers.get("location") == "/docs"
