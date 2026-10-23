import time
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from sqlalchemy.sql import text
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as starletteHTTPException 
from database import engine
from routers import candidates, auth
from logger import get_logger

logger = get_logger("API_GATEWAY")

limiter = Limiter(key_func=get_remote_address)

# App instance
app = FastAPI(
    title="Candidate Management System",
    version="1.0.0"
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS Setup
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Latency & Logging Middleware
@app.middleware("http")
async def add_process_time_and_logging(request: Request, call_next):
    start_time = time.perf_counter()
    logger.info(f"Incoming Request: {request.method} {request.url.path}")

    try:
        response = await call_next(request)
        process_time = time.perf_counter() - start_time
        response.headers["X-Process-Time"] = f"{process_time:.4f}s"
        logger.info(f"Request Completed: {request.method} {request.url.path} | Status: {response.status_code} | Time: {process_time:.4f}s")
        return response
    except (starletteHTTPException, RequestValidationError):
        # Normal HTTP errors ko direct flow (not convert in to500 )
        raise
    except Exception as exc:
        logger.error(f"Unhandled Exception on {request.method} {request.url.path}: {str(exc)}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "An internal server error occurred. Please contact system support."}
        )

# Global Unhandled Exception Handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.critical(f"Fatal Crash on {request.url.path}: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Unexpected system crash intercepted."}
    )

# Root Endpoint
@app.get("/")
def root():
    return {"message": "Welcome to Candidate Management API"}

# Health & Connection Pool Monitoring Endpoint
@app.get("/health", status_code=status.HTTP_200_OK, tags=["Monitoring"])
def health_check():
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))
    
    return {
        "status": "healthy",
        "database": "connected",
        "pool_size": engine.pool.size(),
        "checkedin_connections": engine.pool.checkedin(),
        "checkedout_connections": engine.pool.checkedout(),
        "overflow": engine.pool.overflow()
    }

# Routers
app.include_router(auth.router)
app.include_router(candidates.router)