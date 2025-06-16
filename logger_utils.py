import os
import csv
from datetime import datetime


def init_log_file(log_path):
    """
        Initialize a log file at the specified path.

        This function ensures that the directory structure for the log file exists and
        initializes the log file with a header row if the file does not already exist.

        Args:
            log_path (str): The path where the log file should be created.

        Returns:
            str: The path to the initialized log file.
        """
    # Create the directory structure for the log file if it does not exist
    os.makedirs(os.path.dirname(log_path), exist_ok=True)

    # Initialize the log file with a header row if it does not exist
    if not os.path.exists(log_path):
        with open(log_path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["timestamp", "function", "stage", "count", "status", "info"])
    return log_path


def log_event(log_path, function, stage, count, status, info=""):
    """
        Log an event to the specified log file.

        This function appends a new log entry to the log file, including a timestamp,
        function name, stage, count, status, and additional information.

        Args:
            log_path (str): The path to the log file.
            function (str): The name of the function where the event occurred.
            stage (str): The stage of processing where the event occurred.
            count (int): A count related to the event (e.g., number of items processed).
            status (str): The status of the event (e.g., success, fail).
            info (str, optional): Additional information about the event. Defaults to an empty string.
        """
    # Open the log file in append mode and write the new log entry
    with open(log_path, 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([
            datetime.utcnow().isoformat(),                                                                              # Current timestamp in ISO format
            function,                                                                                                   # Name of the function
            stage,                                                                                                      # Stage of processing
            count,                                                                                                      # Count related to the event
            status,                                                                                                     # Status of the event
            info                                                                                                        # Additional information
        ])