"""
Feature Engineering (Layer 2)
Protocol-aware feature extraction for HTTP, SSH, and DNS payloads.

Feature counts:
    HTTP : 6 stat + 13 SQL + 10 XSS + 9 cmd + 5 traversal + 7 evasion + ~15 ngram = ~65
    SSH  : 6 stat + 14 SSH-specific = 20
    DNS  : 6 stat + 13 DNS-specific = 19
"""

import re
import math
from collections import Counter
from urllib.parse import unquote
import config


# ==============================================================================
# UTILITY FUNCTIONS
# ==============================================================================

def calculate_entropy(text):
    """Shannon entropy — high value indicates obfuscation, shellcode, or DGA."""
    if not text:
        return 0.0
    counter = Counter(text)
    length  = len(text)
    return -sum((c / length) * math.log2(c / length) for c in counter.values())


def count_special_chars(text):
    """Count non-alphanumeric, non-whitespace characters."""
    return sum(1 for c in text if not c.isalnum() and not c.isspace())


def calculate_case_chaos(text):
    """
    Ratio of mixed-case words to total words.
    High value signals case-variation evasion (e.g. SeLeCt).
    """
    if not text:
        return 0.0
    words = re.findall(r'[a-zA-Z]+', text)
    if not words:
        return 0.0
    mixed = sum(
        1 for w in words
        if len(w) >= 3
        and any(c.isupper() for c in w)
        and any(c.islower() for c in w)
    )
    return mixed / len(words)


def calculate_avg_word_length(text):
    """Average length of alphabetic tokens."""
    words = re.findall(r'[a-zA-Z]+', text)
    if not words:
        return 0.0
    return sum(len(w) for w in words) / len(words)


# ==============================================================================
# STATISTICAL FEATURES  (protocol-agnostic, always extracted)
# ==============================================================================

def extract_statistical_features(payload):
    """6 universal baseline features extracted for every protocol."""
    length = len(payload)
    return {
        'stat_length':           length,
        'stat_entropy':          calculate_entropy(payload),
        'stat_special_char_ratio': count_special_chars(payload) / length if length else 0,
        'stat_digit_ratio':      sum(1 for c in payload if c.isdigit()) / length if length else 0,
        'stat_uppercase_ratio':  sum(1 for c in payload if c.isupper()) / length if length else 0,
        'stat_avg_word_length':  calculate_avg_word_length(payload),
    }


# ==============================================================================
# HTTP FEATURE EXTRACTORS
# ==============================================================================

def extract_sql_features(payload):
    """
    SQL injection features — 13 total.
    Applies double URL-decode before matching to catch encoded evasion.
    """
    decoded = payload
    for _ in range(2):
        new_decoded = unquote(decoded)
        if new_decoded == decoded:
            break
        decoded = new_decoded

    upper = decoded.upper()

    return {
        'sql_select_count':    upper.count('SELECT'),
        'sql_union_count':     upper.count('UNION'),
        'sql_drop_count':      upper.count('DROP'),
        'sql_insert_count':    upper.count('INSERT'),
        'sql_delete_count':    upper.count('DELETE'),
        'sql_exec_count':      upper.count('EXEC'),
        'sql_single_quote_count': decoded.count("'"),
        'sql_comment_count':   decoded.count('--') + decoded.count('/*'),
        'sql_semicolon_count': decoded.count(';'),
        'sql_equals_count':    decoded.count('='),
        'sql_or_pattern':      1 if re.search(r"'\s*OR\s*['1]", decoded, re.IGNORECASE) else 0,
        'sql_union_select':    1 if re.search(r'UNION.*SELECT', decoded, re.IGNORECASE) else 0,
        'sql_always_true':     1 if re.search(r"1\s*=\s*1|'1'\s*=\s*'1'", decoded) else 0,
    }


def extract_xss_features(payload):
    """XSS features — 10 total."""
    lower = payload.lower()
    return {
        'xss_script_tag':          lower.count('<script'),
        'xss_img_tag':             lower.count('<img'),
        'xss_iframe_tag':          lower.count('<iframe'),
        'xss_onerror':             lower.count('onerror'),
        'xss_onload':              lower.count('onload'),
        'xss_onclick':             lower.count('onclick'),
        'xss_javascript_protocol': lower.count('javascript:'),
        'xss_alert':               lower.count('alert('),
        'xss_eval':                lower.count('eval('),
        'xss_html_encoded':        payload.count('&#'),
    }


def extract_command_injection_features(payload):
    """Command injection features — 9 total."""
    lower = payload.lower()
    return {
        'cmd_pipe_count':       payload.count('|'),
        'cmd_semicolon_count':  payload.count(';'),
        'cmd_ampersand_count':  payload.count('&&') + payload.count('&'),
        'cmd_backtick_count':   payload.count('`'),
        'cmd_cat':              1 if 'cat ' in lower else 0,
        'cmd_ls':               1 if re.search(r'\bls\b', lower) else 0,
        'cmd_wget':             1 if 'wget' in lower else 0,
        'cmd_curl':             1 if 'curl' in lower else 0,
        'cmd_bash':             1 if '/bin/bash' in lower or '/bin/sh' in lower else 0,
    }


def extract_traversal_features(payload):
    """Path traversal features — 5 total."""
    return {
        'traversal_dotdot_unix':    payload.count('../'),
        'traversal_dotdot_windows': payload.count('..\\'),
        'traversal_etc_passwd':     1 if '/etc/passwd' in payload.lower() else 0,
        'traversal_windows_system': 1 if 'windows\\system' in payload.lower() else 0,
        'traversal_null_byte':      payload.count('%00') + payload.count('\\x00'),
    }


def extract_evasion_features(payload):
    """HTTP evasion detection features — 7 total."""
    encoding_layers = 0
    decoded = payload
    for _ in range(5):
        try:
            new_decoded = unquote(decoded)
            if new_decoded == decoded:
                break
            decoded = new_decoded
            encoding_layers += 1
        except Exception:
            break

    return {
        'evasion_encoding_layers':    encoding_layers,
        'evasion_url_encoded_chars':  payload.count('%'),
        'evasion_hex_chars':          len(re.findall(r'\\x[0-9a-fA-F]{2}', payload)),
        'evasion_unicode_chars':      len(re.findall(r'\\u[0-9a-fA-F]{4}', payload)),
        'evasion_case_variation':     calculate_case_chaos(payload),
        'evasion_comment_injection':  payload.count('/*') + payload.count('*/'),
        'evasion_unusual_whitespace': payload.count('\t') + payload.count('\r') + payload.count('\n'),
    }


def extract_ngram_features(payload):
    """Dangerous n-gram matching — ~15 features from config.DANGEROUS_NGRAMS."""
    lower = payload.lower()
    features = {}
    for ngram in config.DANGEROUS_NGRAMS:
        key = (
            ngram.replace(' ', '_')
                 .replace('/', 'slash')
                 .replace('<', 'lt')
                 .replace('>', 'gt')
        )
        features[f'ngram_{key}'] = 1 if ngram.lower() in lower else 0
    return features


# ==============================================================================
# SSH FEATURE EXTRACTORS
# ==============================================================================

_SSH_EXPLOIT_SIGNATURES = [
    'libssh',
    'openssh 7.',
    'dropbear',
    '\x00' * 8,
    'diffie-hellman-group1',
    'arcfour',
]

_COMMON_SSH_USERNAMES = [
    'root', 'admin', 'administrator', 'ubuntu', 'ec2-user',
    'pi', 'oracle', 'postgres', 'mysql', 'guest', 'test',
    'support', 'user', 'deploy', 'ansible', 'vagrant',
]


def extract_ssh_features(payload):
    """SSH-specific attack features — 14 total."""
    lower        = payload.lower()
    payload_bytes = payload.encode('utf-8', errors='replace')

    is_short_auth       = 1 if len(payload) < 64 else 0
    common_username_hit = 1 if any(
        re.search(rf'\b{re.escape(u)}\b', lower) for u in _COMMON_SSH_USERNAMES
    ) else 0
    repeated_char_ratio = (
        Counter(payload).most_common(1)[0][1] / len(payload) if payload else 0.0
    )
    banner_probe        = 1 if re.search(r'SSH-\d+\.\d+-', payload, re.IGNORECASE) else 0
    openssh_probe       = 1 if re.search(r'openssh[_\s]?\d+\.\d+', lower) else 0
    exploit_sig         = 1 if any(sig in lower for sig in _SSH_EXPLOIT_SIGNATURES) else 0
    cve_2018_10933      = 1 if 'libssh' in lower else 0
    weak_kex            = 1 if re.search(r'diffie-hellman-group1|gss-group1', lower) else 0
    weak_cipher         = 1 if re.search(r'arcfour|rc4|des-cbc|blowfish-cbc', lower) else 0
    null_byte_count     = payload_bytes.count(b'\x00')
    non_printable_ratio = (
        sum(1 for b in payload_bytes if b < 0x20 or b > 0x7E) / len(payload_bytes)
        if payload_bytes else 0.0
    )
    nop_sled            = 1 if payload_bytes.count(b'\x90' * 4) > 0 else 0
    auth_method_enum    = 1 if re.search(
        r'publickey|password|keyboard-interactive|none', lower
    ) else 0
    tunneling_attempt   = 1 if re.search(
        r'direct-tcpip|forwarded-tcpip|tcpip-forward', lower
    ) else 0

    return {
        'ssh_short_auth_payload':    is_short_auth,
        'ssh_common_username':       common_username_hit,
        'ssh_repeated_char_ratio':   round(repeated_char_ratio, 4),
        'ssh_banner_probe':          banner_probe,
        'ssh_openssh_version_probe': openssh_probe,
        'ssh_exploit_signature':     exploit_sig,
        'ssh_cve_2018_10933':        cve_2018_10933,
        'ssh_weak_kex':              weak_kex,
        'ssh_weak_cipher':           weak_cipher,
        'ssh_null_byte_count':       null_byte_count,
        'ssh_non_printable_ratio':   round(non_printable_ratio, 4),
        'ssh_nop_sled':              nop_sled,
        'ssh_auth_method_enum':      auth_method_enum,
        'ssh_tunneling_attempt':     tunneling_attempt,
    }


# ==============================================================================
# DNS FEATURE EXTRACTORS
# ==============================================================================

_ABUSED_DNS_RECORD_TYPES   = ['TXT', 'NULL', 'ANY', 'CNAME', 'MX', 'AAAA']
_COMMON_LEGITIMATE_TLDS    = ['.com', '.org', '.net', '.gov', '.edu', '.co.uk']


def _extract_subdomains(domain):
    """Return subdomain components (excludes SLD and TLD)."""
    parts = domain.rstrip('.').split('.')
    return parts[:-2] if len(parts) > 2 else []


def extract_dns_features(payload):
    """DNS-specific attack features — 13 total."""
    lower = payload.lower().strip()

    domain_match = re.search(
        r'([a-z0-9]([a-z0-9\-]{0,61}[a-z0-9])?\.)+[a-z]{2,}',
        lower
    )
    domain    = domain_match.group(0) if domain_match else lower
    subdomains = _extract_subdomains(domain)
    subdomain_str = '.'.join(subdomains)
    labels    = domain.split('.')

    query_length         = len(domain)
    longest_label        = max(len(l) for l in labels) if labels else 0
    subdomain_entropy    = calculate_entropy(subdomain_str) if subdomain_str else 0.0
    subdomain_base64     = 1 if re.search(r'^[a-z0-9+/]{20,}={0,2}$', subdomain_str) else 0
    subdomain_hex        = 1 if re.search(r'^[a-f0-9]{16,}$', subdomain_str) else 0
    subdomain_depth      = len(subdomains)

    sld             = labels[-2] if len(labels) >= 2 else ''
    vowel_ratio     = sum(1 for c in sld if c in 'aeiou') / len(sld) if sld else 0.0
    consonant_clusters = re.findall(r'[bcdfghjklmnpqrstvwxyz]{4,}', sld)
    max_consonant   = max((len(c) for c in consonant_clusters), default=0)
    sld_entropy     = calculate_entropy(sld)
    sld_digit_ratio = sum(1 for c in sld if c.isdigit()) / len(sld) if sld else 0.0
    common_tld      = 1 if any(domain.endswith(t) for t in _COMMON_LEGITIMATE_TLDS) else 0
    any_query       = 1 if 'any' in lower or ' ANY ' in payload else 0
    abused_record   = 1 if any(r in payload.upper() for r in _ABUSED_DNS_RECORD_TYPES) else 0

    return {
        'dns_query_length':       query_length,
        'dns_longest_label_length': longest_label,
        'dns_subdomain_entropy':  round(subdomain_entropy, 4),
        'dns_subdomain_base64':   subdomain_base64,
        'dns_subdomain_hex':      subdomain_hex,
        'dns_subdomain_depth':    subdomain_depth,
        'dns_sld_vowel_ratio':    round(vowel_ratio, 4),
        'dns_max_consonant_cluster': max_consonant,
        'dns_sld_entropy':        round(sld_entropy, 4),
        'dns_sld_digit_ratio':    round(sld_digit_ratio, 4),
        'dns_uses_common_tld':    common_tld,
        'dns_any_query':          any_query,
        'dns_abused_record_type': abused_record,
    }


# ==============================================================================
# MASTER DISPATCHER
# ==============================================================================

SUPPORTED_PROTOCOLS = {'HTTP', 'SSH', 'DNS'}


def extract_all_features(payload, protocol="HTTP"):
    """
    Extract all features for a given protocol.

    Args:
        payload  (str): Raw network payload string.
        protocol (str): One of 'HTTP', 'SSH', 'DNS'.

    Returns:
        dict: Feature name → value mapping.
    """
    protocol = protocol.upper().strip()
    if protocol not in SUPPORTED_PROTOCOLS:
        raise ValueError(f"Unsupported protocol '{protocol}'. Choose from: {sorted(SUPPORTED_PROTOCOLS)}")

    features = extract_statistical_features(payload)

    if protocol == 'HTTP':
        features.update(extract_sql_features(payload))
        features.update(extract_xss_features(payload))
        features.update(extract_traversal_features(payload))
        features.update(extract_command_injection_features(payload))
        features.update(extract_evasion_features(payload))
        features.update(extract_ngram_features(payload))

    elif protocol == 'SSH':
        features.update(extract_ssh_features(payload))

    elif protocol == 'DNS':
        features.update(extract_dns_features(payload))

    return features


def get_feature_names(protocol="HTTP"):
    """Return sorted feature name list for a given protocol."""
    return sorted(extract_all_features("dummy", protocol=protocol).keys())


def features_to_vector(features, feature_names=None, protocol="HTTP"):
    """Convert feature dict to an ordered numeric list."""
    if feature_names is None:
        feature_names = get_feature_names(protocol=protocol)
    return [features.get(name, 0.0) for name in feature_names]