import psutil
import os

from src.python.utils.logger import setup_logger

logger = setup_logger(__name__)


def get_memory_usage():
    """Get current memory usage of the process"""
    process = psutil.Process(os.getpid())
    memory_info = process.memory_info()
    return memory_info.rss / 1024 / 1024  # Convert to MB


def log_memory_usage(message=""):
    """Log current memory usage"""
    memory_mb = get_memory_usage()
    logger.info(f"Memory usage {message}: {memory_mb:.2f} MB")