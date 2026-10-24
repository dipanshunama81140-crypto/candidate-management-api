import json
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from redis_client import get_redis, invalidate_candidate_cache
import models
import schemas
from database import get_db
import oauth2
import redis
import asyncio
from sqlalchemy import or_

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
    current_user: models.User = Depends(oauth2.get_current_user),
    limit: int = 10,
    skip: int = 0,
    search: Optional[str] = None
): 
    # Unique Cache key generate karein query params ke basis par
    cache_key = f"candidates:{current_user.id}:{limit}:{skip}:{search}"

    # 1. Safe Cache Lookup
    redis_conn = get_redis()
    if redis_conn:
        try:
            cached_data = redis_conn.get(cache_key)
            if cached_data:
                return json.loads(cached_data)
        except Exception as e:
            print(f"[REDIS GET WARNING]: {e}")

    # 2. Database Fetch
    query = db.query(models.Candidate).filter(models.Candidate.owner_id == current_user.id)
    if search:
        query = query.filter(
            or_(
                models.Candidate.name.ilike(f"%{search}%"),
                models.Candidate.skill.ilike(f"%{search}%")
            )
        )
    candidates = query.offset(skip).limit(limit).all()

    # 3. Safe Cache Set
    if redis_conn:
        try:
            # Serializing response for cache
            serialized_data = [
                schemas.CandidateResponse.model_validate(c).model_dump(mode="json") 
                for c in candidates
            ]
            redis_conn.setex(cache_key, 60, json.dumps(serialized_data))
        except Exception as e:
            print(f"[REDIS SET WARNING]: {e}")

    return candidates


# 3. Asynchronous Concurrent Verification Endpoint
async def verify_candidate_profile(candidate_id: int):
    # Simulate network I/O latency (external background check service)
    await asyncio.sleep(1)
    return {"candidate_id": candidate_id, "verification_status": "CLEARED"}

@router.get("/verify-batch", status_code=status.HTTP_200_OK)
async def verify_candidates_batch(
    current_user: models.User = Depends(oauth2.get_current_user)
):
    candidate_ids = [101, 102, 103, 104, 105]

    # Synchronous flow me 5 * 1s = 5 seconds lagte.
    # asyncio.gather se saare 5 network calls parallel trigger honge: Total time ~ 1 second.
    start_time = asyncio.get_event_loop().time()
    
    results = await asyncio.gather(
        *(verify_candidate_profile(c_id) for c_id in candidate_ids)
    )

    total_time = asyncio.get_event_loop().time() - start_time

    return {
        "execution_mode": "concurrent_async",
        "total_time_taken": f"{total_time:.4f} seconds",
        "verified_profiles": results
    }


# 4. Read One Candidate
@router.get("/{candidate_id}", response_model=schemas.CandidateResponse)
def get_Candidate(candidate_id: int, db: Session = Depends(get_db)):
    candidate = db.query(models.Candidate).filter(models.Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    return candidate
# 5. Create Candidate (Logged-in user ki ID link hoti hai)
@router.post("", response_model=schemas.CandidateResponse, status_code=status.HTTP_201_CREATED)
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
    invalidate_candidate_cache()
    return new_candidate

# 6. Update Candidate (Sirf candidate ka owner hi edit kar sakta hai)
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
    invalidate_candidate_cache()
    return candidate

# 7. Delete Candidate (sirf candidate ka owner hi delet kar sakta hai)
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
    invalidate_candidate_cache()
    return {"message": "Candidate successfully deletes from database!"}

# 8. Bulk Create Candidate with Atomic Transaction & Rollback
@router.post("/bulk", response_model=List[schemas.CandidateResponse], status_code=status.HTTP_201_CREATED)
def bulk_create_candidate(
    candidates_in: List[schemas.CandidateCreate],
    db: Session = Depends(get_db),
    current_user: models.User = Depends(oauth2.get_current_user)
):
    if not candidates_in:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            details="List cannot be empty"
        )

    created_records = []

    try: 
        #Atomic Block Start
        for item in candidates_in:
                if item.experience < 0:
                    raise ValueError(f"Invalid experince: {item.experience} for candidate {item.name}")

                new_candidate = models.Candidate(
                    name=item.name,
                    skill=item.skill,
                    experience=item.experience,
                    owner_id=current_user.id
                )
                db.add(new_candidate)
                created_records.append(new_candidate)

        db. commit()

        for record in created_records:
                db.refresh(record)

        invalidate_candidate_cache()

        return created_records
    except Exception as e:

        db.rollback()
        print(f"\n[DATABASE] TRANSACTION FAILED & ROLLED BACK: {str(e)}\n")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Transaction rolled back to error: {str(e)}"
        )