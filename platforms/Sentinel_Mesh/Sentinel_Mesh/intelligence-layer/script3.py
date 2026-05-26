from features import get_feature_names
import config

print("=" * 60)
print("  FEATURE COUNT ALIGNMENT")
print("=" * 60)

for protocol in ['HTTP', 'SSH', 'DNS']:
    with open(config.SCALER_PATHS[protocol], 'rb') as f:
        import pickle
        scaler = pickle.load(f)
    current = len(get_feature_names(protocol))
    trained = scaler.n_features_in_
    match   = '✓ MATCH' if current == trained else '✗ MISMATCH'
    print(f"  {protocol}: trained={trained} | current={current} | {match}")