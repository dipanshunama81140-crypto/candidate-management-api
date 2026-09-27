from typing import Optional
from pydantic import BaseModel

# 1. Pehle independent Auth Schemas define karein
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    user_id: Optional[int] = None


# 2. Phir User Schemas define karein (Taaki CandidateResponse isko pehchan sake)
class UserCreate(BaseModel):
    email: str
    password: str

class UserResponse(BaseModel):
    id: int
    email: str

    class Config:
        from_attributes = True


# 3. Phir Candidate Schemas define karein
class CandidateCreate(BaseModel):
    name: str
    skill: str
    experience: int

class CandidateResponse(BaseModel):
    id: int
    name: str
    skill: str
    experience: int
    owner_id: int
    owner: Optional[UserResponse] = None

    class Config:
        from_attributes = True


# 4. Explicit Model Rebuild (Pydantic 2.x error fix karne ke liye)
CandidateResponse.model_rebuild()