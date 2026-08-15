
# 🛡️ CloudTrail Anomaly Detector

*Unsupervised Behavioral Analytics for Cloud Infrastructure Security*

## 📌 Overview

Cloud environments generate **millions of API audit logs daily**, creating a classic “needle in a haystack” security problem. Traditional rule-based systems fail to detect subtle, low-and-slow reconnaissance or credential theft because attackers often use legitimate, non-destructive API calls.

This project implements an **Unsupervised Machine Learning pipeline** to detect anomalous behavior in AWS CloudTrail logs using **Isolation Forest**.

Instead of relying on brittle static rules, this system builds a **statistical baseline of normal behavior** and flags deviations automatically.

---

## 🚨 Problem Statement

Cloud audit logs (AWS CloudTrail) are:

* **High-volume** – Millions of events daily
* **Low-context** – Individual API calls look normal in isolation
* **Easily bypassed** – Static rules fail against subtle reconnaissance

### Why Traditional Detection Fails

* Attackers use read-only APIs (`GetCallerIdentity`, `DescribeInstances`)
* Legitimate developers trigger false positives
* No behavioral context per user/role/time
* Hard-coded thresholds are predictable and brittle

---

## ✅ Solution Approach

This project implements **Unsupervised Behavioral Analytics**:

* No labeled attack dataset required
* No predefined attack signatures
* Learns what “normal” looks like
* Flags statistical deviations automatically

The model detects:

* Unusual service access patterns
* High failure/error ratios
* Suspicious temporal activity (e.g., 3 AM access)
* API velocity spikes
* Abnormal user-agent switching

---

# 🏗️ Architecture Overview

## 1️⃣ Data Ingestion & Flattening

### Input Format

* AWS CloudTrail logs
* Gzipped JSON files
* Nested `Records` array

### Technical Challenge

CloudTrail logs contain deeply nested structures such as:

* `userIdentity`
* `sessionContext`
* `requestParameters`

Machine Learning models require **tabular data**, not nested JSON trees.

### Solution

We use:

```python
pandas.json_normalize()
```

This flattens nested JSON into a structured dataframe.

Example transformation:

```
userIdentity.sessionContext.sessionIssuer.userName
→ user_name
```

---

## 2️⃣ Feature Engineering (Behavioral Signals)

Raw logs are not ML-ready. We engineer behavioral features grouped by:

* `user_arn`
* `source_ip`

### 🔥 Velocity Features

* `event_rate` → API calls per minute

### 🎯 Variety Features

* `unique_services` → Number of AWS services accessed
* `unique_user_agents` → Tool switching (console, boto3, curl)

### ⚠️ Error Ratio Features

* `failure_rate` → AccessDenied / total requests

### 🕒 Temporal Features

* `hour_of_day` → Encoded as cyclical feature

These features capture behavior, not just raw activity.

---

## 🧠 The Model: Isolation Forest

We use **Isolation Forest** for anomaly detection.

### Why Isolation Forest?

* Works well for high-dimensional log data
* Efficient: O(n log n)
* No labeled dataset required
* Robust to skewed distributions
* Does not require strict feature scaling

### How It Works

Isolation Forest builds random decision trees.

* Normal data → deeper in trees
* Anomalies → isolated quickly (shorter path length)

The shorter the average path length, the higher the anomaly score.

---

# 📊 Detection Philosophy

We do **not** train the model to detect known attacks.

Instead:

> We teach the system what a normal Monday morning looks like.

Anything statistically different is flagged.

This allows detection of:

* Zero-day attacks
* Credential compromise
* Insider threats
* Low-and-slow reconnaissance

---

# 🏢 Production Considerations

### Current Architecture

* Batch processing (ETL-style)
* Pandas-based pipeline
* Offline model scoring

### Production Upgrade Path

In a real-world system, this would evolve into:

* AWS Kinesis / Kafka ingestion
* Apache Flink / Spark Streaming
* Real-time anomaly scoring
* SIEM integration

The mathematical logic remains the same — only the ingestion layer changes.

---

# 🛠️ Tech Stack

* Python
* Pandas
* Scikit-Learn
* Isolation Forest
* AWS CloudTrail Logs

---

# 🎓 Genuine Thoughts

If asked: **“What did I build?”**

> I built an unsupervised machine learning pipeline that detects cloud intrusion attempts by modeling behavioral baselines from raw CloudTrail logs. I engineered velocity, error ratio, service variety, and temporal features, and implemented Isolation Forest to statistically identify anomalous IAM entities that bypass traditional rule-based detection.

If asked: **“Why unsupervised?”**

> In security, we rarely have labeled attack datasets. New attacks differ from old ones. Supervised models overfit to known threats. Unsupervised anomaly detection helps detect unknown unknowns.

---

# 🚀 Future Improvements

* Model persistence & retraining pipeline
* Feature drift detection
* Auto-threshold tuning
* Real-time streaming architecture
* Integration with SOC dashboards

---

# 🚀 Get Started

These steps run the full pipeline locally against the sample CloudTrail dataset already included in the repo (`cloudtrail_logs/CloudTrail_dataset/`) — no AWS account or credentials needed.

### Prerequisites

* Python 3.9+

### 1. Clone the repo

```bash
git clone https://github.com/kartikeyajhamnani-017/myprojects-repo
cd myprojects-repo/Minor-projects/Cloud-trail/Cloud-trail
```

### 2. Create a virtual environment (recommended)

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the pipeline

```bash
python main.py
```

This ingests the JSON logs in `cloudtrail_logs/CloudTrail_dataset/`, engineers behavioral features, runs Isolation Forest, and prints an anomaly report to the console.

### Using your own CloudTrail logs

Drop your own (gzipped or plain) CloudTrail JSON files into `cloudtrail_logs/CloudTrail_dataset/`, or point `LOG_DIRECTORY` in `main.py` at another folder, then re-run `python main.py`.
