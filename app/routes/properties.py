from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models.models import Property, User
from .auth import get_current_user
from pydantic import BaseModel

router = APIRouter()

class PropertyBase(BaseModel):
    title: str
    location: str
    property_type: str
    bedrooms: int
    bathrooms: int
    toilets: int
    size_sqm: float
    has_parking: bool
    has_security: bool
    furnished: bool
    current_rent_price: float
    predicted_rent_price: Optional[float] = None

class PropertyCreate(PropertyBase):
    pass

class PropertyResponse(PropertyBase):
    id: int
    landlord_id: int
    class Config:
        from_attributes = True

@router.post("/", response_model=PropertyResponse)
def create_property(property: PropertyCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role not in ["admin", "landlord"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    db_property = Property(**property.dict(), landlord_id=current_user.id)
    db.add(db_property)
    db.commit()
    db.refresh(db_property)
    return db_property

@router.get("/", response_model=List[PropertyResponse])
def get_properties(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role in ["admin", "landlord"]:
        return db.query(Property).all()
    else:
        # Tenants might only see available or their own properties, but for demo let's show all
        return db.query(Property).all()

@router.put("/{property_id}", response_model=PropertyResponse)
def update_property(property_id: int, property: PropertyCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role not in ["admin", "landlord"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    db_property = db.query(Property).filter(Property.id == property_id).first()
    if not db_property:
        raise HTTPException(status_code=404, detail="Property not found")
    for key, value in property.dict().items():
        setattr(db_property, key, value)
    db.commit()
    db.refresh(db_property)
    return db_property

@router.delete("/{property_id}")
def delete_property(property_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role not in ["admin", "landlord"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    db_property = db.query(Property).filter(Property.id == property_id).first()
    if not db_property:
        raise HTTPException(status_code=404, detail="Property not found")
    
    db.delete(db_property)
    db.commit()
    return {"message": "Property deleted"}
