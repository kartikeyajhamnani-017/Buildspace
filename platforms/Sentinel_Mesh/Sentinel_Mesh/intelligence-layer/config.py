"""
Central configuration for all components
"""
import os

# Redis Configuration (for sequence tracking)
REDIS_HOST = 'localhost'
REDIS_PORT = 6379
REDIS_DB = 0

# Feature Extraction Settings
NGRAM_RANGE = (2, 5)  # Character n-grams from 2 to 5
MAX_NGRAM_FEATURES = 50  # Limit n-gram features

# ML Model Settings
ISOLATION_FOREST_CONTAMINATION = 0.3  # Expected % of anomalies (30%)
ISOLATION_FOREST_N_ESTIMATORS = 100
RANDOM_STATE = 42

# Sequence Analysis Settings
SEQUENCE_WINDOW_SIZE = 10  # Track last 10 payloads per IP
SEQUENCE_TIMEOUT = 3600  # Forget IP after 1 hour of inactivity

# Detection Thresholds
ANOMALY_SCORE_THRESHOLD = 0.6  # 0-1, higher = stricter
RULE_BASED_CONFIDENCE = 1.0  # Rules give 100% confidence
ML_ANOMALY_CONFIDENCE = 0.8  # ML anomalies get 80% confidence

# Known Bad Patterns (Rule-Based Filter)
BLACKLIST_KEYWORDS = [
    # ── HTTP: SQL Injection ───────────────────────────────────────────────────
    "' OR '1'='1",
    "' OR 1=1--",
    "UNION SELECT",
    "DROP TABLE",
    "exec(",
    "xp_cmdshell",

    # ── HTTP: XSS ─────────────────────────────────────────────────────────────
    "<script>",
    "javascript:",
    "onerror=",
    "onload=",

    # ── HTTP: Command Injection ───────────────────────────────────────────────
    "; cat /etc/passwd",
    "| cat /etc/passwd",
    "&& cat /etc/passwd",

    # ── HTTP: Path Traversal ──────────────────────────────────────────────────
    "../../../etc/passwd",
    "..\\..\\..\\windows",

    # ── HTTP: Other ───────────────────────────────────────────────────────────
    "/bin/bash",
    "/bin/sh",
    "wget http",
    "curl http",

    # ── SSH: Brute Force / Credential Stuffing ────────────────────────────────
    "root:root",
    "admin:admin",
    "admin:password",
    "root:toor",

    # ── SSH: Known Exploit Strings ────────────────────────────────────────────
    "libssh",                     # libssh authentication bypass
    "SSH-2.0-masscan", 
    "SSH-1.99-",                    # Old SSHv1 probe

    # ── SSH: Weak Cipher / KEX Downgrade ─────────────────────────────────────
    "diffie-hellman-group1-sha1",
    "arcfour",
    "blowfish-cbc",

    # ── SSH: Tunneling ────────────────────────────────────────────────────────
    "direct-tcpip",
    "forwarded-tcpip",
    "tcpip-forward",

    # ── DNS: Record Type Abuse ────────────────────────────────────────────────
    "NULL encodedpayload",
    "ANY isc.org",                  # Open resolver amplification probe
    "ANY google.com",

    # ── DNS: Known Tunneling Tool Signatures ──────────────────────────────────
    ".tunnel.",                     # iodine/dnscat2 default subdomain
    ".exfil.",                      # Common exfil subdomain pattern
    "dnscat",
]

# Dangerous N-grams (will be detected in feature extraction)
# Used by extract_ngram_features() in features.py for HTTP payloads.
# SSH and DNS use dedicated feature extractors instead of n-grams.
DANGEROUS_NGRAMS = [
    # ── SQL Injection ─────────────────────────────────────────────────────────
    "' OR",
    "' AND",
    "union select",
    "drop table",
    "exec(",
    "xp_cmdshell",

    # ── XSS ───────────────────────────────────────────────────────────────────
    "<script",
    "javascript:",
    "onerror=",
    "onload=",

    # ── Command Injection ─────────────────────────────────────────────────────
    "/bin/sh",
    "/bin/bash",
    "cmd.exe",
    "wget http",
    "curl http",

    # ── Path Traversal ────────────────────────────────────────────────────────
    "../",
    "/etc/passwd",
    "/etc/shadow",

    # ── Evasion ───────────────────────────────────────────────────────────────
    "%00",          # Null byte injection
    "/**/",         # Comment obfuscation
    "0x",           # Hex encoding prefix
]

# MITRE ATT&CK Mapping
ATTACK_PATTERNS = {
    # -- HTTP ------------------------------------------------------------------
    'T1059': r'(bash|sh|cmd\.exe|powershell|exec\()',       # Command execution
    'T1082': r'(whoami|uname|hostname|systeminfo)',            # System info discovery
    'T1083': r'(ls|dir|find)',                                 # File discovery
    'T1003': r'(/etc/passwd|/etc/shadow|SAM)',                 # Credential dumping
    'T1190': r'(UNION|SELECT.*FROM|\'.*OR.*=)',               # Exploit public app (SQLi)
    'T1057': r'(ps aux|tasklist|netstat)',                     # Process discovery
    'T1027': r'(%[0-9a-fA-F]{2}|base64|\\x[0-9a-f]{2})',   # Obfuscated files/info

    # -- SSH -------------------------------------------------------------------
    'T1110': r'(root|admin|administrator|password|passwd)',    # Brute force
    'T1021': r'(SSH-\d+\.\d+|direct-tcpip|publickey)',     # Remote services
    'T1572': r'(direct-tcpip|forwarded-tcpip|tcpip-forward)', # Protocol tunneling
    'T1203': r'(libssh|openssh.*exploit|overflow)',            # Exploitation
    'T1562': r'(arcfour|blowfish-cbc|diffie-hellman-group1)', # Impair defenses (weak cipher)

    # -- DNS -------------------------------------------------------------------
    'T1071': r'(\.tunnel\.|dnscat|iodine)',                  # App layer (DNS tunneling)
    'T1568': r'([a-z0-9]{12,}\.(ru|top|xyz|biz|info))',      # Dynamic resolution (DGA)
    'T1498': r'(ANY\s+\w+\.\w+)',                          # Network DoS (amplification)
    'T1048': r'(TXT\s+\w+\.|NULL\s+\w+\.)',             # Exfil over alt protocol
}
# Logging
LOG_LEVEL = 'INFO'
LOG_FILE = 'sentinel_ml.log'

# Model Persistence
# One model + scaler pair per protocol.
# train_model.py generates all six files.


# Absolute path to the project root (parent of wherever config.py lives)
_PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

MODEL_DIR = os.path.join(_PROJECT_ROOT, 'models')
METRICS_DIR = os.path.join(_PROJECT_ROOT, 'metrics')

MODEL_PATHS = {
    'HTTP': os.path.join(MODEL_DIR, 'sentinel_model_http.pkl'),
    'SSH':  os.path.join(MODEL_DIR, 'sentinel_model_ssh.pkl'),
    'DNS':  os.path.join(MODEL_DIR, 'sentinel_model_dns.pkl'),
}
SCALER_PATHS = {
    'HTTP': os.path.join(MODEL_DIR, 'sentinel_model_http_scaler.pkl'),
    'SSH':  os.path.join(MODEL_DIR, 'sentinel_model_ssh_scaler.pkl'),
    'DNS':  os.path.join(MODEL_DIR, 'sentinel_model_dns_scaler.pkl'),
}

# Legacy single-model paths (kept for backwards compatibility)
MODEL_PATH  = MODEL_PATHS['HTTP']
SCALER_PATH = SCALER_PATHS['HTTP']