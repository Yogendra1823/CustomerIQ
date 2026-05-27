# Deployment Guide (Serverless Cloud Stack)

This document outlines the exact steps to deploy the CustomerIQ stack across free-tier serverless cloud providers.

## 1. Database (Neon Serverless PostgreSQL)

1. Create a project on [Neon](https://neon.tech).
2. Under Connection Details, select the `postgresql` scheme with the `asyncpg` variant, and copy the connection string.
3. Ensure the password placeholder is updated with your actual database password.
4. Add `?ssl=require` to the end of the connection string.

## 2. Redis Cache (Upstash)

1. Log into [Upstash](https://upstash.com) and create a Redis database.
2. Scroll down to the REST API / Connection section and copy the standard `redis://...` connection string.

## 3. Backend (Render)

1. Create a new Web Service on [Render](https://render.com).
2. Connect your Git repository.
3. Configure the **Root Directory** to `backend`.
4. Configure the **Start Command** as:
   ```bash
   alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port $PORT
   ```
5. Add the following **Environment Variables**:
   * `DATABASE_URL`: Your Neon connection string (ensure it uses `postgresql+asyncpg://`)
   * `REDIS_URL`: Your Upstash Redis URL
   * `SECRET_KEY`: A highly secure 64-character hex string
   * `ALGORITHM`: `HS256`
   * `ENVIRONMENT`: `production`
   * `CORS_ORIGINS`: `["https://customeriq-intern.vercel.app"]` (Your Vercel domain)

## 4. Frontend (Vercel)

1. Log into [Vercel](https://vercel.com).
2. Create a new project and import your repository.
3. Configure the **Root Directory** to `frontend`.
4. The **Build Command** should be `npm run build` and **Output Directory** `dist`.
5. Add the environment variable:
   * `VITE_API_BASE_URL`: URL of your deployed Render backend (e.g., `https://customeriq-c1s9.onrender.com`).

## 5. ML Studio (Streamlit Community Cloud)

1. Connect your repository to [Streamlit Share](https://share.streamlit.io/).
2. Select your branch and set the main file path to:
   ```
   streamlit_app/app.py
   ```
3. In the advanced app settings on Streamlit Cloud, add the following to **Secrets**:
   ```toml
   DATABASE_URL = "postgresql+psycopg2://..."  # Note: Use psycopg2 instead of asyncpg here
   API_URL = "https://customeriq-c1s9.onrender.com/api/v1"
   ```
