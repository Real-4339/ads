import os
import loguru
import logging.handlers

from pathlib import Path
from dotenv import load_dotenv


current_file_path = Path(__file__).resolve()
log_file_path = current_file_path.parent.parent.parent / "logs" / "logger.log"
env_path = current_file_path.parent.parent.parent.parent / ".env"

load_dotenv(dotenv_path=env_path)
SYSLOG_HOST = os.getenv("SYSLOG_HOST", "localhost")
SYSLOG_PORT = os.getenv("SYSLOG_PORT", 514)


def init_logger() -> None:
    """Loguru settings"""
    global SYSLOG_PORT, SYSLOG_HOST
    loguru.logger.info("Initializing logger...")

    # Validate port number
    try:
        SYSLOG_PORT = int(SYSLOG_PORT)
    except ValueError:
        loguru.logger.error(
            f"Invalid SYSLOG_PORT value: {SYSLOG_PORT}. Using default port 514."
        )
        SYSLOG_PORT = 514

    loguru.logger.add(
        sink=log_file_path,
        format="{time:YYYY-MM-DD HH:mm:ss} | {name} | {level.icon} {level} | {message}",
        level="TRACE",
        rotation="1 week",
        compression="zip",
    )

    loguru.logger.add(
        logging.handlers.SysLogHandler(address=(SYSLOG_HOST, SYSLOG_PORT)),
        format="{time:UTC} {level} {message}",
        level="CRITICAL",
    )

    loguru.logger.level("CRITICAL", color="<red>", icon="🛑")
    loguru.logger.level("ERROR", color="<light-red>", icon="❌")
    loguru.logger.level("WARNING", color="<yellow>", icon="⚠️")
    loguru.logger.level("SUCCESS", color="<green>", icon="✔️")
    loguru.logger.level("INFO", color="<cyan>", icon="ℹ️")
    loguru.logger.level("DEBUG", color="<blue>", icon="🐛")
    loguru.logger.level("TRACE", color="<white>", icon="🔍")
