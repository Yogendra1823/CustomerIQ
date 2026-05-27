from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from .config import settings

from .routers import auth, customers, segments, analytics, ml, export, dashboard
from .routers.customers import bulk_upload_customers

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield

app = FastAPI(
    title="CustomerIQ API",
    description="Intelligent Segmentation & Analytics Platform API",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers under /api/v1 prefix
app.include_router(auth.router, prefix="/api/v1")
app.include_router(customers.router, prefix="/api/v1")
app.include_router(segments.router, prefix="/api/v1")
app.include_router(analytics.router, prefix="/api/v1")
app.include_router(ml.router, prefix="/api/v1")
app.include_router(export.router, prefix="/api/v1")
app.include_router(dashboard.router, prefix="/api/v1")

# Frontend upload API alias mapping
app.post("/api/v1/upload", tags=["Customers"])(bulk_upload_customers)

from fastapi.responses import RedirectResponse, JSONResponse

@app.get("/", include_in_schema=False)
async def root():
    return RedirectResponse(url="/docs")

@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "ok"}

@app.api_route("/{path_name:path}", include_in_schema=False)
async def catch_all(request: Request, path_name: str):
    if path_name.startswith("api/"):
        return JSONResponse(
            status_code=404,
            content={"detail": f"API endpoint '/{path_name}' not found. Please refer to /docs for the API schema."}
        )
    return RedirectResponse(url="/docs")
