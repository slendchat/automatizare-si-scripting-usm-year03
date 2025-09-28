import logging
from logging import Logger
from pathlib import Path

def get_file_root() -> Path:
    return Path(__file__).resolve().parents[2]

def init_logger(logger_name: str = "app") -> Logger:
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)
    logger.propagate = False

    if logger.handlers:
        return logger

    file_fmt = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_fmt = logging.Formatter("%(asctime)s %(levelname)s %(name)s %(filename)s:%(lineno)d: %(message)s")

    logger_console = logging.StreamHandler()
    logger_console.setFormatter(console_fmt)

    log_path = get_file_root() / 'currency_exchange_rate.log'
    logger_file = logging.FileHandler(log_path, mode='a', encoding='utf-8')
    logger_file.setFormatter(file_fmt)
    logger_file.setLevel(logging.ERROR)

    logger.addHandler(logger_console)
    logger.addHandler(logger_file)
    return logger
