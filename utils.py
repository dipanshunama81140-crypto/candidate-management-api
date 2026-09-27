from passlib.context import CryptContext

# Bcrypt hashing configuration
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """Plain password ko hashed string me convert karta hai"""
    return pwd_context.hash(password)

def verify_password(plan_password: str, hashed_password: str) -> bool:
    """Login ke waqt password match karta hai"""
    return pwd_context.verify(plan_password, hashed_password)