from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

# Database Table Definition
class Candidate(Base):
    __tablename__ = "candidates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    skill = Column(String)
    experience = Column(Integer)
# Foreing key column: ye btata he ki candidate kis user ne banaya 
    owner_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

# SQLAlchemy Relationship: Candidate se direct object access kaene ke liye
owner = relationship("User")

# Naya User Model (Auth ke liye)
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
