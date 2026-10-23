from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Index
from sqlalchemy.sql import func
from sqlalchemy.sql.sqltypes import TIMESTAMP
from sqlalchemy.orm import relationship
from database import Base

# Database Table Definition
class Candidate(Base):
    __tablename__ = "candidates"

    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String, index=True, nullable=False)
    skill = Column(String, index=True, nullable=False)
    experience = Column(Integer, nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    create_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
# SQLAlchemy Relationship: Candidate se direct object access kaene ke liye
owner = relationship("User")

# Naya User Model (Auth ke liye)
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())

__table_args__ = (
    Index("idx_candidate_skill_experience", "skill", "experience"),
)