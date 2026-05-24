"""
Sequence Analyzer (Layer 3)
Sliding-window behavioral analysis per source IP.
Detects multi-step attack campaigns, recon-to-exploit chains, and velocity anomalies.
"""

import time
import json
from collections import deque
import config


class SequenceAnalyzer:
    """
    Layer 3: Sequential attack pattern detection.
    Backed by Redis when available; falls back to in-memory storage.
    """

    def __init__(self, redis_client=None):
        self.redis_client     = redis_client
        self.in_memory_storage = {} if redis_client is None else None

    # ── Public API ─────────────────────────────────────────────────────────────

    def track_payload(self, ip_address, payload, timestamp=None):
        """
        Append a payload entry to the sliding window for ip_address.

        Args:
            ip_address (str): Source IP.
            payload    (str): Raw payload string.
            timestamp  (float): Unix timestamp (defaults to now).
        """
        if timestamp is None:
            timestamp = time.time()

        window = self._get_window(ip_address)
        window.append({
            'payload':   payload,
            'timestamp': timestamp,
            'length':    len(payload),
        })
        self._set_window(ip_address, window)

    def analyze_sequence(self, ip_address):
        """
        Compute behavioral sequence features for ip_address.

        Returns:
            dict: seq_payload_count, seq_escalation_detected,
                  seq_recon_to_exploit, seq_complexity_increase,
                  seq_attack_velocity, seq_time_span.
        """
        window = self._get_window(ip_address)

        if len(window) < 2:
            return {
                'seq_payload_count':      len(window),
                'seq_escalation_detected': 0,
                'seq_recon_to_exploit':    0,
                'seq_complexity_increase': 0,
                'seq_attack_velocity':     0.0,
                'seq_time_span':           0.0,
            }

        return {
            'seq_payload_count':      len(window),
            'seq_escalation_detected': self._detect_escalation(window),
            'seq_recon_to_exploit':    self._detect_recon_to_exploit(window),
            'seq_complexity_increase': self._measure_complexity_trend(window),
            'seq_attack_velocity':     self._calculate_velocity(window),
            'seq_time_span':           self._calculate_time_span(window),
        }

    def get_all_tracked_ips(self):
        """Return list of all currently tracked IP addresses."""
        if self.redis_client:
            return [k.replace('window:', '') for k in self.redis_client.keys('window:*')]
        return list(self.in_memory_storage.keys())

    def clear_ip(self, ip_address):
        """Remove tracking data for ip_address."""
        if self.redis_client:
            self.redis_client.delete(f'window:{ip_address}')
        elif ip_address in self.in_memory_storage:
            del self.in_memory_storage[ip_address]

    # ── Detection Logic ────────────────────────────────────────────────────────

    def _detect_escalation(self, window):
        """Detect privilege escalation: early recon → later privilege commands."""
        payloads = [e['payload'].lower() for e in window]
        early_recon = any(
            kw in payloads[0]
            for kw in ['whoami', 'id', 'uname', 'hostname']
        )
        later_privesc = any(
            kw in p
            for p in payloads[-3:]
            for kw in ['sudo', 'su -', 'passwd', '/etc/shadow']
        )
        return 1 if (early_recon and later_privesc) else 0

    def _detect_recon_to_exploit(self, window):
        """Detect SQL recon (SELECT 1, version()) followed by exploit (UNION, DROP)."""
        if len(window) < 3:
            return 0
        wl            = list(window)
        early         = [e['payload'].lower() for e in wl[:3]]
        later         = [e['payload'].lower() for e in wl[-3:]]
        recon_kws     = ['select 1', 'version()', 'database()', '@@version']
        exploit_kws   = ['union', 'drop', 'insert', 'delete', 'update']
        early_is_recon  = any(kw in p for p in early for kw in recon_kws)
        later_is_exploit = any(kw in p for p in later for kw in exploit_kws)
        return 1 if (early_is_recon and later_is_exploit) else 0

    def _measure_complexity_trend(self, window):
        """Return 1 if payload complexity increases significantly over time."""
        if len(window) < 3:
            return 0
        scores = [
            len(e['payload']) + sum(2 for c in e['payload'] if not c.isalnum())
            for e in window
        ]
        third   = max(len(scores) // 3, 1)
        early   = sum(scores[:third]) / third
        late    = sum(scores[-third:]) / third
        return 1 if late > early * 1.5 else 0

    def _calculate_velocity(self, window):
        """Return payloads-per-minute rate."""
        span = self._calculate_time_span(window)
        if span == 0:
            return 0.0
        return (len(window) / span) * 60

    def _calculate_time_span(self, window):
        """Return elapsed seconds across the window."""
        if len(window) < 2:
            return 0.0
        return window[-1]['timestamp'] - window[0]['timestamp']

    # ── Storage Helpers ────────────────────────────────────────────────────────

    def _get_window(self, ip_address):
        if self.redis_client:
            data = self.redis_client.get(f'window:{ip_address}')
            try:
                entries = json.loads(data) if data else []
                if not isinstance(entries, list):
                    entries = []
            except Exception:
                entries = []
            return deque(entries, maxlen=config.SEQUENCE_WINDOW_SIZE)
        else:
            if ip_address not in self.in_memory_storage:
                self.in_memory_storage[ip_address] = deque(maxlen=config.SEQUENCE_WINDOW_SIZE)
            return self.in_memory_storage[ip_address]

    def _set_window(self, ip_address, window):
        if self.redis_client:
            self.redis_client.setex(
                f'window:{ip_address}',
                config.SEQUENCE_TIMEOUT,
                json.dumps(list(window)),
            )
        else:
            self.in_memory_storage[ip_address] = window