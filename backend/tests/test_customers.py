import pytest
from httpx import AsyncClient
from app.models.users import User
from app.models.customers import Customer
from sqlalchemy.ext.asyncio import AsyncSession
from decimal import Decimal
import io
import uuid

@pytest.mark.asyncio
async def test_create_customer(client: AsyncClient, auth_headers: dict, db: AsyncSession):
    response = await client.post(
        "/api/v1/customers",
        json={
            "external_id": "TEST_CUST_99",
            "age": 30,
            "gender": "Female",
            "region": "Karnataka",
            "membership_status": "premium"
        },
        headers=auth_headers
    )
    assert response.status_code == 201
    data = response.json()
    assert data["external_id"] == "TEST_CUST_99"
    assert data["age"] == 30

@pytest.mark.asyncio
async def test_create_customer_invalid_missing_external_id(client: AsyncClient, auth_headers: dict):
    response = await client.post(
        "/api/v1/customers",
        json={
            "age": 30,
            "gender": "Female"
        },
        headers=auth_headers
    )
    assert response.status_code == 422

@pytest.mark.asyncio
async def test_get_customers_paginated(client: AsyncClient, auth_headers: dict, db: AsyncSession):
    # Seed a customer first
    c_id = uuid.uuid4()
    cust = Customer(
        id=c_id,
        external_id="PAGINATED_TEST_01",
        age=45,
        total_spend=0,
        avg_order_value=0,
        purchase_frequency=0
    )
    db.add(cust)
    await db.commit()
    
    response = await client.get("/api/v1/customers?page=1&limit=5", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert len(data["items"]) > 0

@pytest.mark.asyncio
async def test_get_customer_detail_success(client: AsyncClient, auth_headers: dict, db: AsyncSession):
    c_id = uuid.uuid4()
    cust = Customer(
        id=c_id,
        external_id="DETAIL_TEST_01",
        age=35,
        region="Mumbai"
    )
    db.add(cust)
    await db.commit()

    response = await client.get(f"/api/v1/customers/{c_id}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["external_id"] == "DETAIL_TEST_01"

@pytest.mark.asyncio
async def test_get_customer_detail_not_found(client: AsyncClient, auth_headers: dict):
    random_uuid = uuid.uuid4()
    response = await client.get(f"/api/v1/customers/{random_uuid}", headers=auth_headers)
    assert response.status_code == 404
    assert response.json()["detail"] == "Customer not found"

@pytest.mark.asyncio
async def test_update_customer_success(client: AsyncClient, auth_headers: dict, db: AsyncSession):
    c_id = uuid.uuid4()
    cust = Customer(
        id=c_id,
        external_id="UPDATE_TEST_01",
        age=22,
        region="Delhi"
    )
    db.add(cust)
    await db.commit()

    response = await client.put(
        f"/api/v1/customers/{c_id}",
        json={"age": 23, "region": "Delhi NCR"},
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["age"] == 23
    assert data["region"] == "Delhi NCR"

@pytest.mark.asyncio
async def test_update_customer_not_found(client: AsyncClient, auth_headers: dict):
    random_uuid = uuid.uuid4()
    response = await client.put(
        f"/api/v1/customers/{random_uuid}",
        json={"age": 25},
        headers=auth_headers
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Customer not found"

@pytest.mark.asyncio
async def test_get_customers_filters(client: AsyncClient, auth_headers: dict, db: AsyncSession):
    c1 = Customer(
        external_id="REGION_A_01",
        region="RegionA",
        value_tier="premium"
    )
    c2 = Customer(
        external_id="REGION_B_01",
        region="RegionB",
        value_tier="standard"
    )
    db.add_all([c1, c2])
    await db.commit()

    # Filter by region
    response = await client.get("/api/v1/customers?region=RegionA", headers=auth_headers)
    assert response.status_code == 200
    items = response.json()["items"]
    assert len(items) == 1
    assert items[0]["external_id"] == "REGION_A_01"

    # Filter by value tier
    response = await client.get("/api/v1/customers?value_tier=standard", headers=auth_headers)
    assert response.status_code == 200
    items = response.json()["items"]
    assert len(items) == 1
    assert items[0]["external_id"] == "REGION_B_01"

@pytest.mark.asyncio
async def test_get_customers_search(client: AsyncClient, auth_headers: dict, db: AsyncSession):
    c1 = Customer(external_id="UNIQUE_SEARCH_PREFIX_123")
    c2 = Customer(external_id="ANOTHER_CUSTOMER_456")
    db.add_all([c1, c2])
    await db.commit()

    response = await client.get("/api/v1/customers?search=SEARCH_PREFIX", headers=auth_headers)
    assert response.status_code == 200
    items = response.json()["items"]
    assert len(items) == 1
    assert items[0]["external_id"] == "UNIQUE_SEARCH_PREFIX_123"

@pytest.mark.asyncio
async def test_bulk_upload_success(client: AsyncClient, auth_headers: dict, db: AsyncSession):
    csv_data = "external_id,age,gender,region,membership_status,total_spend\nCUST_CSV_1,34,Male,North,standard,250.00\nCUST_CSV_2,29,Female,South,premium,1500.00\n"
    csv_file = io.BytesIO(csv_data.encode("utf-8"))
    
    response = await client.post(
        "/api/v1/customers/upload",
        files={"file": ("test.csv", csv_file, "text/csv")},
        headers=auth_headers
    )
    assert response.status_code == 200
    assert response.json()["rows_imported"] == 2
    assert response.json()["message"] == "Upload successful"

@pytest.mark.asyncio
async def test_bulk_upload_failure_invalid_csv(client: AsyncClient, auth_headers: dict):
    # Missing required headers/corrupt columns causing parse failures
    csv_data = "external_id,age,gender,region,membership_status,annual_income\nCUST_ERR,invalid_age,Male,North,standard,100\n"
    csv_file = io.BytesIO(csv_data.encode("utf-8"))
    
    response = await client.post(
        "/api/v1/customers/upload",
        files={"file": ("test.csv", csv_file, "text/csv")},
        headers=auth_headers
    )
    # The int(row["age"]) conversion will throw a ValueError causing a 400
    assert response.status_code == 400
    assert "Failed to process CSV file" in response.json()["detail"]

@pytest.mark.asyncio
async def test_predict_customer_segment_not_found(client: AsyncClient, auth_headers: dict):
    random_uuid = uuid.uuid4()
    response = await client.get(f"/api/v1/customers/{random_uuid}/predict", headers=auth_headers)
    assert response.status_code == 404
    assert response.json()["detail"] == "Customer not found"
