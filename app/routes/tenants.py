from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models.models import Tenant, User
from .auth import get_current_user
from pydantic import BaseModel

router = APIRouter()

class TenantBase(BaseModel):
    full_name: str
    phone_number: str
    monthly_income: float
    employment_status: str
    rent_amount: float
    previous_evictions: int
    late_payments: int
    credit_score: int
    property_id: Optional[int] = None
    risk_level: Optional[str] = None

class TenantCreate(TenantBase):
    email: str

class TenantResponse(TenantBase):
    id: int
    user_id: int
    class Config:
        from_attributes = True

@router.post("/", response_model=TenantResponse)
def create_tenant(tenant: TenantCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role not in ["admin", "landlord"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    existing_user = db.query(User).filter(User.email == tenant.email).first()
    if existing_user:
        existing_user.full_name = tenant.full_name
        existing_user.role = "tenant"
        db.commit()
        db.refresh(existing_user)
        new_user = existing_user
    else:
        new_user = User(full_name=tenant.full_name, email=tenant.email, role="tenant")
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

    db_tenant = Tenant(
        user_id=new_user.id,
        phone_number=tenant.phone_number,
        monthly_income=tenant.monthly_income,
        employment_status=tenant.employment_status,
        rent_amount=tenant.rent_amount,
        previous_evictions=tenant.previous_evictions,
        late_payments=tenant.late_payments,
        credit_score=tenant.credit_score,
        property_id=tenant.property_id,
        risk_level=tenant.risk_level
    )
    db.add(db_tenant)
    db.commit()
    db.refresh(db_tenant)
    return {
        "id": db_tenant.id,
        "full_name": new_user.full_name,
        "email": new_user.email,
        "phone_number": db_tenant.phone_number,
        "monthly_income": db_tenant.monthly_income,
        "employment_status": db_tenant.employment_status,
        "rent_amount": db_tenant.rent_amount,
        "previous_evictions": db_tenant.previous_evictions,
        "late_payments": db_tenant.late_payments,
        "credit_score": db_tenant.credit_score,
        "risk_level": db_tenant.risk_level,
        "property_id": db_tenant.property_id,
        "user_id": db_tenant.user_id,
    }

@router.get("/", response_model=List[dict])
def get_tenants(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    tenants = db.query(Tenant).all()
    result = []
    for t in tenants:
        result.append({
            "id": t.id,
            "full_name": t.user.full_name,
            "email": t.user.email,
            "phone_number": t.phone_number,
            "monthly_income": t.monthly_income,
            "employment_status": t.employment_status,
            "rent_amount": t.rent_amount,
            "previous_evictions": t.previous_evictions,
            "late_payments": t.late_payments,
            "credit_score": t.credit_score,
            "risk_level": t.risk_level,
            "property_id": t.property_id
        })
    return result

@router.put("/{tenant_id}", response_model=dict)
def update_tenant(tenant_id: int, tenant: TenantBase, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role not in ["admin", "landlord"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    db_tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not db_tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    for key, value in tenant.dict().items():
        if hasattr(db_tenant, key):
            setattr(db_tenant, key, value)
    if tenant.full_name:
        db_tenant.user.full_name = tenant.full_name
    db.commit()
    db.refresh(db_tenant)
    return {
        "id": db_tenant.id,
        "full_name": db_tenant.user.full_name,
        "email": db_tenant.user.email,
        "phone_number": db_tenant.phone_number,
        "monthly_income": db_tenant.monthly_income,
        "employment_status": db_tenant.employment_status,
        "rent_amount": db_tenant.rent_amount,
        "previous_evictions": db_tenant.previous_evictions,
        "late_payments": db_tenant.late_payments,
        "credit_score": db_tenant.credit_score,
        "risk_level": db_tenant.risk_level,
        "property_id": db_tenant.property_id,
        "user_id": db_tenant.user_id,
    }

@router.delete("/{tenant_id}")
def delete_tenant(tenant_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role not in ["admin", "landlord"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    db_tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not db_tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    
    db.delete(db_tenant)
    db.commit()
    return {"message": "Tenant deleted"}
