import logging
import os
from datetime import datetime

class Logger:
    _instance = None  # Class-level variable to hold the single instance

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            # Create a new instance if one does not exist
            cls._instance = super().__new__(cls)
            cls._instance._initialize(*args, **kwargs)
        return cls._instance

    def _initialize(self, name="CustomLogger"):
        # Create or configure the logger
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)  # Set the base logging level

        # Ensure the logger doesn't already have handlers to avoid duplicates
        if not self.logger.hasHandlers():
            # Create a Logging directory if it doesn't exist
            os.makedirs("Logging", exist_ok=True)

            # Create a file handler to write logs to `Logging/log.txt`
            file_handler = logging.FileHandler("Logging/log.txt")
            file_handler.setLevel(logging.DEBUG)

            # Set a custom formatter for the handler
            file_handler.setFormatter(self.CustomFormatter())

            # Add the handler to the logger
            self.logger.addHandler(file_handler)

    class CustomFormatter(logging.Formatter):
        def format(self, record):
            # Format the message as "[type] timestamp: [error]"
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            return f"[{record.levelname.lower()}] {current_time}: {record.getMessage()}"

    # Wrapper methods for different log levels
    def debug(self, message):
        self.logger.debug(message.replace("\n", ""))

    def info(self, message):
        self.logger.info(message.replace("\n", ""))

    def warning(self, message):
        self.logger.warning(message.replace("\n", ""))

    def error(self, message):
        self.logger.error(message.replace("\n", ""))

    def critical(self, message):
        self.logger.critical(message.replace("\n", ""))
