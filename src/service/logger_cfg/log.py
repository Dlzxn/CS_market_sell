import logging, time
from logging.handlers import RotatingFileHandler

logger = logging.getLogger("main")
logger.setLevel(logging.INFO)

fmt = logging.Formatter(
    "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

console = logging.StreamHandler()
console.setFormatter(fmt)
logger.addHandler(console)

file = RotatingFileHandler(f"data/app_{time.time()}.log", maxBytes=1_000_000, backupCount=5, encoding="utf-8")
file.setFormatter(fmt)
logger.addHandler(file)

__all__ = ["logger"]
