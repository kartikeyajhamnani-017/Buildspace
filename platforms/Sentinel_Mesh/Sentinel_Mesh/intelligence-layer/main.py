"""
Sentinel ML Engine v2.0 - Engine Core
Three-layer threat detection pipeline: Rules → ML → Sequence.
"""

import time
import argparse
import redis
from rules import RuleBasedFilter
from model import MLAnomalyDetector
from sequence_analyser import SequenceAnalyzer
import config


class SentinelMLEngine:
    """
    Orchestrates all three detection layers for a given payload.
    Instantiate once; call analyze() per request.
    """

    def __init__(self, use_redis=True):
        # Layer 1
        self.rule_filter = RuleBasedFilter()

        # Layer 2 — one detector per protocol
        self.ml_detectors = {}
        for protocol, filename in [
            ('HTTP', 'sentinel_model_http.pkl'),
            ('SSH',  'sentinel_model_ssh.pkl'),
            ('DNS',  'sentinel_model_dns.pkl'),
        ]:
            try:
                detector = MLAnomalyDetector(protocol=protocol)
                detector.load_model(filename=filename)
                self.ml_detectors[protocol] = detector
            except Exception:
                self.ml_detectors[protocol] = None

        # Layer 3
        redis_client = None
        if use_redis:
            try:
                redis_client = redis.Redis(
                    host=config.REDIS_HOST,
                    port=config.REDIS_PORT,
                    db=config.REDIS_DB,
                    decode_responses=True,
                )
                redis_client.ping()
            except Exception:
                redis_client = None

        self.sequence_analyzer = SequenceAnalyzer(redis_client=redis_client)

    # ── Core Analysis ──────────────────────────────────────────────────────────

    def analyze(self, payload, ip_address='unknown', protocol='HTTP'):
        """
        Run payload through all three detection layers.

        Args:
            payload    (str): Raw payload string.
            ip_address (str): Source IP address.
            protocol   (str): 'HTTP', 'SSH', or 'DNS'.

        Returns:
            dict: Unified detection result.
        """
        start = time.time()
        self.sequence_analyzer.track_payload(ip_address, payload)

        # Layer 1 — Rules
        rule_result = self.rule_filter.check(payload)
        if rule_result['is_malicious']:
            return {
                'is_malicious':      True,
                'confidence':        rule_result['confidence'],
                'threat_level':      'CRITICAL',
                'detection_layer':   'Layer 1 (Rules)',
                'attack_type':       rule_result['attack_type'],
                'matched_rule':      rule_result['matched_rule'],
                'mitre_attack':      self.rule_filter.map_to_mitre(payload),
                'processing_time_ms': (time.time() - start) * 1000,
                'ip_address':        ip_address,
            }

        # Layer 2 — ML
        detector = self.ml_detectors.get(protocol.upper())
        if detector and detector.is_trained:
            ml_result = detector.predict(payload)
            if ml_result['is_malicious'] and ml_result['confidence'] > config.ANOMALY_SCORE_THRESHOLD:
                return {
                    'is_malicious':      True,
                    'confidence':        ml_result['confidence'],
                    'threat_level':      'HIGH',
                    'detection_layer':   'Layer 2 (ML)',
                    'attack_type':       'Unknown/Novel Attack',
                    'anomaly_score':     ml_result['anomaly_score'],
                    'mitre_attack':      self.rule_filter.map_to_mitre(payload),
                    'processing_time_ms': (time.time() - start) * 1000,
                    'ip_address':        ip_address,
                    'protocol':          protocol,
                }

        # Layer 3 — Sequence
        seq = self.sequence_analyzer.analyze_sequence(ip_address)
        if (
            seq['seq_recon_to_exploit']    == 1 or
            seq['seq_escalation_detected'] == 1 or
            seq['seq_attack_velocity']     >  20
        ):
            return {
                'is_malicious':      True,
                'confidence':        0.85,
                'threat_level':      'HIGH',
                'detection_layer':   'Layer 3 (Sequence)',
                'attack_type':       'Multi-Stage Attack Campaign',
                'sequence_features': seq,
                'mitre_attack':      self.rule_filter.map_to_mitre(payload),
                'processing_time_ms': (time.time() - start) * 1000,
                'ip_address':        ip_address,
            }

        # Clean
        return {
            'is_malicious':      False,
            'confidence':        0.0,
            'threat_level':      'NONE',
            'detection_layer':   'All layers passed',
            'attack_type':       None,
            'processing_time_ms': (time.time() - start) * 1000,
            'ip_address':        ip_address,
        }

    # ── Stats ──────────────────────────────────────────────────────────────────

    def get_statistics(self):
        """Return runtime statistics from all active components."""
        stats = {
            'rule_filter':      self.rule_filter.get_stats(),
            'sequence_analyzer': {
                'tracked_ips': len(self.sequence_analyzer.get_all_tracked_ips())
            },
        }
        for protocol, detector in self.ml_detectors.items():
            if detector:
                stats[f'ml_detector_{protocol.lower()}'] = detector.get_stats()
        return stats

    # ── Output Formatting ──────────────────────────────────────────────────────

    def format_result(self, result):
        """Return a human-readable string for a detection result."""
        lines = [
            '\n' + '=' * 80,
            '🚨 THREAT DETECTED — ' + result['threat_level'] if result['is_malicious'] else '✓ CLEAN — No Threat Detected',
            '=' * 80,
            f"IP Address:       {result['ip_address']}",
            f"Detection Layer:  {result['detection_layer']}",
            f"Confidence:       {result['confidence']:.2%}",
        ]
        if result['is_malicious']:
            lines.append(f"Attack Type:      {result['attack_type']}")
            if 'matched_rule'  in result: lines.append(f"Matched Rule:     {result['matched_rule']}")
            if 'anomaly_score' in result: lines.append(f"Anomaly Score:    {result['anomaly_score']:.3f}")
            if result.get('mitre_attack'):
                lines.append(f"MITRE ATT&CK:     {', '.join(result['mitre_attack'])}")
            if 'sequence_features' in result:
                lines.append('Sequence Features:')
                for k, v in result['sequence_features'].items():
                    lines.append(f"  {k}: {v}")
        lines += [f"\nProcessing Time:  {result['processing_time_ms']:.2f} ms", '=' * 80]
        return '\n'.join(lines)


# ==============================================================================
# ENTRY POINT  (interactive and file-based modes for testing)
# ==============================================================================

def _interactive_mode(engine):
    """Read payload|ip|protocol lines from stdin until quit."""
    print("Input format:  payload|ip_address|protocol")
    print("Protocol:      HTTP (default), SSH, DNS")
    print("Type 'quit' to exit.\n")

    while True:
        try:
            raw = input('> ').strip()
        except (EOFError, KeyboardInterrupt):
            break

        if not raw or raw.lower() in ('quit', 'exit', 'q'):
            break

        parts    = raw.split('|')
        payload  = parts[0].strip()
        ip       = parts[1].strip() if len(parts) > 1 else 'unknown'
        protocol = parts[2].strip().upper() if len(parts) > 2 else 'HTTP'

        result = engine.analyze(payload, ip_address=ip, protocol=protocol)
        print(engine.format_result(result))


def _file_mode(engine, filepath):
    """
    Read test cases from a file and run each through the engine.

    File format (one per line):
        payload|ip_address|protocol
    Lines starting with # are treated as comments and skipped.
    """
    import os
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Test file not found: {filepath}")

    with open(filepath, 'r') as f:
        lines = f.readlines()

    results = []
    for lineno, line in enumerate(lines, 1):
        line = line.strip()
        if not line or line.startswith('#'):
            continue

        parts    = line.split('|')
        if len(parts) < 1:
            continue

        payload  = parts[0].strip()
        ip       = parts[1].strip() if len(parts) > 1 else 'unknown'
        protocol = parts[2].strip().upper() if len(parts) > 2 else 'HTTP'

        result = engine.analyze(payload, ip_address=ip, protocol=protocol)
        results.append(result)
        print(f"[{lineno}] {engine.format_result(result)}")

    # Summary
    total     = len(results)
    threats   = sum(1 for r in results if r['is_malicious'])
    print(f"\n{'='*80}")
    print(f"FILE MODE SUMMARY: {threats}/{total} threats detected")
    print(f"{'='*80}")


def main():
    parser = argparse.ArgumentParser(description='Sentinel ML Engine v2.0')
    parser.add_argument('--mode', choices=['interactive', 'file'], default='interactive')
    parser.add_argument('--file', help='Path to test case file (required for --mode file)')
    parser.add_argument('--no-redis', action='store_true', help='Disable Redis')
    args = parser.parse_args()

    engine = SentinelMLEngine(use_redis=not args.no_redis)

    if args.mode == 'interactive':
        _interactive_mode(engine)
    elif args.mode == 'file':
        if not args.file:
            parser.error('--file is required when --mode file')
        _file_mode(engine, args.file)


if __name__ == '__main__':
    main()