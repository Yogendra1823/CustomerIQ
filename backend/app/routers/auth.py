from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
import httpx
import uuid
from ..database import AsyncSessionLocal
from ..schemas.users import UserCreate, UserResponse, Token, LoginRequest, RefreshTokenRequest
from ..models.users import User
from ..core.security import verify_password, get_password_hash, create_access_token, create_refresh_token
from ..dependencies import get_db, get_current_user
from ..config import settings
from jose import JWTError, jwt

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/signup", response_model=Token)
async def signup(request: UserCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == request.email))
    if result.scalars().first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    new_user = User(
        id=uuid.uuid4(),
        email=request.email,
        full_name=request.full_name,
        role=request.role or "analyst",
        hashed_password=get_password_hash(request.password),
        is_active=True
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    
    access_token = create_access_token(data={"sub": str(new_user.id)})
    refresh_token = create_refresh_token(data={"sub": str(new_user.id)})
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": UserResponse.model_validate(new_user),
    }

@router.post("/login", response_model=Token)
async def login(request: LoginRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == request.email))
    user = result.scalars().first()
    
    if not user or not verify_password(request.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": UserResponse.model_validate(user),
    }

@router.post("/refresh", response_model=Token)
async def refresh_token(request: RefreshTokenRequest, db: AsyncSession = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate refresh token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(request.refresh_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
        
    import uuid
    try:
        user_uuid = uuid.UUID(user_id)
    except ValueError:
        raise credentials_exception
        
    user = await db.get(User, user_uuid)
    if user is None or not user.is_active:
        raise credentials_exception
        
    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": UserResponse.model_validate(user),
    }

@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout():
    return None

@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.get("/google/login")
async def google_login(request: Request):
    if not settings.GOOGLE_CLIENT_ID:
        raise HTTPException(status_code=500, detail="Google Auth not configured")
    
    if settings.GOOGLE_REDIRECT_URI:
        redirect_uri = settings.GOOGLE_REDIRECT_URI
    else:
        proto = request.headers.get("x-forwarded-proto", "http")
        host = request.headers.get("x-forwarded-host", request.base_url.netloc)
        redirect_uri = f"{proto}://{host}/api/v1/auth/google/callback"
        
    google_auth_url = f"https://accounts.google.com/o/oauth2/v2/auth?response_type=code&client_id={settings.GOOGLE_CLIENT_ID}&redirect_uri={redirect_uri}&scope=openid%20email%20profile&access_type=offline"
    return RedirectResponse(google_auth_url)

@router.get("/google/callback")
async def google_callback(code: str, request: Request, db: AsyncSession = Depends(get_db)):
    if not settings.GOOGLE_CLIENT_ID or not settings.GOOGLE_CLIENT_SECRET:
        raise HTTPException(status_code=500, detail="Google Auth not configured")
        
    if settings.GOOGLE_REDIRECT_URI:
        redirect_uri = settings.GOOGLE_REDIRECT_URI
    else:
        proto = request.headers.get("x-forwarded-proto", "http")
        host = request.headers.get("x-forwarded-host", request.base_url.netloc)
        redirect_uri = f"{proto}://{host}/api/v1/auth/google/callback"
    
    async with httpx.AsyncClient() as client:
        # Exchange code for token
        token_response = await client.post(
            "https://oauth2.googleapis.com/token",
            data={
                "code": code,
                "client_id": settings.GOOGLE_CLIENT_ID,
                "client_secret": settings.GOOGLE_CLIENT_SECRET,
                "redirect_uri": redirect_uri,
                "grant_type": "authorization_code",
            },
        )
        token_data = token_response.json()
        
        if "access_token" not in token_data:
            raise HTTPException(status_code=400, detail="Failed to authenticate with Google")
            
        # Get user profile
        profile_response = await client.get(
            "https://www.googleapis.com/oauth2/v2/userinfo",
            headers={"Authorization": f"Bearer {token_data['access_token']}"}
        )
        profile_data = profile_response.json()
        
    email = profile_data.get("email")
    if not email:
        raise HTTPException(status_code=400, detail="Google profile did not return an email")
        
    # Check if user exists
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalars().first()
    
    if not user:
        # Create new user
        user = User(
            id=uuid.uuid4(),
            email=email,
            full_name=profile_data.get("name", "Google User"),
            hashed_password=get_password_hash(uuid.uuid4().hex), # Random password
            role="user",
            is_active=True
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        
    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})
    
    # Redirect to frontend with tokens
    frontend_url = "http://localhost:5173" if settings.ENVIRONMENT == "development" else "https://customeriq-dashboard.vercel.app"
    return RedirectResponse(f"{frontend_url}/auth/callback?access_token={access_token}&refresh_token={refresh_token}")
