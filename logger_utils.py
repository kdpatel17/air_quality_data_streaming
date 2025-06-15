import os
import csv
from datetime import datetime

def init_log_file(log_path):
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    if not os.path.exists(log_path):
        with open(log_path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["timestamp", "function", "stage", "count", "status", "info"])
    return log_path


def log_event(log_path, function, stage, count, status, info=""):
    with open(log_path, 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([
            datetime.utcnow().isoformat(),
            function,
            stage,
            count,
            status,
            info
        ])