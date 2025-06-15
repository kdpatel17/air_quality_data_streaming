import boto3, gzip, io, csv, json, time, os, sys
import botocore
from confluent_kafka import Producer
from tqdm import tqdm
import json
from logger_utils import *

# configuration
with open('./config.json', 'r', encoding='utf-8') as f:
    config_data = json.load(f)

bucket = config_data["input"]["bucket"]
prefix = config_data["input"]["prefix"]
kafka_bootstrap = config_data["kafka"]["bootstrap"]
kafka_topic = config_data["kafka"]["topic"]
fetch_interval = 5
log_conf = config_data["logging"]["ingestion_path"]

# Initialize Logger
log_path = init_log_file(log_conf)

# kafka producer
kafka_conf = {"bootstrap.servers": kafka_bootstrap}
p = Producer(kafka_conf)

# anonymous S3 client
s3 = boto3.client('s3', config=boto3.session.Config(signature_version=botocore.UNSIGNED))

# 1️List every file
keys = []
resp = s3.list_objects_v2(Bucket=bucket, Prefix=prefix)
keys.extend([obj["Key"] for obj in resp.get("Contents", [])])
log_event(log_path, "data_ingestion", "file_listed", len(keys), "success", "S3 file keys listed")
print("Found", len(keys), "gzipped csv files")

# --- Process each file separately ---
for key in tqdm(keys, desc="Sending one file at a time"):
    try:
        obj = s3.get_object(Bucket=bucket, Key=key)
        with gzip.GzipFile(fileobj=io.BytesIO(obj['Body'].read())) as f:
            reader = csv.DictReader(io.TextIOWrapper(f, encoding='utf-8'))
            count = 0

            # Produce all rows in this file
            for row in reader:
                json_row = json.dumps(row)
                p.produce(kafka_topic, value=json_row)
                count += 1

        # Flush messages from this file only
        p.flush()
        log_event(log_path, "data_ingestion", "produce_kafka", count, "success", key)
        print(f"✅ Sent all messages from: {key}")

        time.sleep(fetch_interval)

    except Exception as e:
        log_event(log_path, "data_ingestion", "error", 0, "fail", str(e))
        print(f"❌ Error processing file {key}: {e}")

print("🎉 All files processed one by one and messages sent to Kafka.")