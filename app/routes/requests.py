from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.models import MaintenanceRequest, User
from .auth import get_current_user
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()

class RequestBase(BaseModel):
    tenant_id: int
    property_id: int
    issue_title: str
    issue_description: str
    status: str = "pending"

class RequestCreate(RequestBase):
    pass

class RequestResponse(RequestBase):
    id: int
    created_at: datetime
    class Config:
        from_attributes = True

@router.post("/", response_model=RequestResponse)
def create_request(request: RequestCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_request = MaintenanceRequest(**request.dict())
    db.add(db_request)
    db.commit()
    db.refresh(db_request)
    return db_request

@router.get("/", response_model=List[RequestResponse])
def get_requests(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(MaintenanceRequest).all()

@router.patch("/{request_id}")
def update_request_status(request_id: int, status: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_request = db.query(MaintenanceRequest).filter(MaintenanceRequest.id == request_id).first()
    if not db_request:
        raise HTTPException(status_code=404, detail="Request not found")
    db_request.status = status
    db.commit()
    return db_request
