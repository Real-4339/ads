import os
import loguru
import requests
import logging.handlers

from json import dumps
from pathlib import Path
from dotenv import load_dotenv
from datetime import datetime


current_file_path = Path(__file__).resolve()
basic_log_path = current_file_path.parent.parent / "logs" / "app.log"
predictions_log_path = (
    current_file_path.parent.parent / "logs" / "prediction_anomalies.log"
)
env_path = current_file_path.parent.parent.parent / ".env"

load_dotenv(dotenv_path=env_path)
SYSLOG_HOST = os.getenv("SYSLOG_HOST", "localhost")
SYSLOG_PORT = os.getenv("SYSLOG_PORT", 514)


def init_logger() -> None:
    """Loguru settings"""

    loguru.logger.info("Initializing logger...")

    loguru.logger.add(
        sink=predictions_log_path,
        format="{time:YYYY-MM-DD HH:mm:ss} | {name} | {level.icon} {level} | {message}",
        level="TRACE",
        rotation="1 week",
        compression="zip",
        filter=lambda record: record["extra"]["basic"] is False,
    )

    loguru.logger.add(
        sink=basic_log_path,
        format="{time:YYYY-MM-DD HH:mm:ss} | {name} | {level.icon} {level} | {message}",
        level="TRACE",
        rotation="1 week",
        compression="zip",
        filter=lambda record: record["extra"]["basic"] is True,
    )

    loguru.logger.add(
        logging.handlers.SysLogHandler(address=(SYSLOG_HOST, SYSLOG_PORT)),
        format="{time:UTC} {level} {message}",
        level="CRITICAL",
    )

    loguru.logger.add(send_to_endpoint, format="{message}", level="CRITICAL")

    loguru.logger.level("CRITICAL", color="<red>", icon="🛑")
    loguru.logger.level("ERROR", color="<light-red>", icon="❌")
    loguru.logger.level("WARNING", color="<yellow>", icon="⚠️")
    loguru.logger.level("SUCCESS", color="<green>", icon="✔️")
    loguru.logger.level("INFO", color="<cyan>", icon="ℹ️")
    loguru.logger.level("DEBUG", color="<blue>", icon="🐛")
    loguru.logger.level("TRACE", color="<white>", icon="🔍")


def log_predictions(message: str, level: str = "INFO") -> None:
    """Log predictions into the predictions log file"""

    loguru.logger.bind(basic=False).log(level, message)


def log_basic(message: str, level: str = "INFO") -> None:
    """Log basic information into the basic log file"""

    loguru.logger.bind(basic=True).log(level, message)


def send_to_endpoint(message, source, level="INFO"):
    try:
        payload = {
            "message": message,
            "level": level,
            "source": source,
            "timestamp": datetime.now().isoformat(),
        }
        response = requests.post(
            "http://log-visualizer:8050/logs", json=payload, timeout=5
        )
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Failed to send log to endpoint: {e}")


# def send_to_endpoint(message):
#     try:
#         requests.post(
#             "https://your-endpoint.com/logs", json={"message": dumps(message)}
#         )
#     except Exception as e:
#         # Handle errors, e.g., log them locally
#         print(f"Error sending log: {e}")
