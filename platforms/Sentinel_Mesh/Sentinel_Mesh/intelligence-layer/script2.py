import pickle, config

print("=" * 60)
print("  MODEL LOAD VERIFICATION")
print("=" * 60)

for protocol in ['HTTP', 'SSH', 'DNS']:
    try:
        with open(config.MODEL_PATHS[protocol], 'rb') as f:
            model = pickle.load(f)
        with open(config.SCALER_PATHS[protocol], 'rb') as f:
            scaler = pickle.load(f)
        print(f"  {protocol}: OK — scaler expects {scaler.n_features_in_} features")
    except Exception as e:
        print(f"  {protocol}: FAILED — {e}")