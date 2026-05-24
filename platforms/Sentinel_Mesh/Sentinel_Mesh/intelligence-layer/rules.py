"""
Rule-Based Filter (Layer 1)
Exact keyword and regex matching against known attack signatures.
Response time: <1ms.
"""

import re
import config


class RuleBasedFilter:
    """
    Layer 1: Fast rule-based detection.
    Checks payloads against BLACKLIST_KEYWORDS and ATTACK_PATTERNS from config.
    """

    def __init__(self):
        self.blacklist       = config.BLACKLIST_KEYWORDS
        self.attack_patterns = config.ATTACK_PATTERNS
        self.stats           = {'total_checks': 0, 'blocked_count': 0}

    def check(self, payload):
        """
        Check payload against all blacklist rules.

        Args:
            payload (str): Raw payload string.

        Returns:
            dict: is_malicious, confidence, matched_rule, attack_type, layer.
        """
        self.stats['total_checks'] += 1
        lower = payload.lower()

        for keyword in self.blacklist:
            if keyword.lower() in lower:
                self.stats['blocked_count'] += 1
                return {
                    'is_malicious': True,
                    'confidence':   config.RULE_BASED_CONFIDENCE,
                    'matched_rule': keyword,
                    'attack_type':  self._classify_attack_type(keyword),
                    'layer':        'Rule-Based (Layer 1)',
                }

        return {
            'is_malicious': False,
            'confidence':   0.0,
            'matched_rule': None,
            'attack_type':  None,
            'layer':        'Rule-Based (Layer 1)',
        }

    def map_to_mitre(self, payload):
        """
        Map payload to MITRE ATT&CK technique IDs.

        Returns:
            list[str]: Matched technique IDs (e.g. ['T1059', 'T1190']).
        """
        return [
            tid for tid, pattern in self.attack_patterns.items()
            if re.search(pattern, payload, re.IGNORECASE)
        ]

    def get_stats(self):
        total = self.stats['total_checks']
        return {
            'total_checks':  total,
            'blocked_count': self.stats['blocked_count'],
            'block_rate':    self.stats['blocked_count'] / total if total else 0.0,
        }

    # ── Internal ───────────────────────────────────────────────────────────────

    def _classify_attack_type(self, keyword):
        """
        Map matched keyword to attack category.

        SSH and DNS are checked first to prevent substring false matches
        (e.g. 'sh' inside 'libssh' triggering Command Injection).
        """
        lower = keyword.lower()

        _SSH = [
            'libssh', 'ssh-1.99', 'ssh-2.0-masscan',
            'direct-tcpip', 'forwarded-tcpip', 'tcpip-forward',
            'diffie-hellman-group1', 'arcfour', 'blowfish-cbc',
            'root:root', 'admin:admin', 'root:toor', 'admin:password',
        ]
        if any(k in lower for k in _SSH):
            return 'SSH Exploit / Credential Attack'

        _DNS = [
            '.tunnel.', '.exfil.', 'dnscat', 'iodine',
            'any isc.org', 'any google.com', 'null encodedpayload',
        ]
        if any(k in lower for k in _DNS):
            return 'DNS Tunneling / Amplification'

        if re.search(r'\b(select|union|drop|insert|exec|xp_cmdshell)\b', lower):
            return 'SQL Injection'

        if re.search(r'\b(script|javascript|onerror|onload|alert)\b', lower):
            return 'Cross-Site Scripting (XSS)'

        if re.search(r'\b(cat|bash|sh|wget|curl|whoami|chmod|bin)\b', lower):
            return 'Command Injection'

        if '../' in lower or '..\\' in lower:
            return 'Path Traversal'

        return 'Unknown Attack'