# Air Quality Data Streaming Pipeline

This repository provides a Kafka-based data streaming pipeline for real-time air quality telemetry processing. The project leverages Docker and Apache Kafka to simulate a production-grade event-driven architecture, where ingestion is containerized, and consumption runs locally for analytical flexibility.

===========================================================

## Data Pipeline with Kafka and Docker
This project illustrates the implementation of a data pipeline designed to ingest data from an Amazon S3 bucket, process it using Apache Kafka, and subsequently consume the processed data locally. The data is related to air quality which is being provided by OpenAQ.
This pipeline compromises two primary scripts: 'data_ingestion.py' and 'data_consumer.py'.

## Prerequisites

Prior to initiating the setup process, ensure that the following software components are installed on your system:

1. **Docker**: Utilized for containerizing the Kafka environment.
   - Docker can be downloaded and installed from [Docker's official website](https://www.docker.com/get-started).

2. **Python**: Required to execute the data ingestion and consumption scripts.
   - Python can be downloaded and installed from [Python's official website](https://www.python.org/downloads/).

3. **Required Python Libraries**: Install the necessary Python libraries using pip:
   ```bash
    pip install -r requirements.txt
   ```
## Docker Compose Setup
This command will:
+ Start the kafka broker container using Kafka image.
+ Build and run zookeeper, kafka, init_kafka and data_ingestion.py.
+ Mount necessary volumes for logs and output storages.

1. **Clone the repository**

2. **Configure Docker Compose**:
   - Ensure the presence of a docker-compose.yml file that configures the Kafka environment.
   
3. **Launching Docker Desktop**:
   - Start Docker Desktop: Launch Docker Desktop from your applications menu. This action will start the Docker daemon and provide a graphical user interface for managing your containers.
   
4. **Initiate the Docker Container**:
   + Open a terminal and navigate to the directory containers docker-compose.yml
   + Make sure Docker Desktop is started to compose .yml file and start kafka server
   + Execute following command to start Kafka environment:
     
      ```bash
       docker-composer up -build
     ```


## Run Kafka Consumer
While the Docker containers are running, open a new terminal window and set up your Python environment.
   ```bash
   pip install -r requirements.txt
   python data_consume.py
   ```
This script will:
+ Connect to kafka topic.
+ Read and Process incoming messages.
+ Write filtered and transformed messages as CSV to ./output/ directory.
+ Generate logs under ./logs/

## Output Directories
logs/: Contains application logs from ingestion and consumer processes.
output/: Contains processed data saved as .csv by the consumer.
