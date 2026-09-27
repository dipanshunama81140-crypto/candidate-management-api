import time
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
import database, models, utils, oauth2, schemas
from fastapi import Request
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
router = APIRouter(
    prefix="/api/v1/auth",
    tags=["Authentication"]
)

# 1. Background Task Function (Simulating Email Sending / Logging)
def send_welcome_email(email: str):
    # Simulate network delay (jaise real SMTP server connect ho raha ho)
    time.sleep(3)
    print(f"\n[BACKGROUND TASK] Welcome email successfully sent to: {email}\n")

# 2. Register User with Background Task
@router.post("/register", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(
    user: schemas.UserCreate,
    background_task: BackgroundTasks, # FastAPI Dependency
    db: Session = Depends(database.get_db)
):
    # Check if user already exists
    existing_user = db.query(models.User).filter(models.User.email == user.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registerd"
        )

    # Hash password & save
    hashed_password = utils.hash_password(user.password)
    new_user = models.User(email=user.email, password=hashed_password)
    new_user = models.User(email=user.email, password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Background task queue me add karein
    background_task.add_task(send_welcome_email, user.email)

    #client ko instant response milega (3 second ka wait nahi karna padega)
    return new_user

# 3. Login User (Maximum 5 attempts per minute per IP)
@router.post("/login", response_model=schemas.Token)
@limiter.limit("5/minute")
def login_user(
    request: Request, # Slowapi ke liye Request object zarooro hai
    user_credentials: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(database.get_db)
):
    user = db.query(models.User).filter(models.User.email == user_credentials.username).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            details="Invalid Credentials"
        )
    if not utils.verify_password(user_credentials.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid Credentials"
        )

    access_token = oauth2.create_access_token(data={"user_id": user.id})
    return {"access_token": access_token, "token_type": "bearer"}