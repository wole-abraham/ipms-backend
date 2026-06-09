from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.database import Base

class UserRole(str, enum.Enum):
    ADMIN = "admin"
    LANDLORD = "landlord"
    TENANT = "tenant"

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(String, default="tenant") # admin, landlord, tenant
    is_active = Column(Boolean, default=True)

class Property(Base):
    __tablename__ = "properties"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    location = Column(String)
    property_type = Column(String)
    bedrooms = Column(Integer)
    bathrooms = Column(Integer)
    toilets = Column(Integer)
    size_sqm = Column(Float)
    has_parking = Column(Boolean)
    has_security = Column(Boolean)
    furnished = Column(Boolean)
    current_rent_price = Column(Float)
    predicted_rent_price = Column(Float, nullable=True)
    landlord_id = Column(Integer, ForeignKey("users.id"))
    
    tenants = relationship("Tenant", back_populates="property")

class Tenant(Base):
    __tablename__ = "tenants"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    property_id = Column(Integer, ForeignKey("properties.id"), nullable=True)
    phone_number = Column(String)
    monthly_income = Column(Float)
    employment_status = Column(String)
    rent_amount = Column(Float)
    previous_evictions = Column(Integer)
    late_payments = Column(Integer)
    credit_score = Column(Integer)
    risk_level = Column(String, nullable=True) # Low, Medium, High

    property = relationship("Property", back_populates="tenants")
    user = relationship("User")

class RentPayment(Base):
    __tablename__ = "rent_payments"
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"))
    property_id = Column(Integer, ForeignKey("properties.id"))
    amount = Column(Float)
    payment_date = Column(DateTime(timezone=True), server_default=func.now())
    status = Column(String) # paid, pending, overdue

class MaintenanceRequest(Base):
    __tablename__ = "maintenance_requests"
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"))
    property_id = Column(Integer, ForeignKey("properties.id"))
    issue_title = Column(String)
    issue_description = Column(String)
    status = Column(String, default="pending") # pending, in progress, resolved
    created_at = Column(DateTime(timezone=True), server_default=func.now())
