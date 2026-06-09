from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.models import RentPayment, User
from .auth import get_current_user
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()

class PaymentBase(BaseModel):
    tenant_id: int
    property_id: int
    amount: float
    status: str

class PaymentCreate(PaymentBase):
    pass

class PaymentResponse(PaymentBase):
    id: int
    payment_date: datetime
    class Config:
        from_attributes = True

@router.post("/", response_model=PaymentResponse)
def create_payment(payment: PaymentCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_payment = RentPayment(**payment.dict())
    db.add(db_payment)
    db.commit()
    db.refresh(db_payment)
    return db_payment

@router.get("/", response_model=List[PaymentResponse])
def get_payments(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(RentPayment).all()
