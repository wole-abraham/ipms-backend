from fastapi import APIRouter, HTTPException
import joblib
import pandas as pd
import numpy as np
import os
from pydantic import BaseModel

router = APIRouter()

# Load models
RENT_MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "ml", "rent_model.pkl")
RISK_MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "ml", "risk_model.pkl")

class RentPredictRequest(BaseModel):
    location: str
    property_type: str
    bedrooms: int
    bathrooms: int
    toilets: int
    size_sqm: float
    has_parking: bool
    has_security: bool
    furnished: bool

class RiskPredictRequest(BaseModel):
    monthly_income: float
    employment_status: str # "Unemployed", "Self-employed", "Employed"
    rent_amount: float
    previous_evictions: int
    late_payments: int
    credit_score: int

@router.post("/rent")
def predict_rent(data: RentPredictRequest):
    if not os.path.exists(RENT_MODEL_PATH):
        raise HTTPException(status_code=500, detail="Rent prediction model not found. Please train it first.")
    
    model_data = joblib.load(RENT_MODEL_PATH)
    model = model_data['model']
    features = model_data['features']
    
    # Prepare input
    input_data = {
        'bedrooms': [data.bedrooms],
        'bathrooms': [data.bathrooms],
        'toilets': [data.toilets],
        'size_sqm': [data.size_sqm],
        'has_parking': [1 if data.has_parking else 0],
        'has_security': [1 if data.has_security else 0],
        'furnished': [1 if data.furnished else 0],
    }
    
    # Add dummies for location and property type
    for f in features:
        if f.startswith('location_'):
            loc = f.split('_')[1]
            input_data[f] = [1 if data.location == loc else 0]
        elif f.startswith('property_type_'):
            ptype = f.split('_')[1]
            input_data[f] = [1 if data.property_type == ptype else 0]
            
    df_input = pd.DataFrame(input_data)
    # Ensure all features are present
    for f in features:
        if f not in df_input.columns:
            df_input[f] = 0
    
    # Reorder columns to match training
    df_input = df_input[features]
    
    prediction = model.predict(df_input)[0]
    return {"predicted_rent": float(prediction)}

@router.post("/tenant-risk")
def predict_risk(data: RiskPredictRequest):
    if not os.path.exists(RISK_MODEL_PATH):
        raise HTTPException(status_code=500, detail="Risk assessment model not found. Please train it first.")
    
    model_data = joblib.load(RISK_MODEL_PATH)
    model = model_data['model']
    
    # Map employment status to numeric
    status_map = {"Unemployed": 0, "Self-employed": 1, "Employed": 2}
    emp_status = status_map.get(data.employment_status, 0)
    
    input_data = [[
        data.monthly_income,
        emp_status,
        data.rent_amount,
        data.previous_evictions,
        data.late_payments,
        data.credit_score
    ]]
    
    prediction = model.predict(input_data)[0]
    return {"risk_level": prediction}
