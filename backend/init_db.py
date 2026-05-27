import asyncio
import sys
import os

# Add backend to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.models.base import Base
from sqlalchemy.ext.asyncio import create_async_engine
from app.config import settings
from app.models.users import User
from app.models.customers import Customer
from app.models.segments import Segment
from app.models.transactions import Transaction

async def init_db():
    print(f"Creating tables in {settings.DATABASE_URL}")
    engine = create_async_engine(settings.DATABASE_URL)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("Tables created successfully.")
    
if __name__ == "__main__":
    asyncio.run(init_db())
