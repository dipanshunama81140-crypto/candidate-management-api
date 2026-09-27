from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

import models
import schemas
from database import get_db
import oauth2

router = APIRouter(
    prefix="/api/v1/candidates",
    tags=["Candidate"]
)

# 1. Search Candidates
@router.get("/search", response_model=list[schemas.CandidateResponse])
def search_by_skill(skill: str, db: Session = Depends(get_db)):
    return db.query(models.Candidate).filter(models.Candidate.skill.ilike(f"%{skill}%")).all()

# 2. Read All Candidates (With Pagination & Search)
@router.get("",response_model=list[schemas.CandidateResponse])
def get_all_candidates(
    db: Session = Depends(get_db),
    limit: int = 10,
    skip: int = 0,
    search: str = ""
): 
    # Pagination: limit controls  batch size, skip controls offset
    candidates = (
        db.query(models.Candidate)
        .filter(models.Candidate.skill.ilike(f"%{search}%"))
        .offset(skip)
        .all()
    )
    return candidates

# 3. Read One Candidate
@router.get("/{candidate_id}", response_model=schemas.CandidateResponse)
def get_Candidate(candidate_id: int, db: Session = Depends(get_db)):
    candidate = db.query(models.Candidate).filter(models.Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    return candidate
# 4. Create Candidate (Logged-in user ki ID link hoti hai)
@router.post("/", response_model=schemas.CandidateResponse, status_code=status.HTTP_201_CREATED)
def create_candidate(
    candidate: schemas.CandidateCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(oauth2.get_current_user)
):
    new_candidate = models.Candidate(
        name=candidate.name,
        skill=candidate.skill,
        experience=candidate.experience,
        owner_id =current_user.id # Authentically linked to authenticated user
    )
    db.add(new_candidate)
    db.commit()
    db.refresh(new_candidate)
    return new_candidate

# 5. Update Candidate (Sirf candidate ka owner hi edit kar sakta hai)
@router.put("/{candidate_id}", response_model=schemas.CandidateResponse)
def update_candidate(
    candidate_id: int,
    update_data: schemas.CandidateCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(oauth2.get_current_user)
):
    candidate_query = db.query(models.Candidate).filter(models.Candidate.id == candidate_id)
    candidate = candidate_query.first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")

    if candidate.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this candidate"
        )
    candidate_query.update(update_data.model_dump(), synchronize_session=False)
    db.commit()
    db.refresh(candidate)
    return candidate

# 6. Delete Candidate (sirf candidate ka owner hi delet kar sakta hai)
@router.delete("/{candidate_id}",status_code=status.HTTP_200_OK)
def delete_candidate(
    candidate_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(oauth2.get_current_user)
):
    candidate_query = db.query(models.Candidate).filter(models.Candidate.id == candidate_id)
    candidate = candidate_query.first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    
    if candidate.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this candidate"
        )
    candidate_query.delete(synchronize_session=False)
    db.commit()
    return {"message": "Candidate successfully deletes from database!"}