# Air Quality Data Streaming Pipeline

This repository provides a Kafka-based data streaming pipeline for real-time air quality telemetry processing. The project leverages Docker and Apache Kafka to simulate a production-grade event-driven architecture, where ingestion is containerized, and consumption runs locally for analytical flexibility.

---

## 📁 Project Structure
air_quality_data_streaming/
│
├── config.json # Configuration file for Kafka and processing parameters
├── data-ingestion.py # Kafka producer (runs inside Docker)
├── data_consume.py # Kafka consumer (run locally)
├── docker-compose.yml # Docker setup for Kafka and producer
├── Dockerfile # Image definition for the producer service
├── thresholds.json # Threshold rules for filtering
├── requirements.txt # Python dependencies
├── logger_utils.py # Logging utility
├── .env # Environment variables for Kafka service
├── logs/ # Logs from the pipeline (volume mounted)
├── output/ # Output files from the consumer (volume mounted)
