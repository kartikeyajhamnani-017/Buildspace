def report_anomalies(df_results):
    """
    Step 5: Prints a final, readable report of any detected anomalies.
    """
    print("\n" + "="*40)
    print("--- 🚨 FINAL ANOMALY REPORT 🚨 ---")
    print("="*40)

    # Filter the DataFrame to get only the anomalies
    anomalies = df_results[df_results['is_anomaly'] == -1]

    if anomalies.empty:
        print("\n--- ✅ No Anomalies Detected ---")
        print("The model did not flag any entities as anomalous.")
        
    else:
        print(f"\n--- ❗️ {len(anomalies)} Anomalous Entities Detected! ---")
        
        for principal_id, data in anomalies.iterrows():
            print("\n" + "="*30)
            print(f"  SUSPICIOUS ACTOR ID: {principal_id}")
            print("="*30)
            print("  Behavioral Profile:")
            print(f"    - Total Events:     {int(data['event_count'])}")
            print(f"    - Error Count:      {int(data['error_count'])}")
            print(f"    - Unique Services:  {int(data['unique_services_used'])}")
            print(f"    - Unique Regions:   {int(data['unique_regions'])}")
            print(f"    - Unique IPs:       {int(data['unique_ips'])}")
            print(f"    - Night Events:     {int(data['night_events'])}")
            print(f"\n  Model Anomaly Score: {data['anomaly_score']:.4f}")
            print("="*30)