from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.routes import auth, properties, tenants, payments, requests, predictions

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Property Management System API")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(properties.router, prefix="/api/properties", tags=["Properties"])
app.include_router(tenants.router, prefix="/api/tenants", tags=["Tenants"])
app.include_router(payments.router, prefix="/api/payments", tags=["Payments"])
app.include_router(requests.router, prefix="/api/requests", tags=["Maintenance Requests"])
app.include_router(predictions.router, prefix="/api/predict", tags=["Predictions"])

@app.get("/")
def read_root():
    return {"message": "Welcome to Intelligent Property Management System API"}

@app.api_route("/health", methods=["GET", "HEAD"])
def health():
    return {"status": "ok"}
