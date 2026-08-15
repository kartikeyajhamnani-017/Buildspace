import pandas as pd

def engineer_features(df_clean):
    """
    Step 3: Transforms event logs into behavioral profiles for each user.
    """
    print("--- Step 3: Engineering Behavioral Features ---")
    
    ENTITY_ID = 'userIdentity.principalId'
    
    # Drop rows where this ID is missing
    df_clean = df_clean.dropna(subset=[ENTITY_ID])
    
    # 1. Engineer helper columns
    df_clean['is_error'] = df_clean['errorCode'].notnull().astype(int)
    df_clean['is_night_activity'] = ((df_clean['eventTime'].dt.hour >= 0) & 
                                     (df_clean['eventTime'].dt.hour <= 5)).astype(int)

    # 2. Group by entity and aggregate behaviors
    print(f"Grouping by '{ENTITY_ID}' to build profiles...")
    df_behavior = df_clean.groupby(ENTITY_ID).agg(
        event_count=pd.NamedAgg(column='eventName', aggfunc='count'),
        error_count=pd.NamedAgg(column='is_error', aggfunc='sum'),
        unique_services_used=pd.NamedAgg(column='eventSource', aggfunc='nunique'),
        unique_regions=pd.NamedAgg(column='awsRegion', aggfunc='nunique'),
        unique_ips=pd.NamedAgg(column='sourceIPAddress', aggfunc='nunique'),
        night_events=pd.NamedAgg(column='is_night_activity', aggfunc='sum')
    )
    
    print(f"Created {df_behavior.shape[0]} unique behavioral profiles.")
    return df_behavior