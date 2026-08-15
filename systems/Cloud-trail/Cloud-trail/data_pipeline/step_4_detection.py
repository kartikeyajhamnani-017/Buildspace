import pandas as pd
from sklearn.ensemble import IsolationForest

def detect_anomalies(df_behavior):
    """
    Step 4: Applies the IsolationForest model to find anomalous profiles.
    """
    print("--- Step 4: Running Anomaly Detection Model ---")

    # Initialize and fit the model
    # contamination='auto' is a good, flexible default
    model = IsolationForest(n_estimators=100, contamination='auto', random_state=42)
    model.fit(df_behavior)

    # Get predictions
    scores = model.decision_function(df_behavior)
    predictions = model.predict(df_behavior)

    # Add predictions back to the DataFrame
    df_behavior['anomaly_score'] = scores
    df_behavior['is_anomaly'] = predictions
    
    print("Model fitting and prediction complete.")
    
    # Sort by score to see most anomalous at the top
    df_behavior_results = df_behavior.sort_values(by='anomaly_score', ascending=True)
    return df_behavior_results