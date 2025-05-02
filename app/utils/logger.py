import logging
from colorlog import ColoredFormatter


class CustomLogger:
    def __init__(self):
        self.logger = logging.getLogger("scraping_service")
        self.logger.setLevel(logging.DEBUG)

        formatter = ColoredFormatter(
            "%(log_color)s%(levelname)-8s%(reset)s %(blue)s%(message)s",
            datefmt=None,
            reset=True,
            log_colors={
                'DEBUG': 'cyan',
                'INFO': 'green',
                'WARNING': 'yellow',
                'ERROR': 'red',
                'CRITICAL': 'red,bg_white',
            }
        )

        handler = logging.StreamHandler()
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

    def debug(self, msg):
        self.logger.debug(msg)

    def info(self, msg):
        self.logger.info(msg)

    def warning(self, msg):
        self.logger.warning(msg)

    def error(self, msg):
        self.logger.error(msg)

    def critical(self, msg):
        self.logger.critical(msg)

    def success(self, msg):
        self.logger.info(f"\033[1;32m✓ {msg}\033[0m")

    def progress(self, current, total, prefix="", suffix="", decimals=1, length=50, fill='█'):
        percent = ("{0:." + str(decimals) + "f}").format(100 * (current / float(total)))
        filled_length = int(length * current // total)
        bar = fill * filled_length + '-' * (length - filled_length)
        self.logger.info(f"\r{prefix} |{bar}| {percent}% {suffix}")
        if current == total:
            self.logger.info("")


logger = CustomLogger()