import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
import joblib
import os

def generate_synthetic_rent_data():
    np.random.seed(42)
    n_samples = 1000
    
    locations = ['Lagos', 'Abuja', 'Port Harcourt', 'Ibadan', 'Enugu']
    property_types = ['Apartment', 'House', 'Duplex', 'Studio']
    
    data = {
        'location': np.random.choice(locations, n_samples),
        'property_type': np.random.choice(property_types, n_samples),
        'bedrooms': np.random.randint(1, 6, n_samples),
        'bathrooms': np.random.randint(1, 5, n_samples),
        'toilets': np.random.randint(1, 5, n_samples),
        'size_sqm': np.random.uniform(50, 500, n_samples),
        'has_parking': np.random.choice([0, 1], n_samples),
        'has_security': np.random.choice([0, 1], n_samples),
        'furnished': np.random.choice([0, 1], n_samples),
    }
    
    df = pd.DataFrame(data)
    
    # Base price calculation with some noise
    df['rent_price'] = (
        df['bedrooms'] * 50000 + 
        df['bathrooms'] * 20000 + 
        df['size_sqm'] * 1000 + 
        df['has_parking'] * 30000 + 
        df['has_security'] * 50000 + 
        df['furnished'] * 100000 +
        np.random.normal(0, 50000, n_samples)
    )
    
    # Simple encoding for demo
    df = pd.get_dummies(df, columns=['location', 'property_type'])
    
    return df

def train_model():
    df = generate_synthetic_rent_data()
    X = df.drop('rent_price', axis=1)
    y = df['rent_price']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    
    # Save the model and feature columns
    model_data = {
        'model': model,
        'features': X.columns.tolist()
    }
    
    joblib.dump(model_data, 'rent_model.pkl')
    print("Rent prediction model trained and saved.")

if __name__ == "__main__":
    train_model()
