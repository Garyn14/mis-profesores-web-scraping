# app/utils/logger.py (versión mejorada)
import logging
import time
from logging.handlers import RotatingFileHandler
from pathlib import Path
import sys
from typing import Optional
import colorama

colorama.init()

class ColoredFormatter(logging.Formatter):
    """Formateador con colores para la consola"""
    COLORS = {
        'DEBUG': colorama.Fore.BLUE,
        'INFO': colorama.Fore.GREEN,
        'WARNING': colorama.Fore.YELLOW,
        'ERROR': colorama.Fore.RED,
        'CRITICAL': colorama.Fore.RED + colorama.Style.BRIGHT
    }

    def format(self, record):
        color = self.COLORS.get(record.levelname, '')
        message = super().format(record)
        return f"{color}{message}{colorama.Style.RESET_ALL}"

class ProgressLogger:
    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self.last_progress = 0
        self.current_stage = ""
        self.stage_start_time = None

    def start_stage(self, stage_name: str, total: Optional[int] = None):
        self.current_stage = stage_name
        self.last_progress = 0
        self.stage_start_time = time.time()
        emoji = "🟢" if "fetch" in stage_name.lower() else "🔵"
        if total:
            self.logger.info(f"{emoji} {stage_name} started. Total items: {total}")
        else:
            self.logger.info(f"{emoji} {stage_name} started")

    def progress(self, current: int, total: int, message: str = ""):
        progress_percent = int((current / total) * 100)
        if progress_percent != self.last_progress and (progress_percent % 5 == 0 or current == total):
            self.last_progress = progress_percent
            elapsed = time.time() - self.stage_start_time
            eta = (elapsed / current) * (total - current) if current > 0 else 0
            self.logger.info(
                f"🔄 {self.current_stage}: {progress_percent}% "
                f"({current}/{total}) | Elapsed: {elapsed:.1f}s | ETA: {eta:.1f}s | {message}"
            )

    def end_stage(self, message: str = ""):
        elapsed = time.time() - self.stage_start_time
        self.logger.info(
            f"✅ {self.current_stage} completed in {elapsed:.2f}s. {message}"
        )
        self.current_stage = ""

def setup_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    if logger.handlers:
        return logger

    # Formateador para archivo (sin colores)
    file_formatter = logging.Formatter(
        '%(asctime)s | %(levelname)-8s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Handler de archivo rotativo
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    file_handler = RotatingFileHandler(
        log_dir / "service.log",
        maxBytes=10*1024*1024,  # 10 MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setFormatter(file_formatter)

    # Formateador para consola (con colores)
    console_formatter = ColoredFormatter(
        '%(asctime)s | %(levelname)-8s | %(message)s',
        datefmt='%H:%M:%S'
    )
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(console_formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger

# Logger principal
logger = setup_logger("professor_service")

# Logger de progreso
progress_logger = ProgressLogger(logger)