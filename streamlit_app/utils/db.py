import os
import pandas as pd
import streamlit as st
from sqlalchemy import create_engine
from dotenv import load_dotenv

# Load .env
load_dotenv(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.env")))

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///../customeriq.db")
if "postgresql+asyncpg" in DATABASE_URL:
    DATABASE_URL = DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://")
elif "sqlite+aiosqlite" in DATABASE_URL:
    DATABASE_URL = DATABASE_URL.replace("sqlite+aiosqlite://", "sqlite://")

@st.cache_resource
def get_engine():
    connect_args = {}
    if "postgresql" in DATABASE_URL:
        connect_args["sslmode"] = "require"
    return create_engine(DATABASE_URL, connect_args=connect_args)

@st.cache_data(ttl=300)
def cached_query(query: str):
    """
    Run a SQL query and cache the resulting DataFrame.
    """
    engine = get_engine()
    return pd.read_sql(query, engine)
