import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def detect_fraud_rules(df):
    """
    Apply rule-based fraud detection
    Returns DataFrame with fraud flags and reasons
    """
    
    # Make a copy to avoid modifying original
    df = df.copy()
    
    # Initialize fraud flags
    df['is_suspicious'] = False
    df['fraud_reasons'] = ''
    df['risk_score'] = 0
    
    # Rule 1: Unusually high amounts (> 10,000)
    high_amount_mask = df['amount'] > 10000
    df.loc[high_amount_mask, 'is_suspicious'] = True
    df.loc[high_amount_mask, 'fraud_reasons'] += 'High amount (>₹10,000); '
    df.loc[high_amount_mask, 'risk_score'] += 30
    
    # Rule 2: Micro-transactions (< 1)
    micro_txn_mask = df['amount'] < 1
    df.loc[micro_txn_mask, 'is_suspicious'] = True
    df.loc[micro_txn_mask, 'fraud_reasons'] += 'Micro-transaction (<₹1); '
    df.loc[micro_txn_mask, 'risk_score'] += 20
    
    # Rule 3: High-risk categories
    risky_categories = ['Online Gambling', 'Cryptocurrency', 'Cash Equivalent']
    risky_merchants = df['category'].isin(risky_categories) | df['merchant'].str.contains('Gambling', case=False, na=False)
    df.loc[risky_merchants, 'is_suspicious'] = True
    df.loc[risky_merchants, 'fraud_reasons'] += 'High-risk category; '
    df.loc[risky_merchants, 'risk_score'] += 25
    
    # Rule 4: Check for rapid transactions from same user
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df = df.sort_values('timestamp')
    
    for user_id in df['user_id'].unique():
        user_df = df[df['user_id'] == user_id].copy()
        
        if len(user_df) > 1:
            # Check time difference between consecutive transactions
            user_df['time_diff'] = user_df['timestamp'].diff()
            
            # Transactions within 5 minutes
            rapid_mask = user_df['time_diff'] < timedelta(minutes=5)
            rapid_indices = user_df[rapid_mask].index
            
            df.loc[rapid_indices, 'is_suspicious'] = True
            df.loc[rapid_indices, 'fraud_reasons'] += 'Rapid transactions (<5 min); '
            df.loc[rapid_indices, 'risk_score'] += 35
    
    # Rule 5: Impossible travel (different cities in short time)
    for user_id in df['user_id'].unique():
        user_df = df[df['user_id'] == user_id].copy()
        
        if len(user_df) > 1:
            for i in range(len(user_df) - 1):
                current_location = user_df.iloc[i]['location']
                next_location = user_df.iloc[i + 1]['location']
                time_diff = (user_df.iloc[i + 1]['timestamp'] - user_df.iloc[i]['timestamp']).total_seconds() / 3600
                
                # Different cities within 2 hours = suspicious
                if current_location != next_location and time_diff < 2:
                    next_idx = user_df.iloc[i + 1].name
                    df.loc[next_idx, 'is_suspicious'] = True
                    df.loc[next_idx, 'fraud_reasons'] += f'Impossible travel ({current_location}→{next_location} in {time_diff:.1f}h); '
                    df.loc[next_idx, 'risk_score'] += 40
    
    # Classify risk level
    df['risk_level'] = 'Low'
    df.loc[df['risk_score'] > 30, 'risk_level'] = 'Medium'
    df.loc[df['risk_score'] > 60, 'risk_level'] = 'High'
    
    # Clean up fraud reasons (remove trailing semicolon)
    df['fraud_reasons'] = df['fraud_reasons'].str.rstrip('; ')
    
    return df