
"""
Sentinel ML Engine v2.0 - Feature Test Suite
Tests all 4 implemented enhancements
"""

from main import SentinelMLEngine

# Test cases organized by enhancement
test_cases = {
    "Protocol-Aware (SQL)": [
        ("admin' OR '1'='1'--", True, "Classic SQLi"),
        ("' UNION SELECT password FROM users--", True, "UNION SQLi"),
        ("SELECT id FROM products WHERE category='electronics'", False, "Normal query"),
    ],
    
    "Protocol-Aware (XSS)": [
        ("<script>alert('XSS')</script>", True, "Script tag XSS"),
        ("<img src=x onerror=alert(1)>", True, "Event handler XSS"),
        ("<div class='container'>Hello</div>", False, "Normal HTML"),
    ],
    
    "Protocol-Aware (Command)": [
        ("; cat /etc/passwd", True, "Command injection"),
        ("&& whoami", True, "Chain command"),
        ("echo 'Hello World'", False, "Normal command"),
    ],
    
    "Protocol-Aware (Path Traversal)": [
        ("../../../../etc/passwd", True, "Unix traversal"),
        ("..\\..\\..\\windows\\system32", True, "Windows traversal"),
        ("/var/www/html/images/logo.png", False, "Normal path"),
    ],
    
    "N-grams (Obfuscation)": [
        ("ad'/**/OR/**/1=1--", True, "Comment-obfuscated SQL"),
        ("<ScRiPt>alert(1)</sCrIpT>", True, "Case-varied XSS"),
    ],
    
    "Evasion Detection": [
        ("%2527%2520OR%2520%25271%2527%253D%25271", True, "Double encoding"),
        ("SeLeCt * FrOm uSeRs", True, "Case chaos"),
        ("SEL/**/ECT/**/password", True, "Comment injection"),
    ],
    
    "Benign Traffic": [
        ("GET /index.html HTTP/1.1", False, "Normal request"),
        ("search?q=python tutorials", False, "Normal search"),
        ("POST /api/users {\"name\": \"John\"}", False, "Normal API"),
    ],
}

def run_tests():
    print("="*80)
    print("SENTINEL ML ENGINE v2.0 - FEATURE TEST SUITE")
    print("="*80)
    
    engine = SentinelMLEngine(use_redis=False)
    
    total_tests = 0
    passed_tests = 0
    failed_tests = []
    
    for category, tests in test_cases.items():
        print(f"\n{'='*80}")
        print(f"Testing: {category}")
        print('='*80)
        
        for payload, expected_malicious, description in tests:
            total_tests += 1
            
            result = engine.analyze(payload, ip_address="test_ip")
            detected = result['is_malicious']
            
            if detected == expected_malicious:
                status = "✓ PASS"
                passed_tests += 1
            else:
                status = "✗ FAIL"
                failed_tests.append((category, description, payload, expected_malicious, detected))
            
            print(f"\n{status} - {description}")
            print(f"  Payload: {payload[:60]}...")
            print(f"  Expected: {'Malicious' if expected_malicious else 'Clean'}")
            print(f"  Detected: {'Malicious' if detected else 'Clean'} ({result['confidence']:.0%} confidence)")
            if detected:
                print(f"  Layer: {result['detection_layer']}")
    
    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {passed_tests} ({passed_tests/total_tests*100:.1f}%)")
    print(f"Failed: {len(failed_tests)} ({len(failed_tests)/total_tests*100:.1f}%)")
    
    if failed_tests:
        print("\nFailed Tests:")
        for category, desc, payload, expected, actual in failed_tests:
            print(f"  [{category}] {desc}")
            print(f"    Expected: {expected}, Got: {actual}")
            print(f"    Payload: {payload[:60]}...")
    
    print("="*80)

if __name__ == "__main__":
    run_tests()