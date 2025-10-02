import logging
from logging import Logger
from pathlib import Path

def get_file_root() -> Path:
    return Path(__file__).resolve().parents[2]

def init_logger(log_path: str | Path | None = None, logger_name: str = "app") -> Logger:
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)
    logger.propagate = False

    if logger.handlers:
        return logger

    # форматы логов
    file_fmt = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_fmt = logging.Formatter("%(asctime)s %(levelname)s %(name)s %(filename)s:%(lineno)d: %(message)s")

    # вывод в консоль
    logger_console = logging.StreamHandler()
    logger_console.setFormatter(console_fmt)
    logger.addHandler(logger_console)

    # лог в файл
    if log_path is None:
        log_path = get_file_root() / "currency_exchange_rate.log"

    log_path = Path(log_path).resolve()
    log_path.parent.mkdir(parents=True, exist_ok=True)

    logger_file = logging.FileHandler(log_path, mode="a", encoding="utf-8")
    logger_file.setFormatter(file_fmt)
    logger_file.setLevel(logging.ERROR)
    logger.addHandler(logger_file)

    return logger
