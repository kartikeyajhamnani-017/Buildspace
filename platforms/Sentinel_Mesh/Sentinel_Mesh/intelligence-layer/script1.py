import config
import os

print("=" * 60)
print("  MODEL PATH VERIFICATION")
print("=" * 60)

# Check config paths exist on disk
for protocol in ['HTTP', 'SSH', 'DNS']:
    model_path  = config.MODEL_PATHS[protocol]
    scaler_path = config.SCALER_PATHS[protocol]
    model_ok    = os.path.exists(model_path)
    scaler_ok   = os.path.exists(scaler_path)
    print(f"\n{protocol}")
    print(f"  model  → {model_path}")
    print(f"  {'✓' if model_ok  else '✗ NOT FOUND'}")
    print(f"  scaler → {scaler_path}")
    print(f"  {'✓' if scaler_ok else '✗ NOT FOUND'}")