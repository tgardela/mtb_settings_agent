from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List

from database import get_db
from models import Trail, User
from routers.auth_router import get_current_user

router = APIRouter(prefix="/trails", tags=["trails"])


class TrailCreate(BaseModel):
    name: str
    location: Optional[str] = None
    rating: Optional[float] = None
    notes: Optional[str] = None


class TrailUpdate(BaseModel):
    name: Optional[str] = None
    location: Optional[str] = None
    rating: Optional[float] = None
    notes: Optional[str] = None


class TrailResponse(BaseModel):
    id: int
    user_id: int
    name: str
    location: Optional[str] = None
    rating: Optional[float] = None
    notes: Optional[str] = None

    class Config:
        from_attributes = True


@router.get("", response_model=List[TrailResponse])
def list_trails(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(Trail).filter(Trail.user_id == current_user.id).all()


@router.post("", response_model=TrailResponse, status_code=status.HTTP_201_CREATED)
def create_trail(request: TrailCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    trail = Trail(user_id=current_user.id, **request.model_dump())
    db.add(trail)
    db.commit()
    db.refresh(trail)
    return trail


@router.get("/{trail_id}", response_model=TrailResponse)
def get_trail(trail_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    trail = db.query(Trail).filter(Trail.id == trail_id, Trail.user_id == current_user.id).first()
    if not trail:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trail not found")
    return trail


@router.put("/{trail_id}", response_model=TrailResponse)
def update_trail(trail_id: int, request: TrailUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    trail = db.query(Trail).filter(Trail.id == trail_id, Trail.user_id == current_user.id).first()
    if not trail:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trail not found")
    for field, value in request.model_dump(exclude_unset=True).items():
        setattr(trail, field, value)
    db.commit()
    db.refresh(trail)
    return trail


@router.delete("/{trail_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_trail(trail_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    trail = db.query(Trail).filter(Trail.id == trail_id, Trail.user_id == current_user.id).first()
    if not trail:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trail not found")
    db.delete(trail)
    db.commit()
