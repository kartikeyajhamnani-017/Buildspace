# Overview
## A miniature MLOps-style batch pipeline that does following:

- Loads configuration from YAML
- Processes cryptocurrency OHLCV CSV data
- Computes a rolling mean on the `close` column
- Generates trading signals
- Outputs structured metrics in JSON format
- Logs the full execution process
- Runs as a Dockerized batch job

# Deliverables:

- run.py
- config.yaml
- data.csv
- requirements.txt
- Dockerfile
- metrics.json
- run.log
- README.md

# Setup Instructions:
## Clone the Repository

```bash
git clone https://github.com/kartikeyajhamnani-017/MLOPS-task0.git
cd mlops-task
```
## Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate

```
## Install dependencies
```bash
pip install -r requirements.txt
```

# Local Execution Instructions:
## Run locally
```bash
python run.py --input data.csv --config config.yaml --output metrics.json --log-file run.log
```

# Docker Instructions:
## Build the Docker image
```bash
docker build -t mlops-task .
```
## Run the container
```bash
docker run --rm mlops-task
```

# Expected Output:
## Success output :
```json
{
  "version": "v1",
  "rows_processed": 10000,
  "metric": "signal_rate",
  "value": 0.5015,
  "latency_ms": 91,
  "seed": 42,
  "status": "success"
}
```
## Error output :
```json
{
  "version": "v1",
  "status": "error",
  "error_message": "Description of what went wrong"
}
```

# Dependencies: 
- pandas
- numpy
- pyyaml
