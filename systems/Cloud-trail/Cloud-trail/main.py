# Import the specific functions ("services") from our module
from data_pipeline.step_1_ingest import load_data
from data_pipeline.step_2_preprocess import preprocess_data
from data_pipeline.step_3_feature_eng import engineer_features
from data_pipeline.step_4_detection import detect_anomalies
from data_pipeline.step_5_report import report_anomalies

def main():
    """
    Main pipeline orchestrator.
    """
    LOG_DIRECTORY = './cloudtrail_logs/CloudTrail_dataset/'
    
    # Run each "service" in order, passing data between them
    raw_records = load_data(LOG_DIRECTORY)
    
    if raw_records:
        df_clean = preprocess_data(raw_records)
        
        if df_clean is not None:
            df_behavior = engineer_features(df_clean)
            
            if df_behavior is not None and not df_behavior.empty:
                df_results = detect_anomalies(df_behavior)
                report_anomalies(df_results)
            elif df_behavior is not None:
                print("No behavioral profiles were created. Skipping detection.")
            

# Standard Python entry point
if __name__ == "__main__":
    print("--- Starting Anomaly Detection Pipeline ---")
    main()
    print("\n--- Pipeline Finished ---")