import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import joblib

def generate_synthetic_risk_data():
    np.random.seed(42)
    n_samples = 1000
    
    data = {
        'monthly_income': np.random.uniform(50000, 1000000, n_samples),
        'employment_status': np.random.choice([0, 1, 2], n_samples), # 0: Unemployed, 1: Self-employed, 2: Employed
        'rent_amount': np.random.uniform(20000, 500000, n_samples),
        'previous_evictions': np.random.randint(0, 3, n_samples),
        'late_payments': np.random.randint(0, 10, n_samples),
        'credit_score': np.random.randint(300, 850, n_samples),
    }
    
    df = pd.DataFrame(data)
    
    # Simple risk scoring logic
    def calculate_risk(row):
        score = 0
        if row['monthly_income'] < row['rent_amount'] * 2: score += 2
        if row['employment_status'] == 0: score += 2
        if row['previous_evictions'] > 0: score += 3
        if row['late_payments'] > 2: score += 2
        if row['credit_score'] < 500: score += 3
        
        if score <= 2: return 'Low Risk'
        elif score <= 5: return 'Medium Risk'
        else: return 'High Risk'

    df['risk_level'] = df.apply(calculate_risk, axis=1)
    
    return df

def train_model():
    df = generate_synthetic_risk_data()
    X = df.drop('risk_level', axis=1)
    y = df['risk_level']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    
    # Save the model and feature columns
    model_data = {
        'model': model,
        'features': X.columns.tolist()
    }
    
    joblib.dump(model_data, 'risk_model.pkl')
    print("Tenant risk prediction model trained and saved.")

if __name__ == "__main__":
    train_model()
