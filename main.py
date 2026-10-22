import time 
from fastapi import FastAPI, Request, HTTPException, exception_handlers, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import models
from database import engine
from routers import candidates, auth
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from logger import get_logger

logger = get_logger("API_GATEWAY")

# Client ke IP address ke basis par limil karega
limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title="Candidate Management System",
    version="1.0.0"
)

# Rate limiter state attach karein aur exception gandler register karein
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# 1. CORS Configuration (Allowed origins list)
origins = [
    "http://localhost:3000",        # React Frontend Local Dev
    "http://127.0.0.1:3000",        
    "*"                             # Testing phase ke liye all origins allow
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],             # GET, POST, PUT, DELETE, OPTIONS
    allow_headers=["*"],                 # Authorization, Content-type
)

# Request Latency & Inbound Logging Middleware
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

# Routers
app.include_router(auth.router)
app.include_router(candidates.router)

@app.get("/")
def root():
    return {"message": "Welcome to Candidate Managment API"}