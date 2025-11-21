import os
import sys
from loguru import logger

# Remove default handler
logger.remove()

# Get log level from environment or use INFO
log_level = os.getenv('LOG_LEVEL', 'INFO').upper()

# Get log file path
log_file = os.getenv('LOG_FILE', '/app/logs/app.log')
log_dir = os.path.dirname(log_file)
os.makedirs(log_dir, exist_ok=True)

# Console handler with colors
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level=log_level,
    colorize=True,
    backtrace=True,
    diagnose=True
)

# File handler with rotation
logger.add(
    log_file,
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
    level="DEBUG",  # Always log DEBUG to file
    rotation="10 MB",
    retention="7 days",
    compression="zip",
    backtrace=True,
    diagnose=True,
    enqueue=True  # Thread-safe logging
)

# Error file handler (separate file for errors)
error_log_file = log_file.replace('.log', '_errors.log')
logger.add(
    error_log_file,
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
    level="ERROR",
    rotation="10 MB",
    retention="30 days",
    compression="zip",
    backtrace=True,
    diagnose=True,
    enqueue=True
)

# Suppress noisy loggers
logger.add(
    lambda msg: False,
    filter=lambda record: record["name"].startswith("urllib3") or record["name"].startswith("httpx"),
    level="WARNING"
)
