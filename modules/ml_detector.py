import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

def detect_fraud_ml(df):
    """
    Use Isolation Forest to detect anomalies
    Returns DataFrame with ML-based fraud scores
    """
    
    df = df.copy()
    
    # Select features for ML model
    # We'll use: amount, hour of day, day of week
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df['hour'] = df['timestamp'].dt.hour
    df['day_of_week'] = df['timestamp'].dt.dayofweek
    
    # Count transactions per user
    user_txn_count = df.groupby('user_id').size()
    df['user_txn_count'] = df['user_id'].map(user_txn_count)
    
    # Features for ML
    features = ['amount', 'hour', 'day_of_week', 'user_txn_count']
    X = df[features].copy()
    
    # Handle any missing values
    X = X.fillna(0)
    
    # Standardize features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Train Isolation Forest
    iso_forest = IsolationForest(
        contamination=0.3,  # Expect ~30% anomalies
        random_state=42,
        n_estimators=100
    )
    
    # Predict (-1 for anomalies, 1 for normal)
    predictions = iso_forest.fit_predict(X_scaled)
    
    # Get anomaly scores (lower = more anomalous)
    anomaly_scores = iso_forest.score_samples(X_scaled)
    
    # Add to dataframe
    df['ml_anomaly'] = predictions == -1
    df['ml_anomaly_score'] = anomaly_scores
    
    # Normalize anomaly score to 0-100 (higher = more suspicious)
    min_score = anomaly_scores.min()
    max_score = anomaly_scores.max()
    df['ml_risk_score'] = 100 - ((anomaly_scores - min_score) / (max_score - min_score) * 100)
    
    return df

def combine_detections(df_rules, df_ml):
    """
    Combine rule-based and ML-based detection
    """
    
    df = df_rules.copy()
    
    # Add ML results
    df['ml_anomaly'] = df_ml['ml_anomaly']
    df['ml_risk_score'] = df_ml['ml_risk_score']
    
    # Combine risk scores (weighted average)
    df['combined_risk_score'] = (df['risk_score'] * 0.6 + df['ml_risk_score'] * 0.4)
    
    # Update suspicion flag if ML detects anomaly
    df.loc[df['ml_anomaly'], 'is_suspicious'] = True
    df.loc[df['ml_anomaly'], 'fraud_reasons'] += '; ML detected anomaly'
    
    # Reclassify risk levels based on combined score
    df['final_risk_level'] = 'Low'
    df.loc[df['combined_risk_score'] > 40, 'final_risk_level'] = 'Medium'
    df.loc[df['combined_risk_score'] > 70, 'final_risk_level'] = 'High'
    
    return df