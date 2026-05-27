import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.customers import Customer
from decimal import Decimal
import uuid

@pytest.mark.asyncio
async def test_export_customers_csv(client: AsyncClient, auth_headers: dict, db: AsyncSession):
    # Seed a customer
    cust = Customer(
        id=uuid.uuid4(),
        external_id="EXPORT_CUST_CSV",
        age=28,
        region="Maharashtra",
        total_spend=Decimal("15000.00"),
        clv_estimate=Decimal("45000.00"),
        churn_probability=Decimal("0.05")
    )
    db.add(cust)
    await db.commit()

    response = await client.get("/api/v1/export/customers/csv", headers=auth_headers)
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/csv; charset=utf-8"
    assert "EXPORT_CUST_CSV" in response.text

@pytest.mark.asyncio
async def test_export_report_pdf(client: AsyncClient, auth_headers: dict):
    response = await client.get("/api/v1/export/report/pdf", headers=auth_headers)
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert response.content.startswith(b"%PDF")
