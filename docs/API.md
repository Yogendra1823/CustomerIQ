# CustomerIQ API Reference

The CustomerIQ backend is a REST API powered by FastAPI. This document details the key endpoints, response structures, and sample queries.

## Authentication

All protected endpoints require a JWT bearer token in the `Authorization` header:
`Authorization: Bearer <your_access_token>`

### 1. User Login
Authenticates user and returns credentials.
* **URL**: `/api/v1/auth/login`
* **Method**: `POST`
* **Request Body**:
  ```json
  {
    "email": "admin@customeriq.com",
    "password": "Admin@123"
  }
  ```
* **Response**: `200 OK`
  ```json
  {
    "access_token": "eyJhbG...",
    "refresh_token": "eyJhbG...",
    "token_type": "bearer",
    "user": {
      "id": "a93be9f2...",
      "email": "admin@customeriq.com",
      "full_name": "Administrator",
      "role": "admin"
    }
  }
  ```

---

## Customers

### 2. List Customers
Fetch paginated, filtered customer lists.
* **URL**: `/api/v1/customers`
* **Method**: `GET`
* **Query Parameters**:
  * `page` (int, default: 1)
  * `limit` (int, default: 50)
  * `segment` (int, optional)
  * `region` (str, optional)
  * `search` (str, optional)
* **Response**: `200 OK`
  ```json
  {
    "items": [
      {
        "id": "e0e29b...",
        "external_id": "CUST_001",
        "age": 34,
        "region": "Karnataka",
        "total_spend": 125000.50,
        "clv_estimate": 350000.00,
        "churn_probability": 0.12,
        "value_tier": "premium"
      }
    ],
    "total": 10000,
    "page": 1,
    "limit": 50,
    "pages": 200
  }
  ```

### 3. Retrieve Customer Profile
Get details of a single customer with their transaction history.
* **URL**: `/api/v1/customers/{id}`
* **Method**: `GET`
* **Response**: `200 OK`
  ```json
  {
    "id": "e0e29b...",
    "external_id": "CUST_001",
    "age": 34,
    "region": "Karnataka",
    "total_spend": 125000.50,
    "transactions": [
      {
        "id": "tx_99a...",
        "amount": 15000.00,
        "category": "Electronics",
        "transaction_date": "2026-04-12T14:32:00Z"
      }
    ]
  }
  ```

### 4. Bulk Upload Customers
Parse a CSV file and batch insert rows.
* **URL**: `/api/v1/customers/upload`
* **Method**: `POST`
* **Content-Type**: `multipart/form-data`
* **Response**: `200 OK`
  ```json
  {
    "status": "success",
    "processed": 500,
    "inserted": 498,
    "errors": [
      {"row": 12, "error": "Missing external_id"}
    ]
  }
  ```

---

## Machine Learning

### 5. Train Model
Triggers clustering and model generation in the background.
* **URL**: `/api/v1/ml/train`
* **Method**: `POST`
* **Request Body**:
  ```json
  {
    "algorithm": "kmeans",
    "n_clusters": 5,
    "run_name": "KMeans_Optimal_K5"
  }
  ```
* **Response**: `202 Accepted`
  ```json
  {
    "run_id": "bf8c187e...",
    "status": "started"
  }
  ```

### 6. Get Runs
* **URL**: `/api/v1/ml/runs`
* **Method**: `GET`
* **Response**: `200 OK`
  ```json
  [
    {
      "id": "bf8c187e...",
      "run_name": "KMeans_Optimal_K5",
      "algorithm": "kmeans",
      "n_clusters": 5,
      "silhouette_score": 0.635,
      "is_active": true,
      "created_at": "2026-05-25T08:44:00Z"
    }
  ]
  ```

---

## Exporting

### 7. PDF Report
* **URL**: `/api/v1/export/report/pdf`
* **Method**: `GET`
* **Response**: Stream of application/pdf
