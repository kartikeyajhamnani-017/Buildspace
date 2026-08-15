"""
Sentinel ML Engine v2.0 - Protocol Fingerprinter
Lightweight structural inference used to validate the ingestor's
protocol hint before routing to a single ML model.

This does NOT replace full feature extraction. It is a cheap,
regex/structure-based pre-check that answers one question:
"does this payload structurally look like the protocol it claims to be?"
"""

import re


# ==============================================================================
# SIGNAL DEFINITIONS
# ==============================================================================
# Each signal has a weight. Higher weight = stronger indicator for that protocol.
# Weights are heuristic, not learned — kept intentionally simple and auditable.

_SSH_SIGNALS = [
    (r'^SSH-\d+\.\d+',                                   4),  # version banner prefix
    (r'publickey|diffie-hellman|curve25519|chacha20',    3),
    (r'arcfour|blowfish-cbc|direct-tcpip|tcpip-forward',  3),
    (r'gssapi|keyboard-interactive',                      2),
]

_DNS_SIGNALS = [
    (r'^(ANY|TXT|NULL|MX|AAAA|CNAME)\s',                 4),  # record type prefix
    # Pure domain shape — REQUIRES at least one dot (two labels minimum).
    # A bare word like "admin" or "root" must NOT match here; without the
    # dot requirement this previously misclassified short SSH usernames
    # as high-confidence DNS.
    (r'^[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?)+$', 2),
    (r'\.(ru|top|xyz|biz|info|online|site|club)$',       1),  # common abused TLD
]

_HTTP_SIGNALS = [
    (r'^(GET|POST|PUT|DELETE|HEAD|OPTIONS|PATCH)\s',     4),  # HTTP verb prefix
    (r'HTTP/\d\.\d',                                      3),
    (r"'|\"|<script|UNION|onerror|onload|javascript:",   2),  # injection-style chars
]

_SIGNAL_TABLE = {
    'SSH':  _SSH_SIGNALS,
    'DNS':  _DNS_SIGNALS,
    'HTTP': _HTTP_SIGNALS,
}

# The only protocols a model actually exists for. A hint outside this set
# has nothing to be "trusted" against — see agrees_with_hint().
_KNOWN_PROTOCOLS = {'HTTP', 'SSH', 'DNS'}


# ==============================================================================
# STRUCTURAL ADJUSTMENTS
# ==============================================================================

def _structural_adjustments(payload):
    """
    Additional non-regex structural signals that don't fit the table above.
    Returns a dict of protocol -> bonus score.
    """
    bonus = {'HTTP': 0, 'SSH': 0, 'DNS': 0}

    has_space   = ' ' in payload
    dot_count   = payload.count('.')
    length      = len(payload)

    # DNS payloads are dotted, spaceless, and reasonably short
    if not has_space and dot_count >= 1 and length <= 253:
        bonus['DNS'] += 1

    # SSH payloads are often short and may contain binary/control bytes
    if length < 80 and any(ord(c) < 0x20 or ord(c) > 0x7E for c in payload):
        bonus['SSH'] += 2

    # HTTP payloads tend to contain query-string or path-like structure
    if '/' in payload and has_space:
        bonus['HTTP'] += 1

    # URL-encoded byte sequences (%XX) are a web/HTTP-specific encoding
    # artifact — they don't occur in SSH banners or DNS domain names.
    # Count occurrences anywhere in the payload (not just back-to-back,
    # since real-world encoded payloads interleave %XX with decoded
    # literal characters, e.g. %2527%2520OR%2520%25271%2527%253D%25271).
    # A handful of scattered %XX tokens is normal noise; three or more is
    # a meaningful signal of URL encoding rather than coincidence.
    url_encoded_count = len(re.findall(r'%[0-9a-fA-F]{2}', payload))
    if url_encoded_count >= 3:
        bonus['HTTP'] += 3

    return bonus


# ==============================================================================
# PUBLIC API
# ==============================================================================

def infer_protocol(payload):
    """
    Infer the most likely protocol from payload structure alone.

    Args:
        payload (str): Raw payload string.

    Returns:
        tuple: (protocol: str, confidence: float 0-1)
               confidence is the winning score's share of total score.
               Returns ('HTTP', 0.0) for empty/ambiguous payloads — HTTP
               is the safe structural default since it is the most
               permissive feature set.
    """
    if not payload:
        return 'HTTP', 0.0

    scores = {'HTTP': 0, 'SSH': 0, 'DNS': 0}

    for protocol, signals in _SIGNAL_TABLE.items():
        for pattern, weight in signals:
            if re.search(pattern, payload, re.IGNORECASE):
                scores[protocol] += weight

    bonus = _structural_adjustments(payload)
    for protocol in scores:
        scores[protocol] += bonus[protocol]

    total = sum(scores.values())
    if total == 0:
        return 'HTTP', 0.0

    winner     = max(scores, key=scores.get)
    confidence = scores[winner] / total

    return winner, round(confidence, 4)


def agrees_with_hint(payload, hint, min_confidence=0.55):
    """
    Check whether the structural inference agrees with an externally
    supplied protocol hint (e.g. from the ingestor's port-based guess).

    Args:
        payload        (str):   Raw payload string.
        hint           (str):   Protocol hint from the caller ('HTTP'/'SSH'/'DNS').
        min_confidence (float): Minimum confidence required to trust agreement.

    Returns:
        tuple: (agrees: bool, inferred: str, confidence: float)
               agrees is True only if inferred == hint AND confidence >= min_confidence.
               When confidence is below threshold, the structure is too
               ambiguous to either confirm or contradict the hint, so
               agrees is also True (benefit of the doubt — avoids
               unnecessary full multi-model scans on short/ambiguous payloads).
               A hint outside {'HTTP', 'SSH', 'DNS'} can never agree,
               regardless of confidence — there is no model to route it
               to directly, so it must fall back to the brute-force scan.
    """
    hint = (hint or 'HTTP').upper().strip()
    inferred, confidence = infer_protocol(payload)

    if hint not in _KNOWN_PROTOCOLS:
        # Unrecognized hint (bad ingestor data, typo, unmapped protocol).
        # "Benefit of the doubt" has nothing to defer to here, so this
        # must not be trusted — force the caller onto the brute-force path.
        return False, inferred, confidence

    if confidence < min_confidence:
        # Too ambiguous to contradict the hint — trust it
        return True, inferred, confidence

    return (inferred == hint), inferred, confidence