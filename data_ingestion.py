import boto3, gzip, io, csv, json, time, os, sys
import botocore
from confluent_kafka import Producer
from tqdm import tqdm
import json
from logger_utils import *

# Load configuration from a JSON file
with open('./config.json', 'r', encoding='utf-8') as f:
    config_data = json.load(f)

# Extract configuration parameters
bucket = config_data["input"]["bucket"]                                                                                 # S3 bucket name
prefix = config_data["input"]["prefix"]                                                                                 # prefix for location and time
kafka_bootstrap = config_data["kafka"]["bootstrap"]                                                                     # kafka bootstrap server
kafka_topic = config_data["kafka"]["topic"]                                                                             # kafka topic
fetch_interval = 5                                                                                                      # Interval between processing files
log_conf = config_data["logging"]["ingestion_path"]                                                                     # Logging configuration path

# Initialize Logger
log_path = init_log_file(log_conf)

# Configure Kafka producer
kafka_conf = {"bootstrap.servers": kafka_bootstrap}
p = Producer(kafka_conf)

# Create an anonymous S3 client
s3 = boto3.client('s3', config=boto3.session.Config(signature_version=botocore.UNSIGNED))

# List every file in the specified S3 bucket with the given prefix
keys = []
resp = s3.list_objects_v2(Bucket=bucket, Prefix=prefix)
keys.extend([obj["Key"] for obj in resp.get("Contents", [])])
log_event(log_path, "data_ingestion", "file_listed", len(keys), "success", "S3 file keys listed")
print("Found", len(keys), "gzipped csv files")

# Process each file separately
for key in tqdm(keys, desc="Sending one file at a time"):
    try:
        # Get the object from S3
        obj = s3.get_object(Bucket=bucket, Key=key)

        # Read the gzipped CSV file
        with gzip.GzipFile(fileobj=io.BytesIO(obj['Body'].read())) as f:
            reader = csv.DictReader(io.TextIOWrapper(f, encoding='utf-8'))
            count = 0

            # Produce all rows in this file to Kafka
            for row in reader:
                json_row = json.dumps(row)
                p.produce(kafka_topic, value=json_row)
                count += 1

        # Flush messages from this file only
        p.flush()
        log_event(log_path, "data_ingestion", "produce_kafka", count, "success", key)
        print(f"✅ Sent all messages from: {key}")

        # Wait for the specified interval before processing the next file
        time.sleep(fetch_interval)

    except Exception as e:
        # Log any errors that occur during processing
        log_event(log_path, "data_ingestion", "error", 0, "fail", str(e))
        print(f"❌ Error processing file {key}: {e}")

print("🎉 All files processed one by one and messages sent to Kafka.")