import os
import glob
import json

def load_data(log_dir):
    print(f"--- Step 1: Loading data from {log_dir} ---")
    
    file_pattern = os.path.join(log_dir, '**/*.json')
    log_files = glob.glob(file_pattern, recursive=True)

    if not log_files:
        print(f"Error: No .json files found in {log_dir}.")
        return None

    print(f"Found {len(log_files)} log files.")
    
    all_records = []
    for file in log_files:
        try:
            with open(file, 'r') as f:
                data = json.load(f)
                if 'Records' in data:
                    all_records.extend(data['Records'])
        except Exception as e:
            print(f"Error reading {file}: {e}")

    print(f"Successfully loaded a total of {len(all_records)} log events.")
    return all_records