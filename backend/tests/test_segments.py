import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.segments import Segment
from decimal import Decimal

@pytest.fixture(autouse=True)
async def seed_segment(db: AsyncSession):
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
    await db.commit()

@pytest.mark.asyncio
async def test_get_segments(client: AsyncClient, auth_headers: dict):
    response = await client.get("/api/v1/segments", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert data[0]["name"] == "Premium Loyalists"
    assert data[0]["slug"] == "premium-loyalists"

@pytest.mark.asyncio
async def test_get_segments_unauthorized(client: AsyncClient):
    response = await client.get("/api/v1/segments")
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_get_segment_detail(client: AsyncClient, auth_headers: dict):
    response = await client.get("/api/v1/segments/1", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["name"] == "Premium Loyalists"

@pytest.mark.asyncio
async def test_get_segment_detail_unauthorized(client: AsyncClient):
    response = await client.get("/api/v1/segments/1")
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_get_segment_detail_not_found(client: AsyncClient, auth_headers: dict):
    response = await client.get("/api/v1/segments/999", headers=auth_headers)
    assert response.status_code == 404
    assert response.json()["detail"] == "Segment not found"

@pytest.mark.asyncio
async def test_compare_segments(client: AsyncClient, auth_headers: dict):
    response = await client.get("/api/v1/segments/compare", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert "avg_clv" in data[0]
    assert "avg_order_value" in data[0]

@pytest.mark.asyncio
async def test_compare_segments_unauthorized(client: AsyncClient):
    response = await client.get("/api/v1/segments/compare")
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_radar_data(client: AsyncClient, auth_headers: dict):
    response = await client.get("/api/v1/segments/radar", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert "scores" in data[0]
    assert "recency" in data[0]["scores"]

@pytest.mark.asyncio
async def test_radar_data_unauthorized(client: AsyncClient):
    response = await client.get("/api/v1/segments/radar")
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_radar_data_custom_segment(client: AsyncClient, auth_headers: dict, db: AsyncSession):
    # Add a segment with a non-predefined slug to trigger the default fallback scoring
    custom_seg = Segment(
        id=2,
        name="Custom Cohort",
        slug="custom-cohort",
        description="Dynamic Custom Segment",
        color_hex="#123456",
        size=5,
        revenue_share=Decimal("0.10")
    )
    db.add(custom_seg)
    await db.commit()

    response = await client.get("/api/v1/segments/radar", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    
    # Filter the custom segment from response
    custom_data = [item for item in data if item["segment"] == "Custom Cohort"]
    assert len(custom_data) == 1
    scores = custom_data[0]["scores"]
    # Check default scores (all 5s)
    assert scores["recency"] == 5
    assert scores["frequency"] == 5
    assert scores["monetary"] == 5
    assert scores["engagement"] == 5
    assert scores["loyalty"] == 5
