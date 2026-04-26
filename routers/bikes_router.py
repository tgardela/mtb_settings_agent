from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List

from database import get_db
from models import Bike, User
from routers.auth_router import get_current_user

router = APIRouter(prefix="/bikes", tags=["bikes"])


class BikeCreate(BaseModel):
    name: str
    brand: Optional[str] = None
    model: Optional[str] = None
    year: Optional[int] = None
    suspension_settings: Optional[dict] = None
    geometry: Optional[dict] = None
    notes: Optional[str] = None


class BikeUpdate(BaseModel):
    name: Optional[str] = None
    brand: Optional[str] = None
    model: Optional[str] = None
    year: Optional[int] = None
    suspension_settings: Optional[dict] = None
    geometry: Optional[dict] = None
    notes: Optional[str] = None


class BikeResponse(BaseModel):
    id: int
    user_id: int
    name: str
    brand: Optional[str] = None
    model: Optional[str] = None
    year: Optional[int] = None
    suspension_settings: Optional[dict] = None
    geometry: Optional[dict] = None
    notes: Optional[str] = None

    class Config:
        from_attributes = True


@router.get("", response_model=List[BikeResponse])
def list_bikes(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(Bike).filter(Bike.user_id == current_user.id).all()


@router.post("", response_model=BikeResponse, status_code=status.HTTP_201_CREATED)
def create_bike(request: BikeCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    bike = Bike(user_id=current_user.id, **request.model_dump())
    db.add(bike)
    db.commit()
    db.refresh(bike)
    return bike


@router.get("/{bike_id}", response_model=BikeResponse)
def get_bike(bike_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    bike = db.query(Bike).filter(Bike.id == bike_id, Bike.user_id == current_user.id).first()
    if not bike:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bike not found")
    return bike


@router.put("/{bike_id}", response_model=BikeResponse)
def update_bike(bike_id: int, request: BikeUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    bike = db.query(Bike).filter(Bike.id == bike_id, Bike.user_id == current_user.id).first()
    if not bike:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bike not found")
    for field, value in request.model_dump(exclude_unset=True).items():
        setattr(bike, field, value)
    db.commit()
    db.refresh(bike)
    return bike


@router.delete("/{bike_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_bike(bike_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    bike = db.query(Bike).filter(Bike.id == bike_id, Bike.user_id == current_user.id).first()
    if not bike:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bike not found")
    db.delete(bike)
    db.commit()
