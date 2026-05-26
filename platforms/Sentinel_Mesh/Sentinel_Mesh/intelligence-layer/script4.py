from main import SentinelMLEngine

print("=" * 60)
print("  ENGINE LOAD TEST")
print("=" * 60)

engine = SentinelMLEngine(use_redis=False)

for protocol, detector in engine.ml_detectors.items():
    if detector and detector.is_trained:
        print(f"  {protocol}: ✓ loaded and ready")
    else:
        print(f"  {protocol}: ✗ not loaded")