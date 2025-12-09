import logging
from logging.handlers import RotatingFileHandler
import os

os.makedirs("logs", exist_ok=True)

logger = logging.getLogger("market")
logger.setLevel(logging.DEBUG)   # чтобы не резалось

fmt = logging.Formatter(
    "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

# ─────────────────────────────
#   Консоль вывод
# ─────────────────────────────
console = logging.StreamHandler()
console.setFormatter(fmt)
logger.addHandler(console)


# ─────────────────────────────
#           INFO лог
# ─────────────────────────────
info_handler = RotatingFileHandler(
    "logs/info.log", maxBytes=5_000_000, backupCount=5, encoding="utf-8"
)
info_handler.setFormatter(fmt)
info_handler.setLevel(logging.INFO)

# Запрещаем принимать WARNING и ERROR
info_handler.addFilter(lambda r: r.levelno < logging.WARNING)

logger.addHandler(info_handler)


# ─────────────────────────────
#          ERROR лог
# ─────────────────────────────
error_handler = RotatingFileHandler(
    "logs/error.log", maxBytes=5_000_000, backupCount=5, encoding="utf-8"
)
error_handler.setFormatter(fmt)
error_handler.setLevel(logging.WARNING)

logger.addHandler(error_handler)


__all__ = ["logger"]
