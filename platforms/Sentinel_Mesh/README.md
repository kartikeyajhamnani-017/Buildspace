# 🛡️ Sentinel_Mesh: Distributed Threat Detection Engine

## 1. Project Overview
**Sentinel_Mesh** is a cloud-native, distributed security system designed to bridge the gap between high-speed traffic ingestion and deep-learning threat analysis.

* **The Problem:** Traditional Web Application Firewalls (WAFs) face a trade-off: they are either fast but "dumb" (catching only known signatures) or smart but slow (causing latency for users).
* **Who It’s For:** Cloud Security Engineers and DevSecOps teams looking for a scalable, microservices-based approach to threat detection.
* **Core Idea:** It uses a **"Funnel Architecture."** A high-performance Go ingestor acts as a speed gate, filtering traffic instantly. Suspicious or complex data is buffered in Redis and processed asynchronously by a Python-based ML engine, ensuring zero latency for the end-user while maintaining deep security coverage.

## 2. System Architecture Diagram

```mermaid
graph LR
    A[Client/Attacker] -->|HTTP POST| B(Go Shield)
    B -->|Fast Rule Check| B
    B -->|JSON Log| C[(Redis Buffer)]
    C -->|BLPOP| D{Python Brain}
    D -->|Rule Engine| E[Block Known Threats]
    D -->|Isolation Forest| F[Detect Zero-Day Anomalies]
```

## 3. Key Features

### Hybrid Detection Engine
Combines ultra-fast signature matching (rule-based detection) with an unsupervised machine learning model (Isolation Forest) to detect both known exploits and zero-day anomalies.

### Asynchronous Processing
Decouples traffic ingestion from analysis using Redis, enabling the system to handle traffic spikes without overwhelming the detection engine.

### Resilient Design
Implements data persistence mechanisms to ensure logs survive service crashes. Crash recovery behavior ("Nuclear Resurrection") has been tested.

### Microservices Architecture
Each core component (Ingestion, Queue, Analysis) runs in its own Docker container, allowing independent scaling and isolation.

### Real-Time Anomaly Detection
Capable of identifying obfuscated payloads and statistically abnormal request patterns that may bypass traditional WAF rules.

---

## 4. Tech Stack

### Backend (Ingestion Service)
- Golang (net/http)

### Backend (Dashboard – In Progress)
- Java (Spring Boot, WebSockets)

### Message Queue
- Redis (Lists, Pub/Sub)

### Machine Learning Engine
- Python (Scikit-Learn, NumPy, Joblib)

### Deployment
- Docker
- Docker Compose



---

## 5. Quick Start

### Prerequisites

- Docker
- Docker Compose

---