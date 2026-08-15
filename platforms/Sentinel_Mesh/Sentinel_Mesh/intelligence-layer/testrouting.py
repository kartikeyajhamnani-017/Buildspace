"""
Sentinel ML Engine v2.0 - Hybrid Routing Test Suite
Validates protocol_fingerprint.py routing decisions against real
trained models. Run after main.py loads its .pkl files successfully.

Usage:
    python test_routing.py --no-redis
"""

import argparse
from main import SentinelMLEngine


# Format: (description, payload, ip, protocol_hint, expected_routing, expected_malicious)
# expected_routing: 'direct' or 'full_scan' or None (Layer 1 hit, routing n/a)
ROUTING_CASES = [
    # ── Correctly tagged — expect direct routing ──────────────────────────────
    ("DGA domain, correctly tagged DNS",
     "xkqvzmnprtbsdfghjkl.ru", "10.0.0.1", "DNS", "direct", True),

    ("SSH overflow probe, correctly tagged SSH",
     "SSH-2.0-OpenSSH_9.9p1_" + "A"*60, "10.0.0.2", "SSH", "direct", True),

    # ── Mismatched flag — expect full_scan, still caught ──────────────────────
    ("Deep label DNS chain tagged as HTTP",
     "a.b.c.d.e.f.g.h.transfer.example.org", "127.0.0.1", "HTTP", "full_scan", True),

    ("Base32 exfil domain tagged as SSH",
     "MFRGGZDFMZTWQ2LK.data.example.net", "127.0.0.1", "SSH", "full_scan", True),

    ("Base32 exfil domain tagged as HTTP",
     "MFRGGZDFMZTWQ2LK.data.example.net", "127.0.0.1", "HTTP", "full_scan", True),

    ("Pure DGA domain tagged as SSH",
     "zcrftgvbnhjkmpw.com", "127.0.0.1", "SSH", "full_scan", True),

    # ── No flag supplied — defaults to HTTP hint, structure overrides ─────────
    ("No protocol flag on deep DNS chain",
     "a.b.c.d.e.f.g.h.transfer.example.org", "unknown", "HTTP", "full_scan", True),

    # ── Ambiguous short payloads — expect hint trusted (direct) ───────────────
    ("Bare username 'admin' tagged SSH",
     "admin", "10.0.1.1", "SSH", "direct", None),  # malicious depends on model training

    ("Bare username 'oracle' tagged SSH",
     "oracle", "10.0.1.3", "SSH", "direct", None),

    # ── Correctly tagged evasive payloads — expect direct, still caught ───────
    ("Double-encoded SQLi, correctly tagged HTTP",
     "%2527%2520OR%2520%25271%2527%253D%25271", "10.0.2.1", "HTTP", "direct", True),

    ("Weak cipher list, correctly tagged SSH",
     "3des-cbc,aes128-cbc,aes256-cbc", "10.0.2.2", "SSH", "direct", True),

    # ── Wrong flag on evasive payloads — expect full_scan still catches ───────
    ("Double-encoded SQLi mistagged as DNS",
     "%2527%2520OR%2520%25271%2527%253D%25271", "10.0.3.1", "DNS", "full_scan", True),

    ("Hex DNS subdomain mistagged as HTTP",
     "a1f3c9d2b8e4.a2b3c4d5.evil.com", "10.0.3.2", "HTTP", "full_scan", True),
]


def run():
    parser = argparse.ArgumentParser()
    parser.add_argument('--no-redis', action='store_true')
    args = parser.parse_args()

    engine = SentinelMLEngine(use_redis=not args.no_redis)

    passed, failed = 0, []

    print("=" * 80)
    print("  HYBRID ROUTING TEST SUITE")
    print("=" * 80)

    for desc, payload, ip, hint, expected_routing, expected_malicious in ROUTING_CASES:
        result = engine.analyze(payload, ip_address=ip, protocol=hint)

        actual_routing   = result.get('routing')
        actual_malicious = result['is_malicious']
        actual_layer     = result['detection_layer']

        # Layer 1 hits bypass routing entirely — treat as informational, not a routing failure
        if 'Layer 1' in actual_layer:
            print(f"  ⓘ SKIP  [Layer 1 hit, routing n/a]  {desc}")
            continue

        routing_ok    = (expected_routing is None or actual_routing == expected_routing)
        malicious_ok  = (expected_malicious is None or actual_malicious == expected_malicious)

        if routing_ok and malicious_ok:
            passed += 1
            print(f"  ✓ PASS  routing={actual_routing!s:10s}  malicious={actual_malicious!s:5s}  {desc}")
        else:
            failed.append((desc, expected_routing, actual_routing, expected_malicious, actual_malicious))
            print(f"  ✗ FAIL  routing={actual_routing!s:10s}  malicious={actual_malicious!s:5s}  {desc}")
            if not routing_ok:
                print(f"         expected routing={expected_routing}, got {actual_routing}")
            if not malicious_ok:
                print(f"         expected malicious={expected_malicious}, got {actual_malicious}")

    print("\n" + "=" * 80)
    print(f"  RESULT: {passed} passed, {len(failed)} failed")
    print("=" * 80)

    if failed:
        print("\nFailures:")
        for desc, exp_r, act_r, exp_m, act_m in failed:
            print(f"  - {desc}")
            print(f"    routing:   expected={exp_r} got={act_r}")
            print(f"    malicious: expected={exp_m} got={act_m}")


if __name__ == '__main__':
    run()