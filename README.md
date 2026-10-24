# 🚀 Candidate Management RESTful API

[![CI Pipeline](https://github.com/dipanshunama81140-crypto/candidate-management-api/actions/workflows/ci.yml/badge.svg)](https://github.com/dipanshunama81140-crypto/candidate-management-api/actions)
[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=flat&logo=fastapi)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Neon_Cloud-336791?style=flat&logo=postgresql)](https://neon.tech/)
[![Redis](https://img.shields.io/badge/Redis-Upstash_Cache-DC382D?style=flat&logo=redis)](https://upstash.com/)
[![Deployment](https://img.shields.io/badge/Render-Live_Production-46E3B7?style=flat&logo=render)](https://render.com/)

An enterprise-ready, high-performance RESTful API engineered for candidate profile lifecycle management. Built with FastAPI, PostgreSQL, SQLAlchemy ORM, and Upstash Redis for distributed caching.

---

## 🌐 Live Production Links
* **Live API Base URL:** `https://candidate-management-api-ewvq.onrender.com`
* **Interactive Swagger UI Documentation:** [https://candidate-management-api-ewvq.onrender.com/docs](https://candidate-management-api-ewvq.onrender.com/docs)
* **ReDoc Documentation:** [https://candidate-management-api-ewvq.onrender.com/redoc](https://candidate-management-api-ewvq.onrender.com/redoc)

---

## 🏗️ Architecture & Core Features

* **Authentication & Authorization**: OAuth2 Password-Bearer flow with HS256-signed JSON Web Tokens (JWT) and Bcrypt password hashing.
* **Database & Persistence**: Scalable PostgreSQL serverless database (Neon) mapped using SQLAlchemy ORM with B-Tree indexes on query-heavy columns.
* **Caching & Resilience**: Cache-Aside pattern powered by Upstash Redis with short-circuit exception handling to ensure zero downtime during cache drops.
* **Latency Profiling**: Custom middleware injecting real-time execution duration headers (`X-Process-Time`).
* **Automated CI/CD**: End-to-end GitHub Actions pipeline executing automated pytest test suites on every commit, deploying automatically to Render on green builds.
* **Input Validation & Documentation**: Strict type validation via Pydantic V2 and auto-generated OpenAPI 3.1 documentation.

---

## 🛠️ Tech Stack

* **Framework:** FastAPI, Uvicorn
* **Database:** Neon PostgreSQL, SQLAlchemy ORM, Alembic
* **Caching:** Upstash Redis
* **Security:** Python-JOSE (JWT), Passlib (Bcrypt)
* **Testing & Quality:** Pytest, HTTPX, Flake8
* **CI/CD & Cloud:** GitHub Actions, Render Cloud PaaS

---

## 📡 API Endpoints Overview

| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `GET` | `/health` | Diagnostic check for DB connection pool | No |
| `POST` | `/api/v1/auth/register` | Register a new user account | No |
| `POST` | `/api/v1/auth/login` | Authenticate user & generate JWT access token | No |
| `POST` | `/api/v1/candidates` | Create a new candidate profile | **Yes (Bearer)** |
| `GET` | `/api/v1/candidates` | Paginated listing with Redis caching & search filter | **Yes (Bearer)** |
| `GET` | `/api/v1/candidates/{id}` | Retrieve candidate profile by unique ID | **Yes (Bearer)** |
| `PUT` | `/api/v1/candidates/{id}` | Update candidate details and invalidate cache | **Yes (Bearer)** |
| `DELETE` | `/api/v1/candidates/{id}` | Delete candidate profile | **Yes (Bearer)** |

---

## ⚙️ Local Setup & Execution

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/dipanshunama81140-crypto/candidate-management-api.git](https://github.com/dipanshunama81140-crypto/candidate-management-api.git)
   cd candidate-management-api