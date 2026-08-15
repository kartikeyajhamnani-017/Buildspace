import argparse
import json
import logging
import sys
import time
import os

import pandas as pd
import numpy as np
import yaml


def setup_logging(log_file):
    logging.basicConfig(
        filename=log_file,
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )


def output(output_path, version, rows_processed, signal_rate, latency_ms, seed):
    output_data = {
        "version": version,
        "rows_processed": rows_processed,
        "metric": "signal_rate",
        "value": round(float(signal_rate), 4),
        "latency_ms": int(latency_ms),
        "seed": seed,
        "status": "success",
    }

    with open(output_path, "w") as f:
        json.dump(output_data, f, indent=2)

    print(json.dumps(output_data, indent=2))


def error_output(output_path, version, error_message):
    output_data = {
        "version": version,
        "status": "error",
        "error_message": error_message,
    }

    with open(output_path, "w") as f:
        json.dump(output_data, f, indent=2)

    print(json.dumps(output_data, indent=2))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--config", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--log-file", required=True)

    args = parser.parse_args()

    start_time = time.time()

    setup_logging(args.log_file)
    logging.info("Job started")

    version = "unknown"

    try:
        # 1. Load Configuration
        if not os.path.exists(args.config):
            raise FileNotFoundError("Configuration file not found.")

        with open(args.config, "r") as f:
            config = yaml.safe_load(f)

        if not all(k in config for k in ["seed", "window", "version"]):
            raise ValueError("Invalid configuration structure.")

        seed = config["seed"]
        window = config["window"]
        version = config["version"]

        np.random.seed(seed)

        logging.info(f"Config loaded: seed={seed}, window={window}, version={version}")

        # 2. Load Input Data
  
        if not os.path.exists(args.input):
            raise FileNotFoundError("Input file not found.")

        df = pd.read_csv(args.input)

        if df.empty:
            raise ValueError("Input CSV file is empty.")

        if "close" not in df.columns:
            raise ValueError("Required column 'close' not found in dataset.")

        rows_processed = len(df)

        logging.info(f"Data loaded: {rows_processed} rows")

       
        # 3. Rolling Mean
    
        df["rolling_mean"] = df["close"].rolling(window=window).mean()

        logging.info(f"Rolling mean calculated with window={window}")

     
        # 4. Signal Generation
      
        df["signal"] = np.where(df["close"] > df["rolling_mean"], 1, 0)

        logging.info("Signals generated")

       
        # 5. Metrics
        
        signal_rate = df["signal"].mean()

        latency_ms = (time.time() - start_time) * 1000

        logging.info(f"Metrics: signal_rate={round(signal_rate,4)}, rows_processed={rows_processed}")

        logging.info(f"Job completed successfully in {int(latency_ms)}ms")

        output(
            args.output,
            version,
            rows_processed,
            signal_rate,
            latency_ms,
            seed,
        )

        sys.exit(0)

    except Exception as e:
        error_message = str(e)
        logging.error(f"Error occurred: {error_message}")

        error_output(args.output, version, error_message)

        sys.exit(1)


if __name__ == "__main__":
    main()