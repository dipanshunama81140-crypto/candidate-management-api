# Candidate Management API

A production-ready, modular RESTful API built with **FastAPI**, **SQLAlchemy ORM**, and **PostgreSQL (Neon)**. Designed following the 12-Factor App methodology with automated database migrations, JWT authentication, rate limiting, and automated testing.

---

## Tech Stack & Architecture

- **Framework:** FastAPI
- **Database:** Cloud PostgreSQL (Neon) with SQLAlchemy ORM
- **Migrations:** Alembic
- **Authentication:** OAuth2 Password Bearer with JWT (HS256) & Passlib (Bcrypt)
- **Validation & Settings:** Pydantic V2 & Pydantic-Settings
- **Security & Protection:** SlowAPI (Rate Limiting) & CORS Middleware(Cross-Origin Resource Sharing)
- **Testing:** Pytest & FastAPI TestClient

---

## Key Features

1. **Authentication & Authorization:** Secure registration and token-based login workflows.
2. **Relational Data Modeling:** One-to-many relationship between Authenticated Users and Candidate records.
3. **Query Optimization:** Implemented database-level pagination (`limit`, `skip`) and case-insensitive search queries.
4. **Asynchronous Background Processing:** Non-blocking email notifications executed via `BackgroundTasks`.
5. **Security Layers:**
   - Slotted rate limiting (5 attempts/min on sensitive auth routes) preventing brute-force.
   - Cross-Origin Resource Sharing (CORS) configured for frontend consumption.
   - Dynamic request execution time calculation via custom HTTP middleware (`X-Process-Time`).
6. **Automated Testing:** Test suite covering health checks, auth flows, and CRUD operations using isolated test databases.

---

## Local Setup & Installation

### 1. Clone the Repository
```bash
git clone https://github.com/dipanshunama81140-crypto/candidate-management-api.git
cd candidate-management-api