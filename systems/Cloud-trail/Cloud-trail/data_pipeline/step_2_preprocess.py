import pandas as pd

def preprocess_data(all_records):
    print("--- Step 2: Preprocessing and Cleaning Data ---")
    
    df = pd.json_normalize(all_records)
    df['eventTime'] = pd.to_datetime(df['eventTime'])

    core_columns = [
        'eventTime', 'eventName', 'eventSource', 'awsRegion',
        'sourceIPAddress', 'userAgent', 'errorCode',
        'userIdentity.type', 'userIdentity.principalId',
        'userIdentity.arn', 'userIdentity.userName'
    ]
    
    columns_to_keep = [col for col in core_columns if col in df.columns]
    df_clean = df[columns_to_keep].copy()
    
    if 'userIdentity.principalId' not in df_clean.columns:
        print("Error: 'userIdentity.principalId' column not found.")
        return None

    print(f"Kept {len(columns_to_keep)} relevant columns.")
    return df_clean