import pytest
from httpx import AsyncClient
from unittest.mock import patch, AsyncMock
from app.models.users import User
from sqlalchemy.future import select

@pytest.mark.asyncio
async def test_google_login_redirect(client: AsyncClient):
    response = await client.get("/api/v1/auth/google/login", follow_redirects=False)
    assert response.status_code == 307
    location = response.headers.get("location")
    assert "accounts.google.com" in location
    assert "response_type=code" in location
    assert "client_id=" in location
    assert "redirect_uri=" in location

@pytest.mark.asyncio
async def test_google_login_missing_settings(client: AsyncClient):
    with patch("app.routers.auth.settings") as mock_settings:
        mock_settings.GOOGLE_CLIENT_ID = ""
        response = await client.get("/api/v1/auth/google/login")
        assert response.status_code == 500
        assert response.json()["detail"] == "Google Auth not configured"

@pytest.mark.asyncio
async def test_google_callback_success_existing_user(client: AsyncClient, db, test_user: User):
    mock_token_resp = MagicMock()
    mock_token_resp.json.return_value = {"access_token": "mock_access_token"}
    
    mock_profile_resp = MagicMock()
    mock_profile_resp.json.return_value = {
        "email": "test@customeriq.com",
        "name": "Test User"
    }

    with patch("app.routers.auth.httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client_cls.return_value.__aenter__.return_value = mock_client
        mock_client.post.return_value = mock_token_resp
        mock_client.get.return_value = mock_profile_resp
        
        response = await client.get("/api/v1/auth/google/callback?code=mockcode", follow_redirects=False)
        assert response.status_code == 307
        location = response.headers.get("location")
        assert "/auth/callback" in location
        assert "access_token=" in location
        assert "refresh_token=" in location

@pytest.mark.asyncio
async def test_google_callback_success_new_user(client: AsyncClient, db):
    # Ensure user does not exist
    result = await db.execute(select(User).where(User.email == "newgoogleuser@customeriq.com"))
    assert result.scalars().first() is None

    mock_token_resp = MagicMock()
    mock_token_resp.json.return_value = {"access_token": "mock_access_token"}
    
    mock_profile_resp = MagicMock()
    mock_profile_resp.json.return_value = {
        "email": "newgoogleuser@customeriq.com",
        "name": "New Google User"
    }

    with patch("app.routers.auth.httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client_cls.return_value.__aenter__.return_value = mock_client
        mock_client.post.return_value = mock_token_resp
        mock_client.get.return_value = mock_profile_resp
        
        response = await client.get("/api/v1/auth/google/callback?code=mockcode", follow_redirects=False)
        assert response.status_code == 307
        location = response.headers.get("location")
        assert "/auth/callback" in location
        
        # Verify user was created in DB
        result = await db.execute(select(User).where(User.email == "newgoogleuser@customeriq.com"))
        user = result.scalars().first()
        assert user is not None
        assert user.full_name == "New Google User"

@pytest.mark.asyncio
async def test_google_callback_missing_token(client: AsyncClient):
    mock_token_resp = MagicMock()
    mock_token_resp.json.return_value = {} # No access_token

    with patch("app.routers.auth.httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client_cls.return_value.__aenter__.return_value = mock_client
        mock_client.post.return_value = mock_token_resp
        
        response = await client.get("/api/v1/auth/google/callback?code=mockcode")
        assert response.status_code == 400
        assert response.json()["detail"] == "Failed to authenticate with Google"

@pytest.mark.asyncio
async def test_google_callback_missing_email(client: AsyncClient):
    mock_token_resp = MagicMock()
    mock_token_resp.json.return_value = {"access_token": "mock_access_token"}
    
    mock_profile_resp = MagicMock()
    mock_profile_resp.json.return_value = {
        "name": "User Without Email"
    }

    with patch("app.routers.auth.httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client_cls.return_value.__aenter__.return_value = mock_client
        mock_client.post.return_value = mock_token_resp
        mock_client.get.return_value = mock_profile_resp
        
        response = await client.get("/api/v1/auth/google/callback?code=mockcode")
        assert response.status_code == 400
        assert response.json()["detail"] == "Google profile did not return an email"

from unittest.mock import MagicMock
