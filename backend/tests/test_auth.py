import pytest
from httpx import AsyncClient
from app.models.users import User
from app.core.security import create_refresh_token, get_password_hash
from app.config import settings
import uuid
from jose import jwt
from datetime import datetime, timedelta

@pytest.mark.asyncio
async def test_login_success(client: AsyncClient, test_user: User):
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "test@customeriq.com", "password": "TestPassword@123"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"

@pytest.mark.asyncio
async def test_login_failure(client: AsyncClient):
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "nonexistent@customeriq.com", "password": "WrongPassword"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect email or password"

@pytest.mark.asyncio
async def test_login_invalid_email(client: AsyncClient):
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "invalid-email", "password": "password"}
    )
    # Pydantic schema validation failure (email format)
    assert response.status_code == 422

@pytest.mark.asyncio
async def test_read_users_me_success(client: AsyncClient, auth_headers: dict):
    response = await client.get("/api/v1/auth/me", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["email"] == "test@customeriq.com"

@pytest.mark.asyncio
async def test_read_users_me_unauthorized(client: AsyncClient):
    response = await client.get("/api/v1/auth/me")
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_refresh_token_success(client: AsyncClient, test_user: User):
    refresh_token = create_refresh_token(data={"sub": str(test_user.id)})
    response = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data

@pytest.mark.asyncio
async def test_refresh_token_invalid_signature(client: AsyncClient):
    # Token signed with wrong secret
    bad_token = jwt.encode({"sub": str(uuid.uuid4())}, "wrong-secret", algorithm=settings.ALGORITHM)
    response = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": bad_token}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Could not validate refresh token"

@pytest.mark.asyncio
async def test_refresh_token_expired(client: AsyncClient):
    # Expired token
    expire = datetime.utcnow() - timedelta(days=1)
    payload = {"sub": str(uuid.uuid4()), "exp": expire}
    expired_token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    response = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": expired_token}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Could not validate refresh token"

@pytest.mark.asyncio
async def test_refresh_token_nonexistent_user(client: AsyncClient):
    bad_token = create_refresh_token(data={"sub": str(uuid.uuid4())})
    response = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": bad_token}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Could not validate refresh token"

@pytest.mark.asyncio
async def test_refresh_token_inactive_user(client: AsyncClient, db):
    inactive_user = User(
        email="inactive@customeriq.com",
        hashed_password=get_password_hash("password123"),
        full_name="Inactive User",
        role="analyst",
        is_active=False
    )
    db.add(inactive_user)
    await db.commit()
    await db.refresh(inactive_user)
    
    refresh_token = create_refresh_token(data={"sub": str(inactive_user.id)})
    response = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Could not validate refresh token"

@pytest.mark.asyncio
async def test_logout_endpoint(client: AsyncClient, auth_headers: dict):
    response = await client.post("/api/v1/auth/logout", headers=auth_headers)
    assert response.status_code == 204

@pytest.mark.asyncio
async def test_signup_success(client: AsyncClient, db):
    response = await client.post(
        "/api/v1/auth/signup",
        json={"email": "newuser@customeriq.com", "password": "NewPassword123", "full_name": "New User"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["user"]["email"] == "newuser@customeriq.com"

@pytest.mark.asyncio
async def test_signup_email_exists(client: AsyncClient, test_user: User):
    response = await client.post(
        "/api/v1/auth/signup",
        json={"email": "test@customeriq.com", "password": "NewPassword123", "full_name": "New User"}
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Email already registered"
