from kafka import KafkaConsumer
import json
import pandas as pd
from logger_utils import *


# Function to check if the quality of a parameter's value is acceptable
def is_quality_acceptable(parameter, value, thresholds):
    """
    Return True if value falls under 'Good' or 'Moderate' for the given parameter.

    Args:
        parameter (str): The parameter to check.
        value (str): The value of the parameter.
        thresholds (dict): Dictionary containing threshold values for parameters.

    Returns:
        bool: True if the value is acceptable, False otherwise.
    """
    if parameter not in thresholds:
        return False

    try:
        value = float(value)
    except ValueError:
        return False

    for entry in thresholds[parameter]["thresholds"]:
        if value <= entry["max"]:
            return entry["quality"] in ["Good", "Moderate"]

    return False


# Function to add a quality field to a message based on parameter and value
def add_quality_field(message_dict, thresholds):
    """
    Adds a 'quality' field to the message based on parameter and value.

    Args:
        message_dict (dict): The message dictionary to modify.
        thresholds (dict): Dictionary containing threshold values for parameters.

    Returns:
        dict: The modified message dictionary with a 'quality' field.
    """
    parameter = message_dict.get("parameter")
    value = message_dict.get("value")

    if parameter not in thresholds:
        message_dict["quality"] = "Unknown"
        return message_dict

    try:
        value = float(value)
    except ValueError:
        message_dict["quality"] = "Invalid"
        return message_dict

    for entry in thresholds[parameter]["thresholds"]:
        if value <= entry["max"]:
            message_dict["quality"] = entry["quality"]
            return message_dict

    message_dict["quality"] = "Hazardous"
    return message_dict


# Load configuration from a JSON file
with open('./config.json', 'r', encoding='utf-8') as f:
    config_data = json.load(f)

# Load thresholds from a JSON file
with open('./thresholds.json', 'r', encoding='utf-8') as f:
    thresholds = json.load(f)

# Configuration parameters
#kafka_bootstrap = "localhost:9092"                                                                                     # Kafka bootstrap servers
kafka_bootstrap = config_data["kafka"]["bootstrap"]                                                                     # kafka bootstrap server
kafka_topic = config_data["kafka"]["topic"]                                                                             # Kafka topic to consume messages from
output_file = config_data["output"]["path"]                                                                             # Path to save the output CSV file
log_conf = config_data["logging"]["consumer_path"]                                                                      # Logging configuration path

# Ensure the output directory exists
os.makedirs(os.path.dirname(output_file), exist_ok=True)

# Initialize logging file
log_path = init_log_file(log_conf)

# Configure Kafka consumer
consumer = KafkaConsumer(
    kafka_topic,
    bootstrap_servers=kafka_bootstrap,
    auto_offset_reset='earliest',                                                                                       # Start reading at the earliest message present in the topic
    value_deserializer=lambda m: json.loads(m.decode('utf-8')),                                                         # Deserialize JSON messages
    group_id='simple-consumer-group'                                                                                    # Consumer group ID
)

consumer.subscribe([kafka_topic])
print(f"🔄 Consuming messages from topic: {kafka_topic}")


# Initialize DataFrame and message list
df = pd.DataFrame()
data = []
msg_count = 0

# Fetch each data from Kafka producer and save as DataFrame
try:
    for message in consumer:
        msg = message.value
        msg_count += 1
        if is_quality_acceptable(msg.get("parameter"), msg.get("value"), thresholds):                                   # filter the message
            msg = add_quality_field(msg, thresholds)                                                                    # transform the message
            data.append(msg)

        # Concatenate messages to DataFrame in batches of 100
        if len(data) >= 100:
            new_rows = pd.DataFrame(data)
            df = pd.concat([df, new_rows], ignore_index=True)
            data.clear()
            print(f"✅ Received {msg_count} messages. {len(df)} messages are concat to DataFrame.")
            log_event(log_path, "data_consumer", "batch_save", len(new_rows), "success", output_file)
            log_event(log_path, "data_consumer", "Message Received", msg_count, "success", output_file)
            log_event(log_path, "data_consumer", "DataFrame Data", len(df), "success", output_file)

except KeyboardInterrupt:
    # Handle manual interruption
    last_fetch_data = pd.DataFrame(data)
    df = pd.concat([df, last_fetch_data], ignore_index=True)
    print(f"✅ Received {msg_count} messages. {len(df)} messages are concat to DataFrame.")
    log_event(log_path, "data_consumer", "interrupted_Data", len(last_fetch_data), "last batch", output_file)
    log_event(log_path, "data_consumer", "interrupted", 0, "info", "Manual interrupt")
    print("🛑 Stopping consumer...")

finally:
    # Save the DataFrame to a CSV file if it's not empty
    if not df.empty:
        df.to_csv(output_file, index=False)
        log_event(log_path, "data_consumer", "final_save", len(df), "success", output_file)
        print(f"✅ Data saved to {output_file}")
    else:
        print("⚠️ No data consumed.")


