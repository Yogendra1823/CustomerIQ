from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from .config import settings

connect_args = {}
if "postgresql" in settings.DATABASE_URL:
    connect_args["ssl"] = True

engine_kwargs = {
    "echo": settings.ENVIRONMENT == "development",
    "connect_args": connect_args
}
if "sqlite" not in settings.DATABASE_URL:
    engine_kwargs["pool_size"] = 5
    engine_kwargs["max_overflow"] = 10

engine = create_async_engine(settings.DATABASE_URL, **engine_kwargs)

AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
