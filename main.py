import time 
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import models
from database import engine
from routers import candidates, auth
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

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

# 2. performance Tracking Middleware (X-Process-Time Header)
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.perf_counter()
    response = await call_next(request)
    process_time = time.perf_counter() - start_time
    response.headers["X-Process-Time"] = f"{process_time:.4f}s"
    return response
# Include Router
app.include_router(candidates.router)
app.include_router(auth.router)

@app.get("/")
def root():
    return{"message": "Welcome to Candidate Management API! Go to /docs for Swagger UI"}